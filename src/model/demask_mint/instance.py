import asyncio
import random
from eth_account import Account
from primp import AsyncClient
from web3 import AsyncWeb3
from web3.contract import Contract

from src.utils.constants import EXPLORER_URL, RPC_URL
from src.utils.config import Config
from loguru import logger

# Обновляем ABI для контракта NFT с дополнительными методами
ERC1155_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "account", "type": "address"},
            {"internalType": "uint256", "name": "id", "type": "uint256"},
        ],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32[]", "name": "proof", "type": "bytes32[]"},
            {"internalType": "uint256", "name": "limit", "type": "uint256"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
        ],
        "name": "buy",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "name": "mintedCountPerWallet",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]


class Demask:
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

        self.nft_contract_address = "0x2CDd146Aa75FFA605ff7c5Cc5f62D3B52C140f9c"  # Updated contract address for DeMask
        self.nft_contract: Contract = self.web3.eth.contract(
            address=self.nft_contract_address, abi=ERC1155_ABI
        )

    async def get_nft_balance(self) -> int:
        """
        Проверяет баланс NFT для текущего аккаунта
        Returns:
            int: количество NFT
        """
        try:
            # Пробуем использовать функцию mintedCountPerWallet из контракта
            # Эта функция должна вернуть количество NFT, которые уже минтил пользователь
            stage_id = 0  # Предполагаем, что это первый этап (может потребоваться корректировка)

            balance = await self.nft_contract.functions.mintedCountPerWallet(
                self.account.address, stage_id
            ).call()

            logger.info(f"[{self.account_index}] DeMask NFT balance: {balance}")
            return balance
        except Exception as e:
            # Если первый метод не сработал, пробуем стандартный balanceOf
            try:
                token_id = 46917  # ID токена из транзакции
                balance = await self.nft_contract.functions.balanceOf(
                    self.account.address, token_id
                ).call()

                logger.info(
                    f"[{self.account_index}] DeMask NFT balance (via balanceOf): {balance}"
                )
                return balance
            except Exception as e2:
                # Если оба метода не сработали, логируем ошибки и возвращаем 0
                logger.warning(
                    f"[{self.account_index}] Error checking NFT balance via mintedCountPerWallet: {e}"
                )
                logger.warning(
                    f"[{self.account_index}] Error checking NFT balance via balanceOf: {e2}"
                )

                # Проверяем историю транзакций как последний вариант
                try:
                    # Получаем историю транзакций для адреса контракта
                    tx_count = await self.web3.eth.get_transaction_count(
                        self.account.address
                    )

                    # Для простоты, проверим только последние 10 транзакций
                    for i in range(max(0, tx_count - 10), tx_count):
                        try:
                            nonce = i
                            tx = await self.web3.eth.get_transaction_by_nonce(
                                self.account.address, nonce
                            )

                            # Если транзакция была к нашему контракту и успешно выполнена
                            if (
                                tx
                                and tx.to
                                and tx.to.lower() == self.nft_contract_address.lower()
                            ):
                                receipt = await self.web3.eth.get_transaction_receipt(
                                    tx.hash
                                )
                                if receipt and receipt.status == 1:
                                    # Нашли успешную транзакцию к контракту NFT
                                    logger.info(
                                        f"[{self.account_index}] Found successful transaction to DeMask contract"
                                    )
                                    return (
                                        1  # Возвращаем 1, что означает NFT уже минтили
                                    )
                        except Exception:
                            continue
                except Exception as e3:
                    logger.warning(
                        f"[{self.account_index}] Error checking transaction history: {e3}"
                    )

                # Если все методы не сработали, возвращаем 0
                return 0

    async def mint(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                balance = await self.get_nft_balance()

                random_amount = random.randint(
                    self.config.DEMASK.MAX_AMOUNT_FOR_EACH_ACCOUNT[0],
                    self.config.DEMASK.MAX_AMOUNT_FOR_EACH_ACCOUNT[1],
                )

                if balance >= random_amount:
                    logger.success(
                        f"[{self.account_index}] DeMask NFT already minted: {balance} NFTS"
                    )
                    return True

                logger.info(f"[{self.account_index}] Minting DeMask NFT")

                # Подготавливаем транзакцию минта с методом buy
                # Используем пустой proof, limit=1000000, amount=1
                mint_txn = await self.nft_contract.functions.buy(
                    [], 1000000, 1
                ).build_transaction(
                    {
                        "from": self.account.address,
                        "value": self.web3.to_wei(0.1, "ether"),  # Оплата 0.1 MON
                        "nonce": await self.web3.eth.get_transaction_count(
                            self.account.address
                        ),
                        "maxFeePerGas": await self.web3.eth.gas_price,
                        "maxPriorityFeePerGas": await self.web3.eth.gas_price,
                    }
                )

                # Подписываем транзакцию
                signed_txn = self.web3.eth.account.sign_transaction(
                    mint_txn, self.private_key
                )

                # Отправляем транзакцию
                tx_hash = await self.web3.eth.send_raw_transaction(
                    signed_txn.raw_transaction
                )

                # Ждем подтверждения
                receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)

                if receipt["status"] == 1:
                    logger.success(
                        f"[{self.account_index}] Successfully minted DeMask NFT. TX: {EXPLORER_URL}{tx_hash.hex()}"
                    )
                    return True
                else:
                    logger.error(
                        f"[{self.account_index}] Failed to mint DeMask NFT. TX: {EXPLORER_URL}{tx_hash.hex()}"
                    )
                    return False

            except Exception as e:
                random_pause = random.randint(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in mint on DeMask: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)

        return False
