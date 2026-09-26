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


def run(nodesCount: int, maxColors: int, isPlotNeeded: bool = False, 
        coloringStrategy: str = 'greedy'):

    network = SphericalNetwork(nodesCount)

    colorIndexes, _ = graphDistanceColoring(network.graph, 2, maxColors)
    nodeColors = convertColoringToRgb(colorIndexes)

    nx.set_node_attributes(network.graph, nodeColors, name="color")
    nx.set_node_attributes(network.graph, colorIndexes, name="color index")

    network.voronoiMesh.vertexColors = nodeColors

    logging.info("Максимизация расстояния раскраски")
    logging.info("-" * 48)
    maxMinDistance = calcMaxColoringDistance(network.graph, maxColors, coloringStrategy)
    logging.info(("-" * 48) + "\n")

    logging.info("Минимизация количества цветов 2-дистанционной раскраски")
    logging.info("-" * 48)
    twoDistanceColors = calcMinimumColors(network.graph, 2, coloringStrategy)
    logging.info("-" * 48)
    
    if isPlotNeeded:
        draw.plotNetwork(network)

    return maxMinDistance, twoDistanceColors



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    start = time.perf_counter()
    maxMinDistance, twoDistanceColors = run(100, 30, True)
    end = time.perf_counter()
    logging.info(
        f"""Процедура со 100 точками и 16 цветами исполнена за: {end - start:.6f} сек.
        Максимизированное минимальное расстояние между вершинами разного цвета: {maxMinDistance}
        Минимальное количество цветов для 2-дистанционной раскраски: {twoDistanceColors}
        """)
    
    start = time.perf_counter()
    run(64000, 1008, False)
    end = time.perf_counter()
    logging.info(
        f"""Процедура со 64000 точками и 1008 цветами исполнена за: {end - start:.6f} сек.
        Максимизированное минимальное расстояние между вершинами разного цвета: {maxMinDistance}
        Минимальное количество цветов для 2-дистанционной раскраски: {twoDistanceColors}
        """)