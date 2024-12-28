from database.queries import get_skill_info
import random

class Skill:
    def __init__(self, name, damage, description):
        self.name = name
        self.damage = damage
        self.description = description

    def use(self, attacker, defender):
        attack_roll = random.randint(1, 6)  # 掷骰
        total_damage = self.damage + attack_roll
        return total_damage

def load_skills():
    skills = []
    skill_data = get_skill_info()  # 从数据库中获取技能信息
    for data in skill_data:
        skill = Skill(name=data['name'], damage=data['damage'], description=data['description'])
        skills.append(skill)
    return skills