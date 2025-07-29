# =================================================================
# == nonebot_plugin_binance/handlers/trade.py
# == 说明：处理交易和资产查询命令。
# =================================================================
import asyncio
import re
from typing import Any, Dict
from collections import defaultdict
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Event, Message, MessageSegment
from nonebot import logger
from .. import drawer, api_client, auth_manager
from .market import format_symbol

balance_cmd = on_command(
    "bn balance", aliases={"bn bal", "币安资产"}, priority=10, block=True
)
pos_cmd = on_command("bn pos", aliases={"币安仓位"}, priority=10, block=True)
order_cmd = on_command("bn order", aliases={"币安下单"}, priority=10, block=True)
open_orders_cmd = on_command("bn open", aliases={"币安挂单"}, priority=10, block=True)
cancel_cmd = on_command("bn cancel", aliases={"币安撤单"}, priority=10, block=True)


def get_error_message(data: Any) -> str:
    """从API返回的数据中安全地提取错误信息"""
    if isinstance(data, dict):
        error_content = data.get("error", "未知字典格式错误")
        if isinstance(error_content, dict):
            return error_content.get("msg", str(error_content))
        return str(error_content)
    elif isinstance(data, str):
        return data
    return "未知的错误类型"


def format_float_str(f_val: Any) -> str:
    """将浮点数或字符串格式化为字符串，并移除末尾多余的0和小数点"""
    try:
        f = float(f_val)
        return f"{f:.8f}".rstrip("0").rstrip(".") or "0"
    except (ValueError, TypeError):
        return "0"


@balance_cmd.handle()
async def handle_balance(event: Event):
    user_id = event.get_user_id()
    if not auth_manager.get_keys(user_id):
        await balance_cmd.finish(
            "请先私聊我绑定API Key: bn bind [API Key] [Secret Key]"
        )

    await balance_cmd.send("正在查询您的全账户实时资产...")

    # --- 并发请求多个账户的实时余额 ---
    tasks = {
        "spot": api_client.get_account_info(user_id),
        "margin": api_client.get_margin_account(user_id),
        "funding": api_client.get_funding_wallet(user_id),
        "um_futures": api_client.get_um_futures_balance(user_id),
        "cm_futures": api_client.get_cm_futures_balance(user_id),
    }
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    spot_data, margin_data, funding_data, um_data, cm_data = results

    # --- 数据聚合与处理 ---
    all_assets_names = set()
    final_accounts = []
    total_asset_quantities = defaultdict(float)
    stable_coins = {"USDT", "BUSD", "USDC", "TUSD", "DAI", "PAX", "USDP"}

    type_mapping = {
        "spot": "现货账户 (Spot)",
        "margin": "全仓杠杆 (Margin)",
        "funding": "资金账户 (Funding)",
        "um_futures": "U本位合约 (USD-S)",
        "cm_futures": "币本位合约 (COIN-M)",
    }

    def process_balances(balances, acc_type):
        nonlocal all_assets_names, final_accounts
        filtered_balances = [
            b
            for b in balances
            if float(b.get("free", 0)) + float(b.get("locked", 0)) > 0
        ]
        if filtered_balances:
            for b in filtered_balances:
                asset = b.get("asset")
                total = float(b.get("free", 0)) + float(b.get("locked", 0))
                b["free_str"] = format_float_str(b.get("free", 0))
                b["locked_str"] = format_float_str(b.get("locked", 0))
                b["total_str"] = format_float_str(total)
                all_assets_names.add(asset)
                total_asset_quantities[asset] += total
            final_accounts.append(
                {"type_display": type_mapping[acc_type], "balances": filtered_balances}
            )

    def process_futures_assets(assets, acc_type):
        nonlocal all_assets_names, final_accounts
        filtered_assets = [
            a
            for a in assets
            if float(a.get("balance", 0)) != 0
            or float(a.get("unrealizedProfit", 0)) != 0
        ]
        if filtered_assets:
            for a in assets:
                asset = a.get("asset")
                balance = float(a.get("balance", 0))
                a["walletBalance"] = a.get("balance", "0")
                a["unrealizedProfit"] = a.get("unrealizedProfit", "0")
                all_assets_names.add(asset)
                total_asset_quantities[asset] += balance
            final_accounts.append(
                {"type_display": type_mapping[acc_type], "assets": filtered_assets}
            )

    if isinstance(spot_data, dict) and "balances" in spot_data:
        process_balances(spot_data.get("balances", []), "spot")
    if isinstance(margin_data, dict) and "userAssets" in margin_data:
        process_balances(margin_data.get("userAssets", []), "margin")
    if isinstance(funding_data, list):
        process_balances(funding_data, "funding")
    if isinstance(um_data, list):
        process_futures_assets(um_data, "um_futures")
    if isinstance(cm_data, list):
        process_futures_assets(cm_data, "cm_futures")

    # --- 计算总资产 ---
    total_usdt_value = 0.0
    assets_to_price_check = [
        asset for asset in total_asset_quantities if asset not in stable_coins
    ]
    price_tasks = [
        api_client.get_ticker_24hr(f"{asset}USDT") for asset in assets_to_price_check
    ]
    price_results = await asyncio.gather(*price_tasks, return_exceptions=True)

    price_map = {}
    for i, result in enumerate(price_results):
        if isinstance(result, dict) and "lastPrice" in result:
            price_map[assets_to_price_check[i]] = float(result["lastPrice"])

    for asset, quantity in total_asset_quantities.items():
        if asset in stable_coins:
            total_usdt_value += quantity
        elif asset in price_map:
            total_usdt_value += quantity * price_map[asset]

    # --- 图标获取与最终渲染 ---
    valid_assets = {asset for asset in all_assets_names if asset}
    icon_tasks = [drawer.image_cache.get_icon_path(asset) for asset in valid_assets]
    icon_results = await asyncio.gather(*icon_tasks)
    icon_map = dict(zip(valid_assets, icon_results))

    for account in final_accounts:
        for b in account.get("balances", []):
            b["icon_path"] = icon_map.get(b.get("asset"))
        for a in account.get("assets", []):
            a["icon_path"] = icon_map.get(a.get("asset"))

    if not final_accounts:
        return await balance_cmd.finish("您的所有账户中当前没有非零资产。")

    render_data = {"accounts": final_accounts, "total_usdt_value": total_usdt_value}
    img = await drawer.draw_account_snapshot(render_data)
    if img:
        await balance_cmd.finish(MessageSegment.image(img))
    else:
        await balance_cmd.finish("生成资产总览图片失败，请检查后台日志。")


@pos_cmd.handle()
async def handle_positions(event: Event):
    user_id = event.get_user_id()
    if not auth_manager.get_keys(user_id):
        await pos_cmd.finish("请先私聊我绑定API Key: bn bind [API Key] [Secret Key]")
    await pos_cmd.send("正在查询您的合约持仓...")

    tasks = {
        "um": api_client.get_um_futures_position_risk(user_id),
        "cm": api_client.get_cm_futures_position_risk(user_id),
    }
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    um_positions_raw, cm_positions_raw = results

    positions_data = []
    all_assets_names = set()

    if isinstance(um_positions_raw, list):
        um_positions = [
            p for p in um_positions_raw if float(p.get("positionAmt", 0)) != 0
        ]
        if um_positions:
            for p in um_positions:
                all_assets_names.add(
                    re.sub(r"USDT|BUSD|USDC$", "", p.get("symbol", ""))
                )
            positions_data.append(
                {"name": "U本位合约持仓 (USD-S)", "positions": um_positions}
            )

    if isinstance(cm_positions_raw, list):
        cm_positions = [
            p for p in cm_positions_raw if float(p.get("positionAmt", 0)) != 0
        ]
        if cm_positions:
            for p in cm_positions:
                all_assets_names.add(p.get("pair", "").replace("USD_PERP", ""))
            positions_data.append(
                {"name": "币本位合约持仓 (COIN-M)", "positions": cm_positions}
            )

    if not positions_data:
        return await pos_cmd.finish("您当前没有任何合约持仓。")

    icon_tasks = [
        drawer.image_cache.get_icon_path(asset) for asset in all_assets_names if asset
    ]
    icon_results = await asyncio.gather(*icon_tasks)
    icon_map = dict(zip(filter(None, all_assets_names), icon_results))

    for group in positions_data:
        for pos in group["positions"]:
            symbol = pos.get("symbol") or pos.get("pair", "")
            base_asset = re.sub(r"USDT|BUSD|USDC|USD_PERP$", "", symbol)
            pos["icon_path"] = icon_map.get(base_asset, "")

    render_data = {"position_groups": positions_data}
    img = await drawer.draw_positions(render_data)
    if img:
        await pos_cmd.finish(MessageSegment.image(img))
    else:
        await pos_cmd.finish("生成持仓图片失败，请检查后台日志。")


@open_orders_cmd.handle()
async def handle_open_orders(event: Event, args: Message = CommandArg()):
    user_id = event.get_user_id()
    if not auth_manager.get_keys(user_id):
        await open_orders_cmd.finish(
            "请先私聊我绑定API Key: bn bind [API Key] [Secret Key]"
        )

    arg_text = args.extract_plain_text().strip().lower()

    market_map = {
        "spot": ("现货挂单 (Spot)", api_client.get_open_orders(user_id)),
        "margin": ("杠杆挂单 (Margin)", api_client.get_margin_open_orders(user_id)),
        "um": ("U本位合约挂单 (USD-S)", api_client.get_um_futures_open_orders(user_id)),
        "cm": (
            "币本位合约挂单 (COIN-M)",
            api_client.get_cm_futures_open_orders(user_id),
        ),
    }

    tasks = {}
    if arg_text and arg_text in market_map:
        title, task = market_map[arg_text]
        tasks[title] = task
        await open_orders_cmd.send(f"正在查询 {title}...")
    else:
        # 默认查询所有
        for title, task in market_map.values():
            tasks[title] = task
        await open_orders_cmd.send("正在查询所有市场的当前挂单...")

    results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    order_groups = []
    has_orders = False

    for i, title in enumerate(tasks.keys()):
        result = results[i]
        if isinstance(result, list) and len(result) > 0:
            for order in result:
                if "pair" in order and "symbol" not in order:
                    order["symbol"] = order["pair"]
            order_groups.append({"name": title, "orders": result})
            has_orders = True
        elif isinstance(result, dict) and "error" in result:
            logger.error(f"查询挂单失败 for {title}: {result.get('error')}")

    if not has_orders:
        return await open_orders_cmd.finish("在查询的市场中没有找到任何当前挂单。")

    render_data = {"order_groups": order_groups}
    img = await drawer.draw_orders(render_data)

    if img:
        await open_orders_cmd.finish(MessageSegment.image(img))
    else:
        await open_orders_cmd.finish("生成挂单列表图片失败，请检查后台日志。")


@cancel_cmd.handle()
async def handle_cancel_order(event: Event, args: Message = CommandArg()):
    await cancel_cmd.finish("【暂不开放】为防止误操作，撤单功能默认关闭。")


@order_cmd.handle()
async def handle_order(event: Event, args: Message = CommandArg()):
    await order_cmd.finish("【暂不开放】为防止误操作，下单功能默认关闭。")
