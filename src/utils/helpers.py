def calculate_damage(attack, defense):
    damage = attack - defense
    return max(damage, 0)

def validate_input(value, min_value, max_value):
    if not isinstance(value, (int, float)):
        raise ValueError("Input must be a number.")
    if value < min_value or value > max_value:
        raise ValueError(f"Input must be between {min_value} and {max_value}.")
    return True

def format_result(result):
    return f"结果: {result}"