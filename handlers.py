import ipaddress
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from state import user_data
from tasks import do_ping_in_background, do_nexttrace_in_background
from utils import schedule_delete_message

async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_data:
        await query.edit_message_text("你当前没有进行中的操作，请使用 /ping 或 /nexttrace 重新开始。")
        return

    data = query.data
    info = user_data[user_id]
    chat_id = info["chat_id"]
    message_id = info["message_id"]

    if data.startswith("server_"):
        idx = int(data.split("_")[1])
        from config import SERVERS
        if idx < 0 or idx >= len(SERVERS):
            await context.bot.edit_message_text("无效的服务器下标。", chat_id=chat_id, message_id=message_id)
            return

        server_info = SERVERS[idx]
        info["server_info"] = server_info
        if info.get("operation") == "ping":
            mode = info["mode"]
            if mode == "cmd":
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="已收到请求，正在后台执行 Ping 操作，请稍候..."
                )
                context.application.create_task(
                    do_ping_in_background(context, chat_id, server_info, info["target"], info["count"], user_id)
                )
            elif mode == "interactive":
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"你选择了 {server_info['name']}。\n请发送目标IP或域名（例如：8.8.8.8 或 google.com）。"
                )
        elif info.get("operation") == "nexttrace":
            mode = info["mode"]
            if mode == "cmd":
                try:
                    ipaddress.ip_address(info["target"])
                    await context.bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id,
                        text=f"你选择了 {server_info['name']}。\n目标： {info['target']} 为IP地址，正在后台执行路由追踪操作，请稍候..."
                    )
                    context.application.create_task(
                        do_nexttrace_in_background(context, chat_id, server_info, info["target"], "direct", user_id)
                    )
                except ValueError:
                    keyboard = [
                        [
                            InlineKeyboardButton("IPv4", callback_data="iptype_ipv4"),
                            InlineKeyboardButton("IPv6", callback_data="iptype_ipv6")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await context.bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id,
                        text=f"你选择了 {server_info['name']}。\n目标： {info['target']}\n请选择 IP 协议类型：",
                        reply_markup=reply_markup
                    )
            elif mode == "interactive":
                try:
                    ipaddress.ip_address(info["target"])
                    await context.bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id,
                        text=f"你选择了 {server_info['name']}。\n目标： {info['target']} 为IP地址，正在后台执行路由追踪操作，请稍候..."
                    )
                    context.application.create_task(
                        do_nexttrace_in_background(context, chat_id, server_info, info["target"], "direct", user_id)
                    )
                except ValueError:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=f"你选择了 {server_info['name']}。\n请发送目标IP或域名。"
                    )
    elif data.startswith("count_"):
        if info.get("operation") != "ping":
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                  text="当前操作不支持选择 Ping 次数。")
            return

        count = int(data.split("_")[1])
        info["count"] = count
        if not info.get("server_info") or not info.get("target"):
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                  text="服务器或目标IP信息不完整，请重新开始 /ping 流程。")
            return

        await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                            text="已收到请求，正在后台执行 Ping 操作，请稍候...")
        context.application.create_task(
            do_ping_in_background(context, chat_id, info["server_info"], info["target"], count, user_id)
        )
    elif data.startswith("iptype_"):
        if info.get("operation") != "nexttrace":
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                  text="当前操作不支持 IP 协议类型选择。")
            return
        ip_type = "IPv4" if data == "iptype_ipv4" else "IPv6"
        info["ip_type"] = ip_type
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text="已收到请求，正在后台执行路由追踪操作，请稍候..."
        )
        context.application.create_task(
            do_nexttrace_in_background(context, chat_id, info["server_info"], info["target"], ip_type, user_id)
        )

async def handle_message(update, context):
    user_id = update.effective_user.id
    if user_id not in user_data:
        await update.message.reply_text("请先使用 /ping 或 /nexttrace 重新开始流程。")
        return
    info = user_data[user_id]
    if info["mode"] != "interactive":
        if info.get("operation") == "ping":
            await update.message.reply_text("命令式模式无需输入IP，如需重新测试，请使用 /ping。")
        elif info.get("operation") == "nexttrace":
            await update.message.reply_text("命令式模式无需输入IP，如需重新测试，请使用 /nexttrace。")
        return

    if not info.get("target"):
        target = update.message.text.strip()
        info["target"] = target

        context.application.create_task(schedule_delete_message(context, update.message.chat_id, update.message.message_id, delay=5))

        if info.get("operation") == "ping":
            keyboard = [
                [
                    InlineKeyboardButton("Ping 5次", callback_data="count_5"),
                    InlineKeyboardButton("Ping 10次", callback_data="count_10"),
                    InlineKeyboardButton("Ping 30次", callback_data="count_30")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.edit_message_text(
                chat_id=info["chat_id"],
                message_id=info["message_id"],
                text="请选择要 Ping 的次数：",
                reply_markup=reply_markup
            )
        elif info.get("operation") == "nexttrace":
            try:
                ipaddress.ip_address(target)
                await context.bot.edit_message_text(
                    chat_id=info["chat_id"],
                    message_id=info["message_id"],
                    text=f"目标： {target} 为IP地址，正在后台执行路由追踪操作，请稍候..."
                )
                context.application.create_task(
                    do_nexttrace_in_background(context, info["chat_id"], info["server_info"], target, "direct", user_id)
                )
            except ValueError:
                keyboard = [
                    [
                        InlineKeyboardButton("IPv4", callback_data="iptype_ipv4"),
                        InlineKeyboardButton("IPv6", callback_data="iptype_ipv6")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.edit_message_text(
                    chat_id=info["chat_id"],
                    message_id=info["message_id"],
                    text="请选择 IP 协议类型：",
                    reply_markup=reply_markup
                )
    else:
        await update.message.reply_text("你已输入过目标IP，如需重新测试，请使用相应的命令。")
