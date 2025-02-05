import time
import ipaddress
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import SERVERS, ADMIN_USERS, AUTHORIZED_USERS, save_config
from state import user_data, last_ping_command_time
from tasks import do_ping_in_background, do_nexttrace_in_background
from utils import schedule_delete_message, check_authorization, check_is_admin

async def start_command(update, context):
    user_id = update.effective_user.id
    if not check_authorization(user_id, AUTHORIZED_USERS):
        await update.message.reply_text(
            "对不起，你没有权限使用本机器人\n\n"
            f"当前用户ID：`{user_id}`",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        "欢迎使用网络测试机器人！\n\n"
        "使用说明：\n"
        "1）Ping 测试：/ping 后按提示进行\n"
        "2）路由追踪：/nexttrace 后按提示进行\n\n"
        "管理员命令：/adduser, /rmuser, /addserver, /rmserver"
    )

async def ping_command(update, context):
    user_id = update.effective_user.id
    if not check_authorization(user_id, AUTHORIZED_USERS):
        await update.message.reply_text("对不起，你没有权限使用本机器人")
        return

    now_ts = time.time()
    if user_id in last_ping_command_time:
        elapsed = now_ts - last_ping_command_time[user_id]
        if elapsed < 15:
            await update.message.reply_text(f"你在 {15 - int(elapsed)} 秒后才能再次使用 /ping 命令（每15秒限制一次）。")
            return
    last_ping_command_time[user_id] = now_ts

    if not SERVERS:
        await update.message.reply_text("当前没有配置可用的服务器，请联系管理员。")
        return

    if user_id in user_data:
        del user_data[user_id]

    args = context.args
    if len(args) >= 1:
        ip_or_domain = args[0]
        try:
            ping_count = int(args[1]) if len(args) >= 2 else 4
        except ValueError:
            await update.message.reply_text("输入的Ping次数无效，请输入数字！")
            return
        if ping_count > 50:
            ping_count = 50

        keyboard = []
        for idx, server_info in enumerate(SERVERS):
            btn = InlineKeyboardButton(server_info['name'], callback_data=f"server_{idx}")
            keyboard.append([btn])
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"你输入了：目标= {ip_or_domain} , 次数= {ping_count} 次\n请选择服务器："
        msg = await update.message.reply_text(text, reply_markup=reply_markup)
        user_data[user_id] = {
            "operation": "ping",
            "mode": "cmd",
            "server_info": None,
            "target": ip_or_domain,
            "count": ping_count,
            "chat_id": msg.chat_id,
            "message_id": msg.message_id
        }
    else:
        keyboard = []
        for idx, server_info in enumerate(SERVERS):
            btn = InlineKeyboardButton(server_info['name'], callback_data=f"server_{idx}")
            keyboard.append([btn])
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "请选择要进行 Ping 测试的服务器："
        msg = await update.message.reply_text(text, reply_markup=reply_markup)
        user_data[user_id] = {
            "operation": "ping",
            "mode": "interactive",
            "server_info": None,
            "target": None,
            "count": None,
            "chat_id": msg.chat_id,
            "message_id": msg.message_id
        }

async def nexttrace_command(update, context):
    user_id = update.effective_user.id
    if not check_authorization(user_id, AUTHORIZED_USERS):
        await update.message.reply_text("对不起，你没有权限使用本机器人")
        return

    now_ts = time.time()
    if user_id in last_ping_command_time:
        elapsed = now_ts - last_ping_command_time[user_id]
        if elapsed < 10:
            await update.message.reply_text(f"你在 {10 - int(elapsed)} 秒后才能再次使用命令（每10秒限制一次）。")
            return
    last_ping_command_time[user_id] = now_ts

    if not SERVERS:
        await update.message.reply_text("当前没有配置可用的服务器，请联系管理员。")
        return

    if user_id in user_data:
        del user_data[user_id]

    args = context.args
    if len(args) >= 1:
        target = args[0]
        keyboard = []
        for idx, server_info in enumerate(SERVERS):
            btn = InlineKeyboardButton(server_info['name'], callback_data=f"server_{idx}")
            keyboard.append([btn])
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"你输入了目标： {target}\n请选择服务器："
        msg = await update.message.reply_text(text, reply_markup=reply_markup)
        user_data[user_id] = {
            "operation": "nexttrace",
            "mode": "cmd",
            "server_info": None,
            "target": target,
            "ip_type": None,
            "chat_id": msg.chat_id,
            "message_id": msg.message_id
        }
    else:
        keyboard = []
        for idx, server_info in enumerate(SERVERS):
            btn = InlineKeyboardButton(server_info['name'], callback_data=f"server_{idx}")
            keyboard.append([btn])
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "请选择要进行路由追踪测试的服务器："
        msg = await update.message.reply_text(text, reply_markup=reply_markup)
        user_data[user_id] = {
            "operation": "nexttrace",
            "mode": "interactive",
            "server_info": None,
            "target": None,
            "ip_type": None,
            "chat_id": msg.chat_id,
            "message_id": msg.message_id
        }

# ---------------- 管理员命令 ----------------
async def add_user_command(update, context):
    user_id = update.effective_user.id
    if not check_is_admin(user_id, ADMIN_USERS):
        await update.message.reply_text(
            "你不是管理员，无法执行此操作。\n\n"
            f"当前用户ID：`{user_id}`",
            parse_mode="Markdown"
        )
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("用法：/adduser <user_id>")
        return

    try:
        new_user_id = int(args[0])
    except ValueError:
        await update.message.reply_text("请输入正确的 user_id（数字）。")
        return

    if new_user_id in AUTHORIZED_USERS:
        await update.message.reply_text(f"用户 {new_user_id} 已经在授权名单中。")
    else:
        AUTHORIZED_USERS.append(new_user_id)
        save_config()
        await update.message.reply_text(f"成功添加用户 {new_user_id} 到授权名单。")

async def rm_user_command(update, context):
    user_id = update.effective_user.id
    if not check_is_admin(user_id, ADMIN_USERS):
        await update.message.reply_text(
            "你不是管理员，无法执行此操作。\n\n"
            f"当前用户ID：`{user_id}`",
            parse_mode="Markdown"
        )
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("用法：/rmuser <user_id>")
        return

    try:
        del_user_id = int(args[0])
    except ValueError:
        await update.message.reply_text("请输入正确的 user_id（数字）。")
        return

    if del_user_id in AUTHORIZED_USERS:
        AUTHORIZED_USERS.remove(del_user_id)
        save_config()
        await update.message.reply_text(f"已将用户 {del_user_id} 从授权名单中移除。")
    else:
        await update.message.reply_text(f"用户 {del_user_id} 不在授权名单中。")

async def add_server_command(update, context):
    user_id = update.effective_user.id
    if not check_is_admin(user_id, ADMIN_USERS):
        await update.message.reply_text(
            "你不是管理员，无法执行此操作。\n\n"
            f"当前用户ID：`{user_id}`",
            parse_mode="Markdown"
        )
        return

    args = context.args
    if len(args) < 5:
        await update.message.reply_text("用法：/addserver <名称> <host> <port> <username> <password>")
        return

    name = args[0]
    host = args[1]
    try:
        port = int(args[2])
    except ValueError:
        await update.message.reply_text("端口号必须是数字，请重新输入。")
        return
    username = args[3]
    password = args[4]

    new_server = {
        "name": name,
        "host": host,
        "port": port,
        "username": username,
        "password": password
    }

    SERVERS.append(new_server)
    save_config()

    await update.message.reply_text(f"成功添加服务器：{name} ({host}:{port})")

async def rm_server_command(update, context):
    user_id = update.effective_user.id
    if not check_is_admin(user_id, ADMIN_USERS):
        await update.message.reply_text(
            "你不是管理员，无法执行此操作。\n\n"
            f"当前用户ID：`{user_id}`",
            parse_mode="Markdown"
        )
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("用法：/rmserver <服务器名字>")
        return

    target_name = args[0]
    found_index = None
    for i, s in enumerate(SERVERS):
        if s['name'] == target_name:
            found_index = i
            break

    if found_index is None:
        await update.message.reply_text(f"未找到服务器名称：{target_name}，请确认输入是否正确。")
    else:
        removed_server = SERVERS.pop(found_index)
        save_config()
        await update.message.reply_text(f"成功删除服务器：{removed_server['name']} (host={removed_server['host']})")
