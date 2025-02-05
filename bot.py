from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN
from commands import start_command, ping_command, nexttrace_command, add_user_command, rm_user_command, add_server_command, rm_server_command
from handlers import callback_handler, handle_message

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # 注册用户命令
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("nexttrace", nexttrace_command))

    # 注册管理员命令
    application.add_handler(CommandHandler("adduser", add_user_command))
    application.add_handler(CommandHandler("rmuser", rm_user_command))
    application.add_handler(CommandHandler("addserver", add_server_command))
    application.add_handler(CommandHandler("rmserver", rm_server_command))

    # 注册回调和消息处理
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
