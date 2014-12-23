# -*- coding: utf-8 -*-

import re
import sys
import json
import tempfile
import operator
from gexf import Gexf
from lxml import etree
import networkx as nx

from gquota import compute_quota
from localbridge import GetLocalBridge
from snowball1 import SnowballSampling
# from hadoop_utils import generate_job_id
from makegexf import make_gexf, make_ds_gexf
from spam.pagerank import pagerank
from pagerank_config import PAGERANK_ITER_MAX # 默认值为1
from direct_superior_network import get_superior_userid # 获得直接上级转发网络
from utils import save_rank_results, save_ds_rank_results, acquire_topic_name, \
        is_in_trash_list, acquire_user_by_id, read_key_users, ds_read_key_users, \
        read_graph, read_attribute_dict

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../../')
from ad_filter import ad_classifier
from time_utils import datetime2ts, window2time, ts2datetimestr
from global_config import xapian_search_user as user_search
from dynamic_xapian_weibo import getXapianWeiboByTopic


search_topic_id ='545f4c22cf198b18c57b8014'
Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
DEFAULT_INTERVAL = 1 * Hour
SixHour = Hour * 6
Day = Hour * 24
network_type = 1
ds_network_type = 2
GRAPH_PATH = '/home/ubuntu4/huxiaoqian/mcase/graph/'


def pagerank_rank(top_n, date, topic_id, window_size, topicname, real_topic_id):
    data = []

    tmp_file, N, ds_tmp_file, ds_N = prepare_data_for_pr(topic_id, date, window_size, topicname, real_topic_id)
    top_n = N
    ds_top_n = ds_N
    print 'page_rank start'
    if not tmp_file or not ds_tmp_file:
        return data

    input_tmp_path = tmp_file.name
    ds_input_tmp_path = ds_tmp_file.name
    print input_tmp_path, ds_input_tmp_path

    iter_count = PAGERANK_ITER_MAX
    print 'pagerank_source_network'
    sorted_uids, all_uid_pr = pagerank(iter_count, input_tmp_path, top_n) # 排序的uid的序列
    print 'pagerank_direct_superior_network'
    ds_sorted_uids, ds_all_uid_pr = pagerank(iter_count, ds_input_tmp_path, ds_top_n)
    print 'top_n:', top_n
    #print 'len(sorted_uid):', len(sorted_uids)
    print 'ds_top_n:', ds_top_n
    topicname = acquire_topic_name(topic_id)
    print 'topicname:', topicname
    if not topicname:
        return data
    print 'save_rank_results'
    data = save_rank_results(sorted_uids, 'topic', 'spark_pagerank', date, window_size, topicname, all_uid_pr)
    ds_data = save_ds_rank_results(ds_sorted_uids, 'topic', 'spark_pagerank', date, window_size, topicname, ds_all_uid_pr)

    return all_uid_pr, ds_all_uid_pr, data, ds_data

def prepare_data_for_pr(topic_id, date, window_size, topicname, real_topic_id):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    ds_tmp_file = tempfile.NamedTemporaryFile(delete=False)

    topic = topicname
    if not topic:
        return None

    #g, gg, new_attribute_dict, ds_dg, ds_udg, ds_new_attribute_dict= make_network(topic, date, window_size, attribute_add=False)
    key = str(real_topic_id) + '_' + str(date) + '_' + str(window_size)
    g = nx.read_gexf(str(GRAPH_PATH)+str(key)+'_g_graph.gexf')
    ds_dg = nx.read_gexf(str(GRAPH_PATH)+str(key)+'_ds_dg_graph.gexf')

    if not g or not ds_dg:
        return None

    N = len(g)
    print 'topic source network size %s' % N
    ds_N = len(ds_dg)
    print 'topic direct superior network size %s' % ds_N

    if not N or not ds_N:
        return None
    '''
    在临时文件中存放网络结构，将写入临时文件的过程写为方法write_tmp_file
    '''
    print 'start PageRank tmp_file, ds_tmp_file'
    tmp_file = write_tmp_file(tmp_file, g, N)
    ds_tmp_file = write_tmp_file(ds_tmp_file, ds_dg, ds_N)
    print 'end PageRank tmp_file, ds_tmp_file'
    return tmp_file, N, ds_tmp_file, ds_N

def write_tmp_file(tmp_file, g, N):
    for node in g.nodes():
        outlinks = g.out_edges(nbunch=[node]) # outlinks=[(node,node1),(node,node2)...] 这里不涉及方向，node1是与node联通的店
        outlinks = map(str, [n2 for n1, n2 in outlinks]) # [str(node1),str(node2),str(node3)]
        if not outlinks:
            pass
            # value = 'pr_results,%s,%s' % (1.0/N, N) # 虚构出强连通图，影响力1/n
            # tmp_file.write('%s\t%s\n' % (node, value))
        else:
            for outlink in outlinks:
                tmp_file.write('%s\t%s\n' % (node, outlink))
            # outlinks_str = ','.join(outlinks)
            # value = 'pr_results,%s,%s,' % (1.0/N, N)
            # value += outlinks_str # value=pr_results,1/n,n,str(uid1),str(uid2)
            # tmp_file.write('%s\t%s\n' % (node, value))

    tmp_file.flush() # 强制提交内存中还未提交的内容

    return tmp_file   

def _utf8_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, 'utf-8')


def make_network_graph(current_date, topic_id, topic, window_size, all_uid_pr, pr_data, ds_all_uid_pr, ds_pr_data,  real_topic_id, key_user_labeled=True):
    date = current_date
    '''
    key_users对应的是源头转发网络的pagerank前10的用户，ds_key_users对应的是直接上级转发网络的pagerank前10的用户
    '''
    if key_user_labeled:
        key_users = read_key_users(current_date, window_size, topic, top_n=10)
        ds_key_users = ds_read_key_users(current_date, window_size, topic ,top_n=10)
        #ds_tr_key_users = ds_tr_read_key_users(current_date, window_size, topic, top_n=10)
    else:
        key_users = []
        ds_key_users = []
        #ds_tr_key_users = []
    '''
    读取图结构，并从数据库中获取new_attribute_dict, ds_new_attribute_dict
    '''
    key = str(real_topic_id) + '_' + str(date) + '_' + str(window_size)
    G = nx.read_gexf(str(GRAPH_PATH)+str(key)+'_g_graph.gexf')
    gg = nx.read_gexf(str(GRAPH_PATH)+str(key)+'_gg_graph.gexf')
    ds_dg = nx.read_gexf(str(GRAPH_PATH)+str(key)+'_ds_dg_graph.gexf')
    ds_udg = nx.read_gexf(str(GRAPH_PATH)+str(key)+'_ds_udg_graph.gexf')

    new_attribute_dict = json.loads(read_attribute_dict('g'))
    ds_new_attribute_dict = json.loads(read_attribute_dict('ds_g'))
    # community detection, http://perso.crans.org/aynaud/communities/, undirected graph
    import community
    
    N = len(G)
    print 'len_G_N:', N
    ds_N = len(ds_dg)
    print 'len_ds_dg_N:', ds_N
    if (not N) or (not ds_N):
        return ''
    
    node_degree = nx.degree(G)
    ds_node_degree = nx.degree(ds_dg)
    G.remove_edges_from(G.selfloop_edges())
    gg.remove_edges_from(gg.selfloop_edges())
    ds_dg.remove_edges_from(ds_dg.selfloop_edges())
    ds_udg.remove_edges_from(ds_udg.selfloop_edges())

    
    G = cut_network(G, nx.degree(G), 1) # 筛选出度数大于等于1的节点数
    gg = cut_network(gg, nx.degree(gg), 1)
    ds_dg = cut_network(ds_dg, nx.degree(ds_dg), 1)
    ds_udg = cut_network(ds_udg, nx.degree(ds_udg), 1)
    
    print 'after cut_network:'
    print 'len(G):', len(G)
    print 'len(ds_dg):', len(ds_dg)
    p_gg = nx.read_gexf(str(GRAPH_PATH)+str(key)+'_gg_graph.gexf')
    p_ds_udg = nx.read_gexf(str(GRAPH_PATH)+str(key)+'_ds_udg_graph.gexf')
    partition = community.best_partition(p_gg)
    ds_partition = community.best_partition(p_ds_udg) # 将直接上级转发网络进行社区划分！！！！！！！！！！！！
    
    
    print 'start snowball sampling'
    #new_G, new_gg = SnowballSampling(G, gg, topic, network_type)
    #ds_new_G, ds_new_gg = SnowballSampling(ds_dg, ds_udg, topic, ds_network_type)
    print 'sampling complicated'
    
    # Local Bridge的算法需要提升效率，此处先不显示
    '''
    print 'get local bridge start:'
    GetLocalBridge(gg)
    GetLocalBridge(ds_udg)
    print 'local bridge complicated'
    '''
    print 'start computing quota'
    new_G = G
    new_gg = gg
    ds_new_G = ds_dg
    ds_new_gg = ds_udg
    compute_quota(new_G, new_gg, date, window_size, topic, all_uid_pr, network_type) # compute quota
    compute_quota(ds_new_G, ds_new_gg, date, window_size, topic, ds_all_uid_pr, ds_network_type)
    print 'quota computed complicated'

    # 生成gexf文件
    '''
    将生成gexf文件的部分作为一个函数，将相关的参数传入。以此简洁化两个不同不同网络的gexf生成过程
    '''
    gexf = make_gexf('hxq', 'Source Network', new_G, node_degree, key_users, all_uid_pr, pr_data , partition, new_attribute_dict)
    ds_gexf = make_ds_gexf('hxq', 'Direct Superior Network', ds_new_G, ds_node_degree, ds_key_users, ds_all_uid_pr, ds_pr_data, ds_partition, ds_new_attribute_dict)
    '''
    gexf = Gexf("Yang Han", "Topic Network")

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
        #print 'pagarank_uid:', uid
        try:
            text_add = new_attribute_dict[uid][0][0] # 添加节点属性--text
            _node.addAttribute('text', json.dumps(text_add))
            reposts_count_add = new_attribute_dict[uid][0][1]
            _node.addAttribute('reposts_count', str(reposts_count_add)) # 添加节点属性--reposts_count
            comment_count_add = new_attribute_dict[uid][0][2]
            _node.addAttribute('comments_count', str(comment_count_add)) # 添加节点属性--comment_count
            attitude_count_add = new_attribute_dict[uid][0][3]
            if attitude_count_add == None:
                attitude_count_add = u'未知'
            _node.addAttribute('attitude_count', attitude_count_add) # 添加节点属性--attitude_count
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
    '''

    return etree.tostring(gexf.getXML(), pretty_print=True, encoding='utf-8', xml_declaration=True), etree.tostring(ds_gexf.getXML(), pretty_print=True, encoding='utf-8', xml_declaration=True)# 生成序列化字符串

def cut_network(g, node_degree, degree_threshold): # 筛选出节点度数大于等于2的节点，作为绘图的展示节点
    # degree_threshold = 1
    for node in g.nodes():
        degree = node_degree[node]
        if degree < degree_threshold:
            g.remove_node(node)
    return g


def make_network(topic, date, window_size, max_size=100000, attribute_add = False):
    topics = topic.strip().split(',')
    end_time = int(datetime2ts(date))
    start_time = int(end_time - window2time(window_size))
    print 'start, end:', start_time, end_time
    topic_id='545f4c22cf198b18c57b8014'
    statuses_search = getXapianWeiboByTopic(topic_id)

    g = nx.DiGraph() # 初始化一个有向图
    gg = nx.Graph() # 为计算quota初始化一个无向图
    ds_dg = nx.DiGraph() # direct_superior_network 有向直接上级转发网络
    ds_udg = nx.Graph() # undirect_superior_network 无向直接上级转发网络
    query_dict = {'timestamp':{'$gt': start_time, '$lt': end_time}, 'topics':[]}
    #need repost index
    
    for ctopic in topics:
        query_dict['topics'].append(ctopic)
    
    print 'query_dict:', query_dict
    count, get_statuses_results = statuses_search.search(query=query_dict, fields=['_id', 'user', 'timestamp', 'retweeted_mid','retweeted_uid', 'text', 'reposts_count', 'comments_count', 'attitude_count'], max_offset=max_size)
    print 'count_before_nad:', count
    results_list = []
    '''
    根据微博文本进行广告微博筛选
    '''
    if count:
        for weibo in get_statuses_results():
            results_list.append([weibo['_id'],weibo['text']])
        scount, data_wid = ad_classifier(results_list)
    else:
        data_wid = []
        scount = 0
    print 'count_after_nad:', scount
    
    new_attribute_dict = {} # 星形源头转发网络需要添加的节点对应的text、reposts_count、comment_count、 attitude_count
    ds_new_attribute_dict = {} # 直接上级转发网络需要添加的属性：即节点对应的text、 reposts_count、 comment_count 、attitude_count    
    new_query_dict = {
        '$or':[]
        } # 用于查询retweeted_mid对应的weibo内容
    ds_new_query_dict ={
        '$or':[]
        } # 用于查询direct_superior_user为retweeted_uid对应的retweeted_mid的微博内容
    map_dict = {} # map_dict = {retweeted_mid:[retweeted_uid, user, timestamp],...} 保存_id timestamp与其对应的retweeted_mid之间的对应关系
    ds_map_dict = {} # ds_dict = {retweeted_mid:[retweeted_uid, user, timestamp]} 直接上级转发网络中直接上级就是源头上级时，对应关系
    for status in get_statuses_results():
        if str(status['_id']) in data_wid:
            '''
            当微博信息非垃圾时，进行new_attribute_dict的添加----即[a b]->添加a节点的微博信息
            '''
            nad_uid = status['user']
            nad_id = status['_id']
            r_uid = status['retweeted_uid']
            r_mid = status['retweeted_mid']
            if attribute_add == True:
                text_add = status['text']
                reposts_count_add = status['reposts_count']
                comment_count_add = status['comments_count']
                attitude_count_add = status['attitude_count']
                timestamp_add = status['timestamp']
                try:
                    new_attribute_dict[nad_uid].append([text_add, reposts_count_add, comment_count_add, attitude_count_add, timestamp_add, r_uid])
                    ds_new_attribute_dict[nad_uid].append([text_add, reposts_count_add, comment_count_add, attitude_count_add, timestamp_add, r_uid])
                except:
                    new_attribute_dict[nad_uid] = [[text_add, reposts_count_add, comment_count_add, attitude_count_add, timestamp_add, r_uid]]
                    ds_new_attribute_dict[nad_uid] = [[text_add, reposts_count_add, comment_count_add, attitude_count_add, timestamp_add, r_uid]]
            #print 'len(new_attribute_dict):', len(new_attribute_dict)
            '''
            区别于原创微博
            当是转发微博时，获取直接转发上级----例子：[a b c]->b
            '''
            if status['retweeted_uid'] and status['retweeted_uid']!=0:
                print 'before get_superior_userid'
                direct_superior_userid = get_superior_userid(status) # 获取直接转发上级--只获取一跳
                print 'user_id', direct_superior_userid
                if not direct_superior_userid:
                    '''
                    当直接转发上级的userid获取不到时，则认为直接转发上级就是源头转发微博
                    '''
                    direct_superior_userid = r_uid
                    ds_dg.add_edge(nad_uid, direct_superior_userid)
                    ds_udg.add_edge(nad_uid, direct_superior_userid)
                    ds_new_query_dict['$or'].append({'_id':r_mid})
                    ds_map_dict[r_mid] = [r_uid, nad_uid, status['timestamp']]
                    # 当直接上级就是源头上级时，通过查询xapian获取weibo_text timestamp comment_counts repost_counts attitude_counts
                else:
                    '''
                    存在直接转发上级
                    '''
                    ds_dg.add_edge(nad_uid, direct_superior_userid)
                    ds_udg.add_edge(nad_uid, direct_superior_userid)
                    if attribute_add == 'True':
                        weibo_text = status['text']
                        # 获取直接上级微博文本内容
                        weibo_test1 = weibo_text.split('//@') # 此处不会出现文本中没有//@结构，因为这里的直接转发上级是通过昵称转化而得到的，所以一定有//@结构
                        weibo_test2 = weibo_test1[1]
                        m_index = weibo_test2.find(':')
                        direct_superior_weibo = weibo_test2[m_index+1:]
                        m_all_index = weibo_text.find(':')
                        direct_superior_weibos = weibo_text[m_all_index+1:]
                        '''
                        需要根据文本内容和r_uid获取timestamp
                        '''
                        direct_superior_info = get_ds_info(direct_superior_weibos, direct_superior_userid, topic, timestamp_add) # timestamp_add是最终转发微博额时间戳
                        # 通过直接上级微博文本内容和用户id，查询topic对应的Xapian获取该条微博的时间戳等信息
                        # 如果在xapian中查不到这条信息的timestamp，则根据其转发链条关系，以（源头用户ts-重点用户ts）/（链条中人数-1）----源头微博还是需要根据mid查询，还是有可能不在xapian里面
                        # 根据uid和text获取[timestamp, comment_counts, attitude_counts, reposts_counts, r_uid]
                        timestamp = direct_superior_info['timestamp']
                        comment_count = direct_superior_info['comments_count']
                        attitude_count = direct_superior_info['attitude_count']
                        reposts_count = direct_superior_info['reposts_count']
                        retweeted_uid = direct_superior_info['retweeted_uid']
                        try:
                            ds_new_attribute_dict[direct_superior_userid].append([direct_superior_weibo, reposts_count, comment_count, attitude_count, timestamp, retweeted_uid])
                        except:
                            ds_new_attribute_dict[direct_superior_userid] = [[direct_superior_weibo, reposts_count, comment_count, attitude_count, timestamp, retweeted_uid]]

                print 'after get_superior_userid'     
            try:
                '''
                源头转发网络构建
                '''
                if status['retweeted_uid'] and status['retweeted_uid'] != 0:
                    repost_uid = status['user']
                    source_uid = status['retweeted_uid']
                    if is_in_trash_list(repost_uid) or is_in_trash_list(source_uid):
                        continue
                    g.add_edge(repost_uid, source_uid) # 将所有topic相关的uid作为node，并将它们按照信息传递方向形成有向图
                    gg.add_edge(repost_uid, source_uid)
                    new_query_dict['$or'].append({'_id':r_mid}) # 为了查询转发微博的内容
                    map_dict[r_mid] = [r_uid, nad_uid, status['timestamp']]
            except (TypeError, KeyError):
                continue
    print 'step_1:g', len(g)
    print 'step_1:ds_dg', len(ds_dg)
    
    # 这里还需要处理，由于根据mid查询xapian获取微博的时间戳，但是有可能会没有获取到。若没有获取到，使用check_attribude进行处理
    if attribute_add == True: # 将retweeted_uid用户的text等取出来，存在new_attribute_dict中
        ruid_count, r_results = statuses_search.search(query=new_query_dict, fields=['_id', 'user', 'timestamp', 'retweeted_mid','retweeted_uid', 'text', 'reposts_count', 'comments_count', 'attitude_count'])
        for rresult in r_results():
            text = rresult['text'] # 这里的text需要再做一次处理----剔除掉’//@..:‘的内容，只获取作者自己的微博文本
            text_spl = text.split('//@')
            try:
                text_add = text_spl[0]
            except:
                text_add = text
            timestamp_add = rresult['timestamp']
            reposts_count_add = rresult['reposts_count']
            comment_count_add = rresult['comments_count']
            attitude_count_add = rresult['attitude_count']
            ruid_add = rresult['retweeted_uid']
            try:
                new_attribute_dict[rresult['user']].append([text_add, reposts_count_add, comment_count_add, attitude_count_add, timestamp_add, ruid_add])
            except:
                new_attribute_dict[rresult['user']] = [[text_add, reposts_count_add, comment_count_add, attitude_count_add, timestamp_add, ruid_add]]
        #print 'map_dict:', map_dict
        new_attribute_dict = check_attribute(new_attribute_dict, new_query_dict, map_dict) # 对query_dict中没有查询到的r_mid,在new_attribute_dict中进行补全处理
        print 'quer_dict:', ds_new_query_dict
        print 'len(ds_new_attribute_dict):', len(ds_new_attribute_dict)
        if query_dict!={'$or':[]}:
            ds_ruid_count, ds_r_results = statuses_search.search(query=ds_new_query_dict, fields=['_id', 'user', 'timestamp', 'retweeted_mid','retweeted_uid', 'text', 'reposts_count', 'comments_count', 'attitude_count'])
            for ds_rresult in ds_r_results():
                uid = ds_rresult['user']
                timestamp_add = ds_rresult['timestamp']
                text = ds_rresult['text'] # 这里的text需要再做一次处理----剔除掉’//@..:‘的内容，只获取作者自己的微博文本
                text_spl = text.split('//@')
                try:
                    text_add = text_spl[0]
                except:
                    text_add = text
                reposts_count_add = ds_rresult['reposts_count']
                comment_count_add = ds_rresult['comments_count']
                attitude_count_add = ds_rresult['attitude_count']
                ruid_add = rresult['retweeted_uid']
                try:
                    ds_new_attribute_dict[uid].append([text_add, reposts_count_add, comment_count_add, attitude_count_add, timestamp_add, ruid_add])
                except:
                    ds_new_attribute_dict[uid] = [[text_add, reposts_count_add, comment_count_add, attitude_count_add, timestamp_add, ruid_add]]
        
        ds_new_attribute_dict = check_attribute(ds_new_attribute_dict, ds_new_query_dict, ds_map_dict)
    #print 'new_attribute_dict:', new_attribute_dict
    print 'len(g):', len(g)
    print 'len(ds_dg):', len(ds_dg)
    return g , gg, new_attribute_dict, ds_dg, ds_udg, ds_new_attribute_dict

def get_ds_info(text, userid, topic, timestamp_add, DEFAULT_INTERVAL): # timestamp_add 表示最终极转发用户发表微博的时间戳
    direct_superior_info = {}

    xapian_search_weibo = getXapianWeiboByTopic(search_topic_id)
    query_dict = {
        'user': userid ,
        'text': text
        }
    count, result = xapian_search_weibo.search(query=query_dict, fields=['timestamp', 'comments_count', 'attitude_count','reposts_count', 'retweeted_uid']) # result是一个生成器
    if result:
        for rr in result():
            direct_superior_info = rr
    else:
        direct_superior_info['timestamp'] = DEFAULT_INTERVAL + timestamp_add
        direct_superior_info['comments_count'] = u'未知'
        direct_superior_info['attitude_count'] = u'未知'
        direct_superior_info['reposts_count'] = u'未知'
        direct_superior_info['retweeted_uid'] = None

    return direct_superior_info

def check_attribute(attribute_dict , query_dict, map_dict): # 当批量查询没有获取到微博时间戳及三种count时，由该方法进行处理
    rmid_list = query_dict['$or']
    for rmid in rmid_list:
        #print 'rmid:', rmid
        r_mid = rmid['_id']
        ruid= map_dict[r_mid][0]
        try:
            attributes = attribute_dict[ruid]
        except KeyError:
            timestamp_add = map_dict[r_mid][2]
            attribute_dict[ruid] = [[u'未知', u'未知', u'未知', u'未知', DEFAULT_INTERVAL + timestamp_add, u'未知']]

    return attribute_dict

if __name__=='__main__':
    topic_id = 595
    TOPK = 10000
    date = '2013-09-08'
    window_size = 6
    topicname = u'东盟,博览会'
    real_topic_id = 227
    pagerank_rank(TOPK, date, topic_id, window_size, topicname, real_topic_id)
