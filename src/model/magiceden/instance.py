import random
from eth_account import Account
from loguru import logger
from primp import AsyncClient
from web3 import AsyncWeb3

from src.utils.config import Config
from src.model.magiceden.get_mint_data import get_mint_data
from src.utils.constants import EXPLORER_URL, RPC_URL


class MagicEden:
    def __init__(
        self, account_index: int, config: Config, private_key: str, session: AsyncClient
    ):
        self.account_index = account_index
        self.private_key = private_key
        self.config = config
        self.account = Account.from_key(private_key)
        self.session: AsyncClient = session

        self.web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))

    async def mint(self) -> bool:
        """
        Mint an NFT from the specified contract on MagicEden

        Returns:
            bool: True if minting was successful, False otherwise
        """
        try:
            from src.model.magiceden.abi import ABI

            # Используем to_checksum_address для преобразования адреса в правильный формат
            nft_contract_raw = random.choice(self.config.MAGICEDEN.NFT_CONTRACTS)
            
            nft_contract = self.web3.to_checksum_address(nft_contract_raw)

            logger.info(
                f"[{self.account_index}] | 🚀 Starting MagicEden mint for contract: {nft_contract}"
            )

            # Get mint data from MagicEden API
            mint_data = await get_mint_data(self.session, nft_contract, self.account)

            # Проверяем, не заминтил ли пользователь уже NFT
            if mint_data == "already_minted":
                logger.success(
                    f"[{self.account_index}] | ✅ NFT already minted from MagicEden (max mints per wallet reached)"
                )
                return True

            if mint_data == "all_nfts_minted":
                logger.warning(
                    f"[{self.account_index}] | ⚡️ All NFTs are minted from MagicEden or your balance is low."
                )
                return True

            if not mint_data:
                logger.error(
                    f"[{self.account_index}] | ❌ Failed to get MagicEden mint data for contract: {nft_contract}"
                )
                return False

            # Проверяем наличие данных для транзакции в ответе API
            try:
                # Проверяем, есть ли в ответе данные для прямой транзакции
                if (
                    "steps" in mint_data
                    and len(mint_data["steps"]) > 1
                    and "items" in mint_data["steps"][1]
                ):
                    sale_step = mint_data["steps"][1]
                    if len(sale_step["items"]) > 0 and "data" in sale_step["items"][0]:
                        tx_data = sale_step["items"][0]["data"]

                        # Используем данные транзакции из API
                        # logger.info(
                        #     f"[{self.account_index}] | 📝 Using transaction data from MagicEden API"
                        # )

                        # Получаем необходимые параметры
                        to_address = self.web3.to_checksum_address(tx_data["to"])
                        from_address = self.web3.to_checksum_address(tx_data["from"])
                        data = tx_data["data"]
                        value = (
                            int(tx_data["value"], 16)
                            if tx_data["value"].startswith("0x")
                            else int(tx_data["value"])
                        )

                        # Получаем gas_estimate из API, если доступно
                        gas_estimate = sale_step["items"][0].get("gasEstimate", 500000)

                        # Создаем транзакцию с данными из API
                        base_fee = await self.web3.eth.gas_price
                        priority_fee = int(base_fee * 0.1)  # 10% priority fee
                        max_fee_per_gas = base_fee + priority_fee

                        # Получаем nonce
                        nonce = await self.web3.eth.get_transaction_count(
                            self.account.address
                        )

                        # Создаем транзакцию с обновленными параметрами
                        tx = {
                            "from": from_address,
                            "to": to_address,
                            "value": value,
                            "data": data,
                            "nonce": nonce,
                            "maxFeePerGas": max_fee_per_gas,
                            "maxPriorityFeePerGas": priority_fee,
                            "chainId": 10143,
                        }

                        # Пытаемся оценить газ
                        try:
                            gas_estimate = await self.web3.eth.estimate_gas(tx)
                            gas_with_buffer = int(gas_estimate * 1.2)  # 20% буфер
                            tx["gas"] = gas_with_buffer

                            # logger.info(
                            #     f"[{self.account_index}] | ⛽ Estimated gas: {gas_estimate}, using: {gas_with_buffer}"
                            # )
                        except Exception as e:
                            raise Exception(f"⚠️ Failed to estimate gas: {e}")

                        # Проверяем баланс
                        balance = await self.web3.eth.get_balance(self.account.address)
                        if balance < value:
                            logger.error(
                                f"[{self.account_index}] | ❌ Insufficient balance. "
                                f"Required: {value} wei, Available: {balance} wei"
                            )
                            return False

                        # Подписываем и отправляем транзакцию
                        signed_tx = self.web3.eth.account.sign_transaction(
                            tx, self.private_key
                        )
                        tx_hash = await self.web3.eth.send_raw_transaction(
                            signed_tx.raw_transaction
                        )

                        logger.info(
                            f"[{self.account_index}] | 📤 MagicEden transaction sent: {EXPLORER_URL}{tx_hash.hex()}"
                        )

                        # Ждем подтверждения транзакции
                        tx_receipt = await self.web3.eth.wait_for_transaction_receipt(
                            tx_hash
                        )

                        if tx_receipt["status"] == 1:
                            logger.success(
                                f"[{self.account_index}] | ✅ Successfully minted MagicEden NFT. TX: {EXPLORER_URL}{tx_hash.hex()}"
                            )
                            return True
                        else:
                            logger.error(
                                f"[{self.account_index}] | ❌ MagicEden transaction failed. TX: {EXPLORER_URL}{tx_hash.hex()}"
                            )
                            return False

                # Если не нашли данные для прямой транзакции, используем стандартный подход
                logger.info(f"[{self.account_index}] | 🔄 Using standard mint approach")

                # Extract necessary data from the mint response
                total_price = int(mint_data["path"][0]["totalPrice"])
                if total_price <= 0:
                    # Если цена равна 0, оставляем 0 для бесплатного минта
                    total_price = 0
                    logger.info(
                        f"[{self.account_index}] | 🎁 MagicEden free mint detected"
                    )

                logger.info(
                    f"[{self.account_index}] | 💰 MagicEden mint price: {total_price}"
                )

                # Create contract instance
                contract = self.web3.eth.contract(address=nft_contract, abi=ABI)

                # Get current gas price and calculate max fee
                base_fee = await self.web3.eth.gas_price
                priority_fee = int(base_fee * 0.1)  # 10% priority fee
                max_fee_per_gas = base_fee + priority_fee

                # Build transaction without gas estimate first
                tx_params = {
                    "from": self.account.address,
                    "value": total_price,
                    "nonce": await self.web3.eth.get_transaction_count(
                        self.account.address
                    ),
                    "maxFeePerGas": max_fee_per_gas,
                    "maxPriorityFeePerGas": priority_fee,
                    "chainId": 10143,  # Явно указываем chainId для Monad
                }

                # Пытаемся оценить газ
                try:
                    gas_estimate = await contract.functions.mint(
                        1, self.account.address
                    ).estimate_gas(tx_params)

                    gas_with_buffer = int(gas_estimate * 1.2)
                    logger.info(
                        f"[{self.account_index}] | ⛽ MagicEden gas estimate: {gas_estimate}, using: {gas_with_buffer}"
                    )

                    tx_params["gas"] = gas_with_buffer
                except Exception as e:
                    logger.error(
                        f"[{self.account_index}] | ❌ Failed to estimate gas: {e}. Cannot proceed with transaction."
                    )
                    return False

                # Build the final transaction
                tx = await contract.functions.mint(
                    1, self.account.address
                ).build_transaction(tx_params)

                # Sign transaction
                signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)

                # Send transaction
                tx_hash = await self.web3.eth.send_raw_transaction(
                    signed_tx.raw_transaction
                )
                logger.info(
                    f"[{self.account_index}] | 📤 MagicEden transaction sent: {tx_hash.hex()}"
                )

                # Wait for transaction receipt
                tx_receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)

                if tx_receipt["status"] == 1:
                    logger.success(
                        f"[{self.account_index}] | ✅ Successfully minted MagicEden NFT. TX: {tx_hash.hex()}"
                    )
                    return True
                else:
                    logger.error(
                        f"[{self.account_index}] | ❌ MagicEden transaction failed. TX: {tx_hash.hex()}"
                    )
                    return False

            except (KeyError, IndexError, TypeError) as e:
                logger.error(
                    f"[{self.account_index}] | ❌ Failed to extract data from mint response: {e}. Response: {mint_data}"
                )
                return False

        except Exception as e:
            logger.error(
                f"[{self.account_index}] | ❌ Error minting MagicEden NFT: {e}"
            )
            return False
