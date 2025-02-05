import asyncio
import time
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def check_authorization(user_id: int, authorized_users: list) -> bool:
    return user_id in authorized_users

def check_is_admin(user_id: int, admin_users: list) -> bool:
    return user_id in admin_users

async def schedule_delete_message(context, chat_id: int, message_id: int, delay: int = 10):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.error(f"删除消息 {message_id} 失败: {e}")

async def progress_spinner(context, chat_id: int, message_id: int, base_text: str, done_event: asyncio.Event):
    spinner_states = [".", "..", "...", "...."]
    i = 0
    while not done_event.is_set():
        spinner = spinner_states[i % len(spinner_states)]
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"{base_text}{spinner}",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"更新进度消息失败: {e}")
        await asyncio.sleep(1)
        i += 1
