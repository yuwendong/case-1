# -*-coding: utf-8 -*-

import networkx as nx
from gexf import Gexf

def getgexf(g):
    gexf = Gexf('hxq', 'test graph')
    graph = gexf.addGraph('undirected graph')

    node_counter = 0
    for node in g.nodes():
        graph.addNode(node_counter, node)
        node_couter += 1
        
    edge_counter = 0
    for edge in g.edges():
        start, end = edge
        graph.addEdge(edge_counter, start, end)

    output_file = open('graph.gexf', 'w')
    gexf.write(output_file)

    
