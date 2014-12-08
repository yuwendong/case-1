# -*- coding: utf-8 -*-

import sys
import networkx as nx

from area import pagerank_rank, make_network, make_network_graph 
from topicStatus import _topic_not_calc, _update_topic_status2Computing, \
        _update_topic_status2Completed
from utils import acquire_topic_name, acquire_topic_id, \
        save_rank_results, save_gexf_results, save_attribute_dict, \
        acquire_real_topic_id

reload(sys)
sys.setdefaultencoding('utf-8')
from time_utils import ts2datetime, datetime2ts
from config import db #　用于测试期间，建立topicstatus这张表。待删
import time # 用于测试生成topicStatus入库时间，待删
from model import TopicStatus # 用于测试，待删
from lxml import etree
from get_first_user import get_first_node
# from trendsetter_rank import trendsetter_rank
from area import _utf8_unicode

TOPK = 1000
Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
gexf_type = 1
ds_gexf_type = 2
GRAPH_PATH = u'/home/ubuntu4/huxiaoqian/mcase/graph/'


def main():
    topics = _topic_not_calc() # topics=[{id:x,module:x,status:x,topic:x,start:x,end:x,db_date:x}]
    if topics and len(topics):
        topic = topics[0] # 每次只计算一个----为了做一个缓冲，每个n时间才计算一个
        print 'topic_id', topic.id
        start_ts = topic.start
        end_ts = topic.end
        db_date = topic.db_date
        topicname = topic.topic
        _update_topic_status2Computing(topicname, start_ts, end_ts, db_date)
        print 'update_status'
        topic_id = acquire_topic_id(topicname, start_ts, end_ts) # 重新获取id是因为TopicStatus中id是自增加的，进行更新后，id就不是原来的那一个了
        windowsize = (end_ts - start_ts) / Day # 确定时间跨度的大小
        date = ts2datetime(end_ts)

        print 'start compute first_nodes'
        start_date = ts2datetime(start_ts) # used to compute the first user
        get_first_node(topicname, start_date, date, windowsize)
        print 'end compute first_nodes'

        print 'start make network'
        g, gg, new_attribute_dict, ds_dg, ds_udg, ds_new_attribute_dict = make_network(topicname, date, windowsize, max_size=100000, attribute_add=True)
        print 'write gexf file'
        real_topic_id = acquire_real_topic_id(topicname, start_ts, end_ts)
        if not real_topic_id:
            print 'the topic not exist'
            return None
        key = str(real_topic_id) + '_' + str(date) + '_' + str(windowsize) 
        #print 'GRAPH_PATH:', GRAPH_PATH, type(GRAPH_PATH)
        #print 'key:', type(key)
        #print '_g_graph.gexf', type('_g_graph.gexf')
        print 'gexf_file:', str(GRAPH_PATH)+str(key)+'_g_graph.gexf'
        nx.write_gexf(g, str(GRAPH_PATH) + str(key) + '_g_graph.gexf')
        nx.write_gexf(gg, str(GRAPH_PATH) + str(key) + '_gg_graph.gexf')
        nx.write_gexf(ds_dg, str(GRAPH_PATH) + str(key) + '_ds_dg_graph.gexf')
        nx.write_gexf(ds_udg, str(GRAPH_PATH) + str(key) + '_ds_udg_graph.gexf')
        save_attribute_dict(new_attribute_dict, 'g')
        save_attribute_dict(ds_new_attribute_dict, 'ds_g')
        print 'end make network'

        print 'start PageRank'
        all_uid_pr, ds_all_uid_pr, data, ds_data = pagerank_rank(TOPK, date, topic_id, windowsize, topicname, real_topic_id)
        print 'end PageRank'

        #print 'start TrendSetter Rank'
        #ds_all_uid_tr, ds_tr_data = trendsetter_rank(TOPK, date, topic_id, windowsize, topicname, real_topic_id)
        #print 'end TrendSetter Rank'

        print 'start make network graph'
        topic_id = int(topic_id)
        windowsize = int(windowsize)
        if not topic_id: # 待删
            gexf = ''
        else:
            gexf, ds_gexf = make_network_graph(date, topic_id, topicname, windowsize, all_uid_pr, data, ds_all_uid_pr, ds_data, real_topic_id)
            #gexf, ds_gexf = make_network_graph(date, topic_id, topicname, windowsize, all_uid_pr, data, ds_all_uid_pr, ds_data, ds_all_uid_tr,ds_tr_data, real_topic_id) # 绘制gexf图--返回值是序列化字符串
        print 'save gexf'
        save_gexf_results(topicname, date, windowsize, gexf, gexf_type)
        save_gexf_results(topicname, date, windowsize, ds_gexf, ds_gexf_type)
        print 'update_topic_end'
        _update_topic_status2Completed(topicname, start_ts, end_ts, db_date) 
    

if __name__ == '__main__':
    module_t_s = 'identify'
    status = -1
    topic = u'东盟,博览会'
    #topic = u'APEC'
    start = datetime2ts('2013-09-02')
    end = datetime2ts('2013-09-07') + Day
    db_date = int(time.time())
    save_t_s = TopicStatus(module_t_s, status, topic, start, end, db_date)
    save_t_s_exist = db.session.query(TopicStatus).filter(TopicStatus.module==module_t_s, TopicStatus.topic==topic ,\
                                                  TopicStatus.start==start, TopicStatus.end==end).first()
    if save_t_s_exist:
        db.session.delete(save_t_s_exist)
    db.session.add(save_t_s)
    db.session.commit()
    main()
