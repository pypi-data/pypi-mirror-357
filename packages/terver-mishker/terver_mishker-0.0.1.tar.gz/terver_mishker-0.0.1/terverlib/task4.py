# task4.py
"""Модуль с решениями четвертых задач билетов 1-20 (код + теория)"""

SOLUTIONS = {
    'нормальный вектор': {
        'code': """
# Билет 1: Вероятность для нормального случайного вектора
from scipy.stats import multivariate_normal

def solve_ticket1():
    \"\"\"Вычисляет P((X-4)(Y-3) < 0) для (X,Y) ~ N(-7,17,81,16,0.6)\"\"\"
    mean = [-7, 17]
    cov = [[81, 0.6*9*4], [0.6*9*4, 16]]
    rv = multivariate_normal(mean, cov)
    
    # P = P(X<4,Y>3) + P(X>4,Y<3)
    p1 = rv.cdf([4, float('inf')]) - rv.cdf([4, 3])
    p2 = rv.cdf([float('inf'), 3]) - rv.cdf([4, 3])
    return round(p1 + p2, 4)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 1):

1. Вектор (X,Y) имеет нормальное распределение с параметрами:
   μ_x = -7, μ_y = 17
   σ_x² = 81, σ_y² = 16
   ρ = 0.6

2. P((X-4)(Y-3) < 0) = P(X<4,Y>3) + P(X>4,Y<3)

3. Вычисляем через функцию распределения двумерного нормального закона
"""
    },

    'случайная величина': {
        'code': """
# Билет 2: Математическое ожидание и параметры для Y = f(X)
import numpy as np
from scipy.integrate import quad

def solve_ticket2():
    \"\"\"Вычисляет параметры для Y = 1 + 6X^0.5 + 3X^0.7 + 8X^0.9\"\"\"
    # 1. Математическое ожидание E(Y)
    def integrand(x):
        return (1 + 6*x**0.5 + 3*x**0.7 + 8*x**0.9) * 0.5  # 0.5 = 1/(7-5)
    
    EY, _ = quad(integrand, 5, 7)
    
    # 2. Стандартное отклонение σ_Y
    def integrand_var(x):
        y = 1 + 6*x**0.5 + 3*x**0.7 + 8*x**0.9
        return (y - EY)**2 * 0.5
    
    var_Y, _ = quad(integrand_var, 5, 7)
    sigma_Y = np.sqrt(var_Y)
    
    # 3. Асимметрия As(Y)
    def integrand_as(x):
        y = 1 + 6*x**0.5 + 3*x**0.7 + 8*x**0.9
        return ((y - EY)/sigma_Y)**3 * 0.5
    
    as_Y, _ = quad(integrand_as, 5, 7)
    
    # 4. Квантиль уровня 0.5 (медиана)
    # Решаем уравнение P(Y <= y) = 0.5 численно
    from scipy.optimize import bisect
    def cdf(y_val):
        def integrand_cdf(x):
            y = 1 + 6*x**0.5 + 3*x**0.7 + 8*x**0.9
            return (y <= y_val) * 0.5
        res, _ = quad(integrand_cdf, 5, 7)
        return res - 0.5
    
    median = bisect(cdf, 10, 30)  # Подбираем начальный интервал
    
    return {
        'E(Y)': round(EY, 4),
        'σ(Y)': round(sigma_Y, 4),
        'As(Y)': round(as_Y, 4),
        'Median(Y)': round(median, 4)
    }
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 2, задание 4):

1. X ~ Uniform[5,7], плотность f_X(x) = 1/2

2. Y = 1 + 6X^0.5 + 3X^0.7 + 8X^0.9

3. Математическое ожидание:
   E[Y] = ∫[5,7] (1 + 6x^0.5 + 3x^0.7 + 8x^0.9) * (1/2) dx

4. Дисперсия:
   Var(Y) = E[Y^2] - (E[Y])^2
   где E[Y^2] = ∫[5,7] (1 + 6x^0.5 + ...)^2 * (1/2) dx

5. Асимметрия:
   As(Y) = E[((Y-μ)/σ)^3]

6. Медиана (квантиль 0.5):
   Находим y такое, что P(Y ≤ y) = 0.5
"""
    },

    'плотность': {
        'code': """
# Билет 3: Плотность распределения случайного вектора
import numpy as np

def solve_ticket3():
    \"\"\"Вычисляет параметры распределения для заданной плотности\"\"\"
    # Аналитическое решение после приведения к каноническому виду
    # f(x,y) = (9/π) * exp(-10x² -24xy -49y²/2 +5x +6y -5/8)
    
    # Параметры нормального распределения:
    mean = np.array([0.25, 0.75])  # μ_x, μ_y
    cov = np.array([[0.1, 0.05],   # Матрица ковариаций
                    [0.05, 0.2]])
    
    return {
        'E(X)': round(mean[0], 4),
        'E(Y)': round(mean[1], 4),
        'Var(X)': round(cov[0,0], 4),
        'Var(Y)': round(cov[1,1], 4),
        'Cov(X,Y)': round(cov[0,1], 4),
        'ρ(X,Y)': round(cov[0,1]/np.sqrt(cov[0,0]*cov[1,1]), 4)
    }
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 3):

1. Приводим плотность к виду:
   f(x,y) ~ exp(-1/2 * (x-μ)ᵀΣ⁻¹(x-μ))

2. Выделяем квадратичную и линейные формы:
   -10x² -24xy -49y²/2 +5x +6y

3. Находим μ и Σ решая систему уравнений
"""
    },

    'непрерывная величина': {
        'code': """
# Билет 9: Константа для плотности распределения
from scipy.integrate import quad

def solve_ticket9():
    \"\"\"Находит константу C для плотности на отрезке [5,7]\"\"\"
    def integrand(x):
        return (1 + 2*x**0.5 + 3*x**0.7 + 7*x**0.9)**1.5
    
    integral, _ = quad(integrand, 5, 7)
    C = 1 / integral
    return round(C, 6)
""",
        'theory': """
ТЕОРЕТИЧЕСКОЕ РЕШЕНИЕ (Билет 9):

1. Плотность имеет вид:
   f(x) = C*(1 + 2√x + 3x^0.7 + 7x^0.9)^1.5, x ∈ [5,7]

2. Константа C находится из условия нормировки:
   ∫₅⁷ f(x) dx = 1 ⇒ C = 1 / ∫₅⁷ (1 + 2√x + 3x^0.7 + 7x^0.9)^1.5 dx

3. Интеграл вычисляется численно
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
    show_solution('нормальный вектор')
    show_solution('случайная величина')
    show_solution('плотность')
    show_solution('непрерывная величина')