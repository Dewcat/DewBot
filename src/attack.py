from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from get_info import get_info
from game.dice import roll_for_character
from database.queries import update_character_health
from database.queries import update_character_sanity
from game.dice import compute_cumulative_damage  # 修改后的导入

# 定义对话状态常量
ATTACKER_INFO, TARGET_NAME = range(2)

async def attack_start(update: Update, context: CallbackContext) -> int:
    context.bot_data['attack'] = {}
    await update.message.reply_text("请输入进攻者的角色名称和技能名称，格式: 角色名 技能名")
    return ATTACKER_INFO

async def attack_get_attacker(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text("格式错误，请输入: 角色名 技能名")
        return ATTACKER_INFO
    attack = context.bot_data.setdefault('attack', {})
    attack['attacker_name'], attack['skill_name'] = args
    await update.message.reply_text("请输入受到攻击目标的角色名称：")
    return TARGET_NAME

async def attack_get_target(update: Update, context: CallbackContext) -> int:
    attack = context.bot_data.setdefault('attack', {})
    target_name = update.message.text.strip()
    attack['target_name'] = target_name

    attacker_name = attack['attacker_name']
    attacker_skill_name = attack['skill_name']

    info = get_info(
        player_name=attacker_name,
        player_skill_name=attacker_skill_name,
        opponent_name=target_name
    )
    attacker_stats = info.get("player_stats")
    attacker_skill = info.get("player_skill")
    target_stats = info.get("opponent_stats")
    if not attacker_stats or not attacker_skill or not target_stats:
        await update.message.reply_text("进攻者或目标信息无效。")
        return ConversationHandler.END

    roll = roll_for_character(attacker_skill, attacker_stats)
    # 采用累加计算生成伤害和描述字符串
    total, damage_str = compute_cumulative_damage(attacker_skill['base_value'], roll)
    attacker_line = f"{attacker_stats['name']}: {attacker_skill['name']}: {damage_str}"

    new_health = target_stats['health'] - total
    update_character_health(target_stats['name'], new_health)

    result_message = (
        f"{attacker_line}\n"
        f"对{target_stats['name']}造成 {damage_str} 点伤害"
    )
    if new_health <= 0:
        result_message += f"\n{target_stats['name']} 倒下了"
        current_sanity = attacker_stats.get('sanity', 0)
        new_sanity = current_sanity + 10
        update_character_sanity(attacker_stats['name'], new_sanity)
        result_message += f"\n{attacker_stats['name']} 回复了 10 点理智值，目前理智值为 {new_sanity}"
    await update.message.reply_text(result_message)
    return ConversationHandler.END

async def attack_cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("操作已取消。")
    return ConversationHandler.END

def get_attack_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("attack", attack_start)],
        states={
            ATTACKER_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, attack_get_attacker)],
            TARGET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, attack_get_target)]
        },
        fallbacks=[CommandHandler("cancel", attack_cancel)],
        per_user=False   # 同一聊天内所有用户共享对话状态
    )