# task2.py
"""Модуль с решениями вторых задач билетов 1-20 (код + теория с интегралами)"""

SOLUTIONS = {
    'индикаторы': {
        'code': """
# Билет 1: События A, B, C и индикаторы
def solve_ticket1():
    \"\"\"Вычисляет:
    1) E(U) = E(3X + 7Y + 2Z)
    2) Var(U) = Var(3X + 7Y + 2Z)
    \"\"\"
    p_a, p_b, p_c = 0.1, 0.4, 0.3
    
    # Мат. ожидание
    e_u = 3*p_a + 7*p_b + 2*p_c
    
    # Дисперсия (с учетом попарной независимости)
    var_u = 9*p_a*(1-p_a) + 49*p_b*(1-p_b) + 4*p_c*(1-p_c)
    
    return round(e_u, 3), round(var_u, 3)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 1):

1. Математическое ожидание:
   E(U) = 3E(X) + 7E(Y) + 2E(Z) = 3P(A) + 7P(B) + 2P(C) = 3*0.1 + 7*0.4 + 2*0.3

2. Дисперсия:
   Var(U) = 9Var(X) + 49Var(Y) + 4Var(Z) 
   = 9P(A)(1-P(A)) + 49P(B)(1-P(B)) + 4P(C)(1-P(C))
   (ковариации = 0 из-за попарной независимости)
"""
    },
    
    'контракты': {
        'code': """
# Билет 2: Доход по контрактам
def solve_ticket2():
    \"\"\"Вычисляет:
    1) E(среднего дохода по 9 контрактам)
    2) Var(среднего дохода по 9 контрактам)
    \"\"\"
    # Находим недостающую вероятность P(X=8) = 1 - (0.2+0.2+0.3+0.1) = 0.2
    x = [5, 8, 9, 10, 11]
    p = [0.2, 0.2, 0.2, 0.3, 0.1]
    
    e_x = sum(xi*pi for xi, pi in zip(x, p))
    e_x2 = sum(xi**2*pi for xi, pi in zip(x, p))
    var_x = e_x2 - e_x**2
    
    # Для среднего по 9 контрактам
    e_avg = e_x
    var_avg = var_x / 9
    
    return round(e_avg, 3), round(var_avg, 3)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 2):

1. Находим P(X=8) = 1 - Σ других вероятностей = 0.2

2. Мат. ожидание:
   E(X) = Σ x_i*p_i = 5*0.2 + 8*0.2 + 9*0.2 + 10*0.3 + 11*0.1

3. Дисперсия:
   Var(X) = E(X²) - [E(X)]² 
   = 25*0.2 + 64*0.2 + 81*0.2 + 100*0.3 + 121*0.1 - E(X)²

4. Для среднего по 9 контрактам:
   E(avg) = E(X)
   Var(avg) = Var(X)/9
"""
    },
    
    'акции': {
        'code': """
# Билет 4: Цена акции после 150 дней
import numpy as np

def solve_ticket4():
    \"\"\"Вычисляет:
    1) E(S150)
    2) Std(S150)
    \"\"\"
    s0 = 1000
    changes = [0.05, 0.003, -0.01]
    probs = [0.1, 0.4, 0.5]
    
    # Логарифмическая доходность
    log_returns = [np.log(1 + c) for c in changes]
    e_log = sum(p*r for p, r in zip(probs, log_returns))
    var_log = sum(p*(r**2) for p, r in zip(probs, log_returns)) - e_log**2
    
    # Преобразуем к S150
    e_s = s0 * np.exp(150 * e_log + 150 * var_log / 2)
    std_s = e_s * np.sqrt(np.exp(150 * var_log) - 1)
    
    return round(e_s, 2), round(std_s, 2)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 4):

1. Модель геометрического броуновского движения:
   S_t = S0 * exp(Σ log(1 + R_i))

2. Мат. ожидание:
   E[S150] = S0 * exp(n*μ + n*σ²/2), где n=150

3. Дисперсия:
   Var(S150) = S0² * exp(2nμ + nσ²) * (exp(nσ²) - 1)
"""
    },
    
    'квантили': {
        'code': """
# Билет 5: Квантили для Y = |X - 17.5|
def solve_ticket5():
    \"\"\"Вычисляет квантили для Y\"\"\"
    # X равномерна на 1..40 (40 значений)
    y_values = sorted([abs(x - 17.5) for x in range(1, 41)])
    
    # Q1Min: P(Y <= q) >= 0.25
    q1min = y_values[9]  # 10-й элемент (индекс 9) для 25%
    
    # Q1Max: P(Y >= q) >= 0.75 => P(Y <= q) <= 0.25
    q1max = y_values[9]
    
    # Q3Min: P(Y <= q) >= 0.75
    q3min = y_values[29]  # 30-й элемент для 75%
    
    # Q3Max: P(Y >= q) >= 0.25 => P(Y <= q) <= 0.75
    q3max = y_values[29]
    
    return q1min, q1max, q3min, q3max
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 5):

1. X ~ Uniform(1, 2, ..., 40)
   Y = |X - 17.5|

2. Квантили находятся по точным значениям:
   - Q1Min: минимальное y, где P(Y ≤ y) ≥ 0.25
   - Q1Max: максимальное y, где P(Y ≥ y) ≥ 0.75
   - Q3Min: минимальное y, где P(Y ≤ y) ≥ 0.75
   - Q3Max: максимальное y, где P(Y ≥ y) ≥ 0.25
"""
    },
    
    'попадание': {
        'code': """
# Билет 6: Попадание в фигуры (треугольник и круг)
def solve_ticket6():
    \"\"\"Вычисляет характеристики для U и V\"\"\"
    p_triangle = 44/100
    p_circle = 40/100
    p_intersect = 20/100
    
    # Вероятности для Z = X + Y
    p_z0 = 1 - p_triangle - p_circle + p_intersect
    p_z1 = p_triangle + p_circle - 2*p_intersect
    p_z2 = p_intersect
    
    # Для U = Z1 + Z2 + Z3
    e_u = 3 * (1*p_z1 + 2*p_z2)
    var_u = 3 * (1**2*p_z1 + 2**2*p_z2 - (1*p_z1 + 2*p_z2)**2)
    
    # Для V = Z1*Z2*Z3
    e_v = (p_z2)**3
    var_v = e_v - e_v**2
    
    return round(e_u, 3), round(var_u, 3), round(e_v, 5), round(var_v, 5)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 6):

1. Вероятности для Z:
   P(Z=0) = P(не попал ни в одну фигуру)
   P(Z=1) = P(попал только в треугольник или только в круг)
   P(Z=2) = P(попал в обе фигуры)

2. U = ΣZi:
   E[U] = 3E[Zi]
   Var(U) = 3Var(Zi)

3. V = ΠZi:
   E[V] = E[Z1]^3
   Var(V) = E[V^2] - E[V]^2
"""
    },

    'случай': {
        'code': """
# Билет 8: Характеристики Y = |X - 10|
def solve_ticket8():
    \"\"\"Вычисляет:
    1) E(X), E(Y), E(XY)
    2) Var(X), Var(Y)
    \"\"\"
    x = [2, 6, 9, 13, 15]
    p = [0.1, 0.2, 0.2, 0.3, 0.2]
    
    e_x = sum(xi*pi for xi, pi in zip(x, p))
    e_x2 = sum(xi**2*pi for xi, pi in zip(x, p))
    var_x = e_x2 - e_x**2
    
    y = [abs(xi - 10) for xi in x]
    e_y = sum(yi*pi for yi, pi in zip(y, p))
    e_y2 = sum(yi**2*pi for yi, pi in zip(y, p))
    var_y = e_y2 - e_y**2
    
    e_xy = sum(xi*yi*pi for xi, yi, pi in zip(x, y, p))
    
    return (round(e_x, 3), round(e_y, 3), round(e_xy, 3), 
            round(var_x, 3), round(var_y, 3))
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 8):

1. Мат. ожидания:
   E[X] = Σx_i*p_i
   E[Y] = Σ|x_i - 10|*p_i
   E[XY] = Σx_i*|x_i - 10|*p_i

2. Дисперсии:
   Var(X) = E[X²] - E[X]²
   Var(Y) = E[Y²] - E[Y]²
"""
    },
    

}

def show_solution(ticket_number:str):
    """Выводит полное решение для билета"""
    if ticket_number not in SOLUTIONS:
        print(f"Решение для билета {ticket_number} не найдено")
        return
    
    print(f"\n{'='*60}\nБИЛЕТ {ticket_number}\n{'='*60}")
    print("\n[ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ]:")
    print(SOLUTIONS[ticket_number]['theory'])
    print("\n[PYTHON-КОД ДЛЯ ВЫЧИСЛЕНИЙ]:")
    print(SOLUTIONS[ticket_number]['code'])
    print("="*60)

# Автоматический вывод при импорте
if __name__ != "__main__":
    print("\nДОСТУПНЫЕ РЕШЕНИЯ ДЛЯ БИЛЕТОВ:", list(SOLUTIONS.keys()))
    print("Используйте show_solution(номер_билета) для просмотра\n")

# Пример использования:
if __name__ == "__main__":
    for ticket in sorted(SOLUTIONS.keys()):
        show_solution(ticket)