import itertools
from collections import Counter
from functools import lru_cache

def get_sum_distribution(N, L, U):
    """
    计算N个变量，每个变量在[L, U]范围内均匀分布的和的概率分布。
    
    返回一个字典，键为可能的和，值为该和的概率。
    """
    if N == 0:
        return {0: 1.0}
    
    # 初始化分布，0个变量的和为0，概率为1
    distribution = Counter({0: 1})
    
    for _ in range(N):
        new_distribution = Counter()
        for current_sum, count in distribution.items():
            for value in range(L, U + 1):
                new_sum = current_sum + value
                new_distribution[new_sum] += count
        distribution = new_distribution
    
    total = (U - L + 1) ** N
    # 计算概率
    prob_distribution = {s: c / total for s, c in distribution.items()}
    return prob_distribution

def compute_comparison_probabilities(power1, power2):
    """
    计算玩家1胜、玩家2胜和平局的概率。
    
    power1和power2是两个字典，分别表示两位玩家的威力分布。
    
    返回一个元组 (P1_win, P2_win, Tie)
    """
    P1_win = 0.0
    P2_win = 0.0
    Tie = 0.0
    
    for p1, prob1 in power1.items():
        for p2, prob2 in power2.items():
            if p1 > p2:
                P1_win += prob1 * prob2
            elif p2 > p1:
                P2_win += prob1 * prob2
            else:
                Tie += prob1 * prob2
    return P1_win, P2_win, Tie

def main():
    print("=== 游戏胜率计算器 ===\n")
    
    # 输入玩家1的技能参数
    print("请输入玩家1的技能参数（格式：基础值+变动值数量*变动值下界:变动值上界）：")
    input1 = input("玩家1: ")
    base1, rest1 = input1.split('+')
    N1_initial, range1 = rest1.split('*')
    L1, U1 = range1.split(':')
    base1 = int(base1)
    N1_initial = int(N1_initial)
    L1 = int(L1)
    U1 = int(U1)
    print()
    
    # 输入玩家2的技能参数
    print("请输入玩家2的技能参数（格式：基础值+变动值数量*变动值下界:变动值上界）：")
    input2 = input("玩家2: ")
    base2, rest2 = input2.split('+')
    N2_initial, range2 = rest2.split('*')
    L2, U2 = range2.split(':')
    base2 = int(base2)
    N2_initial = int(N2_initial)
    L2 = int(L2)
    U2 = int(U2)
    print()
    
    # 预计算所有可能的N1和N2的威力分布
    max_N1 = N1_initial
    max_N2 = N2_initial
    
    # 使用缓存来存储计算过的威力分布
    sum_distribution1 = {}
    for n in range(max_N1 + 1):
        if n == 0:
            sum_distribution1[n] = {0: 1.0}
        else:
            dist = get_sum_distribution(n, L1, U1)
            # 加上基础值
            dist_with_base = {s + base1: prob for s, prob in dist.items()}
            sum_distribution1[n] = dist_with_base
    
    sum_distribution2 = {}
    for n in range(max_N2 + 1):
        if n == 0:
            sum_distribution2[n] = {0: 1.0}
        else:
            dist = get_sum_distribution(n, L2, U2)
            # 加上基础值
            dist_with_base = {s + base2: prob for s, prob in dist.items()}
            sum_distribution2[n] = dist_with_base
    
    @lru_cache(maxsize=None)
    def W(n1, n2):
        """
        返回在当前状态(n1, n2)下，玩家1获胜的概率。
        """
        if n1 == 0:
            return 0.0  # 玩家1已失去所有变动值，玩家2获胜
        if n2 == 0:
            return 1.0  # 玩家2已失去所有变动值，玩家1获胜
        
        power1 = sum_distribution1[n1]
        power2 = sum_distribution2[n2]
        
        P1_win, P2_win, Tie = compute_comparison_probabilities(power1, power2)
        
        if Tie == 1.0:
            # 永远平局，无法继续，理论上不可能发生
            return 0.0
        
        # 根据游戏规则，平局时重新进行对战
        # 所以，我们可以写出:
        # W = P1_win * W(n1, n2 -1) + P2_win * W(n1 -1, n2) + Tie * W(n1, n2)
        # => W - Tie * W = P1_win * W(n1, n2 -1) + P2_win * W(n1 -1, n2)
        # => W = (P1_win * W(n1, n2 -1) + P2_win * W(n1 -1, n2)) / (1 - Tie)
        
        W_next = (P1_win * W(n1, n2 -1) + P2_win * W(n1 -1, n2)) / (1 - Tie)
        return W_next
    
    # 计算初始状态的胜率
    win_rate_player1 = W(N1_initial, N2_initial)
    win_rate_player2 = 1.0 - win_rate_player1
    
    print("=== 计算结果 ===")
    print(f"玩家1的胜率: {win_rate_player1 * 100:.2f}%")
    print(f"玩家2的胜率: {win_rate_player2 * 100:.2f}%")

if __name__ == "__main__":
    main()
