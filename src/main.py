import os
import httpx
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from telegram import Update
from telegram.request import HTTPXRequest  # 使用 HTTPXRequest 替代原来的 Request
from stat_checks import get_stat_handlers
from attribute_modifiers import get_attribute_modifier_handlers
from stat_panel import get_stat_panel_handler
from battle import get_battle_conv_handler
from defense import get_defense_conv_handler
from character_management import get_character_management_handlers
from fight import get_fight_conv_handler
from attack import get_attack_conv_handler

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")


request = HTTPXRequest(connection_pool_size=100, proxy="socks5://127.0.0.1:7890")

application = Application.builder()\
    .token(token)\
    .request(request)\
    .build()

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('miamiamiamiaminmi')

application.add_handler(CommandHandler("start", start))

for handler in get_character_management_handlers():
    application.add_handler(handler)

application.add_handler(get_battle_conv_handler())
application.add_handler(get_defense_conv_handler())
application.add_handler(get_fight_conv_handler())
application.add_handler(get_attack_conv_handler())

for handler in get_stat_handlers():
    application.add_handler(handler)

for handler in get_attribute_modifier_handlers():
    application.add_handler(handler)

application.add_handler(get_stat_panel_handler())

# 启动Bot
if __name__ == '__main__':
    application.run_polling()