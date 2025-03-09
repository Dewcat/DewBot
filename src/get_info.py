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
            print(f"\n调试 - 获取角色信息: player_name={player_name}")
            print(f"调试 - 原始数据: {stats}")
            result["player_stats"] = {
                'name': stats[1],
                'health': stats[2],
                'initial_health': stats[3],  # 添加初始生命值
                'strength': stats[4],
                'weakness': stats[5],
                'sanity': stats[6],
                'vul': stats[7],
                'dlv': stats[8],
                'stagger_rate': stats[9],  # 混乱阈值
                'stagger_num': stats[10],  # 混乱阈值个数
                'stagger_ed': stats[11],   # 已触发的混乱阈值数
                'is_stagger': stats[12]    # 当前混乱状态
            }
            print(f"调试 - 混乱相关属性: stagger_rate={stats[9]}, stagger_num={stats[10]}, stagger_ed={stats[11]}, is_stagger={stats[12]}")
    
    if opponent_name:
        stats = get_character_stats(opponent_name)
        if stats:
            print(f"\n调试 - 获取角色信息: opponent_name={opponent_name}")
            print(f"调试 - 原始数据: {stats}")
            result["opponent_stats"] = {
                'name': stats[1],
                'health': stats[2],
                'initial_health': stats[3],  # 添加初始生命值
                'strength': stats[4],
                'weakness': stats[5],
                'sanity': stats[6],
                'vul': stats[7],
                'dlv': stats[8],
                'stagger_rate': stats[9],  # 混乱阈值
                'stagger_num': stats[10],  # 混乱阈值个数
                'stagger_ed': stats[11],   # 已触发的混乱阈值数
                'is_stagger': stats[12]    # 当前混乱状态
            }
            print(f"调试 - 混乱相关属性: stagger_rate={stats[9]}, stagger_num={stats[10]}, stagger_ed={stats[11]}, is_stagger={stats[12]}")
    
    if player_skill_name:
        skill = get_skill_info(player_skill_name)
        if skill:
            result["player_skill"] = {
                'name': skill[1],
                'base_value': skill[2],
                'num_dice': skill[3],
                'dice_range': skill[4],
                'alv': skill[5]
            }
    
    if opponent_skill_name:
        skill = get_skill_info(opponent_skill_name)
        if skill:
            result["opponent_skill"] = {
                'name': skill[1],
                'base_value': skill[2],
                'num_dice': skill[3],
                'dice_range': skill[4],
                'alv': skill[5]
            }
    
    return result if result else None