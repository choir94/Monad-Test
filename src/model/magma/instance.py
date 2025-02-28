import asyncio
import random
from eth_account import Account
from primp import AsyncClient
from web3 import AsyncWeb3, Web3
from loguru import logger
from typing import Dict

from src.utils.config import Config
from src.utils.constants import RPC_URL, EXPLORER_URL
from .constants import STAKE_ADDRESS, STAKE_ABI


class Magma:
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

    async def get_gas_params(self) -> Dict[str, int]:
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

    async def estimate_gas(self, transaction: dict) -> int:
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

    async def stake_mon(self, amount: float = 0.0001):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                random_amount = round(
                    random.uniform(
                        self.config.MAGMA.AMOUNT_TO_STAKE[0],
                        self.config.MAGMA.AMOUNT_TO_STAKE[1],
                    ),
                    5,
                )
                logger.info(
                    f"[{self.account_index}] Staking {random_amount} MON on Magma"
                )

                amount_wei = Web3.to_wei(random_amount, "ether")
                gas_params = await self.get_gas_params()

                # Создаем базовую транзакцию для оценки газа
                transaction = {
                    "from": self.account.address,
                    "to": STAKE_ADDRESS,
                    "data": "0xd5575982",
                    "value": amount_wei,
                    "chainId": 10143,
                    "type": 2,
                }

                # Оцениваем газ
                estimated_gas = await self.estimate_gas(transaction)
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
                    f"[{self.account_index}] Successfully staked {random_amount} MON on Magma. TX: {EXPLORER_URL}{tx_hash.hex()}"
                )
                return True

            except Exception as e:
                random_pause = random.randint(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in stake_mon on Magma: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)
                continue

        return False
