from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from database.queries import reset_character_stats, update_character_strength, update_character_weakness

async def reset(update: Update, context: CallbackContext) -> None:
    reset_character_stats()
    await update.message.reply_text('角色状态已恢复。')

async def strength(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和修改的强壮层数。格式: /strength 角色名 层数')
        return

    character_name, strength_change = args
    try:
        strength_change = int(strength_change)
    except ValueError:
        await update.message.reply_text('强壮层数必须为整数！')
        return
    update_character_strength(character_name, strength_change)
    action = "增加" if strength_change > 0 else "减少"
    await update.message.reply_text(f'{character_name} 的强壮层数{action}了 {abs(strength_change)}。')

async def weakness(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和修改的虚弱层数。格式: /weakness 角色名 层数')
        return

    character_name, weakness_change = args
    try:
        weakness_change = int(weakness_change)
    except ValueError:
        await update.message.reply_text('虚弱层数必须为整数！')
        return
    update_character_weakness(character_name, weakness_change)
    action = "增加" if weakness_change > 0 else "减少"
    await update.message.reply_text(f'{character_name} 的虚弱层数{action}了 {abs(weakness_change)}。')

def get_reset_handler():
    return CommandHandler("reset", reset)

def get_strength_handler():
    return CommandHandler("strength", strength)

def get_weakness_handler():
    return CommandHandler("weakness", weakness)

def get_character_management_handlers():
    """
    返回一个列表，包含重置、修改强壮层数、修改虚弱层数这三个指令的处理器
    """
    return [get_reset_handler(), get_strength_handler(), get_weakness_handler()]