import random
import asyncio
from loguru import logger
from eth_account import Account
from eth_account.signers.local import LocalAccount
from primp import AsyncClient


async def get_mint_data(
    session: AsyncClient,
    nft_contract: str,
    wallet: Account,
    max_retries: int = 10,
    retry_delay: int = 2,
) -> dict:
    """
    Get mint data from MagicEden API for a specific NFT contract.

    Args:
        session: primp.AsyncClient instance
        nft_contract: The NFT contract address
        wallet: The wallet account
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        dict: The mint data response or None if error
        str: Error message if there's a specific error to handle (like "already minted")
    """
    error_log_frequency = 5  # Выводить ошибки каждую 5-ю попытку
    error = ""
    for attempt in range(1, max_retries + 1):
        should_log = (
            attempt % error_log_frequency == 0 or attempt == 1 or attempt == max_retries
        )
        try:
            # Create a random referrer address
            random_wallet = Account.create()
            random_referrer = random_wallet.address

            payload = {
                "currencyChainId": 10143,
                "items": [{"token": f"{nft_contract}:0", "quantity": 1}],
                "partial": True,
                "referrer": random_referrer,
                "source": "magiceden.io",
                "taker": wallet.address,
            }

            headers = {
                "Content-Type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "x-rkc-version": "2.5.4",
                "Accept": "application/json",
                "Origin": "https://magiceden.io",
                "Referer": "https://magiceden.io/",
            }

            response = await session.post(
                "https://api-mainnet.magiceden.io/v3/rtp/monad-testnet/execute/mint/v1",
                headers=headers,
                json=payload,
                timeout=30,  # Increase timeout
            )

            if response.status_code == 200:
                return response.json()
            
            if "Token has no eligible mints":
                logger.warning(
                    f"💀 Wait a bit, MagicEden API returned wrong data..."
                )
                error = "all_nfts_minted"
            elif response.status_code == 400:
                # Проверяем, не связана ли ошибка с тем, что пользователь уже заминтил NFT
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", "")
                    if "max mints per wallet possibly exceeded" in error_message:
                        return "already_minted"
                except:
                    pass

                if should_log:
                    logger.error(
                        f"❌ Failed to get mint data: {response.status_code} - {response.text}"
                    )
            elif response.status_code >= 500:  # Server errors
                if attempt < max_retries:
                    wait_time = retry_delay * attempt
                    # Специальная обработка для "no healthy upstream"
                    if "no healthy upstream" in response.text:
                        if should_log:
                            logger.warning(
                                f"⚠️ MagicEden API temporarily unavailable (attempt {attempt}/{max_retries}). "
                                f"Retrying in {wait_time}s..."
                            )
                    else:
                        if should_log:
                            logger.warning(
                                f"⚠️ MagicEden API server error ({response.status_code}): {response.text}. "
                                f"Retrying in {wait_time}s (attempt {attempt}/{max_retries})"
                            )
                    await asyncio.sleep(wait_time)
                else:
                    if "no healthy upstream" in response.text:
                        logger.error(
                            f"❌ MagicEden API is down after {max_retries} attempts. Please try again later."
                        )
                    else:
                        logger.error(
                            f"❌ Failed to get mint data after {max_retries} attempts: {response.status_code} - {response.text}"
                        )
            else:
                if should_log:
                    logger.error(
                        f"❌ Failed to get mint data: {response.status_code} - {response.text}"
                    )

        except Exception as e:
            if attempt < max_retries:
                wait_time = retry_delay * attempt
                # Специальная обработка для ошибок подключения
                if "connection" in str(e).lower():
                    if should_log:
                        logger.warning(
                            f"⚠️ MagicEden API connection error (attempt {attempt}/{max_retries}). "
                            f"Retrying in {wait_time}s..."
                        )
                else:
                    if should_log:
                        logger.warning(
                            f"⚠️ Error getting mint data: {e}. "
                            f"Retrying in {wait_time}s (attempt {attempt}/{max_retries})"
                        )
                await asyncio.sleep(wait_time)
            else:
                if "connection" in str(e).lower():
                    logger.error(
                        f"❌ Failed to connect to MagicEden API after {max_retries} attempts. Please check your internet connection."
                    )
                else:
                    logger.error(
                        f"❌ Error getting mint data after {max_retries} attempts: {e}"
                    )
                return None

    return error if error != "" else None
