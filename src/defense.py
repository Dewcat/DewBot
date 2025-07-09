import logging
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, filters, CallbackContext
from telegram import Update
from game.dice import DiceGame, roll_for_character
from database.queries import update_character_health
from get_info import get_info
from game.sanity import increase_sanity  # 新增导入
from game.dice import compute_cumulative_damage  # 修改后的导入
from game.stagger import check_stagger, get_stagger_multiplier, clear_stagger  # 新增导入

# 定义对话状态常量
PLAYER1_NAME, PLAYER1_SKILL, PLAYER2_NAME, PLAYER2_SKILL = range(4)

async def defense_start(update: Update, context: CallbackContext) -> int:
    context.bot_data['battle'] = {}
    await update.message.reply_text('请提供防守方角色名称和技能名称。格式: 角色名 技能名')
    return PLAYER1_NAME

async def player1_name_defense(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和技能名称。格式: 角色名 技能名')
        return PLAYER1_NAME
    battle = context.bot_data.setdefault('battle', {})
    battle['player1_name'], battle['player1_skill'] = args
    
    # 检查防守方是否处于混乱状态
    info = get_info(player_name=battle['player1_name'])
    player_stats = info.get("player_stats")
    
    print(f"\n调试 - 防御角色信息: name={player_stats['name'] if player_stats else None}")
    if player_stats:
        print(f"调试 - 混乱相关属性: stagger_rate={player_stats.get('stagger_rate')}, stagger_num={player_stats.get('stagger_num')}")
        print(f"调试 - 混乱状态: stagger_ed={player_stats.get('stagger_ed')}, is_stagger={player_stats.get('is_stagger')}")
    
    if player_stats and player_stats.get('is_stagger', 0) > 0:
        print(f"调试 - 角色处于混乱状态，无法防御")
        await update.message.reply_text(f"{player_stats['name']} 处于混乱状态，无法进行防御。请先使用其他角色或等待混乱状态解除。")
        return ConversationHandler.END
    
    await update.message.reply_text('防守方已准备。请提供进攻方角色名称和技能名称。格式: 角色名 技能名')
    return PLAYER2_NAME

async def player2_name_defense(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和技能名称。格式: 角色名 技能名')
        return PLAYER2_NAME
    battle = context.bot_data.setdefault('battle', {})
    battle['player2_name'], battle['player2_skill'] = args

    # 检查进攻方是否处于混乱状态
    info_attacker = get_info(player_name=battle['player2_name'])
    attacker_stats = info_attacker.get("player_stats")
    
    if attacker_stats and attacker_stats.get('is_stagger', 0) > 0:
        await update.message.reply_text(f"{attacker_stats['name']} 处于混乱状态，无法进行攻击。请先使用其他角色或等待混乱状态解除。")
        return ConversationHandler.END

    player_name = battle['player1_name']
    player_skill_name = battle['player1_skill']
    opponent_name = battle['player2_name']
    opponent_skill_name = battle['player2_skill']

    info = get_info(
        player_name=player_name,
        player_skill_name=player_skill_name,
        opponent_name=opponent_name,
        opponent_skill_name=opponent_skill_name
    )
    player_stats = info.get("player_stats")
    player_skill = info.get("player_skill")
    opponent_stats = info.get("opponent_stats")
    opponent_skill = info.get("opponent_skill")

    if not player_stats or not opponent_stats or not player_skill or not opponent_skill:
        await update.message.reply_text('角色或技能信息无效。')
        return ConversationHandler.END

    # 使用 compute_cumulative_damage 分别计算双方伤害和描述
    roll1 = roll_for_character(player_skill, player_stats)
    roll2 = roll_for_character(opponent_skill, opponent_stats)
    
    # 防守方的计算
    total1, desc1 = compute_cumulative_damage(
        player_skill['base_value'], 
        roll1,
        skill_alv=player_skill.get('alv', 0),
        target_dlv=0,  # 防御时不计算攻击方的dlv
        target_vul=0   # 防御时不计算攻击方的vul
    )
    
    # 进攻方的计算
    total2, desc2 = compute_cumulative_damage(
        opponent_skill['base_value'], 
        roll2,
        skill_alv=opponent_skill.get('alv', 0),
        target_dlv=player_stats.get('dlv', 0),
        target_vul=player_stats.get('vul', 0)
    )
    
    player_roll_str = f"{player_stats['name']}: {player_skill['name']}: {desc1}"
    opponent_roll_str = f"{opponent_stats['name']}: {opponent_skill['name']}: {desc2}"
    result_message = f"{player_roll_str}\n{opponent_roll_str}"

    if total2 > total1:
        damage = total2 - total1
        previous_health = player_stats['health']
        player_stats['health'] -= damage
        new_health = player_stats['health']
        
        print(f"\n调试 - 防御失败: previous_health={previous_health}, damage={damage}, new_health={new_health}")
        
        # 更新受到伤害后的血量到数据库
        update_character_health(player_stats['name'], new_health)
        result_message += f"\n{player_stats['name']} 的防御被破坏，受到 {damage} 点伤害"
        
        # 获取初始生命值作为最大生命值
        initial_health = player_stats.get('initial_health', previous_health)
        print(f"调试 - 最大生命值: {initial_health}")
        
        # 检查是否触发混乱状态
        print(f"调试 - 检查是否触发混乱状态")
        new_stagger, new_stagger_ed, stagger_message = check_stagger(
            player_stats['name'],
            new_health,
            previous_health,
            initial_health,
            player_stats.get('stagger_rate', 0),
            player_stats.get('stagger_num', 0),
            player_stats.get('stagger_ed', 0),
            player_stats.get('is_stagger', 0)
        )
        
        print(f"调试 - 检查混乱结果: new_stagger={new_stagger}, new_stagger_ed={new_stagger_ed}")
        print(f"调试 - 混乱消息: {stagger_message}")
        
        if stagger_message:
            result_message += f"\n{stagger_message}"
            
        if player_stats['health'] <= 0:
            result_message += f"\n{player_stats['name']} 倒下了"
            # 击杀对方后，攻击角色回复 10 点理智值，并写回数据库
            new_sanity = increase_sanity(opponent_stats['name'], 10)
            result_message += f"\n{opponent_stats['name']} 回复 10 点理智"
    else:
        result_message += f"\n{player_stats['name']} 成功防守，没有受到伤害"
    await update.message.reply_text(result_message)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('操作已取消。')
    return ConversationHandler.END

def get_defense_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('defense', defense_start)],
        states={
            PLAYER1_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, player1_name_defense)],
            PLAYER2_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, player2_name_defense)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=False  # 同一聊天内所有用户共享对话状态
    )