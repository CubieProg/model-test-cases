import numpy as np
import json
from typing import NamedTuple, List
from numpy.typing import NDArray
import logging

from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class EarthConstants():
    radius: float = 6378135           # Экваториальный радиус Земли [m]
    GM: float     = 3.986004415e+14   # Гравитационный параметр Земли [m3/s2]
    J2: float     = 1.082626e-3       # Вторая зональная гармоника геопотенциала

earthConstants = EarthConstants()


class Walker(NamedTuple):
    inclination: float           # наклонение орбиты
    satsPerPlane: int            # число КА в каждой орбитальной плоскости группы
    planeCount: int              # число орбитальных плоскостей в группе
    phase: int                   # фазовый сдвиг по аргументу широты между КА в соседних плоскостях
    altitude: float              # высота орбиты
    maxRaan: float               # максимум прямого восхождения восходящего узла (при распределении орбитальных плоскостей)
    startRaan: float             # прямое восхождение восходящего узла для первой плоскости


class WalkerGroup(Walker):

    def getTotalSatCount(self):
        return self.satsPerPlane * self.planeCount
    
    def calcInitialElements(self):
        startRaan   = np.deg2rad(self.startRaan)
        maxRaan     = np.deg2rad(self.maxRaan)
        inclination = np.deg2rad(self.inclination)
        altitude    = self.altitude * 1000
        satCount    = self.getTotalSatCount()
    
        raans = np.linspace(startRaan, startRaan + maxRaan, self.planeCount + 1)
        raans = raans[:-1] % (2 * np.pi)
        
        planeArrange = np.arange(self.planeCount)
        satArrange = np.arange(self.satsPerPlane)
        planeMeshGrid, satMeshGrid = np.meshgrid(planeArrange, satArrange, indexing='ij')
        planeMeshGrid = planeMeshGrid.ravel()
        satMeshGrid = satMeshGrid.ravel()
        aols = 2.0 * np.pi * (
            satMeshGrid / self.satsPerPlane
            + self.phase * planeMeshGrid / satCount)
        
        sma = earthConstants.radius + altitude
        
        elements = np.zeros((satCount, 6))
        elements[:, 0] = sma
        elements[:, 3] = np.repeat(raans, self.satsPerPlane)
        elements[:, 4] = inclination
        elements[:, 5] = aols

        return elements
    

class Constellation:
    def __init__(self, nameCode: str):
        self.totalSatCount: int                 = 0
        self.groups:        List[WalkerGroup]   = []
        self.elements:      NDArray             = np.empty(0)
        self.stateEci:      NDArray             = np.empty(0)
        self.loadGroupsFromConfig(nameCode)

    def loadGroupsFromConfig(self, nameCode: str):
        filename = 'ConstellationsTest.json'
        currentDir = Path(__file__).resolve().parent
        filePath = currentDir.parent / filename

        with filePath.open("r", encoding="utf-8") as f:
            jsonData = json.loads(f.read())

        try:
            constellationData = next(item for item in jsonData if item['name'].lower() == nameCode.lower())
        except StopIteration:
            logging.error(f'Группировка {nameCode} не найдена в файле {filename}')
            raise

        for item in constellationData['Walkers']:
            # Вопрос - что делать если данные некорректные для конкретного item
            newWalkerGroup = WalkerGroup(*item)
            self.groups.append(newWalkerGroup)
            self.totalSatCount += newWalkerGroup.getTotalSatCount()

    def initState(self):
        self.elements = np.zeros((self.totalSatCount, 6))
        shift = 0

        for singleGroup in self.groups:
            ending = shift + singleGroup.getTotalSatCount()
            self.elements[shift:ending, :] = singleGroup.calcInitialElements()
            shift = ending

    def propagateJ2(self, epochs: list[int]):
        self.stateEci = np.zeros((self.totalSatCount, 3, len(epochs)))

        inclination = self.elements[:, 4]
        sma = self.elements[:, 0]
        raan0 = self.elements[:, 3]
        aol0 = self.elements[:, 5]

        raanPrecessionRate = -1.5 * (earthConstants.J2 * np.sqrt(earthConstants.GM) * earthConstants.radius**2) \
                           / (sma**(7/2)) * np.cos(inclination)

        draconicOmega      = np.sqrt(earthConstants.GM / sma**3) \
                           * (1 - 1.5 * earthConstants.J2 * (earthConstants.radius / sma)**2) \
                           * (1 - 4 * np.cos(inclination)**2)

        for epoch in epochs:
            aol = aol0 + epoch * draconicOmega
            raanOmega = raan0 + epoch * raanPrecessionRate

            epochState = sma * [
                (np.cos(aol) * np.cos(raanOmega) - np.sin(aol) * np.cos(inclination) * np.sin(raanOmega)),
                (np.cos(aol) * np.sin(raanOmega) + np.sin(aol) * np.cos(inclination) * np.cos(raanOmega)),
                (np.sin(aol) * np.sin(inclination))]

            self.stateEci[:, :, epochs.index(epoch)] = np.array(epochState).T
