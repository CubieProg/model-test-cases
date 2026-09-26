"""
Точка входа для проверки тестового задания.
Запускает расчёты и рисует картинки.
"""

import networkx as nx
import logging
from collections.abc import Callable

from graphcoloring.SphericalNetwork import SphericalNetwork
from graphcoloring.coloring import graphDistanceColoring, calcMaxColoringDistance, calcMinimumColors, graphDistanceColoringDsatur, convertColoringToRgb
# import graphcoloring.coloring as coloring


import graphcoloring.draw as draw


def run(nodesCount: int, maxColors: int, isPlotNeeded: bool = False, 
        coloringStrategy: str = 'greedy'):


    
    network = SphericalNetwork(nodesCount)

    # strategy = coloring.STRATEGIES.get(coloringStrategy)
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

    logging.info(f"Графу достаточно {two_distance_colors} цветов для 2-дистанционной раскраски")
    logging.info(("-" * 48) + "\n\n\n")

    
    if isPlotNeeded:
        draw.plotMesh3D(network.voronoiMesh)
        draw.plotSphericalGraph(network.graph)
        draw.plotNetwork(network)

    return distance, two_distance_colors



import time

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # run(10000, 500, False, graphDistanceColoring)


    
    # start = time.perf_counter()
    # run(10000, 500, False, graphDistanceColoring)
    # end = time.perf_counter()
    # logging.debug(f"Время выполнения 1000x500: {end - start:.6f} сек")
    
    # start = time.perf_counter()
    # run(10000, 1008, False, graphDistanceColoring)
    # end = time.perf_counter()
    # logging.debug(f"Время выполнения 1000x1008: {end - start:.6f} сек")
    
    # start = time.perf_counter()
    # run(64000, 20, False, graphDistanceColoring)
    # end = time.perf_counter()
    # logging.debug(f"Время выполнения 64000x20: {end - start:.6f} сек")

    # start = time.perf_counter()
    # run(64000, 100, False, graphDistanceColoring)
    # end = time.perf_counter()
    # logging.debug(f"Время выполнения 64000x100: {end - start:.6f} сек")

    # start = time.perf_counter()
    # run(64000, 500, False, graphDistanceColoring)
    # end = time.perf_counter()
    # logging.debug(f"Время выполнения 64000x500: {end - start:.6f} сек")

    # start = time.perf_counter()
    # run(64000, 1008, False, graphDistanceColoringDsatur)
    # end = time.perf_counter()
    # logging.debug(f"Время выполнения 64000x1008: {end - start:.6f} сек")

    # run(100, 16, True, graphDistanceColoringDsatur)
    run(100, 16, True)
    # run(64000, 1008, False, graphDistanceColoring)
    # run(100, 16, True)
