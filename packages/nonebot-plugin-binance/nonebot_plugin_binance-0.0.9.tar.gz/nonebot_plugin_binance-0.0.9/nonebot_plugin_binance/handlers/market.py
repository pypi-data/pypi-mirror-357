# =================================================================
# == nonebot_plugin_binance/handlers/market.py
# == 说明：处理行情查询命令。
# =================================================================
import json
import asyncio
from nonebot import on_command, logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from .. import drawer, api_client

# 已知的所有指令或别名，用于防止快捷指令冲突
KNOWN_COMMANDS = {
    # system.py
    "help",
    "币安帮助",
    "bind",
    "币安绑定",
    "unbind",
    "币安解绑",
    "status",
    "币安状态",
    # market.py - self
    "kline",
    "k",
    "币安K线",
    # trade.py
    "balance",
    "bal",
    "币安资产",
    "order",
    "币安下单",
    "open",
    "币安挂单",
    "cancel",
    "币安撤单",
    "pos",
    # alert.py
    "alert",
    "币安预警",
}


def format_symbol(raw_symbol: str) -> str:
    """格式化交易对，例如 btc-usdt -> BTCUSDT"""
    return raw_symbol.replace("-", "").replace("/", "").upper()


kline_cmd = on_command("bn kline", aliases={"bn k", "币安K线"}, priority=10, block=True)
# 核心指令处理器，用于快捷查询
bn_shortcut_cmd = on_command("bn", priority=15, block=True)


@bn_shortcut_cmd.handle()
async def handle_bn_main_shortcut(args: Message = CommandArg()):
    """
    处理 `bn <币种>` 形式的核心指令。
    一站式查询现货、U本位合约、币本位合约市场的行情。
    """
    arg_text = args.extract_plain_text().strip()

    if " " in arg_text or not arg_text or arg_text.lower() in KNOWN_COMMANDS:
        await bn_shortcut_cmd.finish()
        return

    # --- 交易对智能格式化 ---
    if "-" in arg_text or "/" in arg_text:
        symbol_display = arg_text.upper().replace("/", "-")
    else:
        symbol_display = f"{arg_text.upper()}-USDT"

    spot_um_symbol = format_symbol(symbol_display)
    base_asset = symbol_display.split("-")[0]
    cm_symbol = f"{base_asset}USD_PERP"

    await bn_shortcut_cmd.send(f"正在查询 {symbol_display} 的多市场行情...")

    # --- 并发API请求 ---
    spot_task = api_client.get_ticker_24hr(spot_um_symbol)
    um_futures_task = api_client.get_um_futures_ticker_24hr(spot_um_symbol)
    cm_futures_task = api_client.get_cm_futures_ticker_24hr(cm_symbol)

    results = await asyncio.gather(
        spot_task, um_futures_task, cm_futures_task, return_exceptions=True
    )
    spot_data, um_futures_data, cm_futures_data = results

    markets_data = []

    # --- 数据处理 ---
    if isinstance(spot_data, dict) and "symbol" in spot_data:
        spot_data["name"] = "现货 (Spot)"
        markets_data.append(spot_data)
    elif isinstance(spot_data, Exception):
        logger.warning(f"获取现货行情时出错 for {spot_um_symbol}: {spot_data}")

    if isinstance(um_futures_data, dict) and "symbol" in um_futures_data:
        um_futures_data["name"] = "U本位合约 (Perpetual)"
        markets_data.append(um_futures_data)
    elif isinstance(um_futures_data, Exception):
        logger.warning(
            f"获取U本位合约行情时出错 for {spot_um_symbol}: {um_futures_data}"
        )

    cm_data_to_process = None
    if isinstance(cm_futures_data, list) and len(cm_futures_data) > 0:
        cm_data_to_process = cm_futures_data[0]
    elif isinstance(cm_futures_data, dict) and "symbol" in cm_futures_data:
        cm_data_to_process = cm_futures_data

    if cm_data_to_process:
        try:
            cm_data_to_process["name"] = "币本位合约 (COIN-M)"
            last_price = float(cm_data_to_process.get("lastPrice", 0))
            base_volume = float(cm_data_to_process.get("baseVolume", 0))
            cm_data_to_process["quoteVolume"] = base_volume * last_price
            markets_data.append(cm_data_to_process)
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"处理币本位合约数据时出错 for {cm_symbol}: {e}")
    elif isinstance(cm_futures_data, Exception):
        logger.warning(f"获取币本位合约行情时出错 for {cm_symbol}: {cm_futures_data}")

    if not markets_data:
        error_msg = "未知错误"
        if isinstance(spot_data, dict) and spot_data.get("error"):
            error_msg = spot_data["error"].get("msg", str(spot_data["error"]))
        await bn_shortcut_cmd.finish(
            f"查询失败: {error_msg}。请检查交易对 '{symbol_display}' 是否正确。"
        )
        return

    # --- 渲染并发送 ---
    render_data = {"symbol_display": symbol_display, "markets": markets_data}
    img = await drawer.draw_multi_market_ticker(render_data)
    if img:
        await bn_shortcut_cmd.finish(MessageSegment.image(img))
    else:
        await bn_shortcut_cmd.finish("生成行情图片失败，请检查后台日志。")


@kline_cmd.handle()
async def handle_kline(args: Message = CommandArg()):
    arg_text = args.extract_plain_text().strip()
    if not arg_text:
        await kline_cmd.finish("请输入交易对。例如: `bn k btc-usdt 1h` 或 `bn k btc`")

    parts = arg_text.split()
    symbol_arg = parts[0]

    # --- FIX: 智能格式化交易对 & 周期 ---
    if "-" not in symbol_arg and "/" not in symbol_arg:
        symbol_display = f"{symbol_arg.upper()}-USDT"
    else:
        symbol_display = symbol_arg.upper().replace("/", "-")

    interval = "1d"  # 默认周期
    if len(parts) > 1:
        interval = parts[1].lower()

    valid_intervals = [
        "1m",
        "3m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "4h",
        "6h",
        "8h",
        "12h",
        "1d",
        "3d",
        "1w",
        "1M",
    ]
    if interval not in valid_intervals:
        await kline_cmd.finish(
            f"无效的K线周期 '{interval}'。\n支持的周期: {', '.join(valid_intervals)}"
        )

    # --- FIX: 验证交易对有效性 ---
    spot_um_symbol = format_symbol(symbol_display)
    # 使用现货 ticker 端点快速验证交易对是否存在
    validation_data = await api_client.get_ticker_24hr(spot_um_symbol)
    if "error" in validation_data:
        error_msg = validation_data["error"].get("msg", "交易对无效")
        return await kline_cmd.finish(f"查询失败: {error_msg} ({symbol_display})")

    base_asset = symbol_display.split("-")[0]
    cm_symbol = f"{base_asset}USD_PERP"

    await kline_cmd.send(f"正在获取 {symbol_display} ({interval}) 的多市场K线数据...")

    # --- 并发API请求 ---
    spot_task = api_client.get_klines(spot_um_symbol, interval)
    um_task = api_client.get_um_futures_klines(spot_um_symbol, interval)
    cm_task = api_client.get_cm_futures_klines(cm_symbol, interval)

    results = await asyncio.gather(spot_task, um_task, cm_task, return_exceptions=True)
    spot_klines, um_klines, cm_klines = results

    markets_data = []

    # --- 数据处理 ---
    if isinstance(spot_klines, list) and len(spot_klines) > 0:
        markets_data.append({"name": "现货 (Spot)", "klines": spot_klines})

    if isinstance(um_klines, list) and len(um_klines) > 0:
        markets_data.append({"name": "U本位合约 (Perpetual)", "klines": um_klines})

    if isinstance(cm_klines, list) and len(cm_klines) > 0:
        markets_data.append({"name": "币本位合约 (COIN-M)", "klines": cm_klines})

    if not markets_data:
        await kline_cmd.finish(
            f"无法获取 {symbol_display} 在任何市场的K线数据，请检查交易对或该周期是否有数据。"
        )
        return

    # --- 渲染并发送 ---
    render_data = {
        "symbol_display": symbol_display,
        "interval": interval,
        "markets": markets_data,
    }

    img = await drawer.draw_multi_market_kline(render_data)
    if img:
        await kline_cmd.finish(MessageSegment.image(img))
    else:
        await kline_cmd.finish("生成多市场K线图失败，请检查后台日志。")
