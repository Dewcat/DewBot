from database.db_connection import DatabaseConnection

def get_character_stats(character_name):
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM characters WHERE name=?", (character_name,))
    character = cursor.fetchone()
    db.close()
    return character

def get_skill_info(skill_name):
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM skills WHERE name=?", (skill_name,))
    skill = cursor.fetchone()
    db.close()
    return skill

def update_character_health(character_name, new_health):
    """
    更新角色体力值，确保体力不低于0且不高于初始最大值
    
    参数:
      character_name: 角色名称
      new_health: 要设置的新体力值
    
    返回:
      实际更新后的体力值
    """
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    
    # 先获取角色的初始体力值
    cursor.execute("SELECT initial_health FROM characters WHERE name=?", (character_name,))
    result = cursor.fetchone()
    if not result:
        db.close()
        return None
    
    initial_health = result[0]
    
    # 确保体力值在合理范围内
    if new_health < 0:
        new_health = 0
    elif new_health > initial_health:
        new_health = initial_health
    
    # 更新体力值
    cursor.execute("UPDATE characters SET health=? WHERE name=?", (new_health, character_name))
    db.connection.commit()
    db.close()
    
    return new_health

def reset_character_stats():
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("UPDATE characters SET health = initial_health, strength = 0, weakness = 0, sanity = 0, vul = 0")
    db.connection.commit()
    db.close()

def update_character_strength(character_name, strength_change):
    """
    更新角色强壮层数，并与虚弱层数互相抵消
    """
    if strength_change == 0:
        return
    
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    
    # 读取当前角色的强壮和虚弱值
    cursor.execute("SELECT strength, weakness FROM characters WHERE name=?", (character_name,))
    result = cursor.fetchone()
    if not result:
        db.close()
        return
    
    current_strength, current_weakness = result
    
    # 如果要增加强壮层数
    if strength_change > 0:
        # 先抵消虚弱层数
        if current_weakness > 0:
            # 计算抵消后的值
            cancelled = min(strength_change, current_weakness)
            remaining_strength_change = strength_change - cancelled
            new_weakness = current_weakness - cancelled
            
            # 更新虚弱层数
            cursor.execute("UPDATE characters SET weakness = ? WHERE name=?", 
                         (new_weakness, character_name))
            
            # 如果有剩余的强壮层数，则增加
            if remaining_strength_change > 0:
                cursor.execute("UPDATE characters SET strength = strength + ? WHERE name=?", 
                             (remaining_strength_change, character_name))
        else:
            # 没有虚弱层数，直接增加强壮
            cursor.execute("UPDATE characters SET strength = strength + ? WHERE name=?", 
                         (strength_change, character_name))
    
    # 如果要减少强壮层数
    else:
        # 直接减少强壮，不会低于0
        new_strength = max(0, current_strength + strength_change)  # strength_change是负数
        cursor.execute("UPDATE characters SET strength = ? WHERE name=?", 
                     (new_strength, character_name))
    
    db.connection.commit()
    db.close()

def update_character_weakness(character_name, weakness_change):
    """
    更新角色虚弱层数，并与强壮层数互相抵消
    """
    if weakness_change == 0:
        return
    
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    
    # 读取当前角色的强壮和虚弱值
    cursor.execute("SELECT strength, weakness FROM characters WHERE name=?", (character_name,))
    result = cursor.fetchone()
    if not result:
        db.close()
        return
    
    current_strength, current_weakness = result
    
    # 如果要增加虚弱层数
    if weakness_change > 0:
        # 先抵消强壮层数
        if current_strength > 0:
            # 计算抵消后的值
            cancelled = min(weakness_change, current_strength)
            remaining_weakness_change = weakness_change - cancelled
            new_strength = current_strength - cancelled
            
            # 更新强壮层数
            cursor.execute("UPDATE characters SET strength = ? WHERE name=?", 
                         (new_strength, character_name))
            
            # 如果有剩余的虚弱层数，则增加
            if remaining_weakness_change > 0:
                cursor.execute("UPDATE characters SET weakness = weakness + ? WHERE name=?", 
                             (remaining_weakness_change, character_name))
        else:
            # 没有强壮层数，直接增加虚弱
            cursor.execute("UPDATE characters SET weakness = weakness + ? WHERE name=?", 
                         (weakness_change, character_name))
    
    # 如果要减少虚弱层数
    else:
        # 直接减少虚弱，不会低于0
        new_weakness = max(0, current_weakness + weakness_change)  # weakness_change是负数
        cursor.execute("UPDATE characters SET weakness = ? WHERE name=?", 
                     (new_weakness, character_name))
    
    db.connection.commit()
    db.close()

def get_character_sanity(character_name):
    """
    从数据库中读取角色的理智值
    """
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("SELECT sanity FROM characters WHERE name=?", (character_name,))
    result = cursor.fetchone()
    db.close()
    # 如果数据库中有数据则返回理智值，不然默认返回 0
    return result[0] if result else 0

def update_character_sanity(character_name, new_sanity):
    """
    将新的理智值写回数据库，确保 new_sanity 在 -45 ~ 45 范围内
    """
    # 限制 new_sanity 在合理范围内
    if new_sanity > 45:
        new_sanity = 45
    elif new_sanity < -45:
        new_sanity = -45

    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("UPDATE characters SET sanity=? WHERE name=?", (new_sanity, character_name))
    db.connection.commit()
    db.close()

def update_character_vul(character_name, vul_change):
    """
    更新角色的易伤/守护值
    正值表示易伤，负值表示守护
    """
    if vul_change == 0:
        return
    
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    
    # 读取当前角色的易伤/守护值
    cursor.execute("SELECT vul FROM characters WHERE name=?", (character_name,))
    result = cursor.fetchone()
    if not result:
        db.close()
        return
    
    current_vul = result[0]
    new_vul = current_vul + vul_change
    
    cursor.execute("UPDATE characters SET vul = ? WHERE name=?", (new_vul, character_name))
    db.connection.commit()
    db.close()

def get_character_panels():
    """
    获取五个主要角色（珏、露、笙、莹、曦）的面板信息
    返回格式化后的面板数据，并为角色名添加个性化图标
    """
    # 角色名与对应的图标
    character_icons = {
        "珏": "⚫️珏⚪️",
        "露": "💦露💦",
        "笙": "🔰笙🔰",
        "莹": "✨️莹✨️", 
        "曦": "🫧曦🫧"
    }
    
    characters = list(character_icons.keys())
    result = {}
    
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    
    for character_name in characters:
        cursor.execute("SELECT name, health, initial_health, sanity, strength, weakness, vul, persona FROM characters WHERE name=?", 
                     (character_name,))
        row = cursor.fetchone()
        if row:
            name, health, max_health, sanity, strength, weakness, vul, persona = row
            
            panel = {
                'name': character_icons.get(name, name),  # 使用带图标的名称
                'original_name': name,  # 保留原始名称，以便后续处理
                'health': f"{health}/{max_health}",
                'sanity': sanity,
                'can_fight': health > 0,  # 添加战斗状态标记，体力为0则无法战斗
                'persona': persona  # 添加角色当前使用的人格信息
            }
            
            # 只有当强壮值不为0时才添加
            if strength > 0:
                panel['strength'] = strength
                
            # 只有当虚弱值不为0时才添加
            if weakness > 0:
                panel['weakness'] = weakness
                
            # 根据vul值正负显示易伤或守护
            if vul > 0:
                panel['vulnerability'] = vul
            elif vul < 0:
                panel['protection'] = abs(vul)
                
            result[name] = panel
    
    db.close()
    return result

def get_available_personas(character_name):
    """
    获取指定角色可用的所有人格列表
    返回一个列表，包含所有可用的人格数据
    """
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    
    # 查询所有可用于该角色的人格（persona字段等于该角色名的记录）
    cursor.execute("SELECT id, name, health, initial_health, dlv FROM characters WHERE persona = ?", (character_name,))
    personas = cursor.fetchall()
    
    db.close()
    return personas

def set_character_persona(character_name, persona_id):
    """
    将指定ID的人格数据覆盖到角色记录中
    
    参数:
      character_name: 要设置人格的角色名
      persona_id: 人格记录的ID
      
    返回:
      成功则返回人格名称，失败则返回None
    """
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    
    # 查询人格数据
    cursor.execute("SELECT name, health, initial_health, dlv FROM characters WHERE id = ?", (persona_id,))
    persona = cursor.fetchone()
    
    if not persona:
        db.close()
        return None
    
    persona_name, health, initial_health, dlv = persona
    
    # 更新角色数据，设置为所选人格的数据
    cursor.execute(
        "UPDATE characters SET health = ?, initial_health = ?, dlv = ?, persona = ? WHERE name = ?", 
        (health, initial_health, dlv, persona_name, character_name)
    )
    
    db.connection.commit()
    db.close()
    
    return persona_name

def reset_character_to_default(character_name):
    """
    将角色重置为默认状态
    体力和初始体力设为100，dlv归0，persona清空
    
    参数:
      character_name: 要重置的角色名
    """
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    
    # 重置角色状态
    cursor.execute(
        "UPDATE characters SET health = 100, initial_health = 100, dlv = 0, persona = NULL WHERE name = ?", 
        (character_name,)
    )
    
    db.connection.commit()
    db.close()
    
    return True