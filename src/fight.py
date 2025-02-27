import random
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from get_info import get_info
from game.dice import DiceGame, roll_for_character

# 定义对话状态常量
FIGHT_INFO, FIGHT_FIXED = range(2)

async def fight_start(update: Update, context: CallbackContext) -> int:
    context.bot_data['fight'] = {}
    await update.message.reply_text("请输入角色名称和技能名称，格式: 角色名 技能名")
    return FIGHT_INFO

async def fight_get_info(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text("格式错误，请输入: 角色名 技能名")
        return FIGHT_INFO
    fight = context.bot_data.setdefault('fight', {})
    fight['role_name'], fight['skill_name'] = args
    await update.message.reply_text("请输入一个检定值（固定值）：")
    return FIGHT_FIXED

async def fight_get_fixed(update: Update, context: CallbackContext) -> int:
    fight = context.bot_data.setdefault('fight', {})
    try:
        fixed_value = int(update.message.text)
    except ValueError:
        await update.message.reply_text("检定值必须为整数，请重新输入检定值。")
        return FIGHT_FIXED
    fight['fixed_value'] = fixed_value

    # 修改前:
    # player_stats, player_skill, _, _ = get_info(
    #     fight['role_name'], fight['skill_name'], fight['role_name'], fight['skill_name']
    # )
    # 修改后:
    info = get_info(
        player_name=fight['role_name'],
        player_skill_name=fight['skill_name']
    )
    player_stats = info.get("player_stats")
    player_skill = info.get("player_skill")

    print(f'player_stats: {player_stats}')
    print(f'player_skill: {player_skill}')

    if not player_stats or not player_skill:
        await update.message.reply_text("角色或技能信息无效。")
        return ConversationHandler.END

    # 使用 roll_for_character 获取掷骰结果，传入 player_skill 和 player_stats
    roll = roll_for_character(player_skill, player_stats)
    result = player_skill['base_value'] + sum(roll)
    roll_str = (f"{player_stats['name']}: {player_skill['name']}: " +
                f"({player_skill['base_value']} + " +
                " + ".join(map(str, roll)) + f") = {result}")

    if result >= fixed_value:
        result_text = f"{roll_str}，成功！"
    else:
        result_text = f"{roll_str}，失败。"
    await update.message.reply_text(result_text)
    return ConversationHandler.END

async def fight_cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("操作已取消。")
    return ConversationHandler.END

def get_fight_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("fight", fight_start)],
        states={
            FIGHT_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, fight_get_info)],
            FIGHT_FIXED: [MessageHandler(filters.TEXT & ~filters.COMMAND, fight_get_fixed)]
        },
        fallbacks=[CommandHandler("cancel", fight_cancel)],
        per_user=False  # 同一聊天内所有用户共享对话状态
    )