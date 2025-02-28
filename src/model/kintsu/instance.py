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
from .constants import STAKE_ADDRESS, STAKE_ABI


class Kintsu:
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

    async def get_gas_params(self) -> Dict[str, int]:
        """Get current gas parameters from the network."""
        latest_block = await self.web3.eth.get_block("latest")
        base_fee = latest_block["baseFeePerGas"]
        max_priority_fee = await self.web3.eth.max_priority_fee

        # Calculate maxFeePerGas (base fee + priority fee)
        max_fee = base_fee + max_priority_fee

        return {
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": max_priority_fee,
        }

    async def estimate_gas(self, transaction: dict) -> int:
        """Estimate gas for transaction and add some buffer."""
        try:
            estimated = await self.web3.eth.estimate_gas(transaction)
            # Add 10% to estimated gas for safety
            return int(estimated * 1.1)
        except Exception as e:
            logger.warning(
                f"[{self.account_index}] Error estimating gas: {e}. Using default gas limit"
            )
            raise e

    async def stake_mon(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                # Use a higher minimum amount to avoid "Minimum stake" error
                # Based on the transaction you shared (0.04072 MON)
                random_amount = round(
                    random.uniform(
                        max(
                            0.01, self.config.KINTSU.AMOUNT_TO_STAKE[0]
                        ),  # Ensure minimum of 0   .01
                        max(
                            0.015, self.config.KINTSU.AMOUNT_TO_STAKE[1]
                        ),  # Ensure minimum of 0.015
                    ),
                    5,
                )
                logger.info(
                    f"[{self.account_index}] Staking {random_amount} MON on Kintsu"
                )

                # Create synchronous contract version for encoding data
                contract = Web3().eth.contract(address=STAKE_ADDRESS, abi=STAKE_ABI)
                amount_wei = Web3.to_wei(random_amount, "ether")
                gas_params = await self.get_gas_params()

                # Create base transaction for gas estimation
                transaction = {
                    "from": self.account.address,
                    "to": STAKE_ADDRESS,
                    "value": amount_wei,
                    "data": contract.functions.stake()._encode_transaction_data(),
                    "chainId": 10143,
                    "type": 2,
                }

                # Estimate gas
                estimated_gas = await self.estimate_gas(transaction)
                logger.info(f"[{self.account_index}] Estimated gas: {estimated_gas}")

                # Add remaining transaction parameters
                transaction.update(
                    {
                        "nonce": await self.web3.eth.get_transaction_count(
                            self.account.address,
                            "latest",
                        ),
                        "gas": estimated_gas,
                        **gas_params,
                    }
                )

                signed_txn = self.web3.eth.account.sign_transaction(
                    transaction, self.private_key
                )
                tx_hash = await self.web3.eth.send_raw_transaction(
                    signed_txn.raw_transaction
                )

                # Wait for transaction confirmation
                logger.info(
                    f"[{self.account_index}] Waiting for transaction confirmation..."
                )
                await self.web3.eth.wait_for_transaction_receipt(tx_hash)

                logger.success(
                    f"[{self.account_index}] Successfully staked {random_amount} MON on Kintsu. TX: {EXPLORER_URL}{tx_hash.hex()}"
                )
                return True

            except Exception as e:
                error_message = str(e)
                if "Minimum stake" in error_message:
                    logger.error(
                        f"[{self.account_index}] Error: Minimum stake requirement not met. Trying with a higher amount."
                    )
                    # Update config values to use higher amounts
                    self.config.KINTSU.AMOUNT_TO_STAKE = (0.04, 0.05)
                    continue

                random_pause = random.randint(
                    self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                    self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
                )
                logger.error(
                    f"[{self.account_index}] | Error in stake_mon on Kintsu: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)
        return False

    async def get_token_balance(self, token_symbol: str) -> Decimal:
        """Get balance of specified token."""
        if token_symbol == "native":
            balance_wei = await self.web3.eth.get_balance(self.account.address)
            return Decimal(balance_wei) / Decimal(10**18)
