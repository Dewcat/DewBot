import logging
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, filters, CallbackContext
from telegram import Update
from game.dice import DiceGame, roll_for_character
from database.queries import update_character_health
from get_info import get_info
from game.sanity import increase_sanity  # 新增导入

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
    await update.message.reply_text('防守方已准备。请提供进攻方角色名称和技能名称。格式: 角色名 技能名')
    return PLAYER2_NAME

async def player2_name_defense(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和技能名称。格式: 角色名 技能名')
        return PLAYER2_NAME
    battle = context.bot_data.setdefault('battle', {})
    battle['player2_name'], battle['player2_skill'] = args

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

    print(f'player_stats: {player_stats}')
    print(f'opponent_stats: {opponent_stats}')
    print(f'player_skill: {player_skill}')
    print(f'opponent_skill: {opponent_skill}')

    if not player_stats or not opponent_stats or not player_skill or not opponent_skill:
        await update.message.reply_text('角色或技能信息无效。')
        return ConversationHandler.END

    dice_game = DiceGame(player_stats, opponent_stats, player_skill, opponent_skill)

    # 使用 roll_for_character 获取掷骰结果
    roll1 = roll_for_character(player_skill, player_stats)
    roll2 = roll_for_character(opponent_skill, opponent_stats)
    print(f'roll1: {roll1}')
    print(f'roll2: {roll2}')
    result1 = dice_game.damage(player_skill['base_value'], roll1)
    result2 = dice_game.damage(opponent_skill['base_value'], roll2)
    player_roll_str = (f"{player_stats['name']}: {player_skill['name']}: " +
                       ' + '.join([f"({player_skill['base_value']} + " +
                                    ' + '.join(map(str, roll1[:i+1])) + ")" 
                                    for i in range(len(roll1))])
                       + f" = {result1}")
    opponent_roll_str = (f"{opponent_stats['name']}: {opponent_skill['name']}: " +
                         ' + '.join([f"({opponent_skill['base_value']} + " +
                                      ' + '.join(map(str, roll2[:i+1])) + ")" 
                                      for i in range(len(roll2))])
                         + f" = {result2}")
    result_message = f"{player_roll_str}\n{opponent_roll_str}"
    if result2 > result1:
        damage = result2 - result1
        player_stats['health'] -= damage
        # 更新受到伤害后的血量到数据库
        update_character_health(player_stats['name'], player_stats['health'])
        result_message += f"\n{player_stats['name']} 的防御被破坏，受到 {damage} 点伤害"
        if player_stats['health'] <= 0:
            result_message += f"\n{player_stats['name']} 倒下了"
            # 击杀对方后，攻击角色回复 10 点理智值，并写回数据库
            new_sanity = increase_sanity(opponent_stats['name'], 10)
            result_message += f"\n{opponent_stats['name']} 回复了 10 点理智值，目前理智值为 {new_sanity}"
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