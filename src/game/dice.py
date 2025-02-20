from random import randint

class DiceGame:
    def __init__(self, character1, character2, skill1, skill2):
        self.character1 = character1
        self.character2 = character2
        self.skill1 = skill1
        self.skill2 = skill2

    def roll_dice(self, num_dice, dice_range, strength, weakness):
        return [max(0, randint(dice_range[0], dice_range[1]) + strength - weakness) for _ in range(num_dice)]

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
    根据传入的技能信息和角色状态进行掷骰。
    skill: 包含 'num_dice' 和 'dice_range' 的字典
    stats: 包含 'strength' 和 'weakness' 的字典
    """
    # 使用临时 DiceGame 实例，不需要传入实际角色和技能信息
    dice_game = DiceGame(None, None, None, None)
    return dice_game.roll_dice(skill['num_dice'], skill['dice_range'], stats['strength'], stats['weakness'])