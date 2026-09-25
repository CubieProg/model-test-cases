"""
draw
------

Модуль, предоставляющий методы отрисовки графов и `SphericalNetwork`
"""

import logging
import plotly.graph_objects as go
import numpy as np
import networkx as nx

from graphcoloring.Mesh3D import Mesh3D 
from graphcoloring.SphericalNetwork import SphericalNetwork


class PositionAttributeError(Exception):
    def __init__(self, message):   
        super().__init__(message)

def produceLines(graph: nx.Graph):
    """Служебный метод для создания 3D отрезков из рёбер графа `graph`.

    Все вершины `graph` должны иметь атрибут `'position'`

    Parameters
    ----------
    graph : networkx.Graph
        Граф, для которого строятся отрезки
    """

    def linesGenerator(graph: nx.Graph):
        points = nx.get_node_attributes(graph, 'position')
        if len(points) != len(graph.nodes()):
            raise PositionAttributeError("Не все вершины в графе имеют атрибут 'position'")
        
        for edge in graph.edges():
            yield [points[edge[0]], points[edge[1]]]

    # Собираем массивы координат, вставляя None между отрезками 
    #   потому что go.Scatter3d без None будет рисовать ненужные линии
    linesX, linesY, linesZ = [], [], []

    for segment in linesGenerator(graph): 
        (x0, y0, z0), (x1, y1, z1) = segment
        linesX.extend([x0, x1, None])
        linesY.extend([y0, y1, None])
        linesZ.extend([z0, z1, None])

    return np.array([linesX, linesY, linesZ])

def addSphere(figure: go.Figure):
    """Метод добавления сферы-подложки на 3D сцене.

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        Figure, на котором будет отображена сфера
    """

    eps = 0.925
    density = 100

    lon = np.linspace(0, 2 * np.pi, 2 * density)
    lat = np.linspace(0, np.pi, density)
    sphereX = eps * np.outer(np.cos(lon), np.sin(lat))
    sphereY = eps * np.outer(np.sin(lon), np.sin(lat))
    sphereZ = eps * np.outer(np.ones_like(lon), np.cos(lat))

    figure.add_trace(go.Surface(
        x=sphereX, y=sphereY, z=sphereZ,
        opacity=1.0,
        colorscale=[[0, 'darkgray'], [1, 'darkgray']],
        showscale=False,
        name='Sphere',
        hoverinfo='skip'
    ))


def plotSphericalGraph(graph: nx.Graph):
    """Метод рисования графа на 3D сцене.

    Parameters
    ----------
    graph : networkx.Graph
        Граф, который нужно нарисовать. У каждой его вершины обязательно должен быть атрибут `'position'`
        
    Raises
    ------
    PositionAttributeError
        В случае, если указанного не у всех вершин графа есть атрибут `'position'`
    """

    # Сразу проверяем вершины на наличие 'position'
    points = np.array(list(nx.get_node_attributes(graph, 'position').values()))
    if points.shape[0] != len(graph.nodes()):
        raise PositionAttributeError("Не все вершины в графе имеют атрибут 'position'")

    figure = go.Figure()

    addSphere(figure)

    lines = produceLines(graph)
    figure.add_trace(go.Scatter3d(
        x=lines[0,:], y=lines[1,:], z=lines[2,:],
        mode='lines',
        line=dict(color='blue', width=2),
        hoverinfo='skip'
    ))

    # Если нет цветов на вершинах - рисуем их красным цветом. В тултип добавляет текст 'node'
    try:
        markerColors = [nx.get_node_attributes(graph, 'color')[n] for n in graph.nodes()]
        colorIndexes = [nx.get_node_attributes(graph, 'color index')[n] for n in graph.nodes()]
    except KeyError as e:
        markerColors = 'red'
        colorIndexes = 'node'

    figure.add_trace(go.Scatter3d(
        x=points[:, 0], y=points[:, 1], z=points[:, 2],
        mode='markers',
        marker=dict(size=10, color=markerColors),
        name='Точки',
        text=colorIndexes,
        hoverinfo='text'
    ))

    figure.show()



def plotMesh3D(mesh: Mesh3D):
    """Метод рисования Mesh3D на 3D сцене.

    Parameters
    ----------
    mesh : Mesh3D
        Граф, который нужно нарисовать. У каждой его вершины обязательно должен быть атрибут `'position'`
        
    Note
    ------
    Если в `mesh` не достаточно цветов или они заданы некорректно, 
    то меш отрисуется со стандартным для `plotly.graph_objects.Figure` цветом
    """

    triangleColors = []

    try:
        for vertex in range(mesh.vertices.shape[0]):
            triangleColors.append(
                mesh.vertexColors[mesh.verticiesToRegionsMap[vertex]]
            )
    except IndexError as e:
        logging.warning(f"В меше недостаточно цветов")
        triangleColors = None

    figure = go.Figure()

    figure.add_trace(go.Mesh3d(
        x=mesh.vertices[:, 0], y=mesh.vertices[:, 1], z=mesh.vertices[:, 2],
        i=mesh.triangles[:, 0], j=mesh.triangles[:, 1], k=mesh.triangles[:, 2],
        vertexcolor=triangleColors,
        hoverinfo='skip',
        showlegend=False
    ))

    figure.update_layout(
        scene=dict(aspectmode='data'),
        margin=dict(l=0, r=0, b=0, t=30)
    )

    figure.show()



def plotNetwork(network: SphericalNetwork):
    """Метод рисования SphericalNetwork на 3D сцене.

    Рисует сразу граф сети и его меш

    Parameters
    ----------
    network : SphericalNetwork
        Сферическая сеть, которую нужно нарисовть
        
    Note
    ------
    Если в `voronoiMesh` поданого `network` не достаточно цветов или они заданы некорректно, 
    то меш отрисуется со стандартным для `plotly.graph_objects.Figure` цветом
    """

    points = np.array(list(nx.get_node_attributes(network.graph, 'position').values()))
    if points.shape[0] != len(network.graph.nodes()):
        raise PositionAttributeError("Не все вершины в графе имеют атрибут 'position'")
    
    figure = go.Figure()

    addSphere(figure)
    
    lines = produceLines(network.graph)
    figure.add_trace(go.Scatter3d(
        x=lines[0,:], y=lines[1,:], z=lines[2,:],
        mode='lines',
        line=dict(color='blue', width=2),
        hoverinfo='skip'
    ))

    try:
        markerColors = [nx.get_node_attributes(network.graph, 'color')[n] for n in network.graph.nodes()]
        colorIndexes = [nx.get_node_attributes(network.graph, 'color index')[n] for n in network.graph.nodes()]
    except KeyError:
        markerColors = 'red'
        colorIndexes = 'node'

    # Добавляем вершины. trace = 2
    figure.add_trace(go.Scatter3d(
        x=points[:, 0], y=points[:, 1], z=points[:, 2],
        mode='markers',
        marker=dict(size=10, color=markerColors),
        text=colorIndexes,
        hoverinfo='text'
    ))

    triangleColors = []
    
    try:
        for i in range(network.voronoiMesh.vertices.shape[0]):
            triangleColors.append(network.voronoiMesh.vertexColors[network.voronoiMesh.verticiesToRegionsMap[i]])
    except IndexError as e:
        logging.warning(f"В меше недостаточно цветов")
        triangleColors = None

    # Области Вороного. trace = 3
    figure.add_trace(go.Mesh3d(
        x=network.voronoiMesh.vertices[:, 0], 
        y=network.voronoiMesh.vertices[:, 1], 
        z=network.voronoiMesh.vertices[:, 2],

        i=network.voronoiMesh.triangles[:, 0], 
        j=network.voronoiMesh.triangles[:, 1], 
        k=network.voronoiMesh.triangles[:, 2],

        vertexcolor=triangleColors,
        hoverinfo='skip',
        showlegend=False
    ))

    figure.update_layout(
        showlegend=False,
        updatemenus=[
            dict(
                type='buttons',
                direction='right',
                x=0.0,
                y=1.15,
                showactive=True,
                buttons=[
                    dict(
                        label='Сфера',
                        method='restyle',
                        args=[{'visible': False}, [0]],
                        args2=[{'visible': True}, [0]]
                    ),
                    dict(
                        label='Рёбра',
                        method='restyle',
                        args=[{'visible': False}, [1]],
                        args2=[{'visible': True}, [1]]
                    ),
                    dict(
                        label='Вершины',
                        method='restyle',
                        args=[{'visible': False}, [2]],
                        args2=[{'visible': True}, [2]]
                    ),
                    dict(
                        label='Области Вороного',
                        method='restyle',
                        args=[{'visible': False}, [3]],
                        args2=[{'visible': True}, [3]]
                    ),
                ]
            )
        ]
    )

    figure.show()