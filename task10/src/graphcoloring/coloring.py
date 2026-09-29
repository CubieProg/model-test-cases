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



def calcGraphSphere(graph: nx.Graph, center: int, radius: int, punctured: bool = True) -> set[int]:
    """Фнкция расчёта сферы в графе `graph` радиуса `radius` с центорм в вершине `center`.

    Если параметер `punctured` равен `True`, то функция вернёт тот же результат, но без центра.

    Parameters
    ----------
    graph : networkx.Graph
        Граф, в котором нужно найти сферу
    center : int 
        Номер центральной вершины в графе `graph`
    radius : int
        Радиус сферы
    punctured : bool
        Если `True`, то вернёт сферу без центра.

    Returns
    -------
    sphere : set[int]
        Сфера в графе `graph` радиуса `radius` с центром в вершине `center`
    
    Raises
    ------
    NodeNotFound
        В случае, если указанной вершины `center` нет в графе `graph`

    TypeError
        В случае, если `graph` не объект класса `networkx.Graph`.

    Note
    ------
    В качестве параметра `radius` можно подать произвольный `float`. 
    В таком случае, результат функции будет аналогичен, если подать `int(radius)`.
    Если `radius < 0`, то вернёт пустое множество в независимости от параметра `punctured`.
    """

    sphere = nx.single_source_shortest_path_length(graph, center, radius)
    sphere = set(sphere.keys())

    if punctured and center in sphere:
        sphere.remove(center)
    return sphere



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
    Для `distance`-дистанционной раскраски графа, 
    алгоритм на каждом шаге считает сферы радиуса `distance` вокруг текущей врешины.
    """
    

    # Жадный алгоритм идёт от вершин с большей степенью к вершинам с меньшей
    sortedNodes = sorted(graph.nodes(), key=lambda n: graph.degree(n), reverse=True)

    # Сопоставление вершина: номер цвета
    coloring = dict()
    for node in sortedNodes:
        sphere = calcGraphSphere(graph, node, distance)
        coloredNeighbors = {coloring[neighbor] for neighbor in sphere if neighbor in coloring}

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
    Для `distance`-дистанционной раскраски графа, 
    алгоритм на каждом шаге считает сферы радиуса `distance` вокруг текущей врешины.
    """
    
    # Сопоставление вершина: номер цвета
    coloring = dict()
    uncoloredNodes = set(graph.nodes()) # Можно обойтись и без этого множества. 
                                    # Но, на каждой итерации цикла его нужно бедет высчитывать.

    # DSATUR идёт по убыванию степени насыщения
    # Функция считает степень насыщения для поданой вершины 
    def saturationDegree(node: int, distance: int):
        sphere = calcGraphSphere(graph, node, distance)
        neighborColors = {v for k, v in coloring.items() if k in sphere}
        return len(neighborColors)

    def distanceDegree(node: int, distance: int):
        sphere = calcGraphSphere(graph, node, distance)
        return len(sphere)

    while True:
        if len(coloring) == len(graph.nodes):
            break

        # Выбираем вершину с максимальной степенью насыщения. Потом с максимальной степенью в графе
        maxSaturationNode = max(uncoloredNodes, key= lambda n: saturationDegree(n, distance))
        maxSaturation = saturationDegree(maxSaturationNode, distance)
        maxSaturatedNodes = [node for node in uncoloredNodes if saturationDegree(node, distance) == maxSaturation]

        # currentNode = max(maxSaturatedNodes, key=lambda node: graph.degree[node])
        currentNode = max(maxSaturatedNodes, key=lambda node: distanceDegree(node, distance))


        # currentNode = max(
        #     uncoloredNodes,
        #     key = lambda node: (saturationDegree(node), graph.degree(node))
        # )

        # Ищем доступные цвета
        sphere = calcGraphSphere(graph, currentNode, distance)
        neighborColors = {v for k, v in coloring.items() if k in sphere}
        availableColors = set(range(maxColors)).difference(neighborColors)

        # Если доступного цвета нет, то нельзя раскрасить граф в maxColors цветов
        if len(availableColors) == 0:
            raise ColoringError(f"{maxColors} цветов не достаточно для раскраски графа!", maxColors)

        coloring[currentNode] = min(availableColors)
        uncoloredNodes.remove(currentNode)

    usedColors = max(coloring.values())
    usedColors += 1

    # testData = dict()
    # for node in graph.nodes():
    #     sphere = calcGraphSphere(graph, node, 2, False)
    #     colorsInSphere = {n: coloring[n] for n in sphere}
    #     testData[node] = colorsInSphere
    #     ...

        
    # # testData[0]
    # # calcGraphSphere(graph, 6, 2, False)
    
    # checkCorrectivity(graph, coloring, distance)
    return coloring, usedColors


def checkCorrectness(graph: nx.Graph, coloring: dict, distance: int):
    for node in graph.nodes():
        sphere = calcGraphSphere(graph, node, distance)
        nodeColor = coloring[node]
        conflictColors = {coloring[node] for node in sphere}

        if nodeColor in conflictColors:
            return False
        
    return True

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
            _, usedColors = strategy(graph, distance, maxColors)
            logging.debug(f"Можно покрасить в {maxColors} цветов на дистанции {distance}")
            
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
    return distance



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