from database.queries import update_character_stagger_state

def calculate_stagger_thresholds(max_health, stagger_rate, stagger_num, stagger_ed):
    """
    计算角色的混乱阈值列表
    
    参数:
        max_health: 角色最大生命值
        stagger_rate: 混乱阈值比例（如0.3，表示每个阈值相隔30%生命值）
        stagger_num: 混乱阈值个数（如2表示有两个阈值点）
        stagger_ed: 已触发的混乱阈值数
    
    返回:
        剩余的混乱阈值列表（从高到低排序）
    """
    print(f"调试 - 计算混乱阈值原始参数: max_health={max_health}, stagger_rate={stagger_rate}, stagger_num={stagger_num}, stagger_ed={stagger_ed}")
    
    # 检测并自动修正 stagger_rate 和 stagger_num 如果它们看起来被传反了
    # stagger_rate 应该是小于 1 的小数，stagger_num 应该是正整数
    if isinstance(stagger_rate, (int, float)) and isinstance(stagger_num, (int, float)):
        if stagger_rate > 1 and stagger_num < 1:
            # 它们可能被传反了，交换它们
            print(f"调试 - 检测到参数可能颠倒，交换 stagger_rate 和 stagger_num")
            stagger_rate, stagger_num = stagger_num, stagger_rate
    
    # 确保值为正确类型
    try:
        max_health = int(max_health) if max_health else 100
        
        # stagger_rate 应该是 0-1 之间的小数
        if stagger_rate is not None:
            if isinstance(stagger_rate, (int, float)) and stagger_rate > 1:
                # 如果大于1且是整数，可能是百分比形式，转为小数
                stagger_rate = float(stagger_rate) / 100
            else:
                stagger_rate = float(stagger_rate)
        else:
            stagger_rate = 0.0
            
        # stagger_num 和 stagger_ed 应该是整数
        stagger_num = int(stagger_num) if stagger_num else 0
        stagger_ed = int(stagger_ed) if stagger_ed else 0
        
        print(f"调试 - 处理后的参数: stagger_rate={stagger_rate}, stagger_num={stagger_num}")
    except (ValueError, TypeError) as e:
        print(f"调试 - 混乱阈值参数错误: {e}")
        return []
    
    thresholds = []
    for i in range(stagger_ed, stagger_num):
        # 计算每个阈值点
        threshold = int(max_health * (1 - stagger_rate * (i + 1)))
        print(f"调试 - 计算阈值点 {i+1}: {threshold} = {max_health} * (1 - {stagger_rate} * {i+1})")
        if threshold > 0:  # 确保阈值为正数
            thresholds.append(threshold)
    
    print(f"调试 - 计算得到的混乱阈值: {thresholds}")
    return sorted(thresholds, reverse=True)

def check_stagger(character_name, current_health, previous_health, max_health, stagger_rate, stagger_num, stagger_ed, is_stagger):
    """
    检查角色是否进入混乱状态
    
    参数:
        character_name: 角色名称
        current_health: 当前生命值
        previous_health: 受伤前生命值
        max_health: 最大生命值
        stagger_rate: 混乱阈值比例
        stagger_num: 混乱阈值个数
        stagger_ed: 已触发的混乱阈值数
        is_stagger: 当前混乱状态
    
    返回:
        (新的混乱状态, 新的已触发阈值数, 触发消息)
    """
    print(f"\n调试 - 检查混乱: character_name={character_name}, current_health={current_health}, previous_health={previous_health}")
    print(f"调试 - 混乱参数: max_health={max_health}, stagger_rate={stagger_rate}, stagger_num={stagger_num}, stagger_ed={stagger_ed}, is_stagger={is_stagger}")
    
    # 确保使用初始生命值作为最大生命值
    if max_health is None or max_health <= 0:
        max_health = 100  # 默认值
        print(f"调试 - 使用默认最大生命值: {max_health}")
    
    if is_stagger > 0:  # 已经处于混乱状态
        print("调试 - 已处于混乱状态，跳过检查")
        return is_stagger, stagger_ed, ""
    
    thresholds = calculate_stagger_thresholds(max_health, stagger_rate, stagger_num, stagger_ed)
    if not thresholds:  # 没有剩余的混乱阈值
        print("调试 - 没有剩余的混乱阈值")
        return 0, stagger_ed, ""
    
    # 检查此次伤害是否突破了混乱阈值
    triggered_thresholds = [t for t in thresholds if previous_health > t >= current_health]
    triggered_count = len(triggered_thresholds)
    
    print(f"调试 - 触发的混乱阈值: {triggered_thresholds}, 触发数量: {triggered_count}")
    
    if triggered_count == 0:
        print("调试 - 没有触发混乱阈值")
        return 0, stagger_ed, ""
    
    new_stagger_ed = stagger_ed + triggered_count
    new_stagger_state = min(triggered_count, 3)  # 最高为混乱++（状态3）
    
    print(f"调试 - 新的混乱状态: {new_stagger_state}, 新的已触发阈值数: {new_stagger_ed}")
    
    # 更新角色的混乱状态
    result = update_character_stagger_state(character_name, new_stagger_ed, new_stagger_state)
    print(f"调试 - 更新混乱状态结果: {result}")
    
    stagger_desc = {
        1: "混乱",
        2: "混乱+",
        3: "混乱++"
    }
    
    message = f"{character_name} 陷入{stagger_desc[new_stagger_state]}状态！"
    print(f"调试 - 混乱消息: {message}")
    return new_stagger_state, new_stagger_ed, message

def get_stagger_multiplier(is_stagger):
    """
    获取混乱状态下的伤害乘数
    
    参数:
        is_stagger: 混乱状态（0-3）
    
    返回:
        伤害乘数
    """
    multipliers = {
        0: 1.0,   # 无混乱
        1: 2.0,   # 混乱
        2: 3.0,   # 混乱+
        3: 4.0    # 混乱++
    }
    multiplier = multipliers.get(is_stagger, 1.0)
    print(f"调试 - 混乱伤害乘数: is_stagger={is_stagger}, multiplier={multiplier}")
    return multiplier

def clear_stagger(character_name):
    """
    清除角色的混乱状态
    
    参数:
        character_name: 角色名称
    """
    print(f"调试 - 清除混乱状态: character_name={character_name}")
    result = update_character_stagger_state(character_name, stagger_ed=None, is_stagger=0)
    print(f"调试 - 清除混乱状态结果: {result}")
    return "混乱状态已解除"

def get_stagger_description(is_stagger):
    """
    获取混乱状态的文字描述
    
    参数:
        is_stagger: 混乱状态（0-3）
    
    返回:
        状态描述文本
    """
    descriptions = {
        0: "",
        1: "【陷入混乱】",
        2: "【陷入混乱+】",
        3: "【陷入混乱++】"
    }
    return descriptions.get(is_stagger, "")
