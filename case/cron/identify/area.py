# -*- coding: utf-8 -*-

import tempfile
import operator

import networkx as nx

from time_utils import datetime2ts, window2time, ts2datetimestr
from hadoop_utils import generate_job_id
from utils import save_rank_results, acquire_topic_name, is_in_trash_list, acquire_user_by_id, read_key_users
from pagerank_config import PAGERANK_ITER_MAX # 默认值为1

from config import xapian_search_user as user_search
from dynamic_xapian_weibo import getXapianWeiboByDuration

from pagerank import pagerank

from gexf import Gexf
from lxml import etree

from gquota import compute_quota

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24

def degree_rank(top_n, date, topic_id, window_size):
    data = []
    degree = prepare_data_for_degree(topic_id, date, window_size)

    if not degree:
        return data

    sorted_degree = sorted(degree.iteritems(), key=operator.itemgetter(1), reverse=True)
    sorted_uids = []
    count = 0
    for uid, value in sorted_degree: # 获得top_n的u_id
        if count >= top_n:
            break
        sorted_uids.append(uid)
        count += 1
    topicname = acquire_topic_name(topic_id)
    if not topicname:
        return data
    data = save_rank_results(sorted_uids, 'topic', 'degree', date, window_size, topicname) # 存储结构变为SSDB---改
    return data

def pagerank_rank(top_n, date, topic_id, window_size):
    data = []

    tmp_file = prepare_data_for_pr(topic_id, date, window_size)

    if not tmp_file:
        return data

    input_tmp_path = tmp_file.name
    
    job_id = generate_job_id(datetime2ts(date), window_size, topic_id) # 将其转换为'%s_%s_%s'的形式
    iter_count = PAGERANK_ITER_MAX

    sorted_uids = pagerank(job_id, iter_count, input_tmp_path, top_n) # 排序的uid的序列

    topicname = acquire_topic_name(topic_id)
    if not topicname:
        return data

    data = save_rank_results(sorted_uids, 'topic', 'pagerank', date, window_size, topicname)

    return data

def prepare_data_for_degree(topic_id, date, window_size): 
    topic = acquire_topic_name(topic_id) # 将topic_id>>topic_name
    if not topic:
        return None

    g = make_network(topic, date, window_size)

    if not g:
        return None

    N = len(g.nodes()) 
    print 'topic network size %s' % N

    if not N:
        return None

    return g.degree() # 返回所有节点的度

def prepare_data_for_pr(topic_id, date, window_size): # ？？？为什么把方向破坏了
    tmp_file = tempfile.NamedTemporaryFile(delete=False) # 用来做什么？！----存放pagerank计算过程生成的value数据？

    topic = acquire_topic_name(topic_id)
    if not topic:
        return None

    g = make_network(topic, date, window_size)

    if not g:
        return None

    N = len(g.nodes())
    print 'topic network size %s' % N

    if not N:
        return None

    for node in g.nodes(): # 
        outlinks = g.out_edges(nbunch=[node]) # outlinks=[(node,node1),(node,node2)...] 这里不涉及方向，node1是与node联通的店
        outlinks = map(str, [n2 for n1, n2 in outlinks]) # [str(node1),str(node2),str(node3)]
        if not outlinks:
            value = 'pr_results,%s,%s' % (1.0/N, N) # 虚构出强连通图，影响力1/n
            tmp_file.write('%s\t%s\n' % (node, value))
        else:
            outlinks_str = ','.join(outlinks)
            value = 'pr_results,%s,%s,' % (1.0/N, N)
            value += outlinks_str # value=pr_results,1/n,n,str(uid1),str(uid2)
            tmp_file.write('%s\t%s\n' % (node, value))

    tmp_file.flush() # 强制提交内存中还未提交的内容
    return tmp_file

def make_network_graph(current_date, topic_id, topic, window_size, key_user_labeled=True):
    date = current_date

    if key_user_labeled:
        key_users = read_key_users(current_date, window_size, topic, top_n=10)
    else:
        key_users = []

    #topic = acquire_topic_name(topic_id)
    #if not topic:
    #    return None
              
    G = make_network(topic, date, window_size)

    N = len(G.nodes())

    if not N:
        return ''

    node_degree = nx.degree(G)

    G = cut_network(G, node_degree) # 筛选出节点数>=2的节点数
    
    print 'start computing quota'
    compute_quota(G) # compute quota
    print 'quota computed complicated'

    gexf = Gexf("Yang Han", "Topic Network")

    node_id = {}
    graph = gexf.addGraph("directed", "static", "demp graph")
    graph.addNodeAttribute('name', type='string', force_id='name')
    graph.addNodeAttribute('location', type='string', force_id='location') # 添加地理位置属性
    graph.addNodeAttribute('timestamp', type='int', force_id='timestamp')

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
        user_info = acquire_user_by_id(uid) # 获取对应的用户信息，添加属性
        if user_info:
            _node.addAttribute('name', user_info['name'])
            _node.addAttribute('location', user_info['location'])
        else:
            _node.addAttribute('name', 'Unknown')
            _node.addAttribute('location', 'Unknown')
        #_node.addAttribute('timestamp', str(uid_ts[uid]))

    for edge in G.edges():
        start, end = edge # (repost_uid, source_uid)----顺序好像反着的？！
        start_id = node_id[start]
        end_id = node_id[end]
        graph.addEdge(str(edge_counter), str(start_id), str(end_id))
        edge_counter += 1

    return etree.tostring(gexf.getXML(), pretty_print=True, encoding='utf-8', xml_declaration=True) # 生成序列化字符串

def cut_network(g, node_degree): # 筛选出节点度数大于等于2的节点，作为绘图的展示节点
    degree_threshold = 2
    for node in g.nodes():
        degree = node_degree[node]
        if degree < degree_threshold:
            g.remove_node(node)
    return g


def getXapianweiboByTs(start_time, end_time): # 将查询时间段转化为每一天时间戳组成的字符串，获取时间段内的微博
    xapian_date_list =[]
    days = (int(end_time) - int(start_time)) / Day

    for i in range(0, days):
        _ts = start_time + i * Day
        xapian_date_list.append(ts2datetimestr(_ts))

    statuses_search = getXapianWeiboByDuration(xapian_date_list)
    return statuses_search


def make_network(topic, date, window_size, max_size=100000):
    end_time = datetime2ts(date)
    start_time = end_time - window2time(window_size)

    statuses_search = getXapianweiboByTs(start_time, end_time) # 获得查询时间段的XapianSearch类

    g = nx.DiGraph() # 初始化一个有向图

    #need repost index
    query_dict = {'text': topic, 'timestamp': {'$gt': start_time, '$lt': end_time}}

    count, get_statuses_results = statuses_search.search(query=query_dict, field=['user', 'retweeted_uid'], max_offset=max_size)
    print 'topic statuses count %s' % count

    for status in get_statuses_results():
        try:
            if status['retweeted_uid'] and status['retweeted_uid'] != 0:
                repost_uid = status['user']
                source_uid = status['retweeted_uid']
                if is_in_trash_list(repost_uid) or is_in_trash_list(source_uid):
                    continue
                g.add_edge(repost_uid, source_uid) # 将所有topic相关的uid作为node，并将它们按照信息传递方向形成有向图
        except (TypeError, KeyError):
            continue
    return g
