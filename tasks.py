import asyncio
from network import ping_on_server, nexttrace_on_server, format_nexttrace_result
from utils import progress_spinner
from state import user_data

async def do_ping_in_background(context, chat_id: int, server_info: dict, target: str, ping_count: int, user_id: int):
    done_event = asyncio.Event()
    base_text = (
        "<b>【Ping 测试结果】</b>\n\n"
        f"节点: {server_info['name']}\n"
        f"目标: {target}\n"
        f"Ping 次数: {ping_count}\n\n正在执行 Ping 操作，请稍候"
    )
    spinner_task = asyncio.create_task(progress_spinner(context, chat_id, user_data[user_id]["message_id"], base_text, done_event))
    
    ping_raw_result = await asyncio.to_thread(ping_on_server, server_info, target, ping_count)
    
    done_event.set()
    await spinner_task

    final_text = (
        "<b>【Ping 测试结果】</b>\n\n"
        f"节点: {server_info['name']}\n"
        f"目标: {target}\n"
        f"Ping 次数: {ping_count}\n\n"
        f"{ping_raw_result}"
    )
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=user_data[user_id]["message_id"],
        text=final_text,
        parse_mode="HTML"
    )
    del user_data[user_id]

async def do_nexttrace_in_background(context, chat_id: int, server_info: dict, target: str, ip_type: str, user_id: int):
    done_event = asyncio.Event()
    base_text = (
        "<b>【NextTrace 路由追踪结果】</b>\n\n"
        f"节点: {server_info['name']}\n"
        f"目标: {target}\n"
        f"执行模式: {'直接执行' if ip_type=='direct' else ip_type}\n\n正在执行路由追踪操作，请稍候"
    )
    spinner_task = asyncio.create_task(progress_spinner(context, chat_id, user_data[user_id]["message_id"], base_text, done_event))
    
    result = await asyncio.to_thread(nexttrace_on_server, server_info, target, ip_type)
    
    done_event.set()
    await spinner_task

    final_text = format_nexttrace_result(result, server_info['name'], target, ip_type)
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=user_data[user_id]["message_id"],
        text=final_text,
        parse_mode="HTML"
    )
    del user_data[user_id]
