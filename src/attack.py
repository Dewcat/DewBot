from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from get_info import get_info
from game.dice import roll_for_character
from database.queries import update_character_health
from database.queries import update_character_sanity
from game.dice import compute_cumulative_damage
from game.stagger import check_stagger, get_stagger_multiplier, clear_stagger  # 新增导入

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
    
    # 打印目标角色的混乱相关属性
    print(f"\n调试 - 攻击目标信息: name={target_stats['name']}")
    print(f"调试 - 混乱相关属性: stagger_rate={target_stats.get('stagger_rate')}, stagger_num={target_stats.get('stagger_num')}")
    print(f"调试 - 混乱状态: stagger_ed={target_stats.get('stagger_ed')}, is_stagger={target_stats.get('is_stagger')}")
    print(f"调试 - 当前生命值: health={target_stats['health']}")

    roll = roll_for_character(attacker_skill, attacker_stats)
    
    # 使用新的累加伤害计算，传入所有需要的属性参数
    total, damage_str = compute_cumulative_damage(
        attacker_skill['base_value'], 
        roll,
        skill_alv=attacker_skill.get('alv', 0),
        target_dlv=target_stats.get('dlv', 0),
        target_vul=target_stats.get('vul', 0)
    )
    
    # 检查目标是否处于混乱状态，如果是则增加伤害
    stagger_state = target_stats.get('is_stagger', 0)
    print(f"调试 - 当前混乱状态: {stagger_state}")
    
    clear_message = ""
    if stagger_state > 0:
        stagger_multiplier = get_stagger_multiplier(stagger_state)
        original_total = total
        total = int(total * stagger_multiplier)
        if stagger_state == 1:
            stagger_level = "混乱"
        elif stagger_state == 2:
            stagger_level = "混乱+"
        elif stagger_state >= 3:
            stagger_level = "混乱++"
        else:
            stagger_level = "未知状态"
        damage_str += f"\n目标处于 {stagger_level} 状态，伤害 {original_total} × {stagger_multiplier} = {total}"
        print(f"调试 - 混乱增伤: 原始伤害={original_total}, 增伤后={total}")
        # 受到伤害后解除混乱状态
        clear_message = clear_stagger(target_stats['name'])
    
    previous_health = target_stats['health']
    new_health = previous_health - total
    print(f"调试 - 伤害计算: previous_health={previous_health}, damage={total}, new_health={new_health}")
    update_character_health(target_stats['name'], new_health)

    attacker_line = f"{attacker_stats['name']}: {attacker_skill['name']}: {damage_str}"
    result_message = f"{attacker_line}\n对{target_stats['name']}造成 {total} 点伤害"
    
    # 检查是否触发混乱状态
    print(f"调试 - 检查是否触发新的混乱状态")
    # 获取初始生命值作为最大生命值
    initial_health = target_stats.get('initial_health', previous_health)
    print(f"调试 - 最大生命值: {initial_health}")
    
    new_stagger, new_stagger_ed, stagger_message = check_stagger(
        target_stats['name'],
        new_health,
        previous_health,
        initial_health,
        target_stats.get('stagger_rate', 0),
        target_stats.get('stagger_num', 0),
        target_stats.get('stagger_ed', 0),
        target_stats.get('is_stagger', 0)
    )
    
    print(f"调试 - 检查混乱结果: new_stagger={new_stagger}, new_stagger_ed={new_stagger_ed}")
    print(f"调试 - 混乱消息: {stagger_message}")
    
    if stagger_message:
        result_message += f"\n{stagger_message}"
    
    if stagger_state > 0:
        result_message += f"\n{clear_message}"
    
    if new_health <= 0:
        result_message += f"\n{target_stats['name']} 倒下了"
        current_sanity = attacker_stats.get('sanity', 0)
        new_sanity = min(current_sanity + 10,45)
        update_character_sanity(attacker_stats['name'], new_sanity)
        result_message += f"\n{attacker_stats['name']} 回复 10 点理智"
        
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