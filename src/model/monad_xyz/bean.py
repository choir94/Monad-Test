from web3 import AsyncWeb3
from eth_account import Account
import asyncio
from typing import Dict, Optional, List, Tuple
from decimal import Decimal
import random
from loguru import logger
from src.utils.constants import RPC_URL, EXPLORER_URL, ERC20_ABI
from src.model.monad_xyz.constants import BEAN_CONTRACT, BEAN_ABI, BEAN_TOKENS
import time
from src.utils.config import Config

class BeanDex:
    def __init__(self, private_key: str, proxy: Optional[str] = None, config: Config = None):
        self.web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))
        self.account = Account.from_key(private_key)
        self.proxy = proxy
        self.router_contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(BEAN_CONTRACT),
            abi=BEAN_ABI
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

    async def get_token_balance(self, token: str) -> float:
        try:
            if token == "native":
                balance_wei = await self.web3.eth.get_balance(self.account.address)
                return float(self.web3.from_wei(balance_wei, 'ether'))
            
            token_contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(BEAN_TOKENS[token]["address"]),
                abi=ERC20_ABI
            )
            balance = await token_contract.functions.balanceOf(self.account.address).call()
            decimals = BEAN_TOKENS[token]["decimals"]
            amount = float(Decimal(str(balance)) / Decimal(str(10 ** decimals)))
            return amount
            
        except Exception as e:
            logger.error(f"Failed to get {token} balance: {str(e)}")
            return 0

    async def get_tokens_with_balance(self) -> List[Tuple[str, float]]:
        """Get list of tokens with non-zero balances."""
        tokens_with_balance = []
        
        # Check native token balance
        native_balance = await self.web3.eth.get_balance(self.account.address)
        if native_balance > 0:
            native_amount = float(self.web3.from_wei(native_balance, 'ether'))
            tokens_with_balance.append(("native", native_amount))
        
        # Check other tokens
        for token in BEAN_TOKENS:
            try:
                token_contract = self.web3.eth.contract(
                    address=self.web3.to_checksum_address(BEAN_TOKENS[token]["address"]),
                    abi=ERC20_ABI
                )
                balance = await token_contract.functions.balanceOf(self.account.address).call()
                
                if balance > 0:
                    decimals = BEAN_TOKENS[token]["decimals"]
                    amount = float(Decimal(str(balance)) / Decimal(str(10 ** decimals)))
                    tokens_with_balance.append((token, amount))
                    
            except Exception as e:
                logger.error(f"Failed to get balance for {token}: {str(e)}")
                continue
        
        return tokens_with_balance

    async def approve_token(self, token: str, amount: int) -> Optional[str]:
        try:
            token_contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(BEAN_TOKENS[token]["address"]),
                abi=ERC20_ABI
            )
            
            current_allowance = await token_contract.functions.allowance(
                self.account.address,
                BEAN_CONTRACT
            ).call()
            
            if current_allowance >= amount:
                logger.info(f"Allowance sufficient for {token}")
                return None
            
            nonce = await self.web3.eth.get_transaction_count(self.account.address)
            gas_params = await self.get_gas_params()
            
            approve_tx = await token_contract.functions.approve(
                BEAN_CONTRACT,
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

    async def generate_swap_data(self, token_in: str, token_out: str, amount_in: int, min_amount_out: int) -> Dict:
        """Generate swap transaction data based on token types."""
        try:
            # Calculate deadline as current timestamp + 30 minutes (in seconds)
            current_time = int(time.time())
            deadline = current_time + 1800  # 30 minutes
            logger.info(f"Setting swap deadline to {deadline} ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(deadline))})")
            
            path = []
            if token_in == "native":
                # MON -> Token needs WMON in the path
                path = [BEAN_TOKENS["wmon"]["address"], BEAN_TOKENS[token_out]["address"]]
                logger.info(f"Swap path: MON -> WMON -> {token_out}")
            elif token_out == "native":
                # Token -> MON needs WMON in the path
                path = [BEAN_TOKENS[token_in]["address"], BEAN_TOKENS["wmon"]["address"]]
                logger.info(f"Swap path: {token_in} -> WMON -> MON")
            else:
                # Token -> Token through WMON
                path = [
                    BEAN_TOKENS[token_in]["address"],
                    BEAN_TOKENS["wmon"]["address"],
                    BEAN_TOKENS[token_out]["address"]
                ]
                logger.info(f"Swap path: {token_in} -> WMON -> {token_out}")

            if token_in == "native":
                # MON -> Token
                method = self.router_contract.functions.swapExactETHForTokens(
                    min_amount_out,
                    path,
                    self.account.address,
                    deadline
                )
                value = amount_in
            elif token_out == "native":
                # Token -> MON
                method = self.router_contract.functions.swapExactTokensForETH(
                    amount_in,
                    min_amount_out,
                    path,
                    self.account.address,
                    deadline
                )
                value = 0
            else:
                # Token -> Token
                method = self.router_contract.functions.swapExactTokensForTokens(
                    amount_in,
                    min_amount_out,
                    path,
                    self.account.address,
                    deadline
                )
                value = 0

            gas_estimate = await method.estimate_gas({
                'from': self.account.address,
                'value': value
            })

            tx_data = await method.build_transaction({
                'from': self.account.address,
                'value': value,
                'gas': int(gas_estimate * 1.1),
                'nonce': await self.web3.eth.get_transaction_count(self.account.address),
                **await self.get_gas_params(),
            })

            return tx_data

        except Exception as e:
            logger.error(f"Failed to generate swap data: {str(e)}")
            raise

    async def swap(self, percentage_to_swap: float, type: str = "swap") -> str:
        try:
            tokens_with_balance = await self.get_tokens_with_balance()
            
            if not tokens_with_balance:
                raise ValueError("No tokens with balance found to swap")

            if type == "collect":
                # Filter out native token, wmon, and bean since we're collecting to native
                tokens_to_swap = [(t, b) for t, b in tokens_with_balance 
                                  if t not in ["native", "wmon", "bean"]]
                if not tokens_to_swap:
                    logger.info("No tokens to collect to native")
                    return None
                
                logger.info(f"Found tokens to collect: {[t[0] for t in tokens_to_swap]}")
                
                # Swap all tokens to native
                for token_in, balance in tokens_to_swap:
                    try:
                        decimals = BEAN_TOKENS[token_in]["decimals"]
                        amount_wei = int(Decimal(str(balance)) * Decimal(str(10 ** decimals)))
                        
                        # First check and approve if needed
                        logger.info(f"Checking allowance for {balance} {token_in}")
                        token_contract = self.web3.eth.contract(
                            address=self.web3.to_checksum_address(BEAN_TOKENS[token_in]["address"]),
                            abi=ERC20_ABI
                        )
                        
                        current_allowance = await token_contract.functions.allowance(
                            self.account.address,
                            BEAN_CONTRACT
                        ).call()
                        
                        if current_allowance < amount_wei:
                            logger.info(f"Approving {balance} {token_in} for Bean router")
                            await self.approve_token(token_in, amount_wei)
                            random_pause = random.randint(
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                            )
                            logger.info(f"Sleeping {random_pause} seconds after approve")
                            await asyncio.sleep(random_pause)
                        else:
                            logger.info(f"Allowance sufficient for {token_in}")
                        
                        logger.info(f"Collecting {balance} {token_in} to native")
                        
                        tx_data = await self.generate_swap_data(token_in, "native", amount_wei, 0)
                        await self.execute_transaction(tx_data)
                        
                        if token_in != tokens_to_swap[-1][0]:
                            await asyncio.sleep(random.randint(5, 10))
                            
                    except Exception as e:
                        logger.error(f"Failed to collect {token_in} to native: {str(e)}")
                        continue
                        
                return "Collection complete"
            
            else:
                # Regular swap
                token_in, balance = random.choice(tokens_with_balance)
                logger.info(f"Selected input token: {token_in} with balance: {balance}")
                
                # Create list of available tokens for swapping, excluding only WMON
                available_tokens = []
                if token_in == "native":
                    # If swapping from native, can swap to any token except WMON
                    available_tokens = [t for t in BEAN_TOKENS.keys() if t != "wmon"]
                    logger.info(f"Available output tokens for native: {available_tokens}")
                else:
                    # If swapping from token, can swap to native or other tokens except WMON
                    available_tokens = ["native"] + [t for t in BEAN_TOKENS if t not in [token_in, "wmon"]]
                    logger.info(f"Available output tokens for {token_in}: {available_tokens}")
                
                if not available_tokens:
                    raise ValueError("No available tokens to swap to")
                    
                token_out = random.choice(available_tokens)
                logger.info(f"Selected output token: {token_out}")
                
                # Calculate amount to swap
                if token_in == "native":
                    amount_wei = int(self.web3.to_wei(balance * (percentage_to_swap / 100), 'ether'))
                    amount_token = float(self.web3.from_wei(amount_wei, 'ether'))
                    logger.info(f"Swapping {amount_token} {token_in} to {token_out}")
                else:
                    decimals = BEAN_TOKENS[token_in]["decimals"]
                    full_amount_wei = int(Decimal(str(balance)) * Decimal(str(10 ** decimals)))
                    amount_wei = int(full_amount_wei * percentage_to_swap / 100)
                    amount_token = float(Decimal(str(amount_wei)) / Decimal(str(10 ** decimals)))
                    logger.info(f"Swapping {amount_token} {token_in} to {token_out}")
                    
                    # Approve token spending
                    logger.info(f"Approving {amount_token} {token_in} for Bean router")
                    await self.approve_token(token_in, amount_wei)
                    await asyncio.sleep(random.randint(5, 10))
                
                min_amount_out = 0  # Add slippage calculation if needed
                logger.info(f"Generating swap data for {token_in} -> {token_out}")
                tx_data = await self.generate_swap_data(token_in, token_out, amount_wei, min_amount_out)
                return await self.execute_transaction(tx_data)

        except Exception as e:
            logger.error(f"Swap failed: {str(e)}")
            raise
