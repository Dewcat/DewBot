from database.queries import get_skill_info, get_character_stats

def get_info(*, player_name=None, player_skill_name=None, opponent_name=None, opponent_skill_name=None):
    """
    根据传入的参数单独获取角色和技能信息，
    只返回已传入参数对应的结果，不返回None，也不限定返回顺序。
    
    调用示例：
      只获取角色统计信息：
        result = get_info(player_name="Alice", opponent_name="Bob")
      
      只获取技能信息：
        result = get_info(player_skill_name="斩击", opponent_skill_name="防御")
      
      同时获取角色统计信息和技能信息：
        result = get_info(
          player_name="Alice", player_skill_name="斩击",
          opponent_name="Bob", opponent_skill_name="防御"
        )
      
      返回的result为字典，可能包含的键有：
        "player_stats", "opponent_stats", "player_skill", "opponent_skill"
    """
    result = {}
    
    if player_name:
        stats = get_character_stats(player_name)
        if stats:
            result["player_stats"] = {
                'name': stats[1],
                'health': stats[2],
                'strength': stats[4],
                'weakness': stats[5],
                'sanity': stats[6]
            }
    
    if opponent_name:
        stats = get_character_stats(opponent_name)
        if stats:
            result["opponent_stats"] = {
                'name': stats[1],
                'health': stats[2],
                'strength': stats[4],
                'weakness': stats[5],
                'sanity': stats[6]
            }
    
    if player_skill_name:
        skill = get_skill_info(player_skill_name)
        if skill:
            result["player_skill"] = {
                'name': skill[1],
                'base_value': skill[2],
                'num_dice': skill[3],
                # 修改处：用单个数字表示硬币正面变动值
                'dice_range': skill[4]
            }
    
    if opponent_skill_name:
        skill = get_skill_info(opponent_skill_name)
        if skill:
            result["opponent_skill"] = {
                'name': skill[1],
                'base_value': skill[2],
                'num_dice': skill[3],
                # 修改处：用单个数字表示硬币正面变动值
                'dice_range': skill[4]
            }
    
    return result if result else None