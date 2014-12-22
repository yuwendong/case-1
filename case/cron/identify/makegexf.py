# -*- coding: utf-8 -*-

import json
import networkx as nx
from gexf import Gexf
from utils import acquire_user_by_id


def make_gexf(gexf_name_1, gexf_name_2, G, node_degree, key_users, all_uid_pr, pr_data, partition, new_attribute_dict):
    gexf = Gexf(gexf_name_1, gexf_name_2)

    node_id = {}
    graph = gexf.addGraph("directed", "static", "demp graph")
    graph.addNodeAttribute('name', type='string', force_id='name')
    graph.addNodeAttribute('location', type='string', force_id='location') # 添加地理位置属性
    graph.addNodeAttribute('timestamp', type='int', force_id='timestamp')
    graph.addNodeAttribute('pagerank', type='string', force_id='pagerank')
    graph.addNodeAttribute('acategory', type='string', force_id='acategory')
    graph.addNodeAttribute('text', type='string', force_id='text')
    graph.addNodeAttribute('reposts_count', type='string', force_id='reposts_count') # 新添加的属性
    graph.addNodeAttribute('comments_count', type='string', force_id='comments_count')
    graph.addNodeAttribute('attitude_count', type='string', force_id='attitude_count')
    graph.addNodeAttribute('rank_pr', type='string', force_id='rank_pr') # 用户的pagerank值对应的排名
    pos = nx.spring_layout(G) # 定义一个布局 pos={node:[v...]/(v...)}

    node_counter = 0
    edge_counter = 0

    for node in G.nodes():
        x, y = pos[node] # 返回位置(x,y)
        degree = node_degree[node]
        if node not in node_id: # {node:排名}
            node_id[node] = node_counter
            node_counter += 1
        uid = node # 节点就是用户名
        if uid in key_users: # 根据是否为关键用户添加不同的节点 
            _node = graph.addNode(node_id[node], str(node), x=str(x), y=str(y), z='0', r='255', g='51', b='51', size=str(degree))
        else:
            _node = graph.addNode(node_id[node], str(node), x=str(x), y=str(y), z='0', r='0', g='204', b='204', size=str(degree))
        cluster_id = str(partition[node])
        _node.addAttribute('acategory', cluster_id)
        #print 'al_uid_pr:', all_uid_pr
        pr = str(all_uid_pr[str(uid)])
        _node.addAttribute('pagerank', pr)
        rank = pr_data[uid]
        _node.addAttribute('rank_pr', str(rank))
        #print 'pagarank_uid:', uid
        try:
            text_add = new_attribute_dict[uid][0][0] # 添加节点属性--text
            _node.addAttribute('text', json.dumps(text_add))
            reposts_count_add = i2u(new_attribute_dict[uid][0][1])
            _node.addAttribute('reposts_count', reposts_count_add) # 添加节点属性--reposts_count
            comment_count_add = i2u(new_attribute_dict[uid][0][2])
            _node.addAttribute('comments_count', comment_count_add) # 添加节点属性--comment_count
            attitude_count_add = i2u(new_attribute_dict[uid][0][3])
            if attitude_count_add == None:
                attitude_count_add = u'未知'
            _node.addAttribute('attitude_count', i2u(attitude_count_add)) # 添加节点属性--attitude_count
        except KeyError:
            _node.addAttribute('text', u'未知')
            _node.addAttribute('reposts_count', u'未知')
            _node.addAttribute('comments_count', u'未知')
            _node.addAttribute('attitude_count', u'未知')
        user_info = acquire_user_by_id(uid) # 获取对应的用户信息，添加属性
        if user_info:
            _node.addAttribute('name', user_info['name'])
            _node.addAttribute('location', user_info['location'])
        else:
            _node.addAttribute('name', u'未知')
            _node.addAttribute('location', u'未知')
            #_node.addAttribute('timestamp', str(uid_ts[uid]))

    for edge in G.edges():
        start, end = edge # (repost_uid, source_uid)
        start_id = node_id[start]
        end_id = node_id[end]
        graph.addEdge(str(edge_counter), str(start_id), str(end_id))
        edge_counter += 1

    return gexf

def i2u(s):
    if isinstance(s, unicode):
        return s
    else:
        return str(s)

def make_ds_gexf(gexf_name_1, gexf_name_2, G, node_degree, pr_key_users, all_uid_pr, ds_pr_data, partition, ds_new_attribute_dict):
    gexf = Gexf(gexf_name_1, gexf_name_2)

    node_id = {}
    graph = gexf.addGraph('directed', 'static', 'demp graph')
    graph.addNodeAttribute('name', type='string', force_id='name')
    graph.addNodeAttribute('location', type='string', force_id='location')
    graph.addNodeAttribute('timestamp', type='string', force_id='timestamp')
    graph.addNodeAttribute('pagerank', type='float', force_id='pagerank')
    #graph.addNodeAttribute('trendsetter_rank', type='float', force_id='trendsetter_rank')
    graph.addNodeAttribute('acategory', type='string', force_id='acategory')
    graph.addNodeAttribute('text', type='string', force_id='text')
    graph.addNodeAttribute('reposts_count', type='string', force_id='reposts_count')
    graph.addNodeAttribute('comments_count', type='string', force_id='comments_count')
    graph.addNodeAttribute('attitude_count', type='string', force_id='attitude_count')
    graph.addNodeAttribute('rank_pr', type='string', force_id='rank_pr')
    #graph.addNodeAttribute('rank_tr', type='string', force_id='rank_tr')

    pos = nx.spring_layout(G)

    node_counter = 0
    edge_counter = 0

    for node in G.nodes():
        x, y = pos[node]
        degree = node_degree[node]
        if node not in node_id: # 判断该节点是否已经加入到图中
            node_id[node] = node_counter
            node_counter += 1
        uid = node # 节点就是用户名
        if uid in pr_key_users:
            _node = graph.addNode(node_id[node], str(node), x=str(x), y=str(y), z='0', r='255', g='51', b='51', size=str(degree))
        else:
            _node = graph.addNode(node_id[node], str(node), x=str(x), y=str(y), z='0', r='0', g='204', b='204', size=str(degree))
        cluster_id = str(partition[node])
        _node.addAttribute('acategory', cluster_id)
        pr = str(all_uid_pr[str(uid)])
        _node.addAttribute('pagerank', pr)
        #print 'all_uid_tr:', all_uid_tr
        #print 'all_uid_pr:', all_uid_pr
        #tr = str(all_uid_tr[str(uid)])
        #_node.addAttribute('trendsetter_rank', tr)
        rank_pr = ds_pr_data[uid]
        _node.addAttribute('rank_pr', str(rank_pr))
        #rank_tr = ds_tr_data[uid]
        #_node.addAttribute('rank_tr', str(rank_tr))
        try:
            text_add = ds_new_attribute_dict[uid][0][0]
            _node.addAttribute('text', json.dumps(text_add))
            reposts_count_add = i2u(ds_new_attribute_dict[uid][0][1])
            _node.addAttribute('reposts_count', reposts_count_add)
            comment_count_add = i2u(ds_new_attribute_dict[uid][0][2])
            _node.addAttribute('comments_count', comment_count_add)
            attitude_count_add = i2u(ds_new_attribute_dict[uid][0][3])
            if attitude_count_add == None:
                attitude_count_add = u'未知'
            _node.addAttribute('attitude_count', i2u(attitude_count_add))
            timestamp_add = i2u(ds_new_attribute_dict[uid][0][4])
            _node.addAttribute('timestamp', timestamp_add)
        except KeyError:
            _node.addAttribute('text', u'未知')
            _node.addAttribute('reposts_count', u'未知')
            _node.addAttribute('comments_count', u'未知')
            _node.addAttribute('attitude_count', u'未知')
            _node.addAttribute('timestamp', u'未知')
        user_info = acquire_user_by_id(uid) # 获取对应的用户信息，添加属性
        if user_info:
            _node.addAttribute('name', user_info['name'])
            _node.addAttribute('location', user_info['location'])
        else:
            _node.addAttribute('name', u'未知')
            _node.addAttribute('location', u'未知')


    for edge in G.edges():
        start, end = edge # (repost_uid, source_uid)
        start_id = node_id[start]
        end_id = node_id[end]
        graph.addEdge(str(edge_counter), str(start_id), str(end_id))
        edge_counter += 1

    return gexf
            
