# -*- coding: utf-8 -*-
import networkx as nx
from config import db
from model import TopicIdentification, DsTopicIdentification
from collections import Counter
from snowball_sampling import snowballSamplingEndByNodes, multi_snowballSamplingEndByNodes


def SnowballSampling(di_g, g, topic, network_type):
    if network_type==1:
        items_pr = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topic ,\
                                                                TopicIdentification.rank<=4000).all()
        print 'len(items_pr):', len(items_pr)
    else:
        items_pr = db.session.query(DsTopicIdentification).filter(DsTopicIdentification.topic==topic ,\
                                                                  DsTopicIdentification.rank<=4000).all()
        print 'len(items_pr):', len(items_pr)
    di_centerids = [str(item.userId) for item in items_pr if di_g.has_node(str(item.userId))]
    print 'len(di_g):', len(di_g)
    #for item in items_pr:
    #    if not di_g.has_node(item.userId):
            #print item.userId, type(item.userId)
    #print 'len(di_centerids):', len(di_centerids)
    sample_di_g = nx.DiGraph()
    di_taboo_set = set()
    centerids = [str(item.userId) for item in items_pr if g.has_node(str(item.userId))]
    print centerids[:3]
    sample_g = nx.Graph()
    taboo_set = set()
    
    di_taboo_set = multi_snowballSamplingEndByNodes(sample_di_g, di_g, di_centerids, set(di_g.nodes()), taboo_set=di_taboo_set)
    #taboo_set = multi_snowballSamplingEndByNodes(sample_g, g, centerids, set(g.nodes()), taboo_set=taboo_set)
    sample_g = sample_di_g.to_undirected()
    print len(sample_di_g.nodes()), len(sample_di_g.edges())
    print len(sample_g.nodes()), len(sample_g.edges())

    return sample_di_g, sample_g
    
"""
def SnowballSampling(G, gg, topic):
    new_G = nx.DiGraph()
    new_gg = nx.Graph()
    # 获取pagerank前1000的用户id
    items_pr = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topic ,\
                                                           TopicIdentification.rank<=1518).all()
    new_nodes = set()
    new_edges = set()
    edges_list = G.edges()

    for item in items_pr:
        userid = item.userId
        try:
            neighbors = gg.neighbors(userid)
        except:
            continue
        get_neighbors(gg, userid, neighbors,  new_nodes, new_edges, new_G, new_gg, edges_list)
    
    print 'new_G_nodes:', len(new_G.nodes())
    print 'new_G_edges:', len(new_G.edges())
    print 'new_gg_nodes:', len(new_gg.nodes())
    print 'new_gg_edges:', len(new_gg.edges())
    return new_G, new_gg
"""

def max_degree(gg):
    degree_list = list(gg.degree(gg.nodes()).values())
    cnt = Counter()
    for i in degree_list:
        cnt[i] += 1
    print cnt
    maxdegree = max(list(cnt.values()))

    return maxdegree

def get_neighbors(gg, userid, neighbors,  new_nodes, new_edges, new_G, new_gg, edges_list):
    if userid in new_nodes:
        return new_G, new_gg
    else:
        new_nodes.add(userid)
    for k in neighbors:
        new_nodes.add(k)
        if (userid, k) in edges_list:
            if not (userid, k) in new_edges:
                new_edges.add((userid, k))
                new_G.add_edge(userid, k)
                new_gg.add_edge(userid, k)
        if (k, userid) in edges_list:
            if not (k, userid) in new_edges:
                new_edges.add((k, userid))
                new_G.add_edge(k, userid)
                new_gg.add_edge(k, userid)
        try:
            neighbors = gg.neighbors(k)
        except:
            continue
        new_G, new_gg = get_neighbors(gg, k, neighbors, new_nodes, new_edges, new_G, new_gg, edges_list)
    
    return new_G, new_gg

if __name__== '__main__':
    topic = u'东盟,博览会'
    #di_g = nx.read_gexf('/home/ubuntu4/huxiaoqian/mcase/graph/227_2013-09-08_6_g_graph.gexf')
    di_g = nx.read_gexf('/home/ubuntu4/huxiaoqian/mcase/graph/227_2013-09-08_6_ds_dg_graph.gexf')
    #g = nx.read_gexf('/home/ubuntu4/huxiaoqian/mcase/graph/227_2013-09-08_6_gg_graph.gexf')
    g = nx.read_gexf('/home/ubuntu4/huxiaoqian/mcase/graph/227_2013-09-08_6_ds_udg_graph.gexf')
    #network_type = 1
    network_type = 2
    sample_di_g, sample_g = SnowballSampling(di_g, g, topic, network_type)
    print 'len(sample_di_g):', len(sample_di_g)
    print 'len(sample_g):', len(sample_g)
    
    
