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

    # def play_round(self):
    #     while(1):
    #         roll1 = self.roll_dice(self.skill1['num_dice'], self.skill1['dice_range'])
    #         roll2 = self.roll_dice(self.skill2['num_dice'], self.skill2['dice_range'])

    #         result1 = self.calculate_result(roll1, self.skill1['base_value'])
    #         result2 = self.calculate_result(roll2, self.skill2['base_value'])

    #         if result1 > result2:
    #             self.skill2['num_dice'] -= 1
    #             if self.skill2['num_dice'] == 0:
    #                 damage = result1
    #                 self.character2['health'] -= damage
    #                 return f'{self.character1["name"]} 造成{damage}点伤害'
    #             else:continue
    #         elif result2 > result1:
    #             self.skill1['num_dice'] -= 1
    #             if self.skill1['num_dice'] == 0:
    #                 damage = result2
    #                 self.character1['health'] -= damage
    #                 return f'{self.character2["name"]} 造成{damage}点伤害'
    #             else:continue
    #         return '平局'