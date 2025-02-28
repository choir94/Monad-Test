from web3 import AsyncWeb3
from eth_account import Account
from loguru import logger
from typing import Optional, Tuple
from dataclasses import dataclass
from threading import Lock

from src.utils.constants import RPC_URL
from src.utils.config import Config


@dataclass
class WalletInfo:
    account_index: int
    private_key: str
    address: str
    balance: float
    transactions: int


class WalletStats:
    def __init__(self, config: Config):
        # Используем публичную RPC ноду Base
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))
        self.config = config
        self._lock = Lock()

    async def get_wallet_stats(
        self, private_key: str, account_index: int
    ) -> Optional[bool]:
        """
        Получает статистику кошелька и сохраняет в конфиг

        Args:
            private_key: Приватный ключ кошелька
            account_index: Индекс аккаунта

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            # Получаем адрес из приватного ключа
            account = Account.from_key(private_key)
            address = account.address

            # Получаем баланс
            balance_wei = await self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, "ether")

            # Получаем количество транзакций (nonce)
            tx_count = await self.w3.eth.get_transaction_count(address)

            wallet_info = WalletInfo(
                account_index=account_index,
                private_key=private_key,
                address=address,
                balance=float(balance_eth),
                transactions=tx_count,
            )

            with self._lock:
                self.config.WALLETS.wallets.append(wallet_info)

            logger.info(
                f"Wallet {address}: Balance = {balance_eth:.4f} MON, "
                f"Transactions = {tx_count}"
            )

            return True

        except Exception as e:
            logger.error(f"Error getting wallet stats: {e}")
            return False
