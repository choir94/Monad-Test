from loguru import logger
from web3 import AsyncHTTPProvider, AsyncWeb3
import random
import asyncio
from typing import List

from src.utils.constants import RPC_URL
from src.utils.config import Config
from .utils import get_all_balances, WalletInfo, WalletGroup, process_single_transfer


class DisperseOneOne:
    def __init__(self, main_keys, farm_keys, proxies, config):
        self.main_keys = main_keys
        self.farm_keys = farm_keys
        self.proxies = proxies
        self.config = config
        self.web3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))

    async def disperse(self):
        try:
            main_balances = await self.get_wallets_info(
                web3=self.web3, keys=self.main_keys
            )
            farm_balances = await self.get_wallets_info(
                web3=self.web3, keys=self.farm_keys
            )

            wallet_groups = await self.make_wallets_pairs_for_disperse(
                main_balances, farm_balances
            )

            if not wallet_groups:
                logger.error(
                    "Failed to create wallet pairs for disperse or all wallets have enough balances"
                )
                return False

            success = await self.start_disperse(wallet_groups)
            return success

        except Exception as e:
            logger.error(f"Error in disperse one to one: {e}")
            return False

    async def process_wallet_group(
        self, wallet_group: WalletGroup, semaphore: asyncio.Semaphore, config: Config
    ) -> bool:
        """Process all transfers for a single wallet group sequentially."""
        results = []

        # Process transfers one by one within the group
        for farm_wallet in wallet_group.farm_wallets:
            result = await process_single_transfer(
                self.web3,
                farm_wallet,
                wallet_group.main_wallet.address,
                semaphore,
                config,
            )
            results.append(result)

            # Add pause between transfers within the group
            if result:  # If transfer was successful
                random_pause = random.uniform(
                    config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                    config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                )
                logger.info(
                    f"Transfer completed. Pausing for {random_pause:.2f} seconds..."
                )
                await asyncio.sleep(random_pause)

        return all(results)  # Return True only if all transfers succeeded

    async def start_disperse(self, wallet_groups: List[WalletGroup]) -> bool:
        """Start the disperse process for all wallet groups concurrently."""
        try:
            semaphore = asyncio.Semaphore(self.config.SETTINGS.THREADS)

            # Create tasks for each wallet group to process concurrently
            tasks = [
                self.process_wallet_group(group, semaphore, self.config)
                for group in wallet_groups
            ]

            # Execute all tasks and get results
            results = await asyncio.gather(*tasks)

            # Check if all groups were processed successfully
            success_count = sum(1 for result in results if result)
            total_count = len(wallet_groups)

            logger.info(
                f"Disperse completed. Success: {success_count}/{total_count} groups"
            )

            return success_count > 0

        except Exception as e:
            logger.error(f"Error in start_disperse: {str(e)}")
            return False

    async def get_wallets_info(self, web3: AsyncWeb3, keys: list[str]):
        return await get_all_balances(
            web3=web3, private_keys=keys, max_threads=self.config.SETTINGS.THREADS
        )

    async def make_wallets_pairs_for_disperse(
        self, main_wallets: List[WalletInfo], farm_wallets: List[WalletInfo]
    ) -> List[WalletGroup]:
        """Create groups of wallets for dispersing funds."""
        # Filter out farm wallets with zero balance and copy the list
        available_farm_wallets = [
            wallet for wallet in farm_wallets if wallet.balance_eth > 0
        ]
        wallet_groups = []

        min_balance_range = self.config.DISPERSE.MIN_BALANCE_FOR_DISPERSE

        for main_wallet in main_wallets:
            # Get random target balance between min and max from config
            target_balance = random.uniform(min_balance_range[0], min_balance_range[1])

            # Skip if main wallet already has enough balance
            if main_wallet.balance_eth >= target_balance:
                continue

            needed_balance = target_balance - main_wallet.balance_eth
            current_farm_wallets = []
            current_sum = 0

            # Try to find enough farm wallets to reach target balance
            for farm_wallet in available_farm_wallets[:]:
                current_farm_wallets.append(farm_wallet)
                current_sum += farm_wallet.balance_eth
                available_farm_wallets.remove(farm_wallet)

                if current_sum >= needed_balance:
                    break

            # Create group even if we didn't reach target balance but have some funds
            if current_sum > 0:
                group = WalletGroup(
                    main_wallet=main_wallet,
                    farm_wallets=current_farm_wallets,
                    target_balance=target_balance,
                )
                wallet_groups.append(group)
                if current_sum < needed_balance:
                    logger.warning(
                        f"Insufficient balance for main wallet {main_wallet.address[:8]}... "
                        f"(needed: {needed_balance}, found: {current_sum}, but proceeding anyway)"
                    )
            else:
                # Return farm wallets back to pool if we couldn't get any balance
                available_farm_wallets.extend(current_farm_wallets)
                logger.warning(
                    f"No available farm wallets with balance for main wallet "
                    f"{main_wallet.address[:8]}..."
                )

        return wallet_groups
