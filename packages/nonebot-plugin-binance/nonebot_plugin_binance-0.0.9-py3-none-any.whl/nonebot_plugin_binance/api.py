# =================================================================
# == nonebot_plugin_binance/api.py
# == 说明：封装所有对Binance API的请求。(重构版)
# =================================================================
import hmac
import hashlib
import time
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import aiohttp
from nonebot import logger
from .auth import AuthManager


class ApiClient:
    """
    一个经过重构的币安API客户端，支持现货、U本位合约、币本位合约及账户API。
    """

    # 不同API的根URL
    SPOT_API_URL = "https://api.binance.com"
    UM_FUTURES_API_URL = "https://fapi.binance.com"
    CM_FUTURES_API_URL = "https://dapi.binance.com"
    # SAPI (Sub-Account/System/etc.) 和现货使用相同的基础URL
    SAPI_URL = "https://api.binance.com"

    def __init__(self, auth_manager: AuthManager, config):
        self._auth_manager = auth_manager
        self._proxy = config.binance_api_proxy if config.binance_api_proxy else None
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """获取或创建 aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close_session(self):
        """关闭 aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Aiohttp session closed.")

    def _sign(self, params: Dict[str, Any], secret_key: str) -> str:
        """生成请求签名"""
        query_string = urlencode(params)
        return hmac.new(
            secret_key.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    async def _request(
        self,
        method: str,
        base_url: str,
        path: str,
        user_id: Optional[str] = None,
        signed: bool = False,
        **kwargs,
    ):
        """
        通用请求函数。
        """
        url = f"{base_url}{path}"
        params = kwargs.get("params", {})
        data = kwargs.get("data", {})
        headers = kwargs.get("headers", {})

        if signed:
            if not user_id:
                return {"error": "需要签名的请求必须提供 user_id。"}

            keys = self._auth_manager.get_keys(user_id)
            if not keys:
                return {"error": "用户未绑定或未找到API密钥。"}
            api_key, secret_key = keys
            headers["X-MBX-APIKEY"] = api_key

            payload_to_sign = params if method in ["GET", "DELETE"] else data
            payload_to_sign["timestamp"] = int(time.time() * 1000)
            payload_to_sign["signature"] = self._sign(payload_to_sign, secret_key)

        session = await self.get_session()
        try:
            async with session.request(
                method,
                url,
                proxy=self._proxy,
                params=params,
                data=data,
                headers=headers,
            ) as response:
                logger.debug(f"请求: {method} {response.url} | 状态: {response.status}")
                raw_text = await response.text()

                if not raw_text:
                    logger.warning("API 响应体为空。")
                    return (
                        None
                        if response.status == 200
                        else {"error": "Empty response body"}
                    )
                try:
                    response_data = json.loads(raw_text)
                except json.JSONDecodeError:
                    logger.error(f"JSON 解码失败。 响应文本: {raw_text}")
                    return {"error": "JSON decode error", "data": raw_text}

                if 200 <= response.status < 300:
                    return response_data
                else:
                    logger.error(f"API 错误: {response_data}")
                    return {"error": response_data}
        except aiohttp.ClientError as e:
            logger.error(f"HTTP 请求失败: {e}")
            return {"error": f"请求失败: {e}"}

    # ===============================================================
    # == 公共 & 市场数据 (Public & Market Data)
    # ===============================================================
    async def get_ping(self):
        return await self._request("GET", self.SPOT_API_URL, "/api/v3/ping")

    async def get_ticker_24hr(self, symbol: str):
        return await self._request(
            "GET",
            self.SPOT_API_URL,
            "/api/v3/ticker/24hr",
            params={"symbol": symbol.upper()},
        )

    async def get_klines(self, symbol: str, interval: str, limit: int = 100):
        return await self._request(
            "GET",
            self.SPOT_API_URL,
            "/api/v3/klines",
            params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
        )

    async def get_um_futures_ping(self):
        return await self._request("GET", self.UM_FUTURES_API_URL, "/fapi/v1/ping")

    async def get_um_futures_ticker_24hr(self, symbol: str):
        return await self._request(
            "GET",
            self.UM_FUTURES_API_URL,
            "/fapi/v1/ticker/24hr",
            params={"symbol": symbol.upper()},
        )

    async def get_um_futures_klines(self, symbol: str, interval: str, limit: int = 100):
        return await self._request(
            "GET",
            self.UM_FUTURES_API_URL,
            "/fapi/v1/klines",
            params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
        )

    async def get_cm_futures_ping(self):
        return await self._request("GET", self.CM_FUTURES_API_URL, "/dapi/v1/ping")

    async def get_cm_futures_ticker_24hr(self, symbol: str):
        return await self._request(
            "GET",
            self.CM_FUTURES_API_URL,
            "/dapi/v1/ticker/24hr",
            params={"symbol": symbol.upper()},
        )

    async def get_cm_futures_klines(self, symbol: str, interval: str, limit: int = 100):
        return await self._request(
            "GET",
            self.CM_FUTURES_API_URL,
            "/dapi/v1/klines",
            params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
        )

    # ===============================================================
    # == 账户 & SAPI (Account & SAPI)
    # ===============================================================
    async def get_account_info(self, user_id: str):
        return await self._request(
            "GET",
            self.SPOT_API_URL,
            "/api/v3/account",
            user_id=user_id,
            signed=True,
            params={"omitZeroBalances": "true"},
        )

    async def post_order(
        self, user_id: str, symbol: str, side: str, order_type: str, **kwargs
    ):
        data = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
        }
        data.update(kwargs)
        return await self._request(
            "POST",
            self.SPOT_API_URL,
            "/api/v3/order",
            user_id=user_id,
            signed=True,
            data=data,
        )

    async def get_open_orders(self, user_id: str, symbol: Optional[str] = None):
        params = {}
        (params.update({"symbol": symbol.upper()}) if symbol else None)
        return await self._request(
            "GET",
            self.SPOT_API_URL,
            "/api/v3/openOrders",
            user_id=user_id,
            signed=True,
            params=params,
        )

    async def cancel_order(self, user_id: str, symbol: str, order_id: int):
        return await self._request(
            "DELETE",
            self.SPOT_API_URL,
            "/api/v3/order",
            user_id=user_id,
            signed=True,
            data={"symbol": symbol.upper(), "orderId": order_id},
        )

    async def get_system_status(self):
        return await self._request("GET", self.SAPI_URL, "/sapi/v1/system/status")

    async def get_account_snapshot(self, user_id: str, account_type: str = "SPOT"):
        return await self._request(
            "GET",
            self.SAPI_URL,
            "/sapi/v1/accountSnapshot",
            user_id=user_id,
            signed=True,
            params={"type": account_type.upper()},
        )

    async def get_margin_account(self, user_id: str):
        return await self._request(
            "GET",
            self.SAPI_URL,
            "/sapi/v1/margin/account",
            user_id=user_id,
            signed=True,
        )

    async def get_margin_open_orders(self, user_id: str, symbol: Optional[str] = None):
        params = {}
        (params.update({"symbol": symbol.upper()}) if symbol else None)
        return await self._request(
            "GET",
            self.SAPI_URL,
            "/sapi/v1/margin/openOrders",
            user_id=user_id,
            signed=True,
            params=params,
        )

    async def get_funding_wallet(self, user_id: str):
        """获取资金账户余额"""
        return await self._request(
            "POST",
            self.SAPI_URL,
            "/sapi/v1/asset/get-funding-asset",
            user_id=user_id,
            signed=True,
        )

    # ===============================================================
    # == U本位合约 (USD-S Futures)
    # ===============================================================
    async def get_um_futures_account(self, user_id: str):
        return await self._request(
            "GET",
            self.UM_FUTURES_API_URL,
            "/fapi/v2/account",
            user_id=user_id,
            signed=True,
        )

    async def get_um_futures_balance(self, user_id: str):
        return await self._request(
            "GET",
            self.UM_FUTURES_API_URL,
            "/fapi/v2/balance",
            user_id=user_id,
            signed=True,
        )

    async def get_um_futures_position_risk(
        self, user_id: str, symbol: Optional[str] = None
    ):
        params = {}
        (params.update({"symbol": symbol.upper()}) if symbol else None)
        return await self._request(
            "GET",
            self.UM_FUTURES_API_URL,
            "/fapi/v2/positionRisk",
            user_id=user_id,
            signed=True,
            params=params,
        )

    async def get_um_futures_open_orders(
        self, user_id: str, symbol: Optional[str] = None
    ):
        params = {}
        (params.update({"symbol": symbol.upper()}) if symbol else None)
        return await self._request(
            "GET",
            self.UM_FUTURES_API_URL,
            "/fapi/v1/openOrders",
            user_id=user_id,
            signed=True,
            params=params,
        )

    # ===============================================================
    # == 币本位合约 (COIN-M Futures)
    # ===============================================================
    async def get_cm_futures_account(self, user_id: str):
        return await self._request(
            "GET",
            self.CM_FUTURES_API_URL,
            "/dapi/v1/account",
            user_id=user_id,
            signed=True,
        )

    async def get_cm_futures_balance(self, user_id: str):
        return await self._request(
            "GET",
            self.CM_FUTURES_API_URL,
            "/dapi/v1/balance",
            user_id=user_id,
            signed=True,
        )

    async def get_cm_futures_position_risk(
        self,
        user_id: str,
        pair: Optional[str] = None,
        marginAsset: Optional[str] = None,
    ):
        params = {}
        (params.update({"pair": pair.upper()}) if pair else None)
        (params.update({"marginAsset": marginAsset.upper()}) if marginAsset else None)
        return await self._request(
            "GET",
            self.CM_FUTURES_API_URL,
            "/dapi/v1/positionRisk",
            user_id=user_id,
            signed=True,
            params=params,
        )

    async def get_cm_futures_open_orders(
        self, user_id: str, pair: Optional[str] = None
    ):
        params = {}
        (params.update({"pair": pair.upper()}) if pair else None)
        return await self._request(
            "GET",
            self.CM_FUTURES_API_URL,
            "/dapi/v1/openOrders",
            user_id=user_id,
            signed=True,
            params=params,
        )
