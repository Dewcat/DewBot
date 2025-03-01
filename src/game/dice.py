from random import randint

class DiceGame:
    def __init__(self, character1, character2, skill1, skill2):
        self.character1 = character1
        self.character2 = character2
        self.skill1 = skill1
        self.skill2 = skill2

    def roll_dice(self, num_dice, coin_value, strength, weakness, sanity):
        # 理智值影响正面概率：正面概率 = (50 + sanity)%
        modifier = strength - weakness
        chance = 50 + sanity  # sanity 范围: -45~+45
        # 投掷硬币：randint(1,100)如果小于等于chance，则视为正面；正面则返回 coin_value + modifier，否则返回 0
        return [coin_value + modifier if randint(1, 100) <= chance else 0 for _ in range(num_dice)]

    def calculate_result(self, base_value, roll_results):
        return base_value + sum(roll_results)

    def damage(self, base_value, rolls):
        total_damage = 0
        cumulative_sum = base_value
        for roll in rolls:
            cumulative_sum += roll
            total_damage += cumulative_sum
        return total_damage

def roll_for_character(skill, stats):
    """
    根据传入的技能信息和角色状态进行投掷硬币。
    skill: 包含 'num_dice' 和 'dice_range'（硬币正面数值）的字典
    stats: 包含 'strength'、'weakness' 以及可选的 'sanity'（理智值，默认为0）的字典
    """
    dice_game = DiceGame(None, None, None, None)
    return dice_game.roll_dice(skill['num_dice'], skill['dice_range'], stats['strength'], stats['weakness'], stats['sanity'])