from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from get_info import get_info
from game.dice import roll_for_character
from database.queries import update_character_health

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


    print(f'attacker_name: {attacker_name}')
    print(f'attacker_skill_name: {attacker_skill_name}')
    print(f'target_name: {target_name}')

    # 获取进攻者和目标信息（目标信息用于血量）
    attacker_stats, attacker_skill, target_stats, _ = get_info(
        attacker_name, attacker_skill_name, target_name, attacker_skill_name
    )
    print(attacker_stats)
    print(attacker_skill)
    print(target_stats)
    if not attacker_stats or not attacker_skill or not target_stats:
        await update.message.reply_text("进攻者或目标信息无效。")
        return ConversationHandler.END

    # 使用 roll_for_character 获取进攻者的掷骰结果，传入 attacker_skill 和 attacker_stats
    roll = roll_for_character(attacker_skill, attacker_stats)
    # 第一行：计算总结果 = 基础值 + 所有骰子结果之和
    base_value = attacker_skill['base_value']
    result = base_value + sum(roll)
    # 构造进攻者拼点字符串：例如 "eris: 不死鸟斩: 30 + 3 + 10 + 5 = 49"
    roll_values_str = " + ".join(map(str, roll))
    attacker_line = f"{attacker_stats['name']}: {attacker_skill['name']}: {base_value} + {roll_values_str} = {result}"

    # 计算伤害：伤害为各段累计相加，即：(基础值 + roll[0]) + (基础值 + roll[0] + roll[1]) + ...
    damage_components = []
    cumulative = base_value
    for i, r in enumerate(roll):
        cumulative += r
        # 生成每段字符串，如 "(30 + 3)"，"(30 + 3 + 10)"等
        part = f"({base_value}"
        if i >= 0:
            part += " + " + " + ".join(map(str, roll[:i+1]))
        part += ")"
        damage_components.append(part)
    damage = sum([base_value + sum(roll[:i+1]) for i in range(len(roll))])
    damage_str = " + ".join(damage_components) + f" = {damage}"

    # 更新目标角色血量
    new_health = target_stats['health'] - damage
    update_character_health(target_stats['name'], new_health)

    result_message = (
        f"{attacker_line}\n"
        f"对{target_stats['name']}造成{damage_str}点伤害"
    )
    if new_health <= 0:
        result_message += f"\n{target_stats['name']} 倒下了"
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