# task5.py
"""Модуль с решениями пятых задач билетов 1-7"""

import numpy as np
from scipy.stats import pearsonr

SOLUTIONS = {
    1: {
        'code': """
        import numpy as np
        from scipy.stats import pearsonr
# Билет 1: Анализ совместного распределения (X,Y)
def solve_ticket1():
    # Заданное распределение
    joint_prob = {
        (3,9): 0.24, (5,9): 0.04, (8,9): 0.29,
        (3,10): 0.09, (5,10): 0.11, (8,10): 0.23
    }
    
    # 1. E(X)
    e_x = sum(x * p for (x,y), p in joint_prob.items())
    
    # 2. Var(X)
    e_x2 = sum(x**2 * p for (x,y), p in joint_prob.items())
    var_x = e_x2 - e_x**2
    
    # 3. E(Y)
    e_y = sum(y * p for (x,y), p in joint_prob.items())
    
    # 4. Var(Y)
    e_y2 = sum(y**2 * p for (x,y), p in joint_prob.items())
    var_y = e_y2 - e_y**2
    
    # 5. ρ(X,Y)
    e_xy = sum(x*y * p for (x,y), p in joint_prob.items())
    cov = e_xy - e_x * e_y
    rho = cov / np.sqrt(var_x * var_y)
    
    return {
        'E(X)': round(e_x, 4),
        'Var(X)': round(var_x, 4),
        'E(Y)': round(e_y, 4),
        'Var(Y)': round(var_y, 4),
        'ρ(X,Y)': round(rho, 4)
    }
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ ОБОСНОВАНИЕ:
1. E(X) = Σx Σy x·P(X=x,Y=y)
2. Var(X) = E(X²) - [E(X)]²
3. ρ(X,Y) = Cov(X,Y)/(σ_X·σ_Y)
"""
    },
    
    2: {
        'code': """
# Билет 2: Анализ дискретного распределения (X,Y)
def solve_ticket2():
    dist = {
        (1,7): 0.28, (4,7): 0.02, (5,7): 0.03,
        (1,9): 0.31, (4,9): 0.05, (5,9): 0.31
    }
    
    # 1. E(X²)
    e_x2 = sum(x**2 * p for (x,y), p in dist.items())
    
    # 2. E(X⁴)
    e_x4 = sum(x**4 * p for (x,y), p in dist.items())
    
    # 3. Var(X²)
    var_x2 = e_x4 - e_x2**2
    
    # 4. E(X²Y)
    e_x2y = sum(x**2 * y * p for (x,y), p in dist.items())
    
    # 5. Cov(X²,Y)
    e_y = sum(y * p for (x,y), p in dist.items())
    cov_x2y = e_x2y - e_x2 * e_y
    
    return {
        'E(X²)': round(e_x2, 4),
        'E(X⁴)': round(e_x4, 4),
        'Var(X²)': round(var_x2, 4),
        'E(X²Y)': round(e_x2y, 4),
        'Cov(X²,Y)': round(cov_x2y, 4)
    }
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ ОБОСНОВАНИЕ:
1. E(X²) = Σx Σy x²·P(X=x,Y=y)
2. Cov(X²,Y) = E(X²Y) - E(X²)E(Y)
"""
    },
    
    3: {
        'code': """
# Билет 3: Анализ дискретного распределения (X,Y)
def solve_ticket3():
    dist = {
        (3,10): 0.04, (5,10): 0.18, (7,10): 0.01,
        (3,11): 0.47, (5,11): 0.17, (7,11): 0.13
    }
    
    # 1. E(X²)
    e_x2 = sum(x**2 * p for (x,y), p in dist.items())
    
    # 2. E(Y)
    e_y = sum(y * p for (x,y), p in dist.items())
    
    # 3. σ(X²)
    e_x4 = sum(x**4 * p for (x,y), p in dist.items())
    std_x2 = np.sqrt(e_x4 - e_x2**2)
    
    # 4. σ(Y)
    e_y2 = sum(y**2 * p for (x,y), p in dist.items())
    std_y = np.sqrt(e_y2 - e_y**2)
    
    # 5. ρ(X²,Y)
    e_x2y = sum(x**2 * y * p for (x,y), p in dist.items())
    cov_x2y = e_x2y - e_x2 * e_y
    rho = cov_x2y / (std_x2 * std_y)
    
    return {
        'E(X²)': round(e_x2, 4),
        'E(Y)': round(e_y, 4),
        'σ(X²)': round(std_x2, 4),
        'σ(Y)': round(std_y, 4),
        'ρ(X²,Y)': round(rho, 4)
    }
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ ОБОСНОВАНИЕ:
1. σ(X²) = sqrt(Var(X²))
2. ρ(X²,Y) = Cov(X²,Y)/(σ(X²)·σ(Y))
"""
    },
    
    4: {
        'code': """
# Билет 4: Анализ дискретного распределения (X,Y)
def solve_ticket4():
    dist = {
        (2,10): 0.02, (5,10): 0.31, (6,10): 0.04,
        (2,11): 0.21, (5,11): 0.19, (6,11): 0.23
    }
    
    # 1. E(X²)
    e_x2 = sum(x**2 * p for (x,y), p in dist.items())
    
    # 2. σ(X²)
    e_x4 = sum(x**4 * p for (x,y), p in dist.items())
    std_x2 = np.sqrt(e_x4 - e_x2**2)
    
    # 3. σ(Y²)
    e_y2 = sum(y**2 * p for (x,y), p in dist.items())
    e_y = sum(y * p for (x,y), p in dist.items())
    std_y2 = np.sqrt(e_y2 - e_y**2)
    
    # 4. Cov(X²,Y²)
    e_x2y2 = sum(x**2 * y**2 * p for (x,y), p in dist.items())
    cov_x2y2 = e_x2y2 - e_x2 * e_y2
    
    # 5. ρ(X²,Y²)
    rho = cov_x2y2 / (std_x2 * std_y2)
    
    return {
        'E(X²)': round(e_x2, 4),
        'σ(X²)': round(std_x2, 4),
        'σ(Y²)': round(std_y2, 4),
        'Cov(X²,Y²)': round(cov_x2y2, 4),
        'ρ(X²,Y²)': round(rho, 4)
    }
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ ОБОСНОВАНИЕ:
1. Cov(X²,Y²) = E(X²Y²) - E(X²)E(Y²)
2. ρ(X²,Y²) = Cov(X²,Y²)/(σ(X²)·σ(Y²))
"""
    },
    
    5: {
        'code': """
# Билет 5: Анализ дискретного распределения (X,Y)
def solve_ticket5():
    dist = {
        (2,10): 0.02, (5,10): 0.31, (6,10): 0.04,
        (2,11): 0.21, (5,11): 0.19, (6,11): 0.23
    }
    
    # Аналогично билету 4
    e_x2 = sum(x**2 * p for (x,y), p in dist.items())
    e_x4 = sum(x**4 * p for (x,y), p in dist.items())
    std_x2 = np.sqrt(e_x4 - e_x2**2)
    e_y2 = sum(y**2 * p for (x,y), p in dist.items())
    e_y = sum(y * p for (x,y), p in dist.items())
    std_y2 = np.sqrt(e_y2 - e_y**2)
    e_x2y2 = sum(x**2 * y**2 * p for (x,y), p in dist.items())
    cov_x2y2 = e_x2y2 - e_x2 * e_y2
    rho = cov_x2y2 / (std_x2 * std_y2)
    
    return {
        'E(X²)': round(e_x2, 4),
        'σ(X²)': round(std_x2, 4),
        'σ(Y²)': round(std_y2, 4),
        'Cov(X²,Y²)': round(cov_x2y2, 4),
        'ρ(X²,Y²)': round(rho, 4)
    }
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ ОБОСНОВАНИЕ:
Аналогично билету 4, так как распределение идентичное.
"""
    },
    
    6: {
        'code': """
# Билет 6: Анализ дискретного распределения (X,Y)
def solve_ticket6():
    dist = {
        (2,10): 0.02, (5,10): 0.31, (6,10): 0.04,
        (2,11): 0.21, (5,11): 0.19, (6,11): 0.23
    }
    
    # Аналогично билетам 4 и 5
    e_x2 = sum(x**2 * p for (x,y), p in dist.items())
    e_x4 = sum(x**4 * p for (x,y), p in dist.items())
    std_x2 = np.sqrt(e_x4 - e_x2**2)
    e_y2 = sum(y**2 * p for (x,y), p in dist.items())
    e_y = sum(y * p for (x,y), p in dist.items())
    std_y2 = np.sqrt(e_y2 - e_y**2)
    e_x2y2 = sum(x**2 * y**2 * p for (x,y), p in dist.items())
    cov_x2y2 = e_x2y2 - e_x2 * e_y2
    rho = cov_x2y2 / (std_x2 * std_y2)
    
    return {
        'E(X²)': round(e_x2, 4),
        'σ(X²)': round(std_x2, 4),
        'σ(Y²)': round(std_y2, 4),
        'Cov(X²,Y²)': round(cov_x2y2, 4),
        'ρ(X²,Y²)': round(rho, 4)
    }
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ ОБОСНОВАНИЕ:
Аналогично билетам 4 и 5, так как распределение идентичное.
"""
    },
    
    7: {
        'code': """
# Билет 7: Анализ дискретного распределения (X,Y)
def solve_ticket7():
    dist = {
        (1,8): 0.12, (3,8): 0.06, (5,8): 0.08,
        (1,9): 0.44, (3,9): 0.29, (5,9): 0.01
    }
    
    # 1. E(X)
    e_x = sum(x * p for (x,y), p in dist.items())
    
    # 2. Var(X)
    e_x2 = sum(x**2 * p for (x,y), p in dist.items())
    var_x = e_x2 - e_x**2
    
    # 3. E(XY)
    e_xy = sum(x*y * p for (x,y), p in dist.items())
    
    # 4. Cov(X,Y)
    e_y = sum(y * p for (x,y), p in dist.items())
    cov_xy = e_xy - e_x * e_y
    
    # 5. ρ(X,Y)
    e_y2 = sum(y**2 * p for (x,y), p in dist.items())
    var_y = e_y2 - e_y**2
    rho = cov_xy / np.sqrt(var_x * var_y)
    
    return {
        'E(X)': round(e_x, 4),
        'Var(X)': round(var_x, 4),
        'E(XY)': round(e_xy, 4),
        'Cov(X,Y)': round(cov_xy, 4),
        'ρ(X,Y)': round(rho, 4)
    }
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ ОБОСНОВАНИЕ:
1. E(XY) = Σx Σy x·y·P(X=x,Y=y)
2. ρ(X,Y) = Cov(X,Y)/(σ_X·σ_Y)
"""
    }
}

def show_solution(ticket_number):
    """Выводит полное решение для билета"""
    if ticket_number not in SOLUTIONS:
        print(f"Решение для билета {ticket_number} не найдено")
        return
    
    print(f"\n{'='*60}\nБИЛЕТ {ticket_number}\n{'='*60}")
    print("\n[ТЕОРЕТИЧЕСКОЕ ОБОСНОВАНИЕ]:")
    print(SOLUTIONS[ticket_number]['theory'])
    print("\n[PYTHON-КОД ДЛЯ ВЫЧИСЛЕНИЙ]:")
    print(SOLUTIONS[ticket_number]['code'])
    print("="*60)

if __name__ == "__main__":
    for i in range(1, 8):
        show_solution(i)