from dataclasses import dataclass
from typing import List, Dict

import numpy as np
from numpy.typing import NDArray


@dataclass
class Mesh3D:
    """Класс для представления 3D меша.
    
    Attributes
    ----------
    vertices : NDArray 
        Матрица вершин
    triangles : NDArray
        Массив треугольников. Каждый треугольник - это три целых числа - номера вершин в `verticies`
    vertexColors : Dict
        Словарь сопоставляющий номер_вершины и номер_цвета
    verticiesToRegionsMap : Dict
        Список, сопоставляющий вершины полигонам. 
        Например, в первом элементе списка хранятся вершины соответствующие первому полигону
    """

    vertices: NDArray[np.float64]
    triangles: NDArray[np.int64]
    verticiesToRegionsMap: List[List[int]]
    vertexColors: Dict