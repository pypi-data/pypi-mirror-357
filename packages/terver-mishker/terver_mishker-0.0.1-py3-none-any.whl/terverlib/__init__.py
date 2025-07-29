"""
Пакет terverlib для решения задач по теории вероятностей.

Доступные модули:
- task1: Решения задач билетов 1-20 (код + теория)
- task2: Решения задач билетов 21-40
- task3: Решения задач билетов 41-60
- task4: Решения задач билетов 61-80
- task5: Решения задач билетов 81-100
- task6: Дополнительные утилиты и функции
"""

from .task1 import show_solution as show1
from .task2 import show_solution as show2
from .task3 import show_solution as show3
from .task4 import show_solution as show4
from .task5 import show_solution as show5
from .task6 import show_solution as show6

# Упрощенный доступ ко всем функциям
__all__ = ['show1', 'show2', 'show3', 'show4', 'show5', 'show6']

# Версия пакета
__version__ = '0.0.1'