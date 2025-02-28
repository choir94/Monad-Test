from web3 import AsyncWeb3
from eth_account import Account
import asyncio
from typing import Dict, Optional, List, Tuple
from eth_abi import abi
from decimal import Decimal
from src.utils.constants import RPC_URL, EXPLORER_URL, ERC20_ABI
from src.model.monad_xyz.constants import AMBIENT_ABI, AMBIENT_TOKENS, AMBIENT_CONTRACT, ZERO_ADDRESS, POOL_IDX, RESERVE_FLAGS, TIP, MAX_SQRT_PRICE, MIN_SQRT_PRICE
from loguru import logger
import random
from src.utils.config import Config

    
class AmbientDex:
    def __init__(self, private_key: str, proxy: Optional[str] = None, config: Config = None):
        self.web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))
        self.account = Account.from_key(private_key)
        self.proxy = proxy
        self.router_contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(AMBIENT_CONTRACT),
            abi=AMBIENT_ABI
        )
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
        decimals = AMBIENT_TOKENS[token.lower()]["decimals"]
        return int(Decimal(str(amount)) * Decimal(str(10 ** decimals)))

    def convert_from_wei(self, amount: int, token: str) -> float:
        """Convert wei amount back to token units."""
        if token == "native":
            return float(self.web3.from_wei(amount, 'ether'))
        decimals = AMBIENT_TOKENS[token.lower()]["decimals"]
        return float(Decimal(str(amount)) / Decimal(str(10 ** decimals)))
    
    async def get_tokens_with_balance(self) -> List[Tuple[str, float]]:
        """Get list of tokens with non-zero balances, including native token."""
        tokens_with_balance = []
        
        # Check native token balance
        native_balance = await self.web3.eth.get_balance(self.account.address)
        if native_balance > 0:
            native_amount = float(self.web3.from_wei(native_balance, 'ether'))
            tokens_with_balance.append(("native", native_amount))
        
        # Check other tokens
        for token in AMBIENT_TOKENS:
            try:
                token_contract = self.web3.eth.contract(
                    address=self.web3.to_checksum_address(AMBIENT_TOKENS[token]["address"]),
                    abi=ERC20_ABI
                )
                balance = await token_contract.functions.balanceOf(self.account.address).call()
                
                if balance > 0:
                    decimals = AMBIENT_TOKENS[token]["decimals"]
                    amount = float(Decimal(str(balance)) / Decimal(str(10 ** decimals)))
                    
                    # Skip SETH and WETH with low balances
                    if token.lower() in ["seth", "weth"] and amount < 0.001:
                        # logger.info(f"Skipping {token} with low balance ({amount}) for potential swaps")
                        continue
                        
                    tokens_with_balance.append((token, amount))
                
            except Exception as e:
                logger.error(f"Failed to get balance for {token}: {str(e)}")
                continue
        
        return tokens_with_balance
    
    async def generate_swap_data(self, token_in: str, token_out: str, amount_in_wei: int) -> Dict:
        """Generate swap transaction data for Ambient DEX."""
        try:
            is_native = token_in == "native"
            
            # Get token address based on token symbol
            token_address = (
                AMBIENT_TOKENS[token_out.lower()]["address"] if is_native 
                else AMBIENT_TOKENS[token_in.lower()]["address"]
            )
            
            # Encode the swap parameters
            encode_data = abi.encode(
                ['address', 'address', 'uint16', 'bool', 'bool', 'uint256', 'uint8', 'uint256', 'uint256', 'uint8'],
                [
                    ZERO_ADDRESS,
                    self.web3.to_checksum_address(token_address),
                    POOL_IDX,
                    is_native,
                    is_native,
                    amount_in_wei,
                    TIP,
                    MAX_SQRT_PRICE if is_native else MIN_SQRT_PRICE,
                    0,
                    RESERVE_FLAGS
                ]
            )
            
            # Generate the function selector for userCmd
            function_selector = self.web3.keccak(text="userCmd(uint16,bytes)")[:4]
            
            # Encode the parameters for userCmd
            cmd_params = abi.encode(['uint16', 'bytes'], [1, encode_data])
            
            # Combine function selector and parameters
            tx_data = function_selector.hex() + cmd_params.hex()

            # Estimate gas
            gas_estimate = await self.web3.eth.estimate_gas({
                'to': AMBIENT_CONTRACT,
                'from': self.account.address,
                'data': '0x' + tx_data,
                'value': amount_in_wei if is_native else 0
            })

            return {
                "to": AMBIENT_CONTRACT,
                "data": '0x' + tx_data,
                "value": amount_in_wei if is_native else 0,
                "gas": int(gas_estimate * 1.1)  # Add 10% buffer
            }

        except Exception as e:
            logger.error(f"Failed to generate Ambient swap data: {str(e)}")
            raise

    async def execute_transaction(self, tx_data: Dict) -> str:
        """Execute a transaction and wait for confirmation."""
        nonce = await self.web3.eth.get_transaction_count(self.account.address)
        gas_params = await self.get_gas_params()
        
        transaction = {
            "from": self.account.address,
            "nonce": nonce,
            "type": 2,
            "chainId": 10143,
            **tx_data,
            **gas_params,
        }

        signed_txn = self.web3.eth.account.sign_transaction(transaction, self.account.key)
        tx_hash = await self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        logger.info("Waiting for transaction confirmation...")
        receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash, poll_latency=2)
        
        if receipt['status'] == 1:
            logger.success(f"Transaction successful! Explorer URL: {EXPLORER_URL}{tx_hash.hex()}")
        else:
            logger.error(f"Transaction failed! Explorer URL: {EXPLORER_URL}{tx_hash.hex()}")
            raise Exception("Transaction failed")
        return tx_hash.hex()
    
    async def approve_token(self, token: str, amount: int) -> str:
        """Approve token spending for Ambient DEX."""
        try:
            token_contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(AMBIENT_TOKENS[token.lower()]["address"]),
                abi=ERC20_ABI
            )
            
            # Check current allowance
            current_allowance = await token_contract.functions.allowance(
                self.account.address,
                AMBIENT_CONTRACT
            ).call()
            
            if current_allowance >= amount:
                logger.info(f"Allowance sufficient for {token}")
                return None
            
            # Prepare approval transaction
            nonce = await self.web3.eth.get_transaction_count(self.account.address)
            gas_params = await self.get_gas_params()
            
            approve_tx = await token_contract.functions.approve(
                AMBIENT_CONTRACT,
                amount
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'type': 2,
                'chainId': 10143,
                **gas_params,
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(approve_tx, self.account.key)
            tx_hash = await self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            logger.info(f"Waiting for {token} approval confirmation...")
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash, poll_latency=2)
            
            if receipt['status'] == 1:
                logger.success(f"Approval successful! Explorer URL: {EXPLORER_URL}{tx_hash.hex()}")
                return tx_hash.hex()
            else:
                raise Exception(f"Approval failed for {token}")
            
        except Exception as e:
            logger.error(f"Failed to approve {token}: {str(e)}")
            raise

    async def swap(self, percentage_to_swap: float, type: str) -> str:
        """Execute swap on Ambient DEX."""
        try:
            # Get tokens with actual balances
            tokens_with_balance = await self.get_tokens_with_balance()
            
            if not tokens_with_balance:
                raise ValueError("No tokens with balance found to swap")
            
            if type == "collect":
                # Filter out native token since we're collecting to it
                tokens_to_swap = [(t, b) for t, b in tokens_with_balance if t != "native"]
                if not tokens_to_swap:
                    logger.info("No tokens to collect to native")
                    return None
                
                # Swap all tokens to native
                for token_in, balance in tokens_to_swap:
                    try:
                        decimals = AMBIENT_TOKENS[token_in.lower()]["decimals"]
                        
                        # Special handling for SETH token
                        if token_in.lower() == "seth":
                            # Leave a small random amount between 0.00001 and 0.0001
                            leave_amount = random.uniform(0.00001, 0.0001)
                            balance = balance - leave_amount
                        
                        amount_wei = int(Decimal(str(balance)) * Decimal(str(10 ** decimals)))
                        
                        # Approve token spending
                        await self.approve_token(token_in, amount_wei)
                        random_pause = random.randint(
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                        )
                        logger.info(f"Swapping {balance} {token_in} to MON. Sleeping {random_pause} seconds after approve")
                        await asyncio.sleep(random_pause)
                        
                        logger.info(f"Collecting {balance} {token_in} to native")
                        
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
                
                # Get available output tokens (excluding input token)
                available_out_tokens = list(AMBIENT_TOKENS.keys()) + ["native"]
                available_out_tokens.remove(token_in)
                token_out = random.choice(available_out_tokens)
            
            # Calculate amount based on whether we're swapping from native or not
            if token_in == "native":
                # For native token, apply percentage
                balance_wei = self.web3.to_wei(balance, 'ether')
                percentage = Decimal(str(percentage_to_swap)) / Decimal('100')
                amount_wei = int(Decimal(str(balance_wei)) * percentage)
                amount_token = float(self.web3.from_wei(amount_wei, 'ether'))
            else:
                # For other tokens, use full balance
                decimals = AMBIENT_TOKENS[token_in.lower()]["decimals"]
                balance_decimal = Decimal(str(balance))
                
                # Special handling for SETH - only leave small random amount
                if token_in.lower() == "seth":
                    leave_amount = random.uniform(0.00001, 0.0001)
                    balance_decimal = balance_decimal - Decimal(str(leave_amount))
                
                amount_wei = int(balance_decimal * Decimal(str(10 ** decimals)))
                amount_token = float(balance_decimal)
                
                # Approve token spending if not native
                await self.approve_token(token_in, amount_wei)
                await asyncio.sleep(random.randint(5, 10))
            
            logger.info(f"Swapping {amount_token} {token_in} to {token_out}")
            
            # Generate swap transaction
            tx_data = await self.generate_swap_data(token_in, token_out, amount_wei)
            
            # Execute the transaction
            return await self.execute_transaction(tx_data)

        except Exception as e:
            logger.error(f"Ambient swap failed: {str(e)}")
            raise
        