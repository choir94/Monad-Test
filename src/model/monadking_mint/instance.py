import asyncio
import random
from eth_account import Account
from primp import AsyncClient
from web3 import AsyncWeb3
from web3.contract import Contract

from src.utils.constants import EXPLORER_URL, RPC_URL
from src.utils.config import Config
from loguru import logger

# ABI для Monad King NFT на основе транзакций
MONAD_KING_ABI = [
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
            {"internalType": "address", "name": "_claimer", "type": "address"},
        ],
        "name": "getSupplyClaimedByWallet",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_owner", "type": "address"},
        ],
        "name": "tokensOfOwner",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "receiver", "type": "address"},
            {"internalType": "uint256", "name": "quantity", "type": "uint256"},
            {"internalType": "address", "name": "currency", "type": "address"},
            {"internalType": "uint256", "name": "pricePerToken", "type": "uint256"},
            {
                "internalType": "tuple",
                "name": "allowlistProof",
                "type": "tuple",
                "components": [
                    {"internalType": "bytes32[]", "name": "proof", "type": "bytes32[]"},
                    {
                        "internalType": "uint256",
                        "name": "quantityLimitPerWallet",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "pricePerToken",
                        "type": "uint256",
                    },
                    {"internalType": "address", "name": "currency", "type": "address"},
                ],
            },
            {"internalType": "bytes", "name": "data", "type": "bytes"},
        ],
        "name": "claim",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
]


class Monadking:
    def __init__(self, account_index: int, private_key: str, config: Config):
        self.account_index = account_index
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.config = config
        self.nft_contract_address = "0x5DCC4Cc8F56295Cb486809C77d476B2ea09a6938"
        self.unlocked_contract_address = "0xeC5Fc06e3C1D5d320199f1930cE3c3de9B262570"
        self.web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))
        self.nft_contract = self.web3.eth.contract(
            address=self.nft_contract_address, abi=MONAD_KING_ABI
        )
        self.unlocked_contract = self.web3.eth.contract(
            address=self.unlocked_contract_address, abi=MONAD_KING_ABI
        )

    async def get_nft_balance(self, contract=None) -> int:
        """
        Проверяет баланс NFT у аккаунта
        """
        if contract is None:
            contract = self.nft_contract
            contract_name = "Monad King"
        else:
            contract_name = "Unlocked Monad"

        try:
            # Метод 1: Пробуем использовать tokensOfOwner
            try:
                tokens = await contract.functions.tokensOfOwner(
                    self.account.address
                ).call()
                logger.info(
                    f"[{self.account_index}] {contract_name} NFTs owned: {len(tokens)}"
                )
                return len(tokens)
            except Exception as e:
                logger.debug(f"[{self.account_index}] tokensOfOwner not available: {e}")

            # Метод 2: Стандартный balanceOf
            balance = await contract.functions.balanceOf(self.account.address, 0).call()

            return balance

        except Exception as e:
            logger.error(
                f"[{self.account_index}] Error checking {contract_name} NFT balance: {e}"
            )
            return 0

    async def mint(self) -> bool:
        """
        Минтит Monad King NFT
        """
        for _ in range(self.config.SETTINGS.ATTEMPTS):
            try:
                # Проверяем баланс NFT
                balance = await self.get_nft_balance()

                random_nft_amount = random.randint(
                    self.config.MONADKING.MAX_AMOUNT_FOR_EACH_ACCOUNT[0],
                    self.config.MONADKING.MAX_AMOUNT_FOR_EACH_ACCOUNT[1],
                )

                if balance >= random_nft_amount:
                    logger.info(
                        f"[{self.account_index}] Already have Monad King NFT. Balance: {balance} NFTS"
                    )
                    return True

                logger.info(f"[{self.account_index}] Minting Monad King NFT")

                # Параметры для минта на основе транзакций
                native_token_address = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
                price = self.web3.to_wei(0.02, "ether")

                # Структура allowlistProof из транзакций
                allowlist_proof = (
                    [],  # пустой proof
                    0,  # quantityLimitPerWallet = 0
                    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,  # pricePerToken (max uint256)
                    "0x0000000000000000000000000000000000000000",  # currency address
                )

                # Подготавливаем транзакцию минта
                mint_txn = await self.nft_contract.functions.claim(
                    self.account.address,  # receiver
                    1,  # quantity
                    native_token_address,  # currency
                    price,  # pricePerToken
                    allowlist_proof,  # allowlistProof
                    b"",  # data
                ).build_transaction(
                    {
                        "from": self.account.address,
                        "value": price,
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
                        f"[{self.account_index}] Successfully minted Monad King NFT. TX: {EXPLORER_URL}{tx_hash.hex()}"
                    )
                    return True
                else:
                    logger.error(
                        f"[{self.account_index}] Failed to mint Monad King NFT. TX: {EXPLORER_URL}{tx_hash.hex()}"
                    )
                    return False

            except Exception as e:
                random_pause = random.randint(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in mint on Monad King: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)

        return False

    async def mint_unlocked(self) -> bool:
        """
        Минтит Unlocked Monad NFT
        """
        for _ in range(self.config.SETTINGS.ATTEMPTS):
            try:
                # Проверяем баланс NFT
                balance = await self.get_nft_balance(self.unlocked_contract)

                random_nft_amount = random.randint(
                    self.config.MONADKING.MAX_AMOUNT_FOR_EACH_ACCOUNT[0],
                    self.config.MONADKING.MAX_AMOUNT_FOR_EACH_ACCOUNT[1],
                )

                if balance >= random_nft_amount:
                    logger.info(
                        f"[{self.account_index}] Already have Unlocked Monad NFT. Balance: {balance} NFTS"
                    )
                    return True

                logger.info(f"[{self.account_index}] Minting Unlocked Monad NFT")

                # Параметры для минта на основе транзакций
                native_token_address = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
                price = self.web3.to_wei(
                    0.05, "ether"
                )  # 0.05 ETH based on the transaction

                # Структура allowlistProof из транзакций
                allowlist_proof = (
                    [],  # пустой proof
                    0,  # quantityLimitPerWallet = 0
                    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,  # pricePerToken (max uint256)
                    "0x0000000000000000000000000000000000000000",  # currency address
                )

                # Подготавливаем транзакцию минта
                mint_txn = await self.unlocked_contract.functions.claim(
                    self.account.address,  # receiver
                    1,  # quantity
                    native_token_address,  # currency
                    price,  # pricePerToken
                    allowlist_proof,  # allowlistProof
                    b"",  # data
                ).build_transaction(
                    {
                        "from": self.account.address,
                        "value": price,
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
                        f"[{self.account_index}] Successfully minted Unlocked Monad NFT. TX: {EXPLORER_URL}{tx_hash.hex()}"
                    )
                    return True
                else:
                    logger.error(
                        f"[{self.account_index}] Failed to mint Unlocked Monad NFT. TX: {EXPLORER_URL}{tx_hash.hex()}"
                    )
                    return False

            except Exception as e:
                random_pause = random.randint(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in mint on Unlocked Monad: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)

        return False
