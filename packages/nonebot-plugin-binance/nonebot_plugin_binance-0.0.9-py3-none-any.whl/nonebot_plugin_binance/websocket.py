# =================================================================
# == nonebot_plugin_binance/websocket.py
# == 说明：WebSocket管理与价格预警。(多市场版)
# =================================================================
import asyncio
import json
import websockets
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, DefaultDict, Tuple
from nonebot import logger
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .config import binance_data_path


class WebsocketManager:
    # 不同市场的WebSocket基础URL
    WS_URLS = {
        "spot": "wss://stream.binance.com:9443/ws",
        "um": "wss://fstream.binance.com/ws",
        "cm": "wss://dstream.binance.com/ws",
    }

    def __init__(self, config):
        self._proxy = config.binance_ws_proxy if config.binance_ws_proxy else None
        # _alerts 现在是一个简单的列表，每个元素都是一个包含所有信息的字典
        self._alerts: List[Dict] = []
        # _tasks 的键现在是一个元组 (market, symbol_lower)
        self._tasks: Dict[Tuple[str, str], asyncio.Task] = {}
        self.data_dir = Path(binance_data_path)
        self.alerts_file = self.data_dir / "alerts.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def load_alerts(self):
        """从文件加载预警"""
        if self.alerts_file.exists():
            with open(self.alerts_file, "r", encoding="utf-8") as f:
                try:
                    # 直接加载列表
                    self._alerts = json.load(f)
                    for alert in self._alerts:
                        alert["triggered"] = False  # 重置触发状态
                    logger.info(f"从文件成功加载 {len(self._alerts)} 条预警。")
                except json.JSONDecodeError:
                    logger.error(f"解码 alerts.json 失败，文件可能已损坏。")

    def _save_alerts(self):
        """保存预警到文件"""
        with open(self.alerts_file, "w", encoding="utf-8") as f:
            json.dump(self._alerts, f, indent=4, ensure_ascii=False)
        logger.info("预警已保存到文件。")

    async def add_alert(
        self,
        market: str,
        symbol: str,
        user_id: str,
        group_id: str,
        condition: str,
        value: float,
    ) -> str:
        """添加新的价格预警"""
        alert_id = str(uuid.uuid4())[:8]
        new_alert = {
            "id": alert_id,
            "user_id": user_id,
            "group_id": group_id,
            "market": market,  # 新增市场字段
            "symbol": symbol.upper(),
            "condition": condition,
            "value": value,
            "triggered": False,
        }
        self._alerts.append(new_alert)
        self._save_alerts()

        # 检查并启动对应的WebSocket任务
        await self.start_websocket(market, symbol.lower())
        return alert_id

    def get_user_alerts(self, user_id: str) -> list:
        """获取指定用户的所有预警"""
        return [alert for alert in self._alerts if alert["user_id"] == user_id]

    def remove_alert(self, alert_id: str) -> bool:
        """移除一个预警"""
        alert_to_remove = None
        for alert in self._alerts:
            if alert["id"] == alert_id:
                alert_to_remove = alert
                break

        if alert_to_remove:
            self._alerts.remove(alert_to_remove)
            self._save_alerts()

            # 检查是否需要停止对应的WebSocket任务
            market = alert_to_remove["market"]
            symbol_lower = alert_to_remove["symbol"].lower()
            remaining_alerts = [
                a
                for a in self._alerts
                if a["market"] == market and a["symbol"].lower() == symbol_lower
            ]
            if not remaining_alerts:
                asyncio.create_task(self.stop_websocket(market, symbol_lower))

            return True
        return False

    async def _process_message(self, market: str, symbol_lower: str, message: str):
        """处理收到的WebSocket消息"""
        data = json.loads(message)
        if "p" in data:
            price = float(data["p"])

            # 查找所有匹配此市场和交易对的预警
            alerts_to_check = [
                a
                for a in self._alerts
                if not a.get("triggered", False)
                and a["market"] == market
                and a["symbol"].lower() == symbol_lower
            ]

            for alert in alerts_to_check:
                condition_met = (
                    alert["condition"] == ">" and price > alert["value"]
                ) or (alert["condition"] == "<" and price < alert["value"])

                if condition_met:
                    logger.info(
                        f"预警触发 {market}/{alert['symbol']}: 价格 {price} {alert['condition']} {alert['value']}"
                    )
                    await self._notify_user(alert, price)
                    # 触发后即移除
                    self.remove_alert(alert["id"])

    async def _notify_user(self, alert: dict, price: float):
        """发送通知给用户"""
        try:
            bot = get_bot()
            market_name = {"spot": "现货", "um": "U本位合约", "cm": "币本位合约"}.get(
                alert["market"], "未知市场"
            )
            msg = Message(
                f"[{market_name}价格预警] {MessageSegment.at(alert['user_id'])}\n"
                f"您关注的 {alert.get('symbol', '').upper()} 价格已 {alert['condition']} {alert['value']}！\n"
                f"当前价格: {price}"
            )
            await bot.send_group_msg(group_id=int(alert["group_id"]), message=msg)
        except Exception as e:
            logger.error(f"发送预警通知失败: {e}")

    async def _websocket_client(self, market: str, symbol_lower: str):
        """单个市场交易对的WebSocket客户端，包含自动重连"""
        base_url = self.WS_URLS.get(market)
        if not base_url:
            logger.error(f"未知的预警市场类型: {market}")
            return

        url = f"{base_url}/{symbol_lower}@trade"
        connect_params = {"proxy": self._proxy} if self._proxy else {}

        # 只要还有针对这个(market, symbol)的预警，就保持连接
        while any(
            a["market"] == market and a["symbol"].lower() == symbol_lower
            for a in self._alerts
        ):
            try:
                async with websockets.connect(url, **connect_params) as ws:
                    logger.info(f"WebSocket 已连接: {market}/{symbol_lower}")
                    while any(
                        a["market"] == market and a["symbol"].lower() == symbol_lower
                        for a in self._alerts
                    ):
                        message = await ws.recv()
                        await self._process_message(market, symbol_lower, message)
            except asyncio.CancelledError:
                logger.info(f"WebSocket 任务被取消: {market}/{symbol_lower}")
                break
            except Exception as e:
                logger.warning(
                    f"WebSocket 连接出错 ({market}/{symbol_lower}): {e}. 5秒后重连..."
                )
                await asyncio.sleep(5)
        logger.info(f"WebSocket 已永久停止: {market}/{symbol_lower}")

    async def start_websocket(self, market: str, symbol_lower: str):
        """启动一个WebSocket连接"""
        task_key = (market, symbol_lower)
        if task_key not in self._tasks or self._tasks[task_key].done():
            logger.info(f"正在启动 WebSocket: {market}/{symbol_lower}...")
            task = asyncio.create_task(self._websocket_client(market, symbol_lower))
            self._tasks[task_key] = task

    async def stop_websocket(self, market: str, symbol_lower: str):
        """停止一个WebSocket连接"""
        task_key = (market, symbol_lower)
        if task_key in self._tasks:
            logger.info(f"正在停止 WebSocket: {market}/{symbol_lower}...")
            task = self._tasks.pop(task_key)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def start_all_websockets(self):
        """启动所有需要监控的WebSocket"""
        if not self._alerts:
            logger.info("没有预警需要启动，跳过 WebSocket 连接。")
            return

        # 获取所有不重复的 (market, symbol) 组合
        unique_streams = {(a["market"], a["symbol"].lower()) for a in self._alerts}
        logger.info(f"正在为 {len(unique_streams)} 个数据流启动 WebSockets...")
        for market, symbol_lower in unique_streams:
            await self.start_websocket(market, symbol_lower)

    async def stop_all_websockets(self):
        """停止所有WebSocket连接"""
        logger.info(f"正在停止所有 {len(self._tasks)} 个 WebSocket 连接...")
        tasks_to_stop = list(self._tasks.keys())
        for market, symbol_lower in tasks_to_stop:
            await self.stop_websocket(market, symbol_lower)
        logger.info("所有 WebSocket 连接已停止。")
