#-*- coding: utf-8 -*-

'''
输入为make_network生成的网络结构
输出为trendsetter_rank的结果
执行步骤：
1) 根据网络结构计算向量s1(v), s2(u,v)
2）根据网络结构写入tmp_file
tmp_file内容结构：
tmp_file的形式是：
node(v)  In_node(v)=set{w|(w,v)} s1(v)  s2(u,v)
3) 生成TS的hadoop任务编号,将任务编号和迭代次数以及tmp_file文件路径以及计算的s1(v), s2(u,v)作为输入参数传递给Trendsetter_rank
4) TS-----{map,reduce}
5）将TS value存入mysql
'''
import sys
import json
import tempfile
import math
import networkx as nx
from config import db
from hadoop_utils import generate_job_id
from TrendsetterRank import ts_rank
from utils import read_attribute_dict, read_graph
from model import TsRank
from utils import acquire_user_by_id
sys.path.append('../')
from time_utils import datetime2ts, window2time, ts2datetimestr

DEFAULT_INTERVAL = 3600
ALPHA = 86400.0
ts_netwrok_type = 3
Trendsetter_iter_max = 1
GRAPH_PATH = '/home/ubuntu4/huxiaoqian/mcase/graph/'

def trendsetter_rank(TOPK, date, topic_id, windowsize, topic, real_topic_id):
    data = None
    key = str(real_topic_id) + '_' + str(date) + '_' + str(windowsize)
    ds_g = nx.read_gexf(str(GRAPH_PATH) + str(key) + '_ds_dg_graph.gexf')
    tmp_file, ds_N = prepare_data_for_ts(topic_id, topic, date, windowsize, ds_g)
    top_N = ds_N # 选择保存TS前top_N的数据
    print 'trendsetter rank start'
    if not tmp_file:
        return data

    input_tmp_path = tmp_file.name
    print 'input_tmp_path:', input_tmp_path
    job_id = generate_job_id(datetime2ts(date), windowsize, topic_id, ts_netwrok_type) # pagerank中g与ds_g分别对应的network_type分别为1,2.Trendsetter_rank为3
    print 'job_id:', job_id

    iter_count = Trendsetter_iter_max # ???迭代的最大次数---PageRank的迭代次数设置为1
    print 'trendsetter rank direct_superior_network'
    ds_sorted_uids, ds_all_uid_tr = ts_rank(job_id, iter_count, input_tmp_path, top_N)
    print 'save trendsetter rank result'
    print 'len(ds_sorted_uids):', len(ds_sorted_uids)
    print 'len(ds_all_uid_tr):', len(ds_all_uid_tr)
    data = save_tr_results(topic, date, windowsize, ds_sorted_uids, ds_all_uid_tr)

    return ds_all_uid_tr, data # 标识保存是否成功    

def prepare_data_for_ts(topic_id, topic, date, windowsize, ds_g):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    if not topic:
        return None
    ds_N = len(ds_g)
    print 'topic trendsetter_rank network size %s' % ds_N
    if not ds_N:
        return None
    print 'start tmp_file'
    tmp_file = write_tmp_file(tmp_file, ds_g, ds_N)
    print 'end tmp_file'

    return tmp_file, ds_N
    

def write_tmp_file(tmp_file, ds_g, ds_N): # 这里要重新写，要组成(node, outlinks)应该是从node出来的等够到达的点的集合
    ds_new_attribute_dict = read_attribute_dict('ds_g')
    #new_attribute_dict = read_attribute_dict('g')
    #new_attribute_dict = json.loads(new_attribute_dict)
    #print 'len(new_attribute_dict):', len(new_attribute_dict.keys())
    ds_new_attribute_dict = json.loads(ds_new_attribute_dict)
    for node in ds_g.nodes():
        outlinks = ds_g.out_edges(nbunch=[node]) # 找到节点node对应的direct_superior_user
        if not outlinks:
            value = 'tr_results,%s,%s' % (1.0 / ds_N, ds_N)
            tmp_file.write('%s\t%s\n' % (node, value))
        else:
            outlinks_list = compute_s2(node, outlinks, ds_new_attribute_dict)
            outlinks_str = ','.join(outlinks_list)
            value = 'tr_results,%s,%s,' % (1.0 / ds_N, ds_N)  # value=pr_results,1/n,n,str(uid1),str(i(uid1,v)),str(uid2),str(i(uid2,v))
            value += outlinks_str
            tmp_file.write('%s\t%s\n' % (node, value))
        print '(node,value):', node, value
    tmp_file.flush()
    
    return tmp_file

def compute_s2(node, outlinks, ds_new_attribute_dict): # 需要再考虑考虑！！！
    outlinks_list = [] # ['node_u1, i(u1,v)', 'node_u2, i(u2,v)'...]
    #print 'node:', node, type(node)
    #print 'len(ds_new_attibute_dict):', len(ds_new_attribute_dict.keys())
    #print 'ds_new_attribute_dict:', ds_new_attribute_dict
    #node_info = ds_new_attribute_dict[node]
    #print 'node_info:', node_info
    node_timestamp = ds_new_attribute_dict[node][0][4]
    for out_node in outlinks:
        direct_superior_user = out_node[1]
        node_attribute = ds_new_attribute_dict[node]
        for attribute in node_attribute:
            i = None
            #print 'attribute:',attribute[5], type(attribute[5])
            #print 'direct_superior_user:', direct_superior_user, type(direct_superior_user)
            if attribute[5]==int(direct_superior_user):
                #print 'yes'
                try:
                    #print 'direct_superior_user_info:', ds_new_attribute_dict[direct_superior_user]
                    dsu_timestamp = ds_new_attribute_dict[direct_superior_user][0][4]
                    dt = dsu_timestamp - node_timestamp
                except KeyError:
                    dt = DEFAULT_INTERVAL
                #dt = dsu_timestamp - node_timestamp
                #print 'dt:',dt
                i = math.exp(-dt / ALPHA)
            else:
                continue
        #i = math.exp(-dt / ALPHA) # 需要不需要做标准化？！！！！
        if not i:
            i = math.exp(-DEFAULT_INTERVAL / ALPHA)
        print 'i:', i
        outlinks_element = str(direct_superior_user) + '+' + str(i)
        outlinks_list.append(outlinks_element)
    
    return outlinks_list
    
def save_tr_results(topic, date, windowsize, ds_sorted_uids, ds_all_uid_tr):
    #存直接上级转发网路trendsetter_rank的结果
    data = {}
    rank = 1
    count = 0
    exist_items = db.session.query(TsRank).filter(TsRank.topic==topic ,\
                                                  TsRank.date==date ,\
                                                  TsRank.windowsize==windowsize).all()
    for item in exist_items:
        db.session.delete(item)
    db.session.commit
    for uid in ds_sorted_uids:
        tr = ds_all_uid_tr[uid]
        user = acquire_user_by_id(uid)
        count += 1
        if not user:
            name = '未知'
            location = '未知'
            count1 = '未知'
            count2 = '未知'
        else:
            name = user['name']
            location = user['location']
            count1 = user['count1']
            count2 = user['count2']
        #row = (rank, uid, name, location, count1, count2)
        item = TsRank(topic, rank, uid, date, windowsize, tr)
        data[uid] = rank
        db.session.add(item)
        rank += 1
    db.session.commit()
    print 'success save trendsetter_rank value'
    print 'len(data):', len(data)
    return data
    
if __name__=='__main__':
    topic_id = 7
    TOPK = 10000
    date = '2013-09-08'
    window_size = 6
    topicname = u'东盟,博览会'
    real_topic_id = 227
    trendsetter_rank(TOPK, date, topic_id, window_size, topicname, real_topic_id)
    
    
    
