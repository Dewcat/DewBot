import json
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

PLAYER_ATTRIBUTES_FILE = 'src/player_attributes.json'

def load_player_attributes():
    """
    从 JSON 文件中加载玩家属性
    """
    try:
        with open(PLAYER_ATTRIBUTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

async def stat_panel(update: Update, context: CallbackContext) -> None:
    """
    处理 /stat 命令，展示当前角色属性面板
    """
    attributes = load_player_attributes()
    if not attributes:
        await update.message.reply_text("未能加载属性数据！")
        return

    message = "当前角色属性：\n"
    for attr, value in attributes.items():
        message += f"{attr}: {value}\n"
    await update.message.reply_text(message)

def get_stat_panel_handler():
    """
    返回处理 /stat 命令的 CommandHandler
    """
    return CommandHandler("stat", stat_panel)