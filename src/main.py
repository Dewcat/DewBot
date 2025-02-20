import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from telegram import Update
from stat_checks import get_stat_handlers
from attribute_modifiers import get_attribute_modifier_handlers
from stat_panel import get_stat_panel_handler
from battle_defense import get_battle_conv_handler, get_defense_conv_handler
from character_management import get_character_management_handlers

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")

# 初始化
application = Application.builder().token(token).proxy('socks5://127.0.0.1:7890').build()

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('miamiamiamiaminmi')

application.add_handler(CommandHandler("start", start))

for handler in get_character_management_handlers():
    application.add_handler(handler)

application.add_handler(get_battle_conv_handler())
application.add_handler(get_defense_conv_handler())

for handler in get_stat_handlers():
    application.add_handler(handler)

for handler in get_attribute_modifier_handlers():
    application.add_handler(handler)

application.add_handler(get_stat_panel_handler())

# 启动Bot
if __name__ == '__main__':
    application.run_polling()