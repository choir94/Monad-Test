import asyncio
from loguru import logger
from web3 import AsyncHTTPProvider, AsyncWeb3
from typing import List
import random

from src.utils.config import Config
from src.utils.constants import RPC_URL
from .utils import get_monad_balance, WalletInfo


class DisperseFromOneWallet:
    def __init__(
        self, farm_key: str, main_keys: List[str], proxies: List[str], config: Config
    ):
        self.farm_key = farm_key
        self.main_keys = main_keys
        self.proxies = proxies
        self.config = config
        self.web3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))

    async def disperse(self):
        try:
            logger.info("Starting disperse from one wallet process")
            # Get farm wallet account
            farm_account = self.web3.eth.account.from_key(self.farm_key)
            logger.info(f"Farm wallet address: {farm_account.address[:8]}...")

            success_count = 0
            total_transfers = 0

            # Get initial nonce
            nonce = await self.web3.eth.get_transaction_count(farm_account.address)

            logger.info(f"Processing {len(self.main_keys)} main wallets")
            for index, main_key in enumerate(self.main_keys):
                logger.info(f"Processing wallet {index+1}/{len(self.main_keys)}")

                # Check farm wallet balance for each iteration
                farm_balance_wei, farm_balance_eth = await get_monad_balance(
                    self.web3, farm_account.address
                )
                logger.info(f"Farm wallet balance: {farm_balance_eth} MON")

                if farm_balance_eth is None or farm_balance_eth <= 0:
                    logger.error("Farm wallet has no balance")
                    break

                # Get main wallet info
                main_account = self.web3.eth.account.from_key(main_key)
                logger.info(
                    f"Checking balance for wallet {main_account.address[:8]}..."
                )
                main_balance_wei, main_balance_eth = await get_monad_balance(
                    self.web3, main_account.address
                )

                if main_balance_eth is None:
                    logger.error(
                        f"Failed to get balance for wallet {main_account.address[:8]}..."
                    )
                    continue

                logger.info(
                    f"Wallet {main_account.address[:8]}... balance: {main_balance_eth} MON"
                )

                # Generate random target balance
                min_balance_range = self.config.DISPERSE.MIN_BALANCE_FOR_DISPERSE
                target_balance = random.uniform(
                    min_balance_range[0], min_balance_range[1]
                )
                logger.info(f"Target balance: {target_balance} MON")

                # Skip if wallet already has enough balance
                if main_balance_eth >= target_balance:
                    logger.info(
                        f"Wallet {main_account.address[:8]}... already has sufficient balance: {main_balance_eth} MON"
                    )
                    continue

                amount_needed = target_balance - main_balance_eth
                logger.info(f"Amount needed: {amount_needed} MON")

                # Check if farm wallet has enough balance
                if amount_needed > farm_balance_eth:
                    logger.warning(
                        f"Farm wallet doesn't have enough balance ({farm_balance_eth} MON) for transfer of {amount_needed} MON"
                    )
                    continue

                # Process transfer
                logger.info(
                    f"Initiating transfer of {amount_needed} MON to {main_account.address[:8]}..."
                )
                success = await self.transfer_to_wallet(
                    farm_account, main_account.address, amount_needed, nonce
                )

                if success:
                    success_count += 1
                    nonce += 1
                    logger.info(f"Transfer successful. New nonce: {nonce}")
                else:
                    logger.error("Transfer failed")

                total_transfers += 1

            if total_transfers == 0:
                logger.info("No transfers needed")
                return True

            logger.info(
                f"Disperse completed. Success: {success_count}/{total_transfers} transfers"
            )
            return success_count > 0

        except Exception as e:
            logger.error(f"Error in disperse from one: {str(e)}")
            return False

    async def transfer_to_wallet(
        self,
        farm_account,
        to_address: str,
        amount_eth: float,
        nonce: int,
    ) -> bool:
        """Process a single transfer from farm wallet to main wallet."""
        try:
            amount_wei = self.web3.to_wei(amount_eth, "ether")

            # Create transaction
            transaction = {
                "from": farm_account.address,
                "to": to_address,
                "value": amount_wei,
                "nonce": nonce,
                "gasPrice": await self.web3.eth.gas_price,
            }

            # Estimate gas and update transaction
            gas = await self.web3.eth.estimate_gas(transaction)
            transaction["gas"] = gas

            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, self.farm_key
            )
            tx_hash = await self.web3.eth.send_raw_transaction(
                signed_txn.raw_transaction
            )

            # Wait for transaction receipt
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt["status"] == 1:
                random_pause = random.uniform(
                    self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                    self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                )
                logger.success(
                    f"Successfully transferred {amount_eth} MON to {to_address[:8]}... {random_pause} seconds pause"
                )
                await asyncio.sleep(random_pause)
                return True
            else:
                logger.error(f"Transaction failed for {to_address[:8]}...")
                return False

        except Exception as e:
            logger.error(f"Error processing transfer to {to_address[:8]}...: {str(e)}")
            return False
