from telegram.ext import Application, CommandHandler, CallbackContext
from telegram import Update
import logging
from game.dice import DiceGame
from database.queries import get_skill_info, get_character_stats

token = ""

# 初始化
application = Application.builder().token(token).proxy('socks5://127.0.0.1:7890').build()

# 启动函数
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('欢迎来到掷骰游戏！使用 /battle 命令开始游戏。')

# 掷骰函数
async def battle(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 4:
        await update.message.reply_text('请提供两个角色名称和两个技能名称。格式: /battle 角色1 技能1 角色2 技能2')
        return

    player_name, player_skill_name, opponent_name, opponent_skill_name = args
    player_stats = list(get_character_stats(player_name))
    opponent_stats = list(get_character_stats(opponent_name))
    player_skill = list(get_skill_info(player_skill_name))
    opponent_skill = list(get_skill_info(opponent_skill_name))

    print(f'player_stats: {player_stats}')
    print(f'opponent_stats: {opponent_stats}')
    print(f'player_skill: {player_skill}')
    print(f'opponent_skill: {opponent_skill}')

    if not player_stats or not opponent_stats or not player_skill or not opponent_skill:
        await update.message.reply_text('角色或技能信息无效。')
        return

    dice_game = DiceGame(player_name, opponent_name, player_skill, opponent_skill)
    while True:
        roll1 = dice_game.roll_dice(player_skill[3], player_skill[4:6])
        roll2 = dice_game.roll_dice(opponent_skill[3], opponent_skill[4:6])
        print(f'roll1: {roll1}')
        print(f'roll2: {roll2}')
        result1 = dice_game.calculate_result(player_skill[2], roll1)
        result2 = dice_game.calculate_result(opponent_skill[2], roll2)
        player_roll_str = f'{player_stats[1]}: {player_skill[1]}: {player_skill[2]} + ' + ' + '.join(map(str, roll1)) + f' = {result1}'
        opponent_roll_str = f'{opponent_stats[1]}: {opponent_skill[1]}: {opponent_skill[2]} + ' + ' + '.join(map(str, roll2)) + f' = {result2}'
        result_message = f"{player_roll_str}\n{opponent_roll_str}"
        if result1 > result2:
            result_message += f"\n{player_stats[1]} 胜利"
        elif result2 > result1:
            result_message += f"\n{opponent_stats[1]} 胜利"
        else:
            result_message += "\n不分胜负"
        await update.message.reply_text(result_message)
        if result1 > result2:
            opponent_skill[3] -= 1
            if opponent_skill[3] == 0:
                damage = result1
                opponent_stats[2] -= damage
                await update.message.reply_text(f'{player_stats[1]} 胜利，造成{damage}点伤害')
                break
        elif result2 > result1:
            player_skill[3] -= 1
            if player_skill[3] == 0:
                damage = result2
                player_stats[2] -= damage
                await update.message.reply_text(f'{opponent_stats[1]} 胜利，造成{damage}点伤害')
                break

# 错误处理函数
def error(update: Update, context: CallbackContext) -> None:
    logging.warning(f'Update {update} caused error {context.error}')

# 处理命令和消息
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("battle", battle))
application.add_error_handler(error)

# 启动Bot
if __name__ == '__main__':
    application.run_polling()