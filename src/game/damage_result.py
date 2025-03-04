def compute_simple_damage(base_value, rolls):
    """
    简单计算：总伤害 = 基础值 + 骰子总和
    返回：(总伤害, 描述字符串)
    """
    total = base_value + sum(rolls)
    description = f"({base_value} + {' + '.join(map(str, rolls))}) = {total}"
    return total, description

def compute_cumulative_damage(base_value, rolls):
    """
    累加计算：每段伤害累计
    例如：对 roll=[3, 5, 2] 及 base_value=30，
         计算：(30+3) + (30+3+5) + (30+3+5+2)
    返回：(总伤害, 描述字符串)
    """
    total = 0
    parts = []
    cumulative = base_value
    for i, r in enumerate(rolls):
        cumulative += r
        total += cumulative
        parts.append(f"({base_value} + {' + '.join(map(str, rolls[:i+1]))})")
    description = " + ".join(parts) + f" = {total}"
    return total, description
