# -*- coding: utf-8 -*-
import json
import networkx as nx
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import random
import math
from scipy import linalg
import numpy as np
from collections import Counter

from SSDB import SSDB 
from config import db, SSDB_HOST, SSDB_PORT
from model import DegreeCentralityUser, BetweenessCentralityUser, ClosenessCentralityUser ,\
                  DsDegreeCentralityUser, DsBetweenessCentralityUser, DsClosenessCentralityUser

def _utf8_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, 'utf-8')


def get_ave(dict_value):
    sumvalue = 0
    for nodes, value in dict_value.iteritems():
        sumvalue += value
    ave = float(sumvalue) / float(len(dict_value)) 
    return ave

def get_powerlaw(dhistogram, prekey):
    l = len(dhistogram)
    print 'l:', l
    pre_x = []
    pre_y = []
    for i in range(l):
        if i == 0:
            pre_x.append(0.000000001)
        else:
            pre_x.append(i)

        if dhistogram[i] == 0:
            pre_y.append(0.000000001)
        else:
            pre_y.append(dhistogram[i])
    x = pre_x
    p_y = pre_y
    y =[]
    allcount = sum(dhistogram)
    for count in p_y:
        fre = float(count) / float(allcount)
        y.append(fre)
    lnx = [math.log(f, math.e) for f in x]
    lny = [math.log(f, math.e) for f in y]
    a = np.mat([lnx, [1]*len(x)]).T
    b = np.mat(lny).T

    (t, res, rank, s) = linalg.lstsq(a, b) # 最小二乘求系数,t为2*1的矩阵
    print 'results:', linalg.lstsq(a,b)
    xx = pre_x
    r = t[0][0]
    c = t[1][0]
    results_linalg = [r, c] # r*lnx+c=lny
    save_quota(prekey + '_result_linalg', results_linalg)

    #yy = [math.e**(r*a+c) for a in lnx]
    #lnyy = [math.log(f, math.e) for yyy in yy]
    lnyy = [r*a+c for a in lnx]
    xydict = {}
    xydict['lnx'] = lnx
    xydict['lny'] = lnyy
    save_quota(prekey + '_xydict_lnx', lnx)
    save_quota(prekey + '_xydict_lny', lnyy)
    # 保存回归参数
    return t[0][0]

def get_counter(value_dict):
    value_list = []
    for uid in value_dict:
        v = value_dict[uid]
        value_list.append(v)
    cnt = Counter()
    for v in value_list:
        cnt[v] += 1
    print cnt
    return cnt

def get_spl_histogram(maxwcc):
    pathlist = []
    for mnode in maxwcc.nodes():
        #print 'mnode:', mnode
        for mmnode in maxwcc.nodes():
            #print 'mmnode:', mmnode
            if mnode != mmnode:
                l = nx.shortest_path_length(maxwcc, source=mnode, target=mmnode)
                pathlist.append(l)
    cnt = Counter()
    for v in pathlist:
        cnt[v] += 1
    print cnt
    return cnt


def compute_quota(G, gg, date, windowsize, topic, all_uid_pr, network_type):
    prekey = _utf8_unicode(topic)+'_'+str(date)+'_'+str(windowsize)
    #print 'prekey:', prekey.encode('utf-8')
    #print 'G_nodes:',len(G.nodes())
    #print 'gg_nodes:', len(gg.nodes())
    #无向图的最大连通子图
    

    G_edges = G.edges()
    print 'G_edges:',len(G_edges)
    '''
    nodes_list = G.nodes()
    l = len(nodes_list)
    print 'l:', l
    r = random.randint(0,l-1)
    print 'r:', r
    bfs_edges = list(nx.bfs_edges(gg,nodes_list[r]))
    print 'bfs_edges:', bfs_edges
    print 'len(bfs_edges):', len(bfs_edges)
    '''
    degree = G.degree()
    print 'degree_counter'
    degree_test = get_counter(degree)

    indegree = G.in_degree()
    #print 'indegree:', indegree
    indegree_histogram = get_counter(indegree)
    save_quota(prekey+'_indegree_histogram_'+str(network_type), json.dumps(indegree_histogram))
    outdegree = G.out_degree()
    #print 'outdegree:', outdegree
    outdegree_histogram = get_counter(outdegree)
    save_quota(prekey+'_outdegree_histogram_'+str(network_type), json.dumps(outdegree_histogram))
    
    HH = nx.connected_component_subgraphs(gg)
    maxhn = 0
    for h in HH:
        if maxhn < len(h.nodes()):
            maxhn = len(h.nodes())
            H = h
    #print 'H_nodes:', len(H.nodes())
    
    #ndegree = G.degree()
    # 节点度，dict{nodes:value}
    #get_key_user('node_degree', topic, date, windowsize, ndegree)
    #根据节点度排序，获取节点度层面的关键用户
    
    dCentrality = nx.degree_centrality(G)
    # 度中心性 dict{nodes:value} 度量重要性
    
    avedc = get_ave(dCentrality)
    #平均度中心性 float
    save_quota(prekey+'_ave_degree_centrality_'+str(network_type), avedc)
    
    maxwcc = nx.weakly_connected_component_subgraphs(G).next()
    #print 'maxwcc_G:', len(maxwcc)
    
    bCentrality = nx.betweenness_centrality(G)
    # 介数中心 dict{nodes:value},度量其对网络流程的重要性
    
    avebc = get_ave(bCentrality)
    # 平均介数中心性 float
    save_quota(prekey+'_ave_betweenness_centrality_'+str(network_type), avebc)
    
    cCentrality = nx.closeness_centrality(G)
    # 紧密中心性 dict{nodes:value},度量感知整个网络流程事件的位置
    avecc = get_ave(cCentrality)
    # 平均紧密中心性 float
    save_quota(prekey+'_ave_closeness_centrality_'+str(network_type), avecc)
    
    # get_key_user module
    print 'get_user'
    get_key_user(topic, date, windowsize, dCentrality, bCentrality, cCentrality, network_type)
    
    eCentrality = nx.eigenvector_centrality_numpy(G)
    # 特征向量中心性
    #get_key_user('eigenvector_centrality', topic, date, windowsize, eCentrality)
    # 获取特征向量中心性层面的关键用户
    aveec = get_ave(eCentrality)
    # 平均特征向量中心性 float
    save_quota(prekey+'_eigenvector_centrality_'+str(network_type), aveec)
    
    spl_histogram = get_spl_histogram(H)
    save_quota(prekey + '_shortest_path_length_histogram_'+str(network_type), json.dumps(spl_histogram))
       
    avespl = nx.average_shortest_path_length(H) # !!!!
    # 平均最短路径长度 float--only for connected gragh
    save_quota(prekey+'_average_shortest_path_length_'+str(network_type), avespl)
   
    dhistogram = nx.degree_histogram(G)
    # 节点度分布（从一到最大度的出现频次）
    save_quota(prekey+'_degree_histogram_'+str(network_type), dhistogram)


    '''
    #Hdhistogram = nx.degree_histogram(G) # !!!!
    # histogram of H-----max connected graph
    #save_quota(prekey + '_H_degree_histogram', Hdhistogram)
    '''
    gamma = get_powerlaw(dhistogram, prekey)
    # 幂律分布系数
    save_quota(prekey+'_power_law_distribution_'+str(network_type), gamma)
    
    
    nnodes = len(G.nodes())
    # the number of nodes in G
    save_quota(prekey+'_number_nodes_'+str(network_type), nnodes)
    
    Hnnodes = len(H.nodes())
    # the number o nodes in H
    ratio_H2G = float(Hnnodes) / float(nnodes)
    print '!!!!!ratio_H2G!!!!!:',ratio_H2G
    #save_quota(prekey + '_ratio_H2G', ratio_H2G)
    
    alldegree = sum(dhistogram)
    ave_degree = float(alldegree) / float(nnodes)
    # ave_degree 平均节点度
    save_quota(prekey+'_ave_degree_'+str(network_type), ave_degree)

    
    nedges = len(G.edges())
    # the number of edged in G
    save_quota(prekey+'_number_edges_'+str(network_type), nedges)
    
    gdiameter = nx.diameter(H) # !!!
    # The diameter is the maximum eccentricity   int-n
    save_quota(prekey+'_diameter_'+str(network_type), gdiameter)

    geccentricity = nx.eccentricity(H) # !!!
    # the eccentricity of nodes in gg
    avegec = get_ave(geccentricity)
    save_quota(prekey+'_ave_eccentricity_'+str(network_type), avegec)

    
    sconnectedn = nx.number_strongly_connected_components(G)
    # 强连通子图数量  int-n
    save_quota(prekey+'_number_strongly_connected_components_'+str(network_type), sconnectedn)
    #maxscc = nx.strongly_connected_component_subgraphs(G).next()
    #print 'maxwcc:', len(maxwcc)
    wconnectesn = nx.number_weakly_connected_components(G)
    # 弱连通子图数量 int-n
    
    save_quota(prekey+'_number_weakly_connected_components_'+str(network_type), wconnectesn)
    maxwcc = nx.weakly_connected_component_subgraphs(G).next()
    print 'maxwcc_G:', len(maxwcc.nodes())
    print '!!!!ratio_maxwcc_G!!!:', float(len(maxwcc.nodes()))/float(nnodes)
    
    aveclustering = nx.average_clustering(gg) # !!!!
    # 平均聚类系数
    save_quota(prekey+'_average_clustering_'+str(network_type), aveclustering)

    dassortativity_coefficient = nx.degree_assortativity_coefficient(G)
    # 同配性系数
    save_quota(prekey + '_degree_assortativity_coefficient_'+str(network_type), dassortativity_coefficient)
    
    #print 'G_edges:', len(G.edges())
    #print 'G_edges:', len(G.selfloop_edges())
    #GG = G
    #GG.remove_edges_from(GG.selfloop_edges())
    #print 'test_edges:',len(GG.edges())
    kcore = nx.core_number(G)
    #print 'kcore:', kcore
    # k_score k核数
    #avekc = get_ave(kcore)
    
    maxkc = get_max(kcore)
    save_quota(prekey + '_max_k_core_'+str(network_type), maxkc)
    
def get_max(result_dict):
    for node_id in result_dict:
        max_result = 0
        value = result_dict[node_id]
        if value > max_result:
            max_result = value
    return max_result

def get_key_user(topic, date, windowsize, dCentrality, bCentrality, cCentrality, network_type): # 根据对应指标获取排序在前100的用户
    rank_method = ['degree_centrality', 'betweeness_centrality', 'closeness_centrality', 'page_rank']
    for method in rank_method:
        if method=='degree_centrality':
            sorted_dict = dCentrality
        elif method=='betweeness_centrality':
            sorted_dict = bCentrality
        elif method=='closeness_centrality':
            sorted_dict = cCentrality
        result = sorted(sorted_dict.iteritems(), key=lambda (k, v):v, reverse=True)
        sort_result = result # 全部进行排序
        save_key_user(method, topic, date, windowsize, sort_result, network_type)

def save_key_user(classname, topic, date, windowsize, sorted_dict, network_type): # 将排序结果存放在mysql中
    results_dict = []
    if classname == 'degree_centrality':
        rank = 0
        for k in sorted_dict:
            rank += 1
            uid = k[0]
            centra = k[1]
            if network_type==1:
                item = DegreeCentralityUser(topic, date, windowsize, rank, uid, centra)
                item_exist = db.session.query(DegreeCentralityUser).filter(DegreeCentralityUser.topic==topic ,\
                                                                           DegreeCentralityUser.date==date ,\
                                                                           DegreeCentralityUser.windowsize==windowsize ,\
                                                                           DegreeCentralityUser.userid==uid).first()
            else:
                item = DsDegreeCentralityUser(topic, date, windowsize, rank, uid, centra)
                item_exist = db.session.query(DsDegreeCentralityUser).filter(DsDegreeCentralityUser.topic==topic ,\
                                                                             DsDegreeCentralityUser.date==date ,\
                                                                             DsDegreeCentralityUser.windowsize==windowsize ,\
                                                                             DsDegreeCentralityUser.userid==uid).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
            db.session.commit()
    elif classname == 'betweeness_centrality':
        rank = 0
        for k in sorted_dict:
            rank += 1
            uid = k[0]
            centra = k[1]
            if network_type==1:
                item = BetweenessCentralityUser(topic, date, windowsize, rank, uid, centra)
                item_exist = db.session.query(BetweenessCentralityUser).filter(BetweenessCentralityUser.topic==topic ,\
                                                                               BetweenessCentralityUser.date==date ,\
                                                                               BetweenessCentralityUser.windowsize==windowsize ,\
                                                                               BetweenessCentralityUser.userid==uid).first()
            else:
                item = DsBetweenessCentralityUser(topic, date, windowsize, rank, uid, centra)
                item_exist = db.session.query(DsBetweenessCentralityUser).filter(DsBetweenessCentralityUser.topic==topic ,\
                                                                                 DsBetweenessCentralityUser.date==date ,\
                                                                                 DsBetweenessCentralityUser.windowsize==windowsize ,\
                                                                                 DsBetweenessCentralityUser.userid==uid).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
            db.session.commit()
    elif classname == 'closeness_centrality':
        rank = 0
        for k in sorted_dict:
            rank += 1
            uid = k[0]
            centra = k[1]
            if network_type==1:
                item = ClosenessCentralityUser(topic, date, windowsize, rank, uid, centra)
                item_exist = db.session.query(ClosenessCentralityUser).filter(ClosenessCentralityUser.topic==topic ,\
                                                                              ClosenessCentralityUser.date==date ,\
                                                                              ClosenessCentralityUser.windowsize==windowsize ,\
                                                                              ClosenessCentralityUser.userid==uid).first()
            else:
                item = DsClosenessCentralityUser(topic, date, windowsize, rank, uid, centra)
                item_exist = db.session.query(DsClosenessCentralityUser).filter(DsClosenessCentralityUser.topic==topic ,\
                                                                                DsClosenessCentralityUser.date==date ,\
                                                                                DsClosenessCentralityUser.windowsize==windowsize ,\
                                                                                DsClosenessCentralityUser.userid==uid).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
            db.session.commit()

    print 'save success:', classname

def save_quota(key, value):
    #print 'key, value:', key.encode('utf-8'), value
    try:
        ssdb = SSDB(SSDB_HOST, SSDB_PORT)
        if ssdb:
            print 'ssdb yes'
        else:
            print 'ssdb no'
        result = ssdb.request('set',[key, value])
        if result.code == 'ok':
            print '6666666'
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), 'save success', key.encode('utf-8'),value
        else:
            print '777777'
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), 'save failed'
    except Exception, e:
        print '******'
        print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'SSDB ERROR'
