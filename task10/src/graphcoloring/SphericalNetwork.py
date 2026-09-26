import numpy as np
import networkx as nx
from scipy.spatial import ConvexHull, SphericalVoronoi
from numpy import arange, pi, sin, cos, arccos

from typing import List
from numpy.typing import NDArray

from graphcoloring.Mesh3D import Mesh3D



class SphericalNetwork:
    """Класс для представления сети спутников. 
    Содержит граф спутников и их связей в `graph` и области покрытия спутников в `voronoiMesh`

    Attributes
    ----------
    graph : networkx.Graph 
        Граф, вершины которого представляют спутники, а рёбра - связи между их зонами покрытия. 
        Рёбра являются по сути разбиением Делоне сферы, но вычисляются взятием выпуклой оболочки (см. https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.SphericalVoronoi.html)
    voronoiMesh : Mesh3D
        Диаграма Вороного для сефры, составленная относительно вершин в графе `graph`. 
        Является двоественной к разбиению Делоне, т.е. две области диаграммы Вороного имеют общее ребро тогда и только тогда, 
        когда две соответствующие вершины соеденены ребром в разбиении Делоне.

    Methods
    ----------
    calcFibonacciSphere(self, pointsCount: int) -> NDArray
        Возвращает `pointsCount` точек равномерно распределённых на единичной сфере

    calcEdgesConvexHull(self, points: NDArray) -> List[Tuple]
        Возвращает рёбра выпуклой оболочки точек `points`

    initGraphFromData(self, verticiesData: NDArray, edges_data: List) -> nx.Graph
        Строит `networkx.Graph` вершины которого - это строки из `verticiesData`, рёбра `edges_data`. 
        Также, выставляет всем вершинам аттрибут `'position'` из `verticiesData`.

    calcVoronoiMesh(self, points: List) -> Mesh3D:
        Строит разбиение Вороного сферы на точках `points` и оборачивает его в Mesh3D 
    """

    graph: nx.Graph
    voronoiMesh: Mesh3D

    def __init__(self, pointsCount: int):
        nodes = self.calcFibonacciSphere(pointsCount)
        edges = self.calcEdgesConvexHull(nodes)

        self.graph = self.initGraphFromData(nodes, edges)
        self.voronoiMesh = self.calcVoronoiMesh(nodes)

    def calcFibonacciSphere(self, pointsCount: int) -> NDArray:
        goldenRatio = (1 + 5**0.5) / 2
        i = arange(0, pointsCount)

        longitude = 2 * pi * i / goldenRatio
        latitude = arccos(1 - 2 * (i + 0.5) / pointsCount)

        x, y, z = cos(longitude) * sin(latitude), sin(longitude) * sin(latitude), cos(latitude)

        return np.transpose(np.array([x, y, z]))


    def calcEdgesConvexHull(self, points: NDArray) -> List:
        hull = ConvexHull(points)
        simplices = hull.simplices

        edge_set = set()
        for triangle in simplices:
            i, j, k = sorted(triangle)
            edge_set.add((i, j))
            edge_set.add((i, k))
            edge_set.add((j, k))
            
        edges = sorted(edge_set)

        return edges

    def initGraphFromData(self, verticiesData: NDArray, edges_data: List) -> nx.Graph:
        N = verticiesData.shape[0]
        newGraph = nx.Graph()

        newGraph.add_nodes_from(range(N))
        newGraph.add_edges_from(edges_data)

        pos_attr = dict(zip(range(N), [tuple(item) for item in verticiesData]))
        nx.set_node_attributes(newGraph, pos_attr, 'position')

        return newGraph
    
    def calcVoronoiMesh(self, points: NDArray) -> Mesh3D:
        voronoiDiagramm = SphericalVoronoi(points, radius=1.0, center=np.zeros(3))
        voronoiDiagramm.sort_vertices_of_regions()

        verticesX, verticesY, verticesZ = [], [], []
        triangles = []
        verticiesToRegionsMap = {}


        # Собираем вершины из треугольников в полигоны
        # Указатель на первую вершину в текущем полигоне
        polygonPointer = 0

        for index, region in enumerate(voronoiDiagramm.regions):
            if len(region) < 3:
                continue

            regionVertices = voronoiDiagramm.vertices[region]
            verticiesCount = len(regionVertices)

            # Добавляем вершины
            verticesX.extend(regionVertices[:, 0])
            verticesY.extend(regionVertices[:, 1])
            verticesZ.extend(regionVertices[:, 2])

            # Триангулируем полигон веером
            for t in range(1, verticiesCount - 1):
                triangle = [polygonPointer, polygonPointer + t, polygonPointer + t + 1]

                triangles.append(triangle)
                verticiesToRegionsMap.update({k: index for k in triangle})

            # Сдвигаем указатель на вершину следующего полигона
            polygonPointer += verticiesCount

        meshVertices = np.array([verticesX, verticesY, verticesZ], ndmin=2, dtype=np.float64)
        meshVertices = np.transpose(meshVertices)

        meshTriangles = np.array(triangles, ndmin=2, dtype=np.int64)

        return Mesh3D(
            meshVertices,
            meshTriangles,
            verticiesToRegionsMap,
            []
        )
    