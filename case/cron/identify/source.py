# -*- coding: utf-8 -*-

import sys
import networkx as nx
sys.path.append('../')
from config import db
from model import BetweenessCentralityUser, Source # model.py建表
from time_utils import ts2datetime, datetime2ts

def Get_s(g, positive_m, source):
    new_source, arrived_m, source= get_max_m(g, positive_m, source)
    positive_m = remove_am(positive_m, arrived_m)
    return source, positive_m

def get_max_m(g, positive_m, source):
    max_m = []
    max_m_source = 0
    for i in g.nodes():
        if i in source:
            continue
        arrived_m = []
        arrived_nodes= list(nx.dfs_preorder_nodes(g, i))
        arrived_nodes_set = set(arrived_nodes)
        positive_set = set(positive_m)
        arrived_m = arrived_nodes_set & positive_set
        if len(max_m) < len(arrived_m):
            max_m = list(arrived_m)
            max_m_source = i
    print 'max_m_source:', max_m_source
    print 'source:', source
    if max_m_source != 0:
        source.append(max_m_source)
    else:
        print 'i has no arrived_m'
    return max_m_source, max_m, source
     
def remove_am(positive_m, arrived_m):
    positive_m_set = set(positive_m)
    arrived_m_set = set(arrived_m)
    new_positive_m_set = positive_m_set - arrived_m_set
    positive_m = list(new_positive_m_set)
    print 'positive_m, arrived_m, new_positive_m:', len(positive_m), len(arrived_m), len(new_positive_m_set)
    return positive_m

def save_source(topic, date, windowsize, source):
    for ss in source:
        item = Source(topic, date, windowsize, ss)
        item_exist = db.session.query(Source).filter(Source.topic==topic ,\
                                                     Source.date==date ,\
                                                     Source.windowsize==windowsize ,\
                                                     Source.userid==ss).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
        db.session.commit()
    print 'success save source'
    

def Get_pm(g, ratio_pm, topic, windowsize, date):
    k = int(len(g.nodes()) * ratio_pm)
    items = db.session.query(BetweenessCentralityUser).filter(BetweenessCentralityUser.topic==topic ,\
                                                              BetweenessCentralityUser.rank<=k ,\
                                                              BetweenessCentralityUser.windowsize==windowsize ,\
                                                              BetweenessCentralityUser.date==date).all()
    positive_m = []
    for item in items:
        positive_m.append(item.userid)
        
    print 'len(positive_m):', k
    print 'positive_m:', positive_m
    return positive_m


if __name__=='__main__':
    g = nx.read_gexf('test_graph.gexf')
    positive_m = []
    source = []
    topic = u'东盟,博览会'
    windowsize = 6
    end_ts = datetime2ts('2013-09-08')
    date = ts2datetime(end_ts)
    ratio_pm = 1 / float(30)
    positive_m = Get_pm(g, ratio_pm, topic, windowsize, date)
    while positive_m:
        #print 'positive_m, source:', len(positive_m), len(source)
        source, positive_m = Get_s(g, positive_m, source)
        print 'positive_m, source:', len(positive_m), len(source)
    save_source(source)
    
