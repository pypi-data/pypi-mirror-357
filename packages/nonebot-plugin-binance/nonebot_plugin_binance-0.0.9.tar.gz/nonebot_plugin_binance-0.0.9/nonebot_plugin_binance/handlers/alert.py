# =================================================================
# == nonebot_plugin_binance/handlers/alert.py
# == 说明：处理价格预警命令。
# =================================================================
import re
import asyncio
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from .. import ws_manager, drawer, api_client
from .market import format_symbol

alert_cmd = on_command("bn alert", aliases={"币安预警"}, priority=10, block=True)


# 辅助函数：根据市场获取对应的价格查询API
def get_ticker_api_for_market(market: str):
    if market == "spot":
        return api_client.get_ticker_24hr
    elif market == "um":
        return api_client.get_um_futures_ticker_24hr
    elif market == "cm":
        return api_client.get_cm_futures_ticker_24hr
    return None


@alert_cmd.handle()
async def handle_alert(event: GroupMessageEvent, args: Message = CommandArg()):
    if not isinstance(event, GroupMessageEvent):
        await alert_cmd.finish("价格预警功能请在群聊中使用。")

    arg_text = args.extract_plain_text().strip()
    if not arg_text:
        await alert_cmd.finish("用法: bn alert add [市场] <交易对> <或>价格")

    parts = arg_text.split()
    action = parts[0].lower()
    user_id = event.get_user_id()
    group_id = str(event.group_id)

    if action == "add":
        valid_markets = ["spot", "um", "cm"]
        market = "spot"  # 默认市场

        # 智能解析指令
        if len(parts) < 3:
            return await alert_cmd.finish(
                "添加格式错误！\n用法: bn alert add [市场] <交易对> <或>价格\n示例: bn alert add um btc-usdt >68000"
            )

        if parts[1].lower() in valid_markets:
            if len(parts) != 4:
                return await alert_cmd.finish(
                    "指定市场的格式错误！\n用法: bn alert add <市场> <交易对> <或>价格"
                )
            market = parts[1].lower()
            symbol_raw = parts[2]
            condition_price_str = parts[3]
        else:
            symbol_raw = parts[1]
            condition_price_str = parts[2]

        # 如果输入的是单一币种，默认为USDT交易对
        if "-" not in symbol_raw and "/" not in symbol_raw:
            symbol_raw = f"{symbol_raw}-USDT"

        # 验证价格条件
        match = re.match(r"([><])=?\s*(\d+\.?\d*)", condition_price_str)
        if not match:
            return await alert_cmd.finish(
                "价格条件格式错误！请使用 '>' 或 '<' 加价格，例如 '>68000'。"
            )
        condition, value_str = match.groups()
        value = float(value_str)

        # 格式化交易对并验证其有效性
        formatted_sym = format_symbol(symbol_raw)
        ticker_api = get_ticker_api_for_market(market)
        if not ticker_api:
            return await alert_cmd.finish(f"内部错误：未知的市场类型 '{market}'。")

        ticker_data = await ticker_api(formatted_sym)
        if not isinstance(ticker_data, dict) or "lastPrice" not in ticker_data:
            error_msg = ticker_data.get("error", {}).get("msg", "交易对不存在或无效")
            return await alert_cmd.finish(
                f"无法为 '{symbol_raw.upper()}' 添加预警：{error_msg}"
            )

        current_price = float(ticker_data["lastPrice"])

        # 添加预警
        alert_id = await ws_manager.add_alert(
            market, formatted_sym, user_id, group_id, condition, value
        )
        market_name = {"spot": "现货", "um": "U本位合约", "cm": "币本位合约"}.get(
            market
        )

        await alert_cmd.finish(
            f"✅ {market_name}预警设置成功！\n"
            f"ID: {alert_id}\n"
            f"交易对: {formatted_sym}\n"
            f"当前价格: {current_price}\n"
            f"触发条件: 当价格 {condition} {value} 时，我会 @你。"
        )

    elif action == "list":
        user_alerts = ws_manager.get_user_alerts(user_id)
        if not user_alerts:
            return await alert_cmd.finish("您当前没有设置任何价格预警。")

        # 并发获取所有预警交易对的当前价格
        price_tasks = []
        for alert in user_alerts:
            ticker_api = get_ticker_api_for_market(alert["market"])
            if ticker_api:
                price_tasks.append(ticker_api(alert["symbol"]))

        price_results = await asyncio.gather(*price_tasks, return_exceptions=True)

        price_map = {}
        for result in price_results:
            if isinstance(result, dict) and "symbol" in result:
                price_map[result["symbol"]] = result.get("lastPrice", "N/A")

        # 将价格信息添加到预警数据中
        for alert in user_alerts:
            alert["current_price"] = price_map.get(alert["symbol"], "获取失败")

        img = await drawer.draw_alert_list(user_alerts)
        if img:
            await alert_cmd.finish(MessageSegment.image(img))
        else:
            await alert_cmd.finish("生成预警列表图片失败，请检查后台日志。")

    elif action == "remove":
        if len(parts) != 2:
            await alert_cmd.finish("移除预警格式错误！\n用法: bn alert remove <预警ID>")
        alert_id = parts[1]
        if ws_manager.remove_alert(alert_id):
            await alert_cmd.finish(f"✅ 预警 {alert_id} 已成功移除。")
        else:
            await alert_cmd.finish(f"❌ 未找到ID为 {alert_id} 的预警，或它已被触发。")

    else:
        await alert_cmd.finish(
            f"未知的操作 '{action}'。请使用 'add', 'list', 或 'remove'。"
        )
