import asyncio
import secrets
import random
import primp
from loguru import logger
from src.model.help import Capsolver
from src.utils.config import Config
from eth_account import Account


async def faucet(
    session: primp.AsyncClient,
    account_index: int,
    config: Config,
    wallet: Account,
) -> bool:
    for retry in range(config.SETTINGS.ATTEMPTS):
        try:
            solver = Capsolver(
                config.FAUCET.CAPSOLVER_API_KEY,
                config.FAUCET.PROXY_FOR_CAPTCHA,
                session,
            )
            for _ in range(3):
                result = await solver.solve_turnstile(
                    "0x4AAAAAAA-3X4Nd7hf3mNGx",
                    "https://testnet.monad.xyz/",
                    True,
                )
                if result:
                    logger.success(f"{wallet.address} | Captcha solved for faucet")
                    break
                else:
                    logger.error(
                        f"{wallet.address} | Failed to solve captcha for faucet"
                    )

            if not result:
                raise Exception("failed to solve captcha for faucet 3 times")

            headers = {
                "accept": "*/*",
                "accept-language": "fr-CH,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "content-type": "application/json",
                "origin": "https://testnet.monad.xyz",
                "priority": "u=1, i",
                "referer": "https://testnet.monad.xyz/",
                "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="131", "Google Chrome";v="131"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            }

            visitor_id = secrets.token_hex(16)

            json_data = {
                "address": wallet.address,
                "visitorId": visitor_id,
                "cloudFlareResponseToken": result,
            }

            for _ in range(config.SETTINGS.ATTEMPTS):
                response = await session.post(
                    "https://testnet.monad.xyz/api/claim",
                    headers=headers,
                    json=json_data,
                )

                if "Claimed already" in response.text:
                    logger.success(
                        f"[{account_index}] | Already claimed tokens from faucet"
                    )
                    return True

                if response.status_code == 200:
                    logger.success(
                        f"[{account_index}] | Successfully got tokens from faucet"
                    )
                    return True
                else:
                    if "FUNCTION_INVOCATION_TIMEOUT" in response.text:
                        logger.error(
                            f"[{account_index}] | Failed to get tokens from faucet: server is not responding, wait..."
                        )
                    elif "Server error on QuickNode API" in response.text:
                        logger.error(
                            f"[{account_index}] | FAUCET DOES NOT WORK, QUICKNODE IS DOWN"
                        )
                    elif "Over Enterprise free quota" in response.text:
                        logger.error(
                            f"[{account_index}] | MONAD IS SHIT, FAUCET DOES NOT WORK, TRY LATER"
                        )
                        return False
                    elif "invalid-keys" in response.text:
                        logger.error(
                            f"[{account_index}] | PLEASE UPDATE THE BOT USING GITHUB"
                        )
                        return False
                    else:
                        logger.error(
                            f"[{account_index}] | Failed to get tokens from faucet"
                        )
                    await asyncio.sleep(3)
                    break

        except Exception as e:
            random_pause = random.randint(
                config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
            )
            logger.error(
                f"[{account_index}] | Error faucet to monad.xyz ({retry + 1}/{config.SETTINGS.ATTEMPTS}): {e}. Next faucet in {random_pause} seconds"
            )
            continue
    return False
