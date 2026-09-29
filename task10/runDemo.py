"""
Точка входа для проверки тестового задания.
Запускает расчёты и рисует картинки.
"""

import networkx as nx
import logging
import time

from graphcoloring.SphericalNetwork import SphericalNetwork
from graphcoloring.coloring import (
    convertColoringToRgb,
    graphDistanceColoring,
    graphDistanceColoringDsatur,
    calcMaxColoringDistance, 
    calcMinimumColors
)

import graphcoloring.draw as draw

def demoPlot(nodesCount: int, maxColors: int):
    network = SphericalNetwork(nodesCount)

    colorIndexes, _ = graphDistanceColoring(network.graph, 2, maxColors)
    nodeColors = convertColoringToRgb(colorIndexes)

    nx.set_node_attributes(network.graph, nodeColors, name="color")
    nx.set_node_attributes(network.graph, colorIndexes, name="color index")
    
    network.voronoiMesh.vertexColors = nodeColors
    
    draw.plotNetwork(network)
    
def demoCalc(nodesCount: int, maxColors: int, coloringStrategy: str = 'greedy'):
    network = SphericalNetwork(nodesCount)

    logging.info(f"Построен граф с {nodesCount} вершинами. Максимальная степень вершин: {network.maxNodesDegree}")

    logging.info(f"Запущена процедура со стратегией раскраски '{coloringStrategy}'")
    logging.info("Максимизация расстояния раскраски")
    logging.info("-" * 48)
    maxMinDistance = calcMaxColoringDistance(network.graph, maxColors, coloringStrategy)
    logging.info(("-" * 48) + "\n")

    logging.info("Минимизация количества цветов 2-дистанционной раскраски")
    logging.info("-" * 48)
    twoDistanceColors = calcMinimumColors(network.graph, 2, coloringStrategy)
    logging.info("-" * 48)
    
    return maxMinDistance, twoDistanceColors


def run():
    # Рисуем маленький пример. (Рисование больших примеров занимает много времени)
    demoPlot(100, 20)


    # Запуск двух маленьких примеров для сравнения жадного алгоритма и DSATUR
    # Запуск жадного алгоритма
    start = time.perf_counter()
    maxMinDistance, twoDistanceColors = demoCalc(
        nodesCount = 100, 
        maxColors = 20, 
        coloringStrategy = "greedy"
    )
    end = time.perf_counter()
    logging.info(
        f"""Процедура со 100 точками и 20 цветами исполнена за: {end - start:.6f} сек.
        Максимизированное минимальное расстояние между вершинами разного цвета: {maxMinDistance}
        Минимальное количество цветов для 2-дистанционной раскраски: {twoDistanceColors}
        """)
    # Вывод: maxMinDistance, twoDistanceColors = 2, 13
    # Максимальная степень вершин: 7

    # Запуск алгоритма DSATUR
    start = time.perf_counter()
    maxMinDistance, twoDistanceColors = demoCalc(
        nodesCount = 100, 
        maxColors = 20, 
        coloringStrategy = "DSATUR"
    )
    end = time.perf_counter()
    logging.info(
        f"""Процедура со 100 точками и 20 цветами исполнена за: {end - start:.6f} сек.
        Максимизированное минимальное расстояние между вершинами разного цвета: {maxMinDistance}
        Минимальное количество цветов для 2-дистанционной раскраски: {twoDistanceColors}
        """)
    # Вывод: maxMinDistance, twoDistanceColors = 2, 12
    # Максимальная степень вершин: 7
    # Как видим, DSATUR даёт результат лучше чем greedy, но он требует больше времени


    # Запуск алгоритма на больших данных
    start = time.perf_counter()
    maxMinDistance, twoDistanceColors = demoCalc(
        nodesCount = 64000, 
        maxColors = 1008, 
        coloringStrategy = "greedy"
    )
    end = time.perf_counter()
    logging.info(
        f"""Процедура со 100 точками и 20 цветами исполнена за: {end - start:.6f} сек.
        Максимизированное минимальное расстояние между вершинами разного цвета: {maxMinDistance}
        Минимальное количество цветов для 2-дистанционной раскраски: {twoDistanceColors}
        """)
    # Вывод: maxMinDistance, twoDistanceColors = 23, 14
    # Максимальная степень вершин: 7



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    run()