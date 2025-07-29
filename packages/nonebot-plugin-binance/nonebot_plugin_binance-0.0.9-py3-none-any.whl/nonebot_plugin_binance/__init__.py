# =================================================================
# == nonebot_plugin_binance/__init__.py
# == 说明：插件主入口文件。
# =================================================================
from nonebot import get_driver, require
from nonebot.plugin import PluginMetadata
from .config import plugin_config
from .api import ApiClient
from .drawer import Drawer
from .auth import AuthManager
from .websocket import WebsocketManager

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="币安小助手",
    description="一个功能强大的币安(Binance)插件，提供行情、交易、资产查询和实时价格预警功能。",
    usage="""
        使用 'bn help' 或 '币安帮助' 查看详细指令。
        首次使用请私聊机器人 'bn bind [API Key] [Secret Key]' 绑定账户。
    """,
    type="application",
    homepage="https://github.com/newcovid/nonebot-plugin-binance",
    config=type(plugin_config),
    supported_adapters={"~onebot.v11"},
)

# 依赖注入 htmlrender 插件
require("nonebot_plugin_htmlrender")

# 全局驱动
driver = get_driver()

# 实例化核心模块
auth_manager = AuthManager(plugin_config.binance_master_key)
api_client = ApiClient(auth_manager, plugin_config)
drawer = Drawer(plugin_config)
ws_manager = WebsocketManager(plugin_config)


# 在驱动加载时初始化服务
@driver.on_startup
async def on_startup():
    """在机器人启动时加载数据和启动后台任务"""
    auth_manager.load_keys()
    await ws_manager.load_alerts()
    await ws_manager.start_all_websockets()


# 在驱动关闭时清理资源
@driver.on_shutdown
async def on_shutdown():
    """在机器人关闭时停止所有websocket并关闭会话"""
    await ws_manager.stop_all_websockets()
    await api_client.close_session()


# 注册所有命令处理器
from .handlers import system, market, trade, alert
