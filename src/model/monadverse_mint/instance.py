import asyncio
import random
from eth_account import Account
from primp import AsyncClient
from web3 import AsyncWeb3
from web3.contract import Contract

from src.utils.constants import EXPLORER_URL, RPC_URL
from src.utils.config import Config
from loguru import logger

# Обновляем ABI для ERC1155
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
        "inputs": [],
        "name": "mint",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
]


class MonadverseMint:
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

        self.nft_contract_address = "0x3A9acc3Be6E9678FA5D23810488c37a3192aaf75"
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
            balance = await self.nft_contract.functions.balanceOf(
                self.account.address, 2  # ID токена из транзакции
            ).call()

            return balance
        except Exception as e:
            logger.error(f"[{self.account_index}] Error checking NFT balance: {e}")
            return 0

    async def mint(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                balance = await self.get_nft_balance()

                if balance > 0:
                    logger.success(
                        f"[{self.account_index}] Monadverse NFT already minted"
                    )
                    return True

                logger.info(f"[{self.account_index}] Minting Monadverse NFT")

                # Подготавливаем транзакцию минта
                mint_txn = await self.nft_contract.functions.mint().build_transaction(
                    {
                        "from": self.account.address,
                        "value": self.web3.to_wei(
                            0.5, "ether"
                        ),  # Обновляем оплату до 0.5 MON
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
                        f"[{self.account_index}] Successfully minted Monadverse NFT. TX: {EXPLORER_URL}{tx_hash.hex()}"
                    )
                    return True
                else:
                    logger.error(
                        f"[{self.account_index}] Failed to mint Monadverse NFT. TX: {EXPLORER_URL}{tx_hash.hex()}"
                    )
                    return False

            except Exception as e:
                random_pause = random.randint(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in mint on Monadverse: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)

        return False
