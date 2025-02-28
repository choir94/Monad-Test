import asyncio
from loguru import logger
from primp import AsyncClient
import requests
from typing import Optional, Dict
from enum import Enum
import time


class CaptchaError(Exception):
    """Base exception for captcha errors"""

    pass


class ErrorCodes(Enum):
    ERROR_WRONG_USER_KEY = "ERROR_WRONG_USER_KEY"
    ERROR_KEY_DOES_NOT_EXIST = "ERROR_KEY_DOES_NOT_EXIST"
    ERROR_ZERO_BALANCE = "ERROR_ZERO_BALANCE"
    ERROR_PAGEURL = "ERROR_PAGEURL"
    IP_BANNED = "IP_BANNED"
    ERROR_PROXY_FORMAT = "ERROR_PROXY_FORMAT"
    ERROR_BAD_PARAMETERS = "ERROR_BAD_PARAMETERS"
    ERROR_BAD_PROXY = "ERROR_BAD_PROXY"
    ERROR_SITEKEY = "ERROR_SITEKEY"
    CAPCHA_NOT_READY = "CAPCHA_NOT_READY"
    ERROR_CAPTCHA_UNSOLVABLE = "ERROR_CAPTCHA_UNSOLVABLE"
    ERROR_WRONG_CAPTCHA_ID = "ERROR_WRONG_CAPTCHA_ID"
    ERROR_EMPTY_ACTION = "ERROR_EMPTY_ACTION"


class BestCaptchaSolver:
    def __init__(
        self,
        proxy: str = "",
        api_key: str = "",
    ):
        self.base_url = "https://bcsapi.xyz/api"
        self.proxy = self._format_proxy(proxy) if proxy else None
        self.api_key = api_key

    def _format_proxy(self, proxy: str) -> Dict[str, str]:
        if not proxy:
            return None
        if "@" in proxy:
            return {"proxy": proxy, "proxy_type": "HTTP"}
        return {"proxy": f"http://{proxy}", "proxy_type": "HTTP"}

    def create_task(
        self,
        sitekey: str,
        pageurl: str,
        invisible: bool = None,
        domain: str = None,
        user_agent: str = None,
    ) -> Optional[str]:
        """Создает задачу на решение капчи"""
        data = {
            "access_token": self.api_key,
            "site_key": sitekey,
            "page_url": pageurl,
        }

        if invisible is not None:
            data["invisible"] = invisible
        if domain:
            data["domain"] = domain
        if user_agent:
            data["user_agent"] = user_agent
        if self.proxy:
            data.update(self.proxy)

        try:
            response = requests.post(
                f"{self.base_url}/captcha/recaptcha",
                json=data,
                timeout=30,
                verify=False,
            ).json()

            if "id" in response:
                return response["id"]

            logger.error(f"Error creating task: {response}")
            return None

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    def get_task_result(self, task_id: str) -> Optional[str]:
        """Получает результат решения капчи"""
        params = {"access_token": self.api_key}

        max_attempts = 30
        for _ in range(max_attempts):
            try:
                response = requests.get(
                    f"{self.base_url}/captcha/{task_id}",
                    params=params,
                    timeout=30,
                    verify=False,
                )
                result = response.json()

                if result.get("status") == "completed":
                    return result["gresponse"]
                elif "error" in response.text:
                    logger.error(f"Error getting result: {response.text}")
                    return None

                time.sleep(5)

            except Exception as e:
                logger.error(f"Error getting result: {e}")
                return None

        return None

    def solve_recaptcha(self, sitekey: str, pageurl: str) -> Optional[str]:
        """Решает hCaptcha и возвращает токен"""
        task_id = self.create_task(sitekey, pageurl, True, "monad.xyz")
        if not task_id:
            return None

        return self.get_task_result(task_id)


class TwentyFourCaptchaSolver:
    def __init__(
        self,
        api_key: str,
        proxy: Optional[str] = None,
    ):
        self.api_key = api_key
        self.base_url = "https://24captcha.online"
        self.proxy = self._format_proxy(proxy) if proxy else None

    def _format_proxy(self, proxy: str) -> Dict[str, str]:
        if not proxy:
            return None
        if "@" in proxy:
            return {"proxy": proxy, "proxytype": "HTTP"}
        return {"proxy": f"http://{proxy}", "proxytype": "HTTP"}

    def create_task(
        self,
        sitekey: str,
        pageurl: str,
        invisible: bool = False,
        enterprise: bool = False,
        rqdata: Optional[str] = None,
    ) -> Optional[str]:
        """Создает задачу на решение капчи"""
        data = {
            "key": self.api_key,
            "method": "hcaptcha",
            "sitekey": sitekey,
            "pageurl": pageurl,
            "json": 1,
        }

        if invisible:
            data["invisible"] = invisible
        if enterprise:
            data["enterprise"] = enterprise
        if rqdata:
            data["rqdata"] = rqdata
        if self.proxy:
            data.update(self.proxy)

        try:
            response = requests.post(
                f"{self.base_url}/in.php", json=data, timeout=30, verify=False
            ).json()
            logger.debug(f"Create captcha task request.")

            if "status" in response and response["status"] == 1:
                return response["request"]

            error = response.get("request", "Unknown error")
            if error in ErrorCodes.__members__:
                logger.error(f"API Error: {error}")
            else:
                logger.error(f"Unknown API Error: {error}")
            return None

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    def get_task_result(self, task_id: str) -> Optional[str]:
        """Получает результат решения капчи"""
        data = {"key": self.api_key, "action": "get", "id": task_id, "json": 1}

        max_attempts = 30
        for _ in range(max_attempts):
            try:
                response = requests.post(
                    f"{self.base_url}/res.php", json=data, timeout=30, verify=False
                ).json()

                if "status" in response and response["status"] == 1:
                    return response["request"]

                error = response.get("request", "Unknown error")
                if error == "CAPCHA_NOT_READY":
                    time.sleep(5)
                    continue

                if error in ErrorCodes.__members__:
                    logger.error(f"API Error: {error}")
                else:
                    logger.error(f"Unknown API Error: {error}")
                return None

            except Exception as e:
                logger.error(f"Error getting result: {e}")
                return None

        logger.error("Max polling attempts reached without getting a result")
        return None

    def solve_hcaptcha(
        self,
        sitekey: str,
        pageurl: str,
        invisible: bool = False,
        enterprise: bool = False,
        rqdata: Optional[str] = None,
    ) -> Optional[str]:
        """Решает hCaptcha и возвращает токен"""
        task_id = self.create_task(
            sitekey=sitekey,
            pageurl=pageurl,
            invisible=invisible,
            enterprise=enterprise,
            rqdata=rqdata,
        )
        if not task_id:
            return None

        return self.get_task_result(task_id)


class Capsolver:
    def __init__(
        self,
        api_key: str,
        proxy: Optional[str] = None,
        session: AsyncClient = None,
    ):
        self.api_key = api_key
        self.base_url = "https://api.capsolver.com"
        self.proxy = self._format_proxy(proxy) if proxy else None
        self.session = session or AsyncClient(verify=False)

    def _format_proxy(self, proxy: str) -> str:
        if not proxy:
            return None
        if "@" in proxy:
            return proxy
        return proxy

    async def create_task(
        self,
        sitekey: str,
        pageurl: str,
        invisible: bool = False,
    ) -> Optional[str]:
        """Создает задачу на решение капчи"""
        data = {
            "clientKey": self.api_key,
            "appId": "0F6B2D90-7CA4-49AC-B0D3-D32C70238AD8",
            "task": {
                "type": "ReCaptchaV2Task",
                "websiteURL": pageurl,
                "websiteKey": sitekey,
                "isInvisible": False,
                # "pageAction": "drip_request",
            },
        }

        if self.proxy:
            data["task"]["proxy"] = self.proxy

        try:
            response = await self.session.post(
                f"{self.base_url}/createTask",
                json=data,
                timeout=30,
            )
            result = response.json()

            if "taskId" in result:
                return result["taskId"]

            logger.error(f"Error creating task: {result}")
            return None

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    async def get_task_result(self, task_id: str) -> Optional[str]:
        """Получает результат решения капчи"""
        data = {"clientKey": self.api_key, "taskId": task_id}

        max_attempts = 30
        for _ in range(max_attempts):
            try:
                response = await self.session.post(
                    f"{self.base_url}/getTaskResult",
                    json=data,
                    timeout=30,
                )
                result = response.json()

                if result.get("status") == "ready":
                    # Handle both reCAPTCHA and Turnstile responses
                    solution = result.get("solution", {})
                    return solution.get("token") or solution.get("gRecaptchaResponse")
                elif "errorId" in result and result["errorId"] != 0:
                    logger.error(f"Error getting result: {result}")
                    return None

                await asyncio.sleep(3)

            except Exception as e:
                logger.error(f"Error getting result: {e}")
                return None

        return None

    async def solve_recaptcha(
        self,
        sitekey: str,
        pageurl: str,
        invisible: bool = False,
    ) -> Optional[str]:
        """Решает RecaptchaV2 и возвращает токен"""
        task_id = await self.create_task(sitekey, pageurl, invisible)
        if not task_id:
            return None

        return await self.get_task_result(task_id)

    async def create_turnstile_task(
        self,
        sitekey: str,
        pageurl: str,
        action: Optional[str] = None,
        cdata: Optional[str] = None,
    ) -> Optional[str]:
        """Creates a Turnstile captcha solving task"""
        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "AntiTurnstileTaskProxyLess",
                "websiteURL": pageurl,
                "websiteKey": sitekey,
            },
        }

        # if action or cdata:
        #     metadata = {}
        #     if action:
        #         metadata["action"] = action
        #     if cdata:
        #         metadata["cdata"] = cdata
        #     data["task"]["metadata"] = metadata
        
        try:
            response = await self.session.post(
                f"{self.base_url}/createTask",
                json=data,
                timeout=30,
            )
            result = response.json()

            if "taskId" in result:
                return result["taskId"]

            logger.error(f"Error creating Turnstile task: {result}")
            return None

        except Exception as e:
            logger.error(f"Error creating Turnstile task: {e}")
            return None

    async def solve_turnstile(
        self,
        sitekey: str,
        pageurl: str,
        action: Optional[str] = None,
        cdata: Optional[str] = None,
    ) -> Optional[str]:
        """Solves Cloudflare Turnstile captcha and returns token"""
        task_id = await self.create_turnstile_task(
            sitekey=sitekey,
            pageurl=pageurl,
            action=action,
            cdata=cdata,
        )
        if not task_id:
            return None

        return await self.get_task_result(task_id)
