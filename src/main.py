from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from telegram import Update
import logging
from game.dice import DiceGame
from database.queries import get_skill_info, get_character_stats, update_character_health, reset_character_stats, update_character_strength, update_character_weakness
from game.dice_roll import dice_command
from stat_checks import get_stat_handlers
from attribute_modifiers import get_attribute_modifier_handlers
from stat_panel import get_stat_panel_handler


token = "5769924134:AAFr2m3_mr_HbOdO42Mt8MUGAxFAaG4E4Yg"

# 初始化
application = Application.builder().token(token).proxy('socks5://127.0.0.1:7890').build()

# 定义状态
PLAYER1_NAME, PLAYER1_SKILL, PLAYER2_NAME, PLAYER2_SKILL = range(4)

# 启动函数
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('miamiamiamiaminmi')

# 重置函数
async def reset(update: Update, context: CallbackContext) -> None:
    reset_character_stats()
    await update.message.reply_text('角色状态已恢复。')

# 修改强壮层数函数
async def strength(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和修改的强壮层数。格式: /strength 角色名 层数')
        return

    character_name, strength_change = args
    strength_change = int(strength_change)
    update_character_strength(character_name, strength_change)
    action = "增加" if strength_change > 0 else "减少"
    await update.message.reply_text(f'{character_name} 的强壮层数{action}了 {abs(strength_change)}。')

# 修改虚弱层数函数
async def weakness(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和修改的虚弱层数。格式: /weakness 角色名 层数')
        return

    character_name, weakness_change = args
    weakness_change = int(weakness_change)
    update_character_weakness(character_name, weakness_change)
    action = "增加" if weakness_change > 0 else "减少"
    await update.message.reply_text(f'{character_name} 的虚弱层数{action}了 {abs(weakness_change)}。')

# 获取角色和技能详细信息的通用函数
def get_info(player_name, player_skill_name, opponent_name, opponent_skill_name):
    player_stats = get_character_stats(player_name)
    opponent_stats = get_character_stats(opponent_name)
    player_skill = get_skill_info(player_skill_name)
    opponent_skill = get_skill_info(opponent_skill_name)

    if not player_stats or not opponent_stats or not player_skill or not opponent_skill:
        return None, None, None, None
    
    player_stats = {
        'name': player_stats[1],
        'health': player_stats[2],
        'strength': player_stats[4],
        'weakness': player_stats[5]
    }
    opponent_stats = {
        'name': opponent_stats[1],
        'health': opponent_stats[2],
        'strength': opponent_stats[4],
        'weakness': opponent_stats[5]
    }
    player_skill = {
        'name': player_skill[1],
        'base_value': player_skill[2],
        'num_dice': player_skill[3],
        'dice_range': (player_skill[4], player_skill[5])
    }
    opponent_skill = {
        'name': opponent_skill[1],
        'base_value': opponent_skill[2],
        'num_dice': opponent_skill[3],
        'dice_range': (opponent_skill[4], opponent_skill[5])
    }

    return player_stats, player_skill, opponent_stats, opponent_skill

# 战斗函数
async def battle_start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('请提供敌方角色名称和技能名称。格式: 角色名 技能名')
    return PLAYER1_NAME

async def player1_name(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和技能名称。格式: 角色名 技能名')
        return PLAYER1_NAME

    context.user_data['player1_name'], context.user_data['player1_skill'] = args
    await update.message.reply_text('敌方攻击已准备。请提供你的角色名称和技能名称。格式: 角色名 技能名')
    return PLAYER2_NAME

async def player2_name(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和技能名称。格式: 角色名 技能名')
        return PLAYER2_NAME

    context.user_data['player2_name'], context.user_data['player2_skill'] = args

    player_name = context.user_data['player1_name']
    player_skill_name = context.user_data['player1_skill']
    opponent_name = context.user_data['player2_name']
    opponent_skill_name = context.user_data['player2_skill']

    player_stats, player_skill, opponent_stats, opponent_skill = get_info(player_name, player_skill_name, opponent_name, opponent_skill_name)

    print(f'player_stats: {player_stats}')
    print(f'opponent_stats: {opponent_stats}')
    print(f'player_skill: {player_skill}')
    print(f'opponent_skill: {opponent_skill}')

    if not player_stats or not opponent_stats or not player_skill or not opponent_skill:
        await update.message.reply_text('角色或技能信息无效。')
        return ConversationHandler.END

    dice_game = DiceGame(player_stats, opponent_stats, player_skill, opponent_skill)
    while True:
        roll1 = dice_game.roll_dice(player_skill['num_dice'], player_skill['dice_range'], player_stats['strength'], player_stats['weakness'])
        roll2 = dice_game.roll_dice(opponent_skill['num_dice'], opponent_skill['dice_range'], opponent_stats['strength'], opponent_stats['weakness'])
        print(f'roll1: {roll1}')
        print(f'roll2: {roll2}')
        result1 = dice_game.calculate_result(player_skill['base_value'], roll1)
        result2 = dice_game.calculate_result(opponent_skill['base_value'], roll2)
        player_roll_str = f'{player_stats["name"]}: {player_skill["name"]}: {player_skill["base_value"]} + ' + ' + '.join(map(str, roll1)) + f' = {result1}'
        opponent_roll_str = f'{opponent_stats["name"]}: {opponent_skill["name"]}: {opponent_skill["base_value"]} + ' + ' + '.join(map(str, roll2)) + f' = {result2}'
        result_message = f"{player_roll_str}\n{opponent_roll_str}"
        if result1 > result2:
            result_message += f"\n{player_stats['name']} 胜利"
        elif result2 > result1:
            result_message += f"\n{opponent_stats['name']} 胜利"
        else:
            result_message += "\n不分胜负"
        await update.message.reply_text(result_message)
        if result1 > result2:
            opponent_skill['num_dice'] -= 1
            if opponent_skill['num_dice'] == 0:
                roll1 = dice_game.roll_dice(player_skill['num_dice'], player_skill['dice_range'], player_stats['strength'], player_stats['weakness'])
                player_roll_str = f'{player_stats["name"]}: {player_skill["name"]}: {player_skill["base_value"]} + ' + ' + '.join(map(str, roll1)) + f' = {result1}'
                damage = dice_game.damage(player_skill['base_value'], roll1)
                damage_str = ' + '.join([f'({player_skill["base_value"]} + ' + ' + '.join(map(str, roll1[:i+1])) + ')' for i in range(len(roll1))]) + f' = {damage}'
                opponent_stats['health'] -= damage
                update_character_health(opponent_stats['name'], opponent_stats['health'])
                await update.message.reply_text(f'{player_roll_str}\n{player_stats["name"]} 胜利，造成{damage_str}点伤害')
                if opponent_stats['health'] <= 0:
                    await update.message.reply_text(f'{opponent_stats["name"]} 倒下了')
                break
        elif result2 > result1:
            player_skill['num_dice'] -= 1
            if player_skill['num_dice'] == 0:
                roll2 = dice_game.roll_dice(opponent_skill['num_dice'], opponent_skill['dice_range'], opponent_stats['strength'], opponent_stats['weakness'])
                opponent_roll_str = f'{opponent_stats["name"]}: {opponent_skill["name"]}: {opponent_skill["base_value"]} + ' + ' + '.join(map(str, roll2)) + f' = {result2}'
                damage = dice_game.damage(opponent_skill['base_value'], roll2)
                damage_str = ' + '.join([f'({opponent_skill["base_value"]} + ' + ' + '.join(map(str, roll2[:i+1])) + ')' for i in range(len(roll2))]) + f' = {damage}'
                player_stats['health'] -= damage
                update_character_health(player_stats['name'], player_stats['health'])
                await update.message.reply_text(f'{opponent_roll_str}\n{opponent_stats["name"]} 胜利，造成{damage_str}点伤害')
                if player_stats['health'] <= 0:
                    await update.message.reply_text(f'{player_stats["name"]} 倒下了')
                break
    return ConversationHandler.END

# 防守函数
async def defense_start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('请提供防守方角色名称和技能名称。格式: 角色名 技能名')
    return PLAYER1_NAME

async def player1_name_defense(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和技能名称。格式: 角色名 技能名')
        return PLAYER1_NAME

    context.user_data['player1_name'], context.user_data['player1_skill'] = args
    await update.message.reply_text('防守方已准备。请提供进攻方角色名称和技能名称。格式: 角色名 技能名')
    return PLAYER2_NAME

async def player2_name_defense(update: Update, context: CallbackContext) -> int:
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和技能名称。格式: 角色名 技能名')
        return PLAYER2_NAME

    context.user_data['player2_name'], context.user_data['player2_skill'] = args

    player_name = context.user_data['player1_name']
    player_skill_name = context.user_data['player1_skill']
    opponent_name = context.user_data['player2_name']
    opponent_skill_name = context.user_data['player2_skill']

    player_stats, player_skill, opponent_stats, opponent_skill = get_info(player_name, player_skill_name, opponent_name, opponent_skill_name)

    print(f'player_stats: {player_stats}')
    print(f'opponent_stats: {opponent_stats}')
    print(f'player_skill: {player_skill}')
    print(f'opponent_skill: {opponent_skill}')

    if not player_stats or not opponent_stats or not player_skill or not opponent_skill:
        await update.message.reply_text('角色或技能信息无效。')
        return ConversationHandler.END

    dice_game = DiceGame(player_stats, opponent_stats, player_skill, opponent_skill)
    roll1 = dice_game.roll_dice(player_skill['num_dice'], player_skill['dice_range'], player_stats['strength'], player_stats['weakness'])
    roll2 = dice_game.roll_dice(opponent_skill['num_dice'], opponent_skill['dice_range'], opponent_stats['strength'], opponent_stats['weakness'])
    print(f'roll1: {roll1}')
    print(f'roll2: {roll2}')
    result1 = dice_game.damage(player_skill['base_value'], roll1)
    result2 = dice_game.damage(opponent_skill['base_value'], roll2)
    player_roll_str = f'{player_stats["name"]}: {player_skill["name"]}: ' + ' + '.join([f'({player_skill["base_value"]} + ' + ' + '.join(map(str, roll1[:i+1])) + ')' for i in range(len(roll1))]) + f' = {result1}'
    opponent_roll_str = f'{opponent_stats["name"]}: {opponent_skill["name"]}: ' + ' + '.join([f'({opponent_skill["base_value"]} + ' + ' + '.join(map(str, roll2[:i+1])) + ')' for i in range(len(roll2))]) + f' = {result2}'
    result_message = f"{player_roll_str}\n{opponent_roll_str}"
    if result2 > result1:
        damage = result2 - result1
        player_stats['health'] -= damage
        update_character_health(player_stats['name'], player_stats['health'])
        result_message += f"\n{player_stats['name']} 的防御被破坏，受到 {damage} 点伤害"
        if player_stats['health'] <= 0:
            result_message += f"\n{player_stats['name']} 倒下了"
    else:
        result_message += f"\n{player_stats['name']} 成功防守，没有受到伤害"
    await update.message.reply_text(result_message)
    return ConversationHandler.END

# 错误处理函数
def error(update: Update, context: CallbackContext) -> None:
    logging.warning(f'Update {update} caused error {context.error}')

# 处理命令和消息
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("reset", reset))
application.add_handler(CommandHandler("strength", strength))
application.add_handler(CommandHandler("weakness", weakness))
# application.add_handler(MessageHandler(filters.Regex(r'^\d*d\d+([+-]\d+)?$'), dice_command))  # 添加掷骰命令处理程序

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('操作已取消。')
    return ConversationHandler.END

battle_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('battle', battle_start)],
    states={
        PLAYER1_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, player1_name)],
        PLAYER2_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, player2_name)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

defense_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('defense', defense_start)],
    states={
        PLAYER1_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, player1_name_defense)],
        PLAYER2_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, player2_name_defense)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

application.add_handler(battle_conv_handler)
application.add_handler(defense_conv_handler)

for handler in get_stat_handlers():
    application.add_handler(handler)

for handler in get_attribute_modifier_handlers():
    application.add_handler(handler)

application.add_handler(get_stat_panel_handler())

application.add_error_handler(error)

# 启动Bot
if __name__ == '__main__':
    application.run_polling()