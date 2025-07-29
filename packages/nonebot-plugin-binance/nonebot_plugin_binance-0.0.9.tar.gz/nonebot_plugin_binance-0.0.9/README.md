<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-binance

_✨ NoneBot 插件简单描述 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/newcovid/nonebot-plugin-binance.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-binance">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-binance.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

一个币安 NoneBot2 插件

## 📖 介绍

通过集成币安官方 API，为用户提供行情查询、K线图表、资产管理、实盘交易及价格监控等功能。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-binance

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-binance
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-binance
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-binance
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-binance
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_binance"]

</details>

## ⚙️ 配置

### 必填配置
在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|       配置项       | 必填  | 默认值 |          说明           |
| :----------------: | :---: | :----: | :---------------------: |
| binance_master_key |  是   |   无   | 用于加密用户API的主密钥 |

### 可选配置
在 nonebot2 项目的`.env`文件中添加下表中的可选配置

|         配置项         | 必填  | 默认值 |                                       说明                                       |
| :--------------------: | :---: | :----: | :------------------------------------------------------------------------------: |
|   binance_api_proxy    |  否   |   无   |           币安API的代理URL，如果您的服务器无法直接访问币安，请设置此项           |
| binance_renderer_proxy |  否   |   无   | 用于下载图片、字体等渲染资源的代理，如果服务器访问Github等网络不稳定，请设置此项 |
|    binance_ws_proxy    |  否   |   无   |                       币安WebSocket的代理URL，如果需要的话                       |

## 🎉 使用
### 主密钥
可以使用以下代码生成: 
``` python
from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())
```
### 指令表
使用bn help查看帮助
### 效果图
![](/images/help.png)
![](/images/status.png)
![](/images/ticker.png)
![](/images/kline.png)
![](/images/balance.png)
![](/images/pos.png)
![](/images/alert.png)
![](/images/open.png)


