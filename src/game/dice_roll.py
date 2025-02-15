import random
from telegram.ext import CommandHandler, CallbackContext
from telegram import Update
import re

# 掷骰函数
def roll_dice(dice_notation: str) -> int:
    match = re.match(r'(\d*)d(\d+)([+-]\d+)?', dice_notation)
    if not match:
        return None

    num_dice = int(match.group(1)) if match.group(1) else 1
    dice_type = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    return sum(random.randint(1, dice_type) for _ in range(num_dice)) + modifier

# 处理掷骰命令
async def dice_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        await update.message.reply_text('请提供正确的掷骰命令。格式: 1d20, 4d5, 8d7+3')
        return

    dice_notation = context.args[0]
    result = roll_dice(dice_notation)
    if result is None:
        await update.message.reply_text('无效的掷骰命令。格式: 1d20, 4d5, 8d7+3')
    else:
        await update.message.reply_text(f'掷骰结果: {result}')