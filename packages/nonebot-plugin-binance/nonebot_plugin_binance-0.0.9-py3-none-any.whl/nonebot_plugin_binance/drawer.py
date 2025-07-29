# =================================================================
# == nonebot_plugin_binance/drawer.py
# == 说明：使用htmlrender生成所有图片，并包含图片缓存逻辑。
# =================================================================
import aiohttp
from pathlib import Path
from typing import Dict, Any, List, Optional
from nonebot import logger
import jinja2
from datetime import datetime
from .config import binance_data_path


# --- 自定义Jinja2过滤器 ---
def format_timestamp(ms_timestamp: float, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    if not isinstance(ms_timestamp, (int, float)):
        return ""
    dt_object = datetime.fromtimestamp(ms_timestamp / 1000)
    return dt_object.strftime(fmt)


class ImageCache:
    def __init__(self, base_path: str, proxy: Optional[str] = None):
        self.cache_dir = Path(base_path) / "image_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.proxy = proxy
        self._session: Optional[aiohttp.ClientSession] = None
        self.generic_url_templates = [
            "https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@master/128/color/{asset_lower}.png",
            "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/{asset_lower}.png",
            "https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/{asset_address}/logo.png",
        ]
        logger.info(f"图片缓存已初始化，路径: {self.cache_dir}")

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _download_image(self, url: str, file_path: Path):
        try:
            session = await self.get_session()
            async with session.get(url, proxy=self.proxy) as response:
                if response.status == 200:
                    with open(file_path, "wb") as f:
                        f.write(await response.read())
                    logger.success(f"成功下载并缓存图片: {url} -> {file_path}")
                    return True
                else:
                    logger.debug(f"下载尝试失败，状态码 {response.status}: {url}")
                    return False
        except Exception as e:
            logger.error(f"下载图片时发生网络错误: {e}, URL: {url}")
            return False

    async def get_icon_path(
        self, asset_name: str, asset_address: Optional[str] = None
    ) -> str:
        if not asset_name:
            return ""
        file_name = f"{asset_name.lower()}.png"
        local_path = (self.cache_dir / file_name).resolve()
        if local_path.exists():
            return local_path.as_uri()
        for url_template in self.generic_url_templates:
            if "{asset_address}" in url_template and not asset_address:
                continue
            url = url_template.format(
                asset_lower=asset_name.lower(), asset_address=asset_address
            )
            if await self._download_image(url, local_path):
                return local_path.as_uri()
        return f"https://via.placeholder.com/32/363940/FFFFFF?text={asset_name[0]}"

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


class Drawer:
    def __init__(self, config):
        self.template_path = Path(__file__).parent.resolve() / "templates"
        self.proxy = config.binance_renderer_proxy
        self.image_cache = ImageCache(binance_data_path, self.proxy)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_path),
            enable_async=True,
            autoescape=True,
        )
        self.jinja_env.filters["format_timestamp"] = format_timestamp

    async def render(self, template_name: str, data: Dict[str, Any]) -> bytes:
        from nonebot_plugin_htmlrender import html_to_pic

        try:
            template = self.jinja_env.get_template(template_name)
            html_content = await template.render_async(
                data=data, template_path=self.template_path.as_uri()
            )
            render_kwargs = {}
            if self.proxy:
                render_kwargs["proxy"] = {"server": self.proxy}

            return await html_to_pic(
                html=html_content,
                template_path=self.template_path.as_uri(),
                viewport={"width": 800, "height": 10},
                **render_kwargs,
            )
        except Exception as e:
            logger.error(f"渲染模板 {template_name} 时出错: {e}")
            return b""

    async def draw_help(self) -> bytes:
        return await self.render("help.html", {})

    async def draw_multi_market_ticker(self, data: Dict[str, Any]) -> bytes:
        return await self.render("multi_ticker.html", data)

    async def draw_multi_market_kline(self, data: Dict[str, Any]) -> bytes:
        return await self.render("multi_kline.html", data)

    async def draw_balance(self, balance_data: Dict[str, Any]) -> bytes:
        return await self.render("balance.html", balance_data)

    async def draw_account_snapshot(self, snapshot_data: Dict[str, Any]) -> bytes:
        return await self.render("account_snapshot.html", snapshot_data)

    async def draw_positions(self, data: Dict[str, Any]) -> bytes:
        return await self.render("positions.html", data)

    async def draw_orders(self, data: Dict[str, Any]) -> bytes:
        """渲染挂单模板 (支持分组)"""
        return await self.render("orders.html", data)

    async def draw_alert_list(self, alerts: List[Dict[str, Any]]) -> bytes:
        return await self.render("alert_list.html", {"alerts": alerts})

    async def draw_status(self, status_data: Dict[str, Any]) -> bytes:
        return await self.render("status.html", status_data)
