from web3 import AsyncWeb3
from eth_account import Account
import asyncio
from typing import Dict, Optional, List, Tuple
from decimal import Decimal
import random
from loguru import logger
from src.utils.constants import RPC_URL, EXPLORER_URL, ERC20_ABI
from src.model.monad_xyz.constants import IZUMI_ABI, IZUMI_TOKENS, IZUMI_CONTRACT
import time
from src.utils.config import Config

class IzumiDex:
    def __init__(self, private_key: str, proxy: Optional[str] = None, config: Config = None):
        self.web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))
        self.account = Account.from_key(private_key)
        self.proxy = proxy
        self.router_contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(IZUMI_CONTRACT),
            abi=IZUMI_ABI
        )
        self.FEE_TIER = 10000  # 1%
        self.config = config
        
    async def get_gas_params(self) -> Dict[str, int]:
        latest_block = await self.web3.eth.get_block('latest')
        base_fee = latest_block['baseFeePerGas']
        max_priority_fee = await self.web3.eth.max_priority_fee
        max_fee = base_fee + max_priority_fee
        
        return {
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": max_priority_fee,
        }

    def convert_to_wei(self, amount: float, token: str) -> int:
        """Convert amount to wei based on token decimals."""
        if token == "native":
            return self.web3.to_wei(amount, 'ether')
        decimals = IZUMI_TOKENS[token.lower()]["decimals"]
        return int(Decimal(str(amount)) * Decimal(str(10 ** decimals)))

    def convert_from_wei(self, amount: int, token: str) -> float:
        """Convert wei amount back to token units."""
        if token == "native":
            return float(self.web3.from_wei(amount, 'ether'))
        decimals = IZUMI_TOKENS[token.lower()]["decimals"]
        return float(Decimal(str(amount)) / Decimal(str(10 ** decimals)))

    async def get_tokens_with_balance(self) -> List[Tuple[str, float]]:
        """Get list of tokens with non-zero balances."""
        tokens_with_balance = []
        
        # Check native token balance
        native_balance = await self.web3.eth.get_balance(self.account.address)
        if native_balance > 10**14:  # More than 0.0001 MON
            native_amount = float(self.web3.from_wei(native_balance, 'ether'))
            tokens_with_balance.append(("native", native_amount))
        
        # Check other tokens
        for token in IZUMI_TOKENS:
            if token == "wmon":  # Skip WMON as we handle it internally
                continue
            try:
                token_contract = self.web3.eth.contract(
                    address=self.web3.to_checksum_address(IZUMI_TOKENS[token]["address"]),
                    abi=ERC20_ABI
                )
                balance = await token_contract.functions.balanceOf(self.account.address).call()
                
                # Only add tokens with sufficient balance (more than 0.0001 tokens)
                min_amount = 10 ** (IZUMI_TOKENS[token]["decimals"] - 4)
                if balance >= min_amount:
                    decimals = IZUMI_TOKENS[token]["decimals"]
                    amount = float(Decimal(str(balance)) / Decimal(str(10 ** decimals)))
                    tokens_with_balance.append((token, amount))
                    
            except Exception as e:
                logger.error(f"Failed to get balance for {token}: {str(e)}")
                continue
        
        return tokens_with_balance

    async def approve_token(self, token: str, amount: int) -> Optional[str]:
        """Approve token spending for Izumi router."""
        try:
            token_contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(IZUMI_TOKENS[token]["address"]),
                abi=ERC20_ABI
            )
            
            current_allowance = await token_contract.functions.allowance(
                self.account.address,
                IZUMI_CONTRACT
            ).call()
            
            if current_allowance >= amount:
                logger.info(f"Allowance sufficient for {token}")
                return None
            
            nonce = await self.web3.eth.get_transaction_count(self.account.address)
            gas_params = await self.get_gas_params()
            
            approve_tx = await token_contract.functions.approve(
                IZUMI_CONTRACT,
                amount
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'type': 2,
                'chainId': 10143,
                **gas_params,
            })
            
            return await self.execute_transaction(approve_tx)
            
        except Exception as e:
            logger.error(f"Failed to approve {token}: {str(e)}")
            raise

    async def execute_transaction(self, transaction: Dict) -> str:
        """Execute a transaction and wait for confirmation."""
        signed_txn = self.web3.eth.account.sign_transaction(transaction, self.account.key)
        tx_hash = await self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        logger.info("Waiting for transaction confirmation...")
        receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash, poll_latency=2)
        
        if receipt['status'] == 1:
            logger.success(f"Transaction successful! Explorer URL: {EXPLORER_URL}{tx_hash.hex()}")
            return tx_hash.hex()
        else:
            logger.error(f"Transaction failed! Explorer URL: {EXPLORER_URL}{tx_hash.hex()}")
            raise Exception("Transaction failed")

    async def swap(self, percentage_to_swap: float, type: str = "swap") -> str:
        """Execute swap on Izumi DEX."""
        try:
            tokens_with_balance = await self.get_tokens_with_balance()
            
            if not tokens_with_balance:
                logger.info("No tokens with sufficient balance found to swap")
                return None

            if type == "collect":
                # Filter out native token since we're collecting to it
                tokens_to_swap = [(t, b) for t, b in tokens_with_balance if t != "native"]
                if not tokens_to_swap:
                    logger.info("No tokens to collect to native")
                    return None
                
                # Swap all tokens to native
                for token_in, balance in tokens_to_swap:
                    try:
                        # Get actual balance directly in wei
                        token_contract = self.web3.eth.contract(
                            address=self.web3.to_checksum_address(IZUMI_TOKENS[token_in]["address"]),
                            abi=ERC20_ABI
                        )
                        amount_wei = await token_contract.functions.balanceOf(self.account.address).call()
                            
                        # Approve token spending
                        await self.approve_token(token_in, amount_wei)
                        random_pause = random.randint(
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                        )
                        logger.info(f"Sleeping {random_pause} seconds after approve")
                        await asyncio.sleep(random_pause)

                        amount_token = self.convert_from_wei(amount_wei, token_in)
                        logger.info(f"Collecting {amount_token} {token_in} to native")
                        
                        # Generate and execute swap transaction
                        tx_data = await self.generate_swap_data(token_in, "native", amount_wei)
                        tx_hash = await self.execute_transaction(tx_data)
                        
                        # Wait between swaps
                        if token_in != tokens_to_swap[-1][0]:  # If not the last token
                            await asyncio.sleep(random.randint(5, 10))
                            
                    except Exception as e:
                        logger.error(f"Failed to collect {token_in} to native: {str(e)}")
                        continue
                
                return "Collection complete"
                
            else:  # Regular swap
                # Pick random token with balance as input token
                token_in, balance = random.choice(tokens_with_balance)
                
                # For output token, if input is native, pick any token except native
                # If input is a token, output must be native
                available_out_tokens = (
                    [t for t in IZUMI_TOKENS.keys() if t != "wmon"]
                    if token_in == "native"
                    else ["native"]
                )
                token_out = random.choice(available_out_tokens)
                
                # Calculate amount to swap based on direction
                if token_in == "native":
                    # For native to token, use percentage
                    actual_balance = await self.web3.eth.get_balance(self.account.address)
                    amount_wei = int(actual_balance * percentage_to_swap / 100)
                    amount_token = float(self.web3.from_wei(amount_wei, 'ether'))
                else:
                    # Get actual balance directly in wei
                    token_contract = self.web3.eth.contract(
                        address=self.web3.to_checksum_address(IZUMI_TOKENS[token_in]["address"]),
                        abi=ERC20_ABI
                    )
                    amount_wei = await token_contract.functions.balanceOf(self.account.address).call()
                    amount_token = self.convert_from_wei(amount_wei, token_in)
                    
                    # Approve token spending if not native
                    await self.approve_token(token_in, amount_wei)
                    random_pause = random.randint(
                        self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                        self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                    )
                    logger.info(f"Sleeping {random_pause} seconds after approve")
                    await asyncio.sleep(random_pause)
                
                logger.info(f"Swapping {amount_token} {token_in} to {token_out}")
                
                # Generate and execute swap transaction
                tx_data = await self.generate_swap_data(token_in, token_out, amount_wei)
                return await self.execute_transaction(tx_data)

        except Exception as e:
            logger.error(f"Izumi swap failed: {str(e)}")
            raise

    async def estimate_gas(self, tx_params: Dict) -> int:
        """Estimate gas for a transaction with a safety buffer."""
        try:
            # Create a copy of tx params without gas
            estimation_params = tx_params.copy()
            if 'gas' in estimation_params:
                del estimation_params['gas']
            
            # Estimate gas
            estimated_gas = await self.web3.eth.estimate_gas(estimation_params)
            
            # Add 20% safety buffer
            return int(estimated_gas * 1.2)
        except Exception as e:
            logger.warning(f"Gas estimation failed: {str(e)}")


    async def generate_swap_data(self, token_in: str, token_out: str, amount_in: int) -> Dict:
        """Generate swap transaction data."""
        try:
            # Get token addresses and handle native token case
            token_in_address = IZUMI_TOKENS["wmon"]["address"] if token_in == "native" else IZUMI_TOKENS[token_in]["address"]
            token_out_address = IZUMI_TOKENS["wmon"]["address"] if token_out == "native" else IZUMI_TOKENS[token_out]["address"]
            
            # Pack addresses and fee tier: [tokenA, fee, tokenB]
            path = bytes.fromhex(
                self.web3.to_checksum_address(token_in_address)[2:] +  # Input token address
                format(self.FEE_TIER, '06x') +  # 3-byte fee tier
                self.web3.to_checksum_address(token_out_address)[2:]  # Output token address
            )
            
            # Parameters for swapAmount
            deadline = int(time.time() + 3600 * 6)  # 6 hours from now
            min_acquired = 0  # For testing, set to 0
            
            # Determine recipient based on whether we're receiving native token
            recipient = IZUMI_CONTRACT if token_out == "native" else self.account.address
            
            # Encode swapAmount call
            swap_data = self.router_contract.encode_abi(
                "swapAmount",
                [(path, recipient, amount_in, min_acquired, deadline)]
            )
            
            # Prepare multicall data array
            multicall_array = [swap_data]
            
            # Add unwrapWETH9 if receiving native token
            if token_out == "native":
                unwrap_data = self.router_contract.encode_abi(
                    "unwrapWETH9",
                    [min_acquired, self.account.address]
                )
                multicall_array.append(unwrap_data)
            
            # Add refundETH call
            refund_data = self.router_contract.encode_abi("refundETH")
            multicall_array.append(refund_data)
            
            # Encode the final multicall
            multicall_data = self.router_contract.encode_abi(
                "multicall",
                [multicall_array]  # Pass as a single array argument
            )
            
            # Prepare base transaction
            nonce = await self.web3.eth.get_transaction_count(self.account.address)
            gas_params = await self.get_gas_params()
            
            tx_data = {
                'from': self.account.address,
                'to': self.web3.to_checksum_address(IZUMI_CONTRACT),
                'value': amount_in if token_in == "native" else 0,
                'data': multicall_data,
                'nonce': nonce,
                'chainId': 10143,
                **gas_params,
            }
            
            # Estimate gas for the transaction
            gas_limit = await self.estimate_gas(tx_data)
            tx_data['gas'] = gas_limit
            
            return tx_data
            
        except Exception as e:
            logger.error(f"Failed to generate swap data: {str(e)}")
            raise
