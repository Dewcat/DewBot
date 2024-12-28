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