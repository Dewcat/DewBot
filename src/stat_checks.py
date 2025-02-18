import json
import random
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

def load_player_attributes():
    """
    从 JSON 文件中加载玩家属性
    """
    try:
        with open('src/player_attributes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

async def check_stat(update: Update, context: CallbackContext) -> None:
    """
    根据命令 /属性 难度执行属性检定
    例如: /INT 16 表示进行智力检定，难度为16
    检定规则：每偏离10 2点获得＋1或-1加成，然后掷1d20并加上该加成，与难度比较
    """
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_text('请提供难度等级，例如: /INT 16')
        return

    # 获取命令对应的属性（去掉斜杠，并转换为大写）
    command = args[0]
    attribute = command[1:].upper()
    try:
        difficulty = int(args[1])
    except ValueError:
        await update.message.reply_text('难度等级必须为整数')
        return

    attributes = load_player_attributes()
    print(attributes)
    if attribute not in attributes:
        await update.message.reply_text(f'属性 {attribute} 不存在，请检查 JSON 文件。')
        return

    base_value = attributes[attribute]
    bonus = (base_value - 10) // 2

    roll = random.randint(1, 20)
    total = roll + bonus
    result = "成功" if total >= difficulty else "失败"

    reply = (
        f"{attribute} 检定：\n"
        f"属性值: {base_value} (加成 {bonus}),\n"
        f"骰子结果: {roll}, 总计: {total}。\n"
        f"目标难度: {difficulty}。结果: {result}"
    )
    await update.message.reply_text(reply)

def get_stat_handlers():
    """
    返回一个列表，包含体质、敏捷、智力、感知、魅力、意志这6个检定的命令处理器
    """
    attributes = ['CON', 'DEX', 'INT', 'WIS', 'CHA', 'WIL']
    return [CommandHandler(attr, check_stat) for attr in attributes]