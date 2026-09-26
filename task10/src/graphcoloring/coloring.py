"""
coloring
------

Модуль, предоставляющий методы раскраски графов и оптимизации раскрасок

Алгоритмы раскрасок из `networkx` не используются т.к. им нельзя задать ограничение на максимальное количество цветов.
"""

import logging
import networkx as nx
import math
from matplotlib.pyplot import get_cmap
from typing import Dict, Tuple
from collections.abc import Callable


class ColoringError(Exception):
    def __init__(self, message, colors):   
        super().__init__(message)
        self.colors = colors


def convertColoringToRgb(coloring: Dict[int, int]) -> Dict[int, Tuple]:
    """Функция конвертирует словарь `{номерВершины: номерЦвета}` в словарь `{номерВершины: (r, g, b)}`

    Parameters
    ----------
    coloring : Dict[int, int]
        Словарь сопоставляющий номер_вершины -> номер_цвета
        
    Returns
    -------
    nodeRgbColors : Dict[int, Tuple[float, float, float]]
        Словарь сопоставляющий номер_вершины -> кортеж rgb цвета
    """

    cmap = get_cmap('gist_rainbow')

    colorsCount = len(set(coloring.values()))
    nodeRgbColors = {k: cmap(v / max(1, colorsCount - 1)) for (k, v) in coloring.items()}

    return nodeRgbColors



def graphDistanceColoring(graph: nx.Graph, distance: int, maxColors: int) -> Tuple[Dict, int]:
    """Жадный алгоритм раскраски.

    Возвращает `distance`-дистанционную раскраску графа `graph` с не более чем `maxColors` цветами.

    Parameters
    ----------
    graph : networkx.Graph
        Граф, который нужно раскрасить
    distance : int
        Дистанция раскраски графа
    maxColors : int
        Максимальное допустимое количество цветов

    Returns
    -------
    coloring : Dict[int, int]
        Словарь сопоставляющий номер_вершины -> номер_цвета
    usedColors : int
        Использованное количество цветов
    
    Raises
    ------
    ColoringError
        В случае, если указанного `maxColors` не хватает для `distance`-дистанционной раскраска графа,
        в том числе, если `maxColors` < 0.

    TypeError
        В случае, если `maxColors` не `int`.

    ValueError
        В случае, если `distance` < 0.


        
    Note
    ------
    Для `distance`-дистанционной раскраски графа, изначальный `graph` возводится в степень `distance` 
    и раскрашивается уже степень графа обычным методом. 

    Описание корректности этого подхода смотри в 
    "МИНИМАЛЬНЫЕ СТЕПЕНИ И ХРОМАТИЧЕСКИЕ ЧИСЛА КВАДРАТОВ ПЛОСКИХ ГРАФОВ" 
    О. В. Бородин, X. Брусма, А. Н. Глебов, Я. ван ден Хойвел, стр. 2, абзацы 2-3.
    """
    
    G: nx.Graph = nx.power(graph, distance)

    # Жадный алгоритм идёт от вершин с большей степенью к вершинам с меньшей
    sortedNodes = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)

    # Сопоставление вершина: номер цвета
    coloring = dict()
    for node in sortedNodes:
        coloredNeighbors = {coloring[neighbor] for neighbor in G.neighbors(node) if neighbor in coloring}

        # Ищем первый доступный цвет меньший чем maxColors
        for colorIndex in range(maxColors):
            if colorIndex not in coloredNeighbors:
                coloring[node] = colorIndex
                break
        else:
            raise ColoringError(f"{maxColors} colors is not enough!", maxColors)

    usedColors = max(coloring.values())
    usedColors += 1

    return coloring, usedColors



def graphDistanceColoringDsatur(graph: nx.Graph, distance: int, maxColors: int) -> Tuple[Dict, int]:
    """Алгоритм раскраски **DSATUR**
    
    Возвращает `distance`-дистанционную раскраску графа `graph` с не более чем `maxColors` цветами.

    Parameters
    ----------
    graph : networkx.Graph
        Граф, который нужно раскрасить
    distance : int
        Дистанция раскраски графа
    maxColors : int
        Максимальное допустимое количество цветов

    Returns
    -------
    coloring : Dict[int, int]
        Словарь сопоставляющий номер_вершины -> номер_цвета
    usedColors : int
        Использованное количество цветов
        
    Raises
    ------
    ColoringError
        В случае, если указанного `maxColors` не хватает для `distance`-дистанционной раскраска графа,
        в том числе, если `maxColors` < 0.

    TypeError
        В случае, если `maxColors` не `int`.

    ValueError
        В случае, если `distance` < 0.

    Note
    ------
    Для `distance`-дистанционной раскраски графа, изначальный `graph` возводится в степень `distance` 
    и раскрашивается уже степень графа обычным методом. 

    Описание корректности этого подхода смотри в 
    "МИНИМАЛЬНЫЕ СТЕПЕНИ И ХРОМАТИЧЕСКИЕ ЧИСЛА КВАДРАТОВ ПЛОСКИХ ГРАФОВ" 
    О. В. Бородин, X. Брусма, А. Н. Глебов, Я. ван ден Хойвел, стр. 2, абзацы 2-3.
    """

    G: nx.Graph = nx.power(graph, distance)

    # Сопоставление вершина: номер цвета
    coloring = dict()
    uncoloredNodes = set(G.nodes()) # Можно обойтись и без этого множества. 
                                    # Но, на каждой итерации цикла его нужно бедет высчитывать.

    # DSATUR идёт по убыванию степени насыщения
    # Функция считает степень насыщения для вершины
    def saturationDegree(node: int):
        neighborColors = {v for k, v in coloring.items() if k in G.neighbors(node)}
        return len(neighborColors)

    while True:
        if len(coloring) == len(G.nodes):
            break

        # Выбираем вершину с максимальной степенью насыщения. Потом с максимальной степенью в графе
        maxSaturation = max(uncoloredNodes, key=saturationDegree)
        maxSaturation = saturationDegree(maxSaturation)
        maxSaturatedNodes = [node for node in uncoloredNodes if saturationDegree(node) == maxSaturation]
        
        currentNode = max(maxSaturatedNodes, key=lambda node: G.degree[node])

        # Ищем доступные цвета
        neighborColors = {v for k, v in coloring.items() if k in G.neighbors(currentNode)}
        availableColors = set(range(maxColors)).difference(neighborColors)

        # Если доступного цвета нет, то нельзя раскрасить граф в maxColors цветов
        if len(availableColors) == 0:
            raise ColoringError(f"{maxColors} цветов не достаточно для раскраски графа!", maxColors)

        coloring[currentNode] = min(availableColors)
        uncoloredNodes.remove(currentNode)

    usedColors = max(coloring.values())
    usedColors += 1
    
    return coloring, usedColors


STRATEGIES = {
    "greedy": graphDistanceColoring,
    "DSATUR": graphDistanceColoringDsatur
}



def calcMaxColoringDistance(graph: nx.Graph, maxColors: int, 
                            strategyName: str = "greedy") -> int:
    """Возвращает максимальное число `N` такое, 
    что граф `graph` может быть раскрашен `N`-дистанционной раскраской в не более чем `maxColors` цвета

    Parameters
    ----------
    graph : networkx.Graph
        Граф, который нужно раскрасить
    maxColors : int
        Максимальное допустимое количество цветов
    coloringStrategy : str
        Имя стратегии раскрашивания. Доступны только `'greedy'` и `'DSATUR'`. По умолчанию используется `'greedy'`.

    Returns
    -------
    distance : int
        Максимальное расстояние раскраски графа

    Raises
    ------
    ValueError
        В случае, если указанная `strategyName` не равна `'greedy'` или `'DSATUR'`
        
    Notes
    -----
    Алгоритм сначала определяет верхнюю границу для `distance` расширяющимся поиском. 
    После чего бинарным поиском находит точное значение `distance`.

    Таким образом, функция максимизирует минимальное растояние между вершинами с одинаковыми цветами.
    """

    # Проверяем валидность стратегии
    if not strategyName in STRATEGIES:
        availableStrategies = ", ".join(name for name in list(STRATEGIES.keys())) 
        raise ValueError(
            f"Стратегия раскрашивания {strategyName} не доступна. Доступные варианты: {availableStrategies}")

    strategy = STRATEGIES.get(strategyName)

    distance = 1
    usedColors = 0

    # Изначально, diameter был одним из критериев остановки (где distance >= len (graph.nodes()))
    # Однако, расчёт диаметра для графов с более 10000 вершинами занимал больше времени чем основные расчёты
    # diameter = nx.diameter(graph) 
    
    memoizedGraph = graph.copy()
    
    # Расширяющийся поиск верхней оценки для расстояния
    logging.debug(f"--- Расширяющийся поиск ---")
    while True:
        try:
            _, usedColors = strategy(memoizedGraph, 1, maxColors)
            logging.debug(f"Можно покрасить в {maxColors} цветов на дистанции {distance}")
            memoizedGraph = nx.power(memoizedGraph, 2)
            distance *= 2
        except ColoringError as e:
            logging.debug(f"Нельзя покрасить в {maxColors} цветов на дистанции {distance}")
            break

        if distance >= len(graph.nodes()):
            logging.info(f"Очень много ({maxColors}) цветов. Граф может быть раскрашен на любой дистанции")
            return len(graph.nodes())

    # Бинарный поиск точного расстояния
    logging.debug(f"--- Бинарный поиск ---")
    lowerBoundary = distance / 2
    upperBoundary = distance
    
    while True:
        center = math.floor((lowerBoundary + upperBoundary) / 2)
        if center == distance:
            break
        
        distance = center

        try:
            # Можем -> повышаем нижнюю границу
            _, usedColors = strategy(graph, distance, maxColors)
            lowerBoundary = distance
            logging.debug(f"Можно покрасить в {maxColors} цветов на дистанции {distance}")
        except ColoringError as e:
            # Не можем -> понижаем верхнюю границу
            logging.debug(f"Нельзя покрасить в {maxColors} цветов на дистанции {distance}")
            upperBoundary = distance

    logging.debug(f"--- Рузультат ---")
    logging.debug(f"Граф можно раскрасить в {usedColors} из {maxColors} цветов на дистанции {distance}")
    return distance #, nodeColors, coloring, usedColors



def calcMinimumColors(graph: nx.Graph, distance: int, 
                      strategyName: str = "greedy") -> int:
    """Возвращает минимальное число `N` такое, 
    что граф `graph` может быть раскрашен `distance`-дистанционной раскраской в `N` цвета

    Parameters
    ----------
    graph : networkx.Graph
        Граф, который нужно раскрасить
    distance : int
        Дистанция раскраски
    coloringStrategy : Callable
        Стратегия раскрашивания. Доступны только `graphDistanceColoring` и `graphDistanceColoringDsatur`

    Returns
    -------
    usedColors : int
        Количество использованныйх цветов для раскраски

    Raises
    ------
    ValueError
        В случае, если указанная `strategyName` не равна `'greedy'` или `'DSATUR'`
        
    Notes
    -----
    Метод находит верхнюю границу для `usedColors` расширяющимся поиском. 
    Точное значение `usedColors` возвращается методом, указанным в `coloringStrategy`.

    Таким образом, функция вычисляет верхнюю оценку минимального количества цветов 
    для `distance`-дистанционной раскраски.
    """

    # Проверяем валидность стратегии
    if not strategyName in STRATEGIES:
        availableStrategies = ", ".join(name for name in list(STRATEGIES.keys())) 
        raise ValueError(
            f"Стратегия раскрашивания {strategyName} не доступна. Доступные варианты: {availableStrategies}")

    strategy = STRATEGIES.get(strategyName)


    maxColors = 1
    usedColors = 0

    # Расширяющийся поиск верхней оценки для количества цветов
    logging.debug(f"--- Расширяющийся поиск ---")
    while True:
        try:
            _, usedColors = strategy(graph, distance, maxColors)
            logging.debug(f"Можно покрасить в {maxColors} цветов на дистанции {distance}")
            break
        except ColoringError as e:
            logging.debug(f"Нельзя покрасить в {maxColors} цветов на дистанции {distance}")
            maxColors *= 2

    logging.debug(f"--- Рузультат ---")
    logging.debug(f"Графу достаточно {usedColors} из {maxColors} цветов для {distance}-дистанционной раскраски")
    
    return usedColors