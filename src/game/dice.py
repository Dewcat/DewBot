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
    """
    dice_game = DiceGame(None, None, None, None)
    return dice_game.roll_dice(skill['num_dice'], skill['dice_range'], stats['strength'], stats['weakness'], stats.get('sanity', 0))

# 新增：整合自 damage_result.py 的函数
def compute_simple_damage(base_value, rolls):
    """
    简单计算：总伤害 = 基础值 + 骰子总和
    返回：(总伤害, 描述字符串)
    """
    total = base_value + sum(rolls)
    description = f"({base_value} + {' + '.join(map(str, rolls))}) = {total}"
    return total, description

def compute_cumulative_damage(base_value, rolls, skill_alv=0, target_dlv=0, target_vul=0):
    """
    累加计算：每段伤害累计，并应用属性乘数
    例如：对 roll=[3, 5, 2] 及 base_value=30，
         计算：(30+3) + (30+3+5) + (30+3+5+2)
         然后应用公式：原始伤害 * (100+技能alv*10)% * (100-目标dlv*10)% * (100+目标vul*10)%
    
    参数:
      base_value: 基础伤害值
      rolls: 骰子结果列表
      skill_alv: 攻击技能的alv值
      target_dlv: 目标角色的dlv值
      target_vul: 目标角色的vul值(正值为易伤，负值为守护)
    
    返回:
      (最终伤害值, 描述字符串)
    """
    # 计算原始累加伤害
    raw_total = 0
    parts = []
    cumulative = base_value
    for i, r in enumerate(rolls):
        cumulative += r
        raw_total += cumulative
        parts.append(f"({base_value} + {' + '.join(map(str, rolls[:i+1]))})")
    
    damage_desc = " + ".join(parts) + f" = {raw_total}"
    
    # 应用属性乘数
    alv_multiplier = (100 + skill_alv * 10) / 100
    dlv_multiplier = (100 - target_dlv * 10) / 100
    vul_multiplier = (100 + target_vul * 10) / 100
    
    # 计算最终伤害
    final_damage = int(raw_total * alv_multiplier * dlv_multiplier * vul_multiplier)
    
    # 组织详细描述
    modifiers_desc = []
    if skill_alv != 0:
        modifiers_desc.append(f"技能攻击等级加成: {alv_multiplier:.1f}x")
    if target_dlv != 0:
        modifiers_desc.append(f"角色防御等级减免: {dlv_multiplier:.1f}x")
    if target_vul != 0:
        status = "易伤" if target_vul > 0 else "守护"
        modifiers_desc.append(f"{status}效果: {vul_multiplier:.1f}x")
    
    # 如果有修正因子，添加到描述中
    if modifiers_desc:
        modifiers_text = " * ".join(modifiers_desc)
        damage_desc += f"\n原始伤害 {raw_total} * {modifiers_text} = {final_damage}"
    
    return final_damage, damage_desc