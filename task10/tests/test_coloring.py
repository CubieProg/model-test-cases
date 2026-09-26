import pytest 
import networkx as nx
import matplotlib.pyplot as plt

from graphcoloring.coloring import graphDistanceColoringDsatur, calcMaxColoringDistance, calcMinimumColors

def test_coloringC6():
    C6 = nx.cycle_graph(6)
    _, usedColors = graphDistanceColoringDsatur(C6, 1, 6)
    assert usedColors == 2

def test_coloringC7():
    C7 = nx.cycle_graph(7)
    _, usedColors = graphDistanceColoringDsatur(C7, 1, 7)
    assert usedColors == 3

def test_coloringP6():
    P6 = nx.path_graph(6)
    _, usedColors = graphDistanceColoringDsatur(P6, 1, 6)
    assert usedColors == 2

def test_coloringK6():
    K6 = nx.complete_graph(6)
    _, usedColors = graphDistanceColoringDsatur(K6, 1, 6)
    assert usedColors == 6

def test_maxColoringDistance():
    C6 = nx.cycle_graph(6)
    distance = calcMaxColoringDistance(C6, 3, 'DSATUR')
    assert distance == 2
    
def test_minimumColors():
    C6 = nx.cycle_graph(6)
    colorsCount = calcMinimumColors(C6, 2)
    assert colorsCount == 3