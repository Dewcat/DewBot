import logging
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, filters, CallbackContext
from telegram import Update
from game.dice import DiceGame, roll_for_character
from database.queries import update_character_health
from get_info import get_info

# 定义对话状态常量
PLAYER1_NAME, PLAYER1_SKILL, PLAYER2_NAME, PLAYER2_SKILL = range(4)

async def battle_start(update: Update, context: CallbackContext) -> int:
    context.bot_data['battle'] = {}
    await update.message.reply_text('请提供敌方角色名称和技能名称。格式: 角色名 技能名')
    return PLAYER1_NAME

async def player1_name(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和技能名称。格式: 角色名 技能名')
        return PLAYER1_NAME
    battle = context.bot_data.setdefault('battle', {})
    battle['player1_name'], battle['player1_skill'] = args
    await update.message.reply_text('敌方设置完成。请提供你的角色名称和技能名称。格式: 角色名 技能名')
    return PLAYER2_NAME

async def player2_name(update: Update, context: CallbackContext) -> int:
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
    round_counter = 0  # 记录拼点次数

    while True:
        round_counter += 1
        # 使用 roll_for_character 获取掷骰结果
        roll1 = roll_for_character(player_skill, player_stats)
        roll2 = roll_for_character(opponent_skill, opponent_stats)
        print(f'roll1: {roll1}')
        print(f'roll2: {roll2}')
        result1 = dice_game.calculate_result(player_skill['base_value'], roll1)
        result2 = dice_game.calculate_result(opponent_skill['base_value'], roll2)
        player_roll_str = (f"{player_stats['name']}: {player_skill['name']}: {player_skill['base_value']} + " +
                           ' + '.join(map(str, roll1)) + f' = {result1}')
        opponent_roll_str = (f"{opponent_stats['name']}: {opponent_skill['name']}: {opponent_skill['base_value']} + " +
                             ' + '.join(map(str, roll2)) + f' = {result2}')
        result_message = f"{player_roll_str}\n{opponent_roll_str}"

        if result1 > result2:
            result_message += f"\n{player_stats['name']} 获得优势"
        elif result2 > result1:
            result_message += f"\n{opponent_stats['name']} 获得优势"
        else:
            result_message += "\n不分胜负"
        await update.message.reply_text(result_message)

        # 根据本轮结果减少对应方的骰子（未即时更新理智值）
        if result1 > result2:
            opponent_skill['num_dice'] -= 1
            if opponent_skill['num_dice'] == 0:
                # 玩家最终获胜
                bonus = int(10 * (1 + 0.2 * round_counter))
                # 更新理智值：胜者增加，败者减少
                from game.sanity import increase_sanity, decrease_sanity
                increase_sanity(player_stats['name'], bonus)
                decrease_sanity(opponent_stats['name'], bonus/2)
                # 计算伤害
                roll1 = roll_for_character(player_skill, player_stats)
                result1 = dice_game.calculate_result(player_skill['base_value'], roll1)
                player_roll_str = (f"{player_stats['name']}: {player_skill['name']}: {player_skill['base_value']} + " +
                                   ' + '.join(map(str, roll1)) + f' = {result1}')
                damage = dice_game.damage(player_skill['base_value'], roll1)
                damage_str = ' + '.join(
                    [f"({player_skill['base_value']} + " +
                     ' + '.join(map(str, roll1[:i+1])) + ")" for i in range(len(roll1))]
                ) + f' = {damage}'
                opponent_stats['health'] -= damage
                update_character_health(opponent_stats['name'], opponent_stats['health'])
                # 击杀对方时，胜者额外增加10点理智值
                if opponent_stats['health'] <= 0:
                    increase_sanity(player_stats['name'], 10)
                    await update.message.reply_text(f'{opponent_stats["name"]} 倒下了')
                await update.message.reply_text(
                    f'{player_roll_str}\n{player_stats["name"]} 胜利，造成{damage_str}点伤害\n'
                    f"胜者增加 {bonus} 点理智，败者减少 {bonus/2} 点理智。"
                )
                break
        elif result2 > result1:
            player_skill['num_dice'] -= 1
            if player_skill['num_dice'] == 0:
                # 对手最终获胜
                bonus = int(10 * (1 + 0.2 * round_counter))
                from game.sanity import increase_sanity, decrease_sanity
                increase_sanity(opponent_stats['name'], bonus)
                decrease_sanity(player_stats['name'], bonus)
                roll2 = roll_for_character(opponent_skill, opponent_stats)
                result2 = dice_game.calculate_result(opponent_skill['base_value'], roll2)
                opponent_roll_str = (f"{opponent_stats['name']}: {opponent_skill['name']}: {opponent_skill['base_value']} + " +
                                     ' + '.join(map(str, roll2)) + f' = {result2}')
                damage = dice_game.damage(opponent_skill['base_value'], roll2)
                damage_str = ' + '.join(
                    [f"({opponent_skill['base_value']} + " +
                     ' + '.join(map(str, roll2[:i+1])) + ")" for i in range(len(roll2))]
                ) + f' = {damage}'
                player_stats['health'] -= damage
                update_character_health(player_stats['name'], player_stats['health'])
                if player_stats['health'] <= 0:
                    await update.message.reply_text(f'{player_stats["name"]} 倒下了')
                await update.message.reply_text(
                    f'{opponent_roll_str}\n{opponent_stats["name"]} 胜利，造成{damage_str}点伤害\n'
                    f"胜者增加 {bonus} 点理智，败者减少 {bonus} 点理智。"
                )
                break
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('操作已取消。')
    return ConversationHandler.END

def get_battle_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('battle', battle_start)],
        states={
            PLAYER1_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, player1_name)],
            PLAYER2_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, player2_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=False  # 同一聊天内所有用户共享对话状态
    )