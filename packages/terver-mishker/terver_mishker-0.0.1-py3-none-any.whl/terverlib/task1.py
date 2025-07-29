# task1.py
"""Модуль с решениями первых задач билетов 1-20 (код + теория с интегралами)"""

SOLUTIONS = {
    'эллипс': {
        'code': """
# Билет 1: Две точки в эллипсе (Метод Монте-Карло)
import numpy as np

def solve_ticket1(trials=100000):
    \"\"\"Вычисляет:
    1) P(расстояние между точками < 5.2)
    2) P(расстояние < 5.2 | все координаты < 0)
    \"\"\"
    a, b = np.sqrt(13), 3
    u = np.random.uniform(-a, a, trials)
    v = np.random.uniform(-b, b, trials)
    mask = (u**2/13 + v**2/9) <= 1
    u, v = u[mask], v[mask]
    
    pairs = np.random.choice(len(u), (trials, 2))
    dist = np.hypot(u[pairs[:,0]]-u[pairs[:,1]], v[pairs[:,0]]-v[pairs[:,1]])
    
    p_a = np.mean(dist < 5.2)
    mask_b = (u[pairs[:,0]]<0) & (u[pairs[:,1]]<0) & (v[pairs[:,0]]<0) & (v[pairs[:,1]]<0)
    p_ab = np.mean(dist[mask_b] < 5.2)
    
    return round(p_a, 3), round(p_ab, 3)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 1):

1. Совместная плотность распределения двух точек в эллипсе:
   f(x₁,y₁,x₂,y₂) = (1/(πab))² = 1/(9π²·13)

2. Вероятность P(ρ < 5.2):
   P = ∫∫∫∫_{D} f(x₁,y₁,x₂,y₂) dx₁dy₁dx₂dy₂
   где D = {(x₁,y₁,x₂,y₂) | √[(x₂-x₁)²+(y₂-y₁)²] < 5.2}

3. Условная вероятность P(A|B):
   P = ∫∫∫∫_{D∩B} f(x₁,y₁,x₂,y₂) dx₁dy₁dx₂dy₂ / ∫∫∫∫_{B} f(x₁,y₁,x₂,y₂) dx₁dy₁dx₂dy₂
   где B = {x₁<0, y₁<0, x₂<0, y₂<0}
"""
    },
    
    'прямоугольник': {
        'code': """
# Билет 3: Две точки в прямоугольнике
import numpy as np

def solve_ticket3(trials=100000):
    \"\"\"Вычисляет:
    1) P(расстояние < 6.4)
    2) P(расстояние < 6.4 | |x₁-x₂| < 14)
    \"\"\"
    x = np.random.uniform(-20, 20, (trials, 2))
    y = np.random.uniform(-12, 12, (trials, 2))
    
    dist = np.hypot(x[:,0]-x[:,1], y[:,0]-y[:,1])
    dx = np.abs(x[:,0]-x[:,1])
    
    p_a = np.mean(dist < 6.4)
    mask_b = dx < 14
    p_ab = np.mean(dist[mask_b] < 6.4)
    
    return round(p_a, 3), round(p_ab, 3)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 3):

1. Совместная плотность в прямоугольнике:
   f(x₁,y₁,x₂,y₂) = (1/960)² = 1/921600

2. Вероятность P(ρ < 6.4):
   P = ∫_{-20}^{20} ∫_{-12}^{12} ∫_{-20}^{20} ∫_{-12}^{12} 
       I[√[(x₂-x₁)²+(y₂-y₁)²] < 6.4] f(x₁,y₁,x₂,y₂) dy₂dx₂dy₁dx₁

3. Условная вероятность:
   P = ∫∫∫∫_{|x₁-x₂|<14} I[ρ < 6.4] f(x₁,y₁,x₂,y₂) dx₁dy₁dx₂dy₂ / 
       P(|x₁-x₂| < 14)
"""
    },
    
    'банки': {
        'code': """
# Билет 4: Проблемные банки
from scipy.stats import hypergeom

def solve_ticket4():
    \"\"\"Вычисляет P(хотя бы 1 проблемный банк из 3)\"\"\"
    return round(1 - hypergeom.pmf(0, 25, 12, 3), 4)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 4):

Комбинаторное решение без интегралов:
P = 1 - C(12,3)/C(25,3) = 1 - 220/2300 ≈ 0.904
"""
    },
    
    'вагоны': {
        'code': """
# Билет 5: Люди в вагонах
def solve_ticket5():
    \"\"\"Вычисляет P(хотя бы 2 человека в одном вагоне)\"\"\"
    return round(1 - (11*10*9*8)/(11**4), 3)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 5):

Комбинаторное решение:
P = 1 - 11×10×9×8/11⁴ = 1 - 7920/14641 ≈ 0.459
"""
    },
    
    'шары': {
        'code': """
# Билет 7: Вероятность белого шара
def solve_ticket7():
    \"\"\"Вычисляет:
    1) P(белый шар в 3-й корзине)
    2) P(шар из 1-й корзины | белый)
    \"\"\"
    white1 = 5*(13/28)
    white2 = 10*(17/37)
    p_a = (white1 + white2)/15
    p_ha = white1/(white1 + white2)
    return round(p_a, 3), round(p_ha, 3)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 7):

1. Вероятность вынуть белый из 1-й корзины:
   P₁ = C(13,1)/C(28,1) = 13/28
   Ожидаемое число белых при выборе 5 шаров: 5*(13/28) ≈ 2.32

2. Вероятность вынуть белый из 2-й корзины:
   P₂ = C(17,1)/C(37,1) = 17/37
   Ожидаемое число белых при выборе 10 шаров: 10*(17/37) ≈ 4.59

3. Итоговая вероятность:
   P = (2.32 + 4.59)/15 ≈ 0.461
   P(из 1-й|белый) = 2.32/(2.32 + 4.59) ≈ 0.336
"""
    },
    
    'треугольник': {
        'code': """
# Билет 8: Остроугольные треугольники (Монте-Карло)
import numpy as np

def solve_ticket8(trials=100000):
    \"\"\"Вычисляет для остроугольных треугольников:
    1) P(есть угол <35.6°)
    2) P(все углы <68.4°)
    \"\"\"
    edge = 3**(1/3)
    count_r = count_s = total = 0
    
    for _ in range(trials):
        points = np.random.uniform(0, edge, (3, 3))
        vectors = points - np.roll(points, 1, axis=0)
        dots = np.sum(vectors * np.roll(vectors, -1, axis=0), axis=1)
        norms = np.linalg.norm(vectors, axis=1) * np.linalg.norm(np.roll(vectors, -1, axis=0), axis=1)
        angles = np.arccos(dots/norms) * 180/np.pi
        
        if all(angles < 90):  # Остроугольный
            total += 1
            if any(angles < 35.6):
                count_r += 1
            if all(angles < 68.4):
                count_s += 1
    
    return round(count_r/total, 2), round(count_s/total, 2)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 8):

1. Объем куба: V = 3 → ребро a = 3^(1/3) ≈ 1.442

2. Вероятность для остроугольного треугольника:
   P = ∫∫∫_{T} I[все углы <90°] dx₁dy₁dz₁dx₂dy₂dz₂dx₃dy₃dz₃ / V³
   где T - пространство всех треугольников

3. Условные вероятности вычисляются через отношение объемов
"""
    },
    
    'бином': {
        'code': """
# Билет 12: Биномиальное распределение шаров
def solve_ticket12():
    \"\"\"Вычисляет:
    1) P(белый шар)
    2) P(из 1-й корзины | белый)
    \"\"\"
    white1 = 7*0.3  # Биномиальное распределение
    white2 = 5*0.5
    p_a = (white1 + white2)/18
    p_ha = white1/(white1 + white2)
    return round(p_a, 3), round(p_ha, 3)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 12):

1. Ожидаемое число белых в 1-й корзине:
   E = 7*0.3 = 2.1

2. Ожидаемое число белых во 2-й корзине:
   E = 5*0.5 = 2.5

3. Итоговая вероятность:
   P = (2.1 + 2.5)/18 ≈ 0.256
   P(из 1-й|белый) = 2.1/(2.1 + 2.5) ≈ 0.457
"""
    }
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
    show_solution('эллипс')
    show_solution('прямоугольник')
    show_solution('банки')
    show_solution('вагоны')
    show_solution('шары')
    show_solution('треугольник')
    show_solution('бином')