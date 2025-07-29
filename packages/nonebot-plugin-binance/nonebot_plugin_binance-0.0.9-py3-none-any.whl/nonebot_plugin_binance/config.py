# =================================================================
# == nonebot_plugin_binance/config.py
# == 说明：Pydantic配置模型。
# =================================================================
from pydantic import BaseModel
from nonebot import get_plugin_config

class Config(BaseModel):
    """插件配置项"""

    # 用于加密用户API密钥的主密钥，请务必修改为一个复杂且随机的字符串
    # 可以使用以下代码生成: from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())
    binance_master_key: str = ""

    # 【API代理】币安API的代理URL，如果您的服务器无法直接访问币安，请设置此项
    binance_api_proxy: str = ""

    # 【渲染器代理】用于下载图片、字体等渲染资源的代理，如果服务器访问Github等网络不稳定，请设置此项
    # 例如: "http://127.0.0.1:7890"
    binance_renderer_proxy: str = ""

    # 【WS代理】币安WebSocket的代理URL，如果需要的话
    binance_ws_proxy: str = ""
    


plugin_config = get_plugin_config(Config)

from pathlib import Path
from nonebot import require

require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store

# 数据存储路径
binance_data_path: Path = store.get_plugin_data_dir()