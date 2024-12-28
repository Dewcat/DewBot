class Character:
    def __init__(self, name, health, attack, defense, skills):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.skills = skills

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0

    def use_skill(self, skill_name):
        if skill_name in self.skills:
            return self.skills[skill_name].use()
        else:
            return f"{self.name} does not have the skill: {skill_name}"

    def __str__(self):
        return f"Character({self.name}, Health: {self.health}, Attack: {self.attack}, Defense: {self.defense})"