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
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("UPDATE characters SET health=? WHERE name=?", (new_health, character_name))
    db.connection.commit()
    db.close()

def reset_character_stats():
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("UPDATE characters SET health = initial_health, strength = 0, weakness = 0, sanity = 0")
    db.connection.commit()
    db.close()

def update_character_strength(character_name, strength_change):
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("UPDATE characters SET strength = strength + ? WHERE name=?", (strength_change, character_name))
    db.connection.commit()
    db.close()

def update_character_weakness(character_name, weakness_change):
    db = DatabaseConnection('game.db')
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("UPDATE characters SET weakness = weakness + ? WHERE name=?", (weakness_change, character_name))
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