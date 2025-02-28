import asyncio
import random
from loguru import logger
from eth_account import Account
import primp

from src.model.monad_xyz.bean import BeanDex
from src.model.monad_xyz.ambient import AmbientDex
from src.model.monad_xyz.izumi import IzumiDex
from src.model.monad_xyz.uniswap_swaps import MonadSwap
from src.model.monad_xyz.faucet import faucet
from src.utils.config import Config


class MonadXYZ:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        discord_token: str,
        config: Config,
        session: primp.AsyncClient,
    ):
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.discord_token = discord_token
        self.config = config
        self.session: primp.AsyncClient = session

        self.wallet = Account.from_key(private_key)

    async def swaps(self, type: str):
        try:
            if type == "swaps":
                number_of_swaps = random.randint(
                    self.config.FLOW.NUMBER_OF_SWAPS[0], self.config.FLOW.NUMBER_OF_SWAPS[1]
                )
                logger.info(f"[{self.account_index}] | Will perform {number_of_swaps} swaps")
                
                for swap_num in range(number_of_swaps):
                    success = False
                    for retry in range(self.config.SETTINGS.ATTEMPTS):
                        try:
                            swapper = MonadSwap(self.private_key, self.proxy)
                            amount = random.randint(
                                self.config.FLOW.PERCENT_OF_BALANCE_TO_SWAP[0],
                                self.config.FLOW.PERCENT_OF_BALANCE_TO_SWAP[1],
                            )
                            random_token = random.choice(["DAK", "YAKI", "CHOG"])
                            logger.info(
                                f"[{self.account_index}] | Swapping {amount}% of balance to {random_token}"
                            )

                            await swapper.swap(
                                percentage_to_swap=amount, token_out=random_token,
                            )
                            random_pause = random.randint(
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                            )
                            logger.success(
                                f"[{self.account_index}] | Swapped {amount}% of balance to {random_token}. Swap {swap_num + 1}/{number_of_swaps}. Next swap in {random_pause} seconds"
                            )
                            await asyncio.sleep(random_pause)
                            success = True
                            break  # Break retry loop on success
                            
                        except Exception as e:
                            logger.error(
                                f"[{self.account_index}] | Error swap in monad.xyz ({retry + 1}/{self.config.SETTINGS.ATTEMPTS}): {e}"
                            )
                            if retry == self.config.SETTINGS.ATTEMPTS - 1:
                                raise  # Re-raise if all retries failed
                            continue
                    
                    if not success:
                        logger.error(f"[{self.account_index}] | Failed to complete swap {swap_num + 1}/{number_of_swaps} after all retries")
                        break

                return True
            
            elif type == "ambient":
                number_of_swaps = random.randint(
                    self.config.FLOW.NUMBER_OF_SWAPS[0], self.config.FLOW.NUMBER_OF_SWAPS[1]
                )
                logger.info(f"[{self.account_index}] | Will perform {number_of_swaps} Ambient swaps")
                
                for swap_num in range(number_of_swaps):
                    success = False
                    for retry in range(self.config.SETTINGS.ATTEMPTS):
                        try:
                            swapper = AmbientDex(self.private_key, self.proxy, self.config)
                            amount = random.randint(
                                self.config.FLOW.PERCENT_OF_BALANCE_TO_SWAP[0],
                                self.config.FLOW.PERCENT_OF_BALANCE_TO_SWAP[1],
                            )
                            await swapper.swap(
                                percentage_to_swap=amount,
                                type="swap",
                            )
                            random_pause = random.randint(
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                            )
                            logger.success(
                                f"[{self.account_index}] | Completed Ambient swap {swap_num + 1}/{number_of_swaps}. Next swap in {random_pause} seconds"
                            )
                            await asyncio.sleep(random_pause)
                            success = True
                            break  # Break retry loop on success
                            
                        except Exception as e:
                            logger.error(
                                f"[{self.account_index}] | Error swap in ambient ({retry + 1}/{self.config.SETTINGS.ATTEMPTS}): {e}"
                            )
                            if retry == self.config.SETTINGS.ATTEMPTS - 1:
                                raise  # Re-raise if all retries failed
                            continue
                    
                    if not success:
                        logger.error(f"[{self.account_index}] | Failed to complete swap {swap_num + 1}/{number_of_swaps} after all retries")
                        break

                return True
            
            elif type == "bean":
                number_of_swaps = random.randint(
                    self.config.FLOW.NUMBER_OF_SWAPS[0], self.config.FLOW.NUMBER_OF_SWAPS[1]
                )
                logger.info(f"[{self.account_index}] | Will perform {number_of_swaps} Bean swaps")
                
                for swap_num in range(number_of_swaps):
                    success = False
                    for retry in range(self.config.SETTINGS.ATTEMPTS):
                        try:
                            swapper = BeanDex(self.private_key, self.proxy, self.config)
                            amount = random.randint(
                                self.config.FLOW.PERCENT_OF_BALANCE_TO_SWAP[0],
                                self.config.FLOW.PERCENT_OF_BALANCE_TO_SWAP[1],
                            )
                            await swapper.swap(
                                percentage_to_swap=amount,
                                type="swap",
                            )
                            random_pause = random.randint(
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                            )
                            logger.success(
                                f"[{self.account_index}] | Completed Bean swap {swap_num + 1}/{number_of_swaps}. Next swap in {random_pause} seconds"
                            )
                            await asyncio.sleep(random_pause)
                            success = True
                            break  # Break retry loop on success
                            
                        except Exception as e:
                            logger.error(
                                f"[{self.account_index}] | Error swap in bean ({retry + 1}/{self.config.SETTINGS.ATTEMPTS}): {e}"
                            )
                            if retry == self.config.SETTINGS.ATTEMPTS - 1:
                                raise  # Re-raise if all retries failed
                            continue
                    
                    if not success:
                        logger.error(f"[{self.account_index}] | Failed to complete swap {swap_num + 1}/{number_of_swaps} after all retries")
                        break

                return True
            
            elif type == "izumi":
                number_of_swaps = random.randint(
                    self.config.FLOW.NUMBER_OF_SWAPS[0], self.config.FLOW.NUMBER_OF_SWAPS[1]
                )
                logger.info(f"[{self.account_index}] | Will perform {number_of_swaps} Izumi swaps")
                
                for swap_num in range(number_of_swaps):
                    success = False
                    for retry in range(self.config.SETTINGS.ATTEMPTS):
                        try:
                            swapper = IzumiDex(self.private_key, self.proxy, self.config)
                            amount = random.randint(
                                self.config.FLOW.PERCENT_OF_BALANCE_TO_SWAP[0],
                                self.config.FLOW.PERCENT_OF_BALANCE_TO_SWAP[1],
                            )
                            await swapper.swap(
                                percentage_to_swap=amount,
                                type="swap",
                            )
                            random_pause = random.randint(
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                                self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                            )
                            logger.success(
                                f"[{self.account_index}] | Completed Izumi swap {swap_num + 1}/{number_of_swaps}. Next swap in {random_pause} seconds"
                            )
                            await asyncio.sleep(random_pause)
                            success = True
                            break  # Break retry loop on success
                            
                        except Exception as e:
                            logger.error(
                                f"[{self.account_index}] | Error swap in izumi ({retry + 1}/{self.config.SETTINGS.ATTEMPTS}): {e}"
                            )
                            if retry == self.config.SETTINGS.ATTEMPTS - 1:
                                raise  # Re-raise if all retries failed
                            continue
                    
                    if not success:
                        logger.error(f"[{self.account_index}] | Failed to complete swap {swap_num + 1}/{number_of_swaps} after all retries")
                        break

                return True
            
            elif type == "collect_all_to_monad":
                success = False
                for retry in range(self.config.SETTINGS.ATTEMPTS):
                    try:
                        # First try collecting via MonadSwap
                        swapper = MonadSwap(self.private_key, self.proxy)
                        await swapper.swap(
                            percentage_to_swap=100, token_out="native",
                        )
                        random_pause = random.randint(
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                        )
                        logger.success(
                            f"[{self.account_index}] | Collected all to monad.xyz. Next collect in {random_pause} seconds"
                        )
                        await asyncio.sleep(random_pause)

                        # Then try collecting via Ambient
                        ambient_swapper = AmbientDex(self.private_key, self.proxy, self.config)
                        await ambient_swapper.swap(
                            percentage_to_swap=100, type="collect"
                        )
                        random_pause = random.randint(
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                        )
                        logger.success(
                            f"[{self.account_index}] | Collected all tokens via Ambient. Next collect in {random_pause} seconds"
                        )
                        await asyncio.sleep(random_pause)
                        
                        # Then try collecting via Bean
                        bean_swapper = BeanDex(self.private_key, self.proxy, self.config)
                        await bean_swapper.swap(
                            percentage_to_swap=100, type="collect"
                        )
                        random_pause = random.randint(
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                        )
                        logger.success(
                            f"[{self.account_index}] | Collected all tokens via Bean. Next collect in {random_pause} seconds"
                        )
                        await asyncio.sleep(random_pause)

                        # Then try collecting via Izumi
                        izumi_swapper = IzumiDex(self.private_key, self.proxy, self.config)
                        await izumi_swapper.swap(
                            percentage_to_swap=100, type="collect"
                        )
                        random_pause = random.randint(
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                            self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                        )   
                        logger.success(
                            f"[{self.account_index}] | Collected all tokens via Izumi. Next collect in {random_pause} seconds"
                        )
                        await asyncio.sleep(random_pause)

                        success = True
                        break  # Break the retry loop on success
                        
                    except Exception as e:
                        random_pause = random.randint(
                            self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                            self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
                        )
                        logger.error(
                            f"[{self.account_index}] | Error collecting tokens ({retry + 1}/{self.config.SETTINGS.ATTEMPTS}): {e}. Next collect in {random_pause} seconds"
                        )
                        await asyncio.sleep(random_pause)
                        continue
                    
                return success  # Return True if succeeded, False if all retries failed
        except Exception as e:
            logger.error(f"[{self.account_index}] | Error swaps: {e}")
            return False

    async def faucet(self):
        try:
            return await faucet(
                self.session, self.account_index, self.config, self.wallet
            )
        except Exception as e:
            logger.error(f"[{self.account_index}] | Error faucet to monad.xyz: {e}")
            return False

    async def connect_discord(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                headers = {
                    "sec-ch-ua-platform": '"Windows"',
                    "content-type": "application/json",
                    "sec-ch-ua-mobile": "?0",
                    "accept": "*/*",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-dest": "empty",
                    "referer": "https://testnet.monad.xyz/",
                    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                    "priority": "u=1, i",
                }

                response = await self.session.get(
                    "https://testnet.monad.xyz/api/auth/csrf", headers=headers
                )

                if response.status_code == 200:
                    csrf_token = response.json().get("csrfToken")
                    headers = {
                        "sec-ch-ua-platform": '"Windows"',
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                        "content-type": "application/x-www-form-urlencoded",
                        "sec-ch-ua-mobile": "?0",
                        "accept": "*/*",
                        "origin": "https://testnet.monad.xyz",
                        "sec-fetch-site": "same-origin",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-dest": "empty",
                        "referer": "https://testnet.monad.xyz/",
                        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                        "priority": "u=1, i",
                    }

                    data = {
                        "csrfToken": csrf_token,
                        "callbackUrl": "https://testnet.monad.xyz/",
                        "json": "true",
                    }

                    response = await self.session.post(
                        "https://testnet.monad.xyz/api/auth/signin/discord",
                        headers=headers,
                        data=data,
                    )
                    if response.status_code == 200:
                        url = response.json().get("url")
                        state = url.split("state=")[1].strip()

                        headers = {
                            "sec-ch-ua-platform": '"Windows"',
                            "authorization": self.discord_token,
                            "x-debug-options": "bugReporterEnabled",
                            "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="131", "Chromium";v="131"',
                            "sec-ch-ua-mobile": "?0",
                            "x-discord-timezone": "Etc/GMT-2",
                            "x-discord-locale": "en-US",
                            "content-type": "application/json",
                            "accept": "*/*",
                            "origin": "https://discord.com",
                            "sec-fetch-site": "same-origin",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-dest": "empty",
                            "referer": f"https://discord.com/oauth2/authorize?client_id=1330973073914069084&scope=identify%20email%20guilds%20guilds.members.read&response_type=code&redirect_uri=https%3A%2F%2Ftestnet.monad.xyz%2Fapi%2Fauth%2Fcallback%2Fdiscord&state={state}",
                            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                            "priority": "u=1, i",
                        }

                        params = {
                            "client_id": "1330973073914069084",
                            "response_type": "code",
                            "redirect_uri": "https://testnet.monad.xyz/api/auth/callback/discord",
                            "scope": "identify email guilds guilds.members.read",
                            "state": state,
                        }

                        json_data = {
                            "permissions": "0",
                            "authorize": True,
                            "integration_type": 0,
                            "location_context": {
                                "guild_id": "10000",
                                "channel_id": "10000",
                                "channel_type": 10000,
                            },
                        }

                        response = await self.session.post(
                            "https://discord.com/api/v9/oauth2/authorize",
                            params=params,
                            headers=headers,
                            json=json_data,
                        )

                        if response.status_code == 200:
                            location = response.json().get("location")
                            code = location.split("code=")[1].split("&")[0]
                            headers = {
                                "sec-ch-ua-mobile": "?0",
                                "sec-ch-ua-platform": '"Windows"',
                                "upgrade-insecure-requests": "1",
                                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                                "sec-fetch-site": "cross-site",
                                "sec-fetch-mode": "navigate",
                                "sec-fetch-user": "?1",
                                "sec-fetch-dest": "document",
                                "referer": "https://discord.com/",
                                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                                "priority": "u=0, i",
                            }

                            params = {
                                "code": code,
                                "state": state,
                            }

                            response = await self.session.get(
                                "https://testnet.monad.xyz/api/auth/callback/discord",
                                params=params,
                                headers=headers,
                            )
                            if response.status_code == 200:
                                logger.success(
                                    f"[{self.account_index}] | Discord connected!"
                                )
                                return True
                            else:
                                logger.error(
                                    f"[{self.account_index}] | Failed to connect to discord: {response.text}"
                                )
                                continue
                        else:
                            logger.error(
                                f"[{self.account_index}] | Failed to connect to discord: {response.text}"
                            )
                            continue

                else:
                    logger.error(
                        f"[{self.account_index}] | Failed to get csrf token: {response.text}"
                    )
                    continue

            except Exception as e:
                random_pause = random.randint(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] | Error connect discord to monad.xyz ({retry + 1}/{self.config.SETTINGS.ATTEMPTS}): {e}. Next connect in {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)
                continue
        return False
