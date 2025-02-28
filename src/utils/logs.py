import os
from typing import Dict, Any
from asyncio import Lock


async def report_success(
    lock: Lock, private_key: str, proxy: str, discord_token: str
) -> None:
    """
    Log successful operations to separate files in data/success_data directory.
    Uses asyncio lock to prevent race conditions.

    Args:
        lock: Asyncio lock for thread-safe file operations
        private_key: The private key to log
        proxy: The proxy to log
        discord_token: The Discord token to log
    """
    base_dir = "data/success_data"
    async with lock:
        os.makedirs(base_dir, exist_ok=True)

        # Write each type of data to its respective file
        files_data = {
            "private_keys.txt": private_key,
            "proxies.txt": proxy,
            "discord_tokens.txt": discord_token,
        }

        for filename, data in files_data.items():
            if data:  # Only write if data is not empty
                filepath = os.path.join(base_dir, filename)
                with open(filepath, "a", encoding="utf-8") as f:
                    f.write(f"{data}\n")


async def report_error(
    lock: Lock, private_key: str, proxy: str, discord_token: str
) -> None:
    """
    Log failed operations to separate files in data/error_data directory.
    Uses asyncio lock to prevent race conditions.

    Args:
        lock: Asyncio lock for thread-safe file operations
        private_key: The private key to log
        proxy: The proxy to log
        discord_token: The Discord token to log
    """
    base_dir = "data/error_data"
    async with lock:
        os.makedirs(base_dir, exist_ok=True)

        # Write each type of data to its respective file
        files_data = {
            "private_keys.txt": private_key,
            "proxies.txt": proxy,
            "discord_tokens.txt": discord_token,
        }

        for filename, data in files_data.items():
            if data:  # Only write if data is not empty
                filepath = os.path.join(base_dir, filename)
                with open(filepath, "a", encoding="utf-8") as f:
                    f.write(f"{data}\n")