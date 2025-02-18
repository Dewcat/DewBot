import json
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

PLAYER_ATTRIBUTES_FILE = 'src/player_attributes.json'

def load_player_attributes():
    """从 JSON 文件中加载玩家属性"""
    try:
        with open(PLAYER_ATTRIBUTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_player_attributes(attributes):
    """保存玩家属性到 JSON 文件"""
    with open(PLAYER_ATTRIBUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(attributes, f, ensure_ascii=False, indent=4)

async def modify_attribute(update: Update, context: CallbackContext) -> None:
    """
    根据指令修改属性，例如 /wisplus 1 或 /wisminus 1
    指令规则：命令名称包含属性代码及 "plus" 或 "minus"，后接修改的数量
    """
    text = update.message.text.strip()
    # 获取命令部分，例如 "wisplus" 或 "wisminus"
    if not text.startswith('/'):
        await update.message.reply_text("命令格式错误")
        return

    parts = text.split()
    if len(parts) != 2:
        await update.message.reply_text("请提供修改的数量，例如: /wisplus 1")
        return

    cmd = parts[0][1:]   # 去除斜杠, 得到 "wisplus" 或 "wisminus"
    try:
        change_amount = int(parts[1])
    except ValueError:
        await update.message.reply_text("修改的数量必须为整数")
        return

    if cmd.endswith('plus'):
        attribute = cmd[:-4].upper()
        change = change_amount
    elif cmd.endswith('minus'):
        attribute = cmd[:-5].upper()
        change = -change_amount
    else:
        await update.message.reply_text("命令格式错误，请使用 /属性plus 或 /属性minus 格式")
        return

    attributes = load_player_attributes()
    if attribute not in attributes:
        await update.message.reply_text(f"属性 {attribute} 不存在，请检查 JSON 文件。")
        return

    attributes[attribute] += change
    save_player_attributes(attributes)
    await update.message.reply_text(f"{attribute} 属性已变更为 {attributes[attribute]} (变更: {change})")

def get_attribute_modifier_handlers():
    """
    返回一个列表，包含 6 个属性（CON, DEX, INT, WIS, CHA, WIL）的修改指令处理器
    命令名称使用小写字母，例如: /conplus, /conminus, /dexplus, /dexminus ...
    """
    attribute_list = ['CON', 'DEX', 'INT', 'WIS', 'CHA', 'WIL']
    handlers = []
    for attr in attribute_list:
        handlers.append(CommandHandler(f'{attr.lower()}plus', modify_attribute))
        handlers.append(CommandHandler(f'{attr.lower()}minus', modify_attribute))
    return handlers