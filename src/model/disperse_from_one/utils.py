from dataclasses import dataclass
from loguru import logger
from web3 import AsyncWeb3
import asyncio
from typing import List, Tuple


@dataclass
class WalletInfo:
    address: str
    private_key: str
    balance_wei: int
    balance_eth: float


async def get_monad_balance(
    web3: AsyncWeb3, address: str
) -> Tuple[int, float] | Tuple[None, None]:
    """Get native MON balance in both wei and ether."""
    try:
        balance_wei = await web3.eth.get_balance(address)
        balance_eth = float(web3.from_wei(balance_wei, "ether"))
        return balance_wei, balance_eth
    except Exception as e:
        logger.error(f"Failed to get MON balance: {str(e)}")
        return None, None


async def process_wallet(
    web3: AsyncWeb3, private_key: str, semaphore: asyncio.Semaphore
) -> WalletInfo | None:
    """Process single wallet with semaphore for thread safety."""
    async with semaphore:
        try:
            account = web3.eth.account.from_key(private_key)
            address = account.address

            balance_wei, balance_eth = await get_monad_balance(web3, address)
            if balance_wei is not None:
                return WalletInfo(
                    address=address,
                    private_key=private_key,
                    balance_wei=balance_wei,
                    balance_eth=balance_eth,
                )
        except Exception as e:
            logger.error(f"Error processing wallet {private_key[:8]}...: {e}")
        return None


async def get_all_balances(
    web3: AsyncWeb3, private_keys: List[str], max_threads: int
) -> List[WalletInfo]:
    """Get balances for multiple wallets asynchronously with thread limit."""
    semaphore = asyncio.Semaphore(max_threads)

    # Create tasks for all wallets
    tasks = [
        process_wallet(web3, private_key, semaphore) for private_key in private_keys
    ]

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)

    # Filter out None results and return valid WalletInfo objects
    return [result for result in results if result is not None] 