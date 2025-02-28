import asyncio
import random
from typing import Dict
from eth_account import Account
from eth_account.messages import encode_defunct
from loguru import logger
from primp import AsyncClient
from web3 import AsyncWeb3, Web3
from src.utils.config import Config
from src.utils.constants import RPC_URL, EXPLORER_URL
from .constants import (
    FAUCET_ADDRESS,
    FAUCET_ABI,
    bmBTC,
    TOKEN_ABI,
    SPENDER_ADDRESS,
    LENDING_ABI,
    MARKET_PARAMS,
)


class Bima:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        config: Config,
        session: AsyncClient,
    ):
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.config = config
        self.session = session

        self.account: Account = Account.from_key(private_key=private_key)
        self.web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))

    async def login(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                message_to_sign, timestamp = await self._get_nonce()

                if not message_to_sign:
                    raise Exception("Message to sign is empty")

                signature = "0x" + self._get_signature(message_to_sign)

                headers = {
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "fr-CH,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                    "Origin": "https://bima.money",
                    "Referer": "https://bima.money/",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
                    "address": self.account.address,
                    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                }

                json_data = {
                    "signature": signature,
                    "timestamp": int(timestamp),
                }

                response = await self.session.post(
                    "https://mainnet-api-v1.bima.money/bima/wallet/connect",
                    headers=headers,
                    json=json_data,
                )

                if response.status_code != 200:
                    raise Exception(f"Status code: {response.status_code}")

                logger.success(f"[{self.account_index}] Successfully logged in to Bima")
                return True

            except Exception as e:
                random_pause = random.uniform(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in login Bima: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)
                continue
        return False

    async def lend(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                logger.info(f"[{self.account_index}] Lending on Bima...")

                # Создаем контракт токена
                token_contract = self.web3.eth.contract(address=bmBTC, abi=TOKEN_ABI)

                # Получаем баланс токена
                balance = await token_contract.functions.balanceOf(
                    self.account.address
                ).call()

                if balance == 0:
                    raise Exception("Token balance is 0")

                logger.info(
                    f"[{self.account_index}] Token balance: {Web3.from_wei(balance, 'ether')} bmBTC"
                )

                # Вычисляем сумму для лендинга
                percent = random.uniform(
                    self.config.BIMA.PERCENT_OF_BALANCE_TO_LEND[0],
                    self.config.BIMA.PERCENT_OF_BALANCE_TO_LEND[1],
                )

                # Округляем до 4 знаков после запятой для логов
                amount_to_show = round(
                    Web3.from_wei(balance * percent / 100, "ether"), 4
                )
                amount_to_lend = int(
                    balance * percent / 100
                )  # для транзакции оставляем точное значение

                logger.info(
                    f"[{self.account_index}] Approving {amount_to_show} bmBTC for lending"
                )

                # 1. Сначала делаем approve
                await self._approve_token(amount_to_lend)

                # Пауза между транзакциями
                random_pause = random.uniform(
                    self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                    self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                )
                logger.info(
                    f"[{self.account_index}] Sleeping for {random_pause} seconds after approve"
                )
                await asyncio.sleep(random_pause)

                # 2. Затем делаем supplyCollateral
                logger.info(f"[{self.account_index}] Supplying collateral...")

                lending_contract = Web3().eth.contract(
                    address=SPENDER_ADDRESS, abi=LENDING_ABI
                )
                gas_params = await self._get_gas_params()

                transaction = {
                    "from": self.account.address,
                    "to": SPENDER_ADDRESS,
                    "data": lending_contract.functions.supplyCollateral(
                        MARKET_PARAMS,
                        amount_to_lend,
                        self.account.address,
                        "0x",  # пустые данные
                    )._encode_transaction_data(),
                    "chainId": 10143,
                    "type": 2,
                    "value": 0,
                }

                # Оцениваем газ
                estimated_gas = await self._estimate_gas(transaction)
                logger.info(f"[{self.account_index}] Estimated gas: {estimated_gas}")

                # Добавляем остальные параметры транзакции
                transaction.update(
                    {
                        "nonce": await self.web3.eth.get_transaction_count(
                            self.account.address,
                            "latest",
                        ),
                        "gas": estimated_gas,
                        **gas_params,
                    }
                )

                signed_txn = self.web3.eth.account.sign_transaction(
                    transaction, self.private_key
                )
                tx_hash = await self.web3.eth.send_raw_transaction(
                    signed_txn.raw_transaction
                )

                # Ждем подтверждения транзакции
                logger.info(
                    f"[{self.account_index}] Waiting for supply confirmation..."
                )
                await self.web3.eth.wait_for_transaction_receipt(tx_hash)

                logger.success(
                    f"[{self.account_index}] Successfully supplied collateral. TX: {EXPLORER_URL}{tx_hash.hex()}"
                )
                return True

            except Exception as e:
                random_pause = random.uniform(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in lend Bima: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)
                continue

        return False

    async def _approve_token(self, amount: int):
        """Helper method to approve token spending"""
        contract = Web3().eth.contract(address=bmBTC, abi=TOKEN_ABI)
        gas_params = await self._get_gas_params()

        transaction = {
            "from": self.account.address,
            "to": bmBTC,
            "data": contract.functions.approve(
                SPENDER_ADDRESS, amount
            )._encode_transaction_data(),
            "chainId": 10143,
            "type": 2,
            "value": 0,
        }

        estimated_gas = await self._estimate_gas(transaction)
        logger.info(f"[{self.account_index}] Estimated gas: {estimated_gas}")

        transaction.update(
            {
                "nonce": await self.web3.eth.get_transaction_count(
                    self.account.address,
                    "latest",
                ),
                "gas": estimated_gas,
                **gas_params,
            }
        )

        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, self.private_key
        )
        tx_hash = await self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)

        logger.info(f"[{self.account_index}] Waiting for approve confirmation...")
        await self.web3.eth.wait_for_transaction_receipt(tx_hash)

        logger.success(
            f"[{self.account_index}] Successfully approved bmBTC for lending. TX: {EXPLORER_URL}{tx_hash.hex()}"
        )

    async def get_faucet_tokens(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                logged = await self.login()
                if not logged:
                    raise Exception("Failed to login to Bima")

                logger.info(
                    f"[{self.account_index}] Getting tokens from Bima faucet..."
                )

                # Создаем синхронную версию контракта для кодирования данных
                contract = Web3().eth.contract(address=FAUCET_ADDRESS, abi=FAUCET_ABI)
                gas_params = await self._get_gas_params()

                # Создаем базовую транзакцию для оценки газа
                transaction = {
                    "from": self.account.address,
                    "to": FAUCET_ADDRESS,
                    "data": contract.functions.getTokens(
                        bmBTC
                    )._encode_transaction_data(),
                    "chainId": 10143,
                    "type": 2,
                    "value": 0,
                }

                # Оцениваем газ
                estimated_gas = await self._estimate_gas(transaction)
                logger.info(f"[{self.account_index}] Estimated gas: {estimated_gas}")

                # Добавляем остальные параметры транзакции
                transaction.update(
                    {
                        "nonce": await self.web3.eth.get_transaction_count(
                            self.account.address,
                            "latest",
                        ),
                        "gas": estimated_gas,
                        **gas_params,
                    }
                )

                signed_txn = self.web3.eth.account.sign_transaction(
                    transaction, self.private_key
                )
                tx_hash = await self.web3.eth.send_raw_transaction(
                    signed_txn.raw_transaction
                )

                # Ждем подтверждения транзакции
                logger.info(
                    f"[{self.account_index}] Waiting for transaction confirmation..."
                )
                await self.web3.eth.wait_for_transaction_receipt(tx_hash)

                logger.success(
                    f"[{self.account_index}] Successfully got tokens from Bima faucet. TX: {EXPLORER_URL}{tx_hash.hex()}"
                )
                return True

            except Exception as e:
                random_pause = random.uniform(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in get_faucet_tokens Bima: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)
                continue
        return False

    async def _get_nonce(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                headers = {
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "fr-CH,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Connection": "keep-alive",
                    "Origin": "https://bima.money",
                    "Referer": "https://bima.money/",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
                    "address": self.account.address,
                    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                }

                response = await self.session.get(
                    "https://mainnet-api-v1.bima.money/bima/wallet/tip_info",
                    headers=headers,
                )

                if response.status_code != 200:
                    raise Exception(f"Status code: {response.status_code}")

                data = response.json()
                return data["data"]["tip_info"], data["data"]["timestamp"]

            except Exception as e:
                random_pause = random.uniform(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in _get_nonce Bima: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)
                continue
        return "", ""

    async def _get_gas_params(self) -> Dict[str, int]:
        """Get current gas parameters from the network."""
        latest_block = await self.web3.eth.get_block("latest")
        base_fee = latest_block["baseFeePerGas"]
        max_priority_fee = await self.web3.eth.max_priority_fee

        # Calculate maxFeePerGas (base fee + priority fee)
        max_fee = base_fee + max_priority_fee

        return {
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": max_priority_fee,
        }

    async def _estimate_gas(self, transaction: dict) -> int:
        """Estimate gas for transaction and add some buffer."""
        try:
            estimated = await self.web3.eth.estimate_gas(transaction)
            # Добавляем 10% к estimated gas для безопасности
            return int(estimated * 1.1)
        except Exception as e:
            logger.warning(
                f"[{self.account_index}] Error estimating gas: {e}. Using default gas limit"
            )
            raise e

    def _get_signature(self, message: str):
        encoded_msg = encode_defunct(text=message)
        signed_msg = Web3().eth.account.sign_message(
            encoded_msg, private_key=self.private_key
        )
        signature = signed_msg.signature.hex()

        return signature


# Welcome to Bima Money!
# 	Click to bind your wallet and accept the Bima Money Terms of Service https://bima.money
# 	This request will not trigger a blockchain transaction or cost any gas fees.
# 	Wallet address: 0x90230C11F89fE1Ea9B70B6910ad1769544b6a2Df
# 	Invite Code:
# 	Timestamp: 1740044586
