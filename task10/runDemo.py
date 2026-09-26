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
    distance = calcMaxColoringDistance(network.graph, maxColors, coloringStrategy)

    logging.info(("-" * 48) + "\n")


    logging.info("Минимизация количества цветов 2-дистанционной раскраски")
    logging.info("-" * 48)
    two_distance_colors = calcMinimumColors(network.graph, 2, coloringStrategy)

    logging.info("-" * 48)

    
    if isPlotNeeded:
        draw.plotNetwork(network)

    return distance, two_distance_colors



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    # start = time.perf_counter()
    # run(10000, 500, False)
    # end = time.perf_counter()
    # logging.debug(f"Время выполнения 1000x500: {end - start:.6f} сек")

    run(100, 16, True)
