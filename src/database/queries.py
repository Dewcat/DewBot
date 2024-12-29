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
    cursor.execute("UPDATE characters SET health = initial_health, strength = 0, weakness = 0")
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