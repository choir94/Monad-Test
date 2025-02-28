from dataclasses import dataclass
from loguru import logger
from web3 import AsyncWeb3
import asyncio
from typing import List
import random

from src.utils.config import Config


@dataclass
class WalletInfo:
    address: str
    private_key: str
    balance_wei: int
    balance_eth: float


@dataclass
class WalletGroup:
    main_wallet: WalletInfo
    farm_wallets: List[WalletInfo]
    target_balance: float

    @property
    def total_balance(self) -> float:
        """Calculate total balance of main + farm wallets"""
        return self.main_wallet.balance_eth + sum(
            w.balance_eth for w in self.farm_wallets
        )


async def get_monad_balance(
    web3: AsyncWeb3, address: str
) -> tuple[int, float] | tuple[None, None]:
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


async def process_single_transfer(
    web3: AsyncWeb3,
    farm_wallet: WalletInfo,
    main_address: str,
    semaphore: asyncio.Semaphore,
    config: Config,
) -> bool:
    """Process a single transfer from farm wallet to main wallet."""
    async with semaphore:
        try:
            # Get the nonce for this wallet
            nonce = await web3.eth.get_transaction_count(farm_wallet.address)

            # Create transaction
            transaction = {
                "from": farm_wallet.address,
                "to": main_address,
                "value": farm_wallet.balance_wei,  # Send entire balance
                "nonce": nonce,
                "gasPrice": await web3.eth.gas_price,
            }

            # Estimate gas and update transaction
            gas = await web3.eth.estimate_gas(transaction)
            transaction["gas"] = gas

            # Adjust value to account for gas cost
            gas_cost = gas * transaction["gasPrice"]
            transaction["value"] = farm_wallet.balance_wei - gas_cost

            # Sign and send transaction
            signed_txn = web3.eth.account.sign_transaction(
                transaction, farm_wallet.private_key
            )
            tx_hash = await web3.eth.send_raw_transaction(signed_txn.raw_transaction)

            # Wait for transaction receipt
            receipt = await web3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt["status"] == 1:
                logger.success(
                    f"Successfully transferred {web3.from_wei(transaction['value'], 'ether')} "
                    f"MON from {farm_wallet.address[:8]}... to {main_address[:8]}..."
                )
                return True
            else:
                logger.error(f"Transaction failed for {farm_wallet.address[:8]}...")
                return False

        except Exception as e:
            logger.error(
                f"Error processing transfer from {farm_wallet.address[:8]}...: {str(e)}"
            )
            return False
