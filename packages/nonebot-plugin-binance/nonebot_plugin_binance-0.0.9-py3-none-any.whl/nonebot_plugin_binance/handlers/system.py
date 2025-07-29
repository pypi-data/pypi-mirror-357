# =================================================================
# == nonebot_plugin_binance/handlers/system.py
# == 说明：处理帮助、绑定等系统命令。
# =================================================================
import asyncio
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageSegment,
    PrivateMessageEvent,
)
from .. import drawer, auth_manager, api_client
from nonebot import logger

help_cmd = on_command("bn help", aliases={"币安帮助"}, priority=5, block=True)
bind_cmd = on_command("bn bind", aliases={"币安绑定"}, priority=5, block=True)
unbind_cmd = on_command("bn unbind", aliases={"币安解绑"}, priority=5, block=True)
status_cmd = on_command("bn status", aliases={"币安状态"}, priority=5, block=True)


@help_cmd.handle()
async def handle_help():
    img = await drawer.draw_help()
    if img:
        await help_cmd.finish(MessageSegment.image(img))
    else:
        await help_cmd.finish("生成帮助图片失败，请联系管理员。")


@bind_cmd.handle()
async def handle_bind(bot: Bot, event: Event, args: Message = CommandArg()):
    if not isinstance(event, PrivateMessageEvent):
        await bind_cmd.finish(
            "为了您的账户安全，请私聊我并使用 'bn bind [API Key] [Secret Key]' 命令进行绑定。"
        )

    keys = args.extract_plain_text().strip().split()
    if len(keys) != 2:
        await bind_cmd.finish("格式错误！请使用: bn bind [API Key] [Secret Key]")

    api_key, secret_key = keys[0], keys[1]
    user_id = event.get_user_id()

    try:
        if event.message_id:
            await bot.delete_msg(message_id=event.message_id)
            await bind_cmd.send("收到，正在处理您的绑定请求...", at_sender=False)
    except Exception as e:
        logger.warning(f"尝试撤回绑定消息失败: {e}。可能机器人不是管理员。")
        await bind_cmd.send(
            "收到，正在处理您的绑定请求... (消息撤回失败，请尽快手动删除)",
            at_sender=False,
        )

    auth_manager.bind_keys(user_id, api_key, secret_key)
    account_info = await api_client.get_account_info(user_id)

    if account_info and "error" not in account_info:
        await bind_cmd.finish("API密钥绑定成功！您的账户已准备就绪。")
    else:
        auth_manager.unbind_keys(user_id)
        # 健壮地处理不同类型的错误信息
        error_content = account_info.get("error", "未知错误")
        if isinstance(error_content, dict):
            error_msg = error_content.get("msg", str(error_content))
        else:
            error_msg = str(error_content)
        await bind_cmd.finish(
            f"API密钥验证失败，绑定已取消。\n错误: {error_msg}\n请检查您的Key是否正确、未过期，并已开启现货交易权限。"
        )


@unbind_cmd.handle()
async def handle_unbind(event: Event):
    user_id = event.get_user_id()
    if auth_manager.unbind_keys(user_id):
        await unbind_cmd.finish("您的API密钥已成功解绑。")
    else:
        await unbind_cmd.finish("您尚未绑定API密钥。")


@status_cmd.handle()
async def handle_status(event: Event):
    user_id = event.get_user_id()
    if not auth_manager.get_keys(user_id):
        status_data = {"bound": False}
        img = await drawer.draw_status(status_data)
        if img:
            await status_cmd.finish(MessageSegment.image(img))
        else:
            await status_cmd.finish("生成状态图片失败，请检查后台日志。")
        return

    await status_cmd.send("您已绑定API密钥。正在查询详细权限...")

    # 并发查询现货和合约账户信息
    tasks = {
        "spot": api_client.get_account_info(user_id),
        "futures": api_client.get_um_futures_account(user_id),
    }
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    spot_info, futures_info = results

    permissions = {}
    api_error = None

    # 处理现货账户信息
    if isinstance(spot_info, dict) and "error" not in spot_info:
        permissions["spot_trade"] = spot_info.get("canTrade", False)
        permissions["margin_trade"] = spot_info.get("isMarginTradingAllowed", False)
        permissions["withdraw"] = spot_info.get("canWithdraw", False)
    elif isinstance(spot_info, dict):
        api_error = spot_info.get("error", {}).get("msg", "未知API错误")
    else:
        api_error = "获取现货账户信息失败"

    # 处理U本位合约账户信息
    if isinstance(futures_info, dict) and "error" not in futures_info:
        permissions["futures_trade"] = futures_info.get("canTrade", False)
    # 如果现货API已报错，则不再覆盖错误信息
    elif isinstance(futures_info, dict) and not api_error:
        api_error = futures_info.get("error", {}).get("msg", "未知API错误")
    elif not api_error:
        api_error = "获取合约账户信息失败"

    status_data = {"bound": True, "permissions": permissions, "error": api_error}

    img = await drawer.draw_status(status_data)
    if img:
        await status_cmd.finish(MessageSegment.image(img))
    else:
        await status_cmd.finish("生成状态图片失败，请检查后台日志。")
