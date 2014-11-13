# -*- coding: utf-8 -*-
import networkx as nx

g = nx.DiGraph()
g.add_edge(1,2)
nx.write_gexf(g,'/home/ubuntu4/huxiaoqian/mcase/graph/test.gexf')
