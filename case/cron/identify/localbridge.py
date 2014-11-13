# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
import networkx as nx
from config import db
from model import LocalBridge
from time_utils import ts2datetime, datetime2ts

def GetLocalBridge(g, topic, windowsize, date):
    '''
    通过遍历边，对是否为捷径进行判断，将跨度最大的前10名存放在数据库中
    '''
    localbridge = []
    edges_list = g.edges()
    for (a,b) in edges_list:
        a_n = set(g.neighbors(a))
        b_n = set(g.neighbors(b))
        l_a_n = len(a_n)
        l_b_n = len(b_n)
        l_ab_n = len(a_n & b_n)
        if (l_a_n!=1)&(l_b_n!=1)&(l_ab_n==0):
            paths_list = nx.all_simple_paths(g, source=a, target=b)
            span_ab = 0
            len_path = 0
            for path in paths_list:
                len_path += 1
                if len(path) > span_ab:
                    span_ab = len(path)
            if len_path == 1:
                span_ab = 10000 # 当去除了仅有的那条边之后没有其他路径能够连接ab，则使跨度为10000
            
            localbridge.append((a, b, span_ab, l_a_n, l_b_n))
            
    SaveLocalBridge(topic, date, windowsize, localbridge) # 存放localbridge数组

def SaveLocalBridge(topic, date, windowsize, lb_list):
    '''
    对localbridge根据跨度值span_ab进行排序，选择跨度值最大的前十进行存储
    '''
    lb_list = sorted(lb_list, key=lambda x:(x[3]+x[4]), reverse=False)
    lbs = lb_list[len(lb_list)-100:]
    lbs = sorted(lb_list, key=lambda x:(x[3]+x[4]), reverse=True)
    print 'lb_list:', lb_list
    print 'len(lb_list):', len(lb_list)
    
    for lb in lbs:
        print lb
        item = LocalBridge(topic, date, windowsize, lb[0], lb[1], lb[2])
        item_exist = db.session.query(LocalBridge).filter(LocalBridge.a_node==lb[0] ,\
                                                          LocalBridge.b_node==lb[1] ,\
                                                          LocalBridge.topic==topic ,\
                                                          LocalBridge.windowsize==windowsize ,\
                                                          LocalBridge.date==date).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
        db.session.commit()
        

if __name__=='__main__':
    #读取无向图结构
    g = nx.read_gexf('test_graph.gexf') # 待处理
    topic = '东盟,博览会'
    windowsize = 6
    end_ts = datetime2ts('2013-09-08')
    date = ts2datetime(end_ts)
    GetLocalBridge(g, topic, windowsize, date)

