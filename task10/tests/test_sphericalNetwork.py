import pytest 
import networkx as nx
from graphcoloring.SphericalNetwork import SphericalNetwork


def test_networkCreationDefaults():
    network = SphericalNetwork(100)
    nodesCount = len(network.graph.nodes())
    positionAttrsCount = len(nx.get_node_attributes(network.graph, 'position'))
    isConnected = nx.is_connected(network.graph)

    assert nodesCount == 100
    assert positionAttrsCount == 100
    assert isConnected

