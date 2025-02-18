from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from telegram import Update
# import logging
# from game.dice import DiceGame
# from database.queries import get_skill_info, get_character_stats, update_character_health, reset_character_stats, update_character_strength, update_character_weakness
# from game.dice_roll import dice_command
from stat_checks import get_stat_handlers
from attribute_modifiers import get_attribute_modifier_handlers
from stat_panel import get_stat_panel_handler
from battle_defense import get_battle_conv_handler, get_defense_conv_handler
from character_management import get_character_management_handlers

token = "5769924134:AAFr2m3_mr_HbOdO42Mt8MUGAxFAaG4E4Yg"

# 初始化
application = Application.builder().token(token).proxy('socks5://127.0.0.1:7890').build()


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('miamiamiamiaminmi')



application.add_handler(CommandHandler("start", start))

for handler in get_character_management_handlers():
    application.add_handler(handler)

# application.add_handler(MessageHandler(filters.Regex(r'^\d*d\d+([+-]\d+)?$'), dice_command))  # 添加掷骰命令处理程序

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