from database.queries import get_skill_info, get_character_stats

def get_info(player_name, player_skill_name, opponent_name, opponent_skill_name):
    player_stats = get_character_stats(player_name)
    opponent_stats = get_character_stats(opponent_name)
    player_skill = get_skill_info(player_skill_name)
    opponent_skill = get_skill_info(opponent_skill_name)
#这里要改
    if not player_stats or not opponent_stats or not player_skill or not opponent_skill:
        return None, None, None, None

    player_stats = {
        'name': player_stats[1],
        'health': player_stats[2],
        'strength': player_stats[4],
        'weakness': player_stats[5]
    }
    opponent_stats = {
        'name': opponent_stats[1],
        'health': opponent_stats[2],
        'strength': opponent_stats[4],
        'weakness': opponent_stats[5]
    }
    player_skill = {
        'name': player_skill[1],
        'base_value': player_skill[2],
        'num_dice': player_skill[3],
        'dice_range': (player_skill[4], player_skill[5])
    }
    opponent_skill = {
        'name': opponent_skill[1],
        'base_value': opponent_skill[2],
        'num_dice': opponent_skill[3],
        'dice_range': (opponent_skill[4], opponent_skill[5])
    }
    return player_stats, player_skill, opponent_stats, opponent_skill