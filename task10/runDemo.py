"""
Точка входа для проверки тестового задания.
Запускает расчёты и рисует картинки.
"""

import networkx as nx
import logging
from collections.abc import Callable

from graphcoloring.SphericalNetwork import SphericalNetwork
from graphcoloring.coloring import graphDistanceColoring, calcMaxColoringDistance, calcMinimumColors, graphDistanceColoringDsatur, convertColoringToRgb

import graphcoloring.draw as draw


def run(nodesCount: int, maxColors: int, isPlotNeeded: bool = False, 
        coloringStrategy: Callable = graphDistanceColoring):
    network = SphericalNetwork(nodesCount)

    colorIndexes, _ = coloringStrategy(network.graph, 2, maxColors)

    nodeColors = convertColoringToRgb(colorIndexes)

    nx.set_node_attributes(network.graph, nodeColors, name="color")
    nx.set_node_attributes(network.graph, colorIndexes, name="color index")

    network.voronoiMesh.vertexColors = nodeColors

    logging.info("Максимизация расстояния раскраски")
    logging.info("-" * 48)
    distance = calcMaxColoringDistance(network.graph, maxColors)

    logging.info(("-" * 48) + "\n")


    logging.info("Минимизация количества цветов 2-дистанционной раскраски")
    logging.info("-" * 48)
    two_distance_colors = calcMinimumColors(network.graph, 2)

    logging.info(f"Графу достаточно {two_distance_colors} цветов для 2-дистанционной раскраски")
    logging.info(("-" * 48) + "\n\n\n")

    
    if isPlotNeeded:
        draw.plotMesh3D(network.voronoiMesh)
        draw.plotSphericalGraph(network.graph)
        draw.plotNetwork(network)

    return distance, two_distance_colors





if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    
    run(64000, 1008, False, graphDistanceColoring)

    # run(100, 16, True, graphDistanceColoringDsatur)
    # run(100, 16, True, graphDistanceColoring)
    # run(64000, 1008, False, graphDistanceColoring)
    # run(100, 16, True)
