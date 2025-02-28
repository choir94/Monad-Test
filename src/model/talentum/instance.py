import asyncio
from decimal import Decimal
import random
from eth_account import Account
from loguru import logger
from web3 import AsyncWeb3, Web3
from primp import AsyncClient
from typing import Dict

from src.utils.config import Config
from src.utils.constants import EXPLORER_URL, RPC_URL


class Talentum:
    def __init__(self, account_index: int, private_key: str, config: Config, session: Session):
        self.account_index = account_index
        self.private_key = private_key
        self.config = config
        self.session = session

        self.web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))
        self.account = Account.from_key(private_key)

    async def login(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                pass
            except Exception as e:
                random_pause = random.randint(
                    self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                    self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
                )
                logger.error(f"[{self.account_index}] Error logging in to Talentum: {e}. Sleeping {random_pause} seconds")
                await asyncio.sleep(random_pause)
        return False
    


