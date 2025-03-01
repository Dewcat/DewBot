from database.queries import get_character_sanity, update_character_sanity

def increase_sanity(character_name, amount):
    """
    增加角色理智值，确保不超过 45。
    
    参数:
      character_name: 角色名称
      amount: 增加的数值
    返回:
      更新后的理智值
    """
    current = get_character_sanity(character_name)
    new_value = current + amount
    if new_value > 45:
        new_value = 45
    update_character_sanity(character_name, new_value)
    return new_value

def decrease_sanity(character_name, amount):
    """
    降低角色理智值，确保不低于 -45。
    
    参数:
      character_name: 角色名称
      amount: 降低的数值
    返回:
      更新后的理智值
    """
    current = get_character_sanity(character_name)
    new_value = current - amount
    if new_value < -45:
        new_value = -45
    update_character_sanity(character_name, new_value)
    return new_value
