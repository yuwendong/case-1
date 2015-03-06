# -*- coding: utf-8 -*-
'''
version:2014.12
author:hxq
'''
import sys
import networkx as nx
from parameter import MODULE_T_S, TOPIC, START, END, MAX_SIZE, TOPK
from parameter import Minute, Fifteenminutes, Hour, sixHour, Day, gexf_type, ds_gexf_type
from parameter import weibo_topic2xapian
from area import pagerank_rank, make_network, make_network_graph 
from topicStatus import _topic_not_calc, _update_topic_status2Computing, \
        _update_topic_status2Completed
from utils import acquire_topic_name, acquire_topic_id, \
        save_rank_results, save_gexf_results, save_attribute_dict, \
        acquire_real_topic_id

reload(sys)
sys.setdefaultencoding('utf-8')
from time_utils import ts2datetime, datetime2ts
#from config import db, GRAPH_PATH #　用于测试期间，建立topicstatus这张表。待删
import time # 用于测试生成topicStatus入库时间，待删
#from model import TopicStatus, Topics # 用于测试，待删
from lxml import etree
from get_first_user import get_first_node
from area import _utf8_unicode
from fu_tr import get_interval_count

sys.path.append('../../')
from global_config import db, GRAPH_PATH
from model import TopicStatus, Topics

'''
Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
gexf_type = 1
ds_gexf_type = 2
'''
#topic_xapian_id = '54ccbfab5a220134d9fc1b37' 

def main(topic, start_ts, ens_ts):
    '''
    topics = _topic_not_calc() # topics=[{id:x,module:x,status:x,topic:x,start:x,end:x,db_date:x}]
    '''
    topic_status _info = db.session.query(TopicStatus).filter(TopicStatus.topic==topic ,\
                                                                                              TopicStatus.start==start_ts ,\
                                                                                              TopicStatus.end==end_ts ,\
                                                                                              TopicStatus.module=='identify' ,\
                                                                                              TopicStatus.status==-1).first()
    if topic_status_info:
        #topic = topics[0] # 每次只计算一个----为了做一个缓冲，每个n时间才计算一个
        print 'topic_id', topic_status_info.id
        start_ts = topic_status_info.start
        end_ts = topic_status_info.end
        db_date = topic_status_info.db_date
        topicname = topic_name
        _update_topic_status2Computing(topicname, start_ts, end_ts, db_date)
        print 'update_status'
        topic_id = acquire_topic_id(topicname, start_ts, end_ts) # 重新获取id是因为TopicStatus中id是自增加的，进行更新后，id就不是原来的那一个了
        windowsize = (end_ts - start_ts) / Day # 确定时间跨度的大小
        date = ts2datetime(end_ts)

        print 'start topic2xapianid'
        topic_xapian_id = weibo_topic2xapian(topicname, start_ts, end_ts)
        print 'topic_xapian_id:', topic_xapian_id
        
        print 'start compute first_nodes'
        start_date = ts2datetime(start_ts) # used to compute the first user
        get_first_node(topicname, start_date, date, windowsize, topic_xapian_id)
        print 'end compute first_nodes'
#
        print 'start make network'
        max_size = MAX_SIZE
        attribute_add = True
        g, gg, new_attribute_dict, ds_dg, ds_udg, ds_new_attribute_dict = make_network(topicname, date, windowsize, topic_xapian_id, max_size, attribute_add)
        print 'write gexf file'
        real_topic_id = acquire_real_topic_id(topicname, start_ts, end_ts)
        if not real_topic_id:
            print 'the topic not exist'
            return None
        key = str(real_topic_id) + '_' + str(date) + '_' + str(windowsize) 
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

        print 'start make network graph'
        topic_id = int(topic_id)
        windowsize = int(windowsize)
        if not topic_id: # 待删
            gexf = ''
        else:
            gexf, ds_gexf = make_network_graph(date, topic_id, topicname, windowsize, all_uid_pr, data, ds_all_uid_pr, ds_data, real_topic_id)
        print 'save gexf'
        save_gexf_results(topicname, date, windowsize, gexf, gexf_type)
        save_gexf_results(topicname, date, windowsize, ds_gexf, ds_gexf_type)
        print 'start fu_tr'
        get_interval_count(topicname, date, windowsize, topic_xapian_id)
        print 'update_topic_end'
        _update_topic_status2Completed(topicname, start_ts, end_ts, db_date) 
    

if __name__ == '__main__':
    #module_t_s = 'identify'
    status = -1
    #topic = u'高校思想宣传'
    #start = datetime2ts('2015-01-23')
    #end = datetime2ts('2015-01-31') + Day
    model_t_s = MODULE_T_S
    topic = TOPIC
    start = datetime2ts(START)
    end = datetime2ts(END)
    save_topics = Topics(topic, start, end)
    save_topics_exist = db.session.query(Topics).filter(Topics.topic==topic ,\
                                                        Topics.start_ts==start ,\
                                                        Topics.end_ts==end).first()
    if save_topics_exist:
        db.session.delete(save_topics_exist)
    db.session.add(save_topics)
    db.session.commit()
    
    db_date = int(time.time())
    save_t_s = TopicStatus(module_t_s, status, topic, start, end, db_date)
    save_t_s_exist = db.session.query(TopicStatus).filter(TopicStatus.module==module_t_s, TopicStatus.topic==topic ,\
                                                  TopicStatus.start==start, TopicStatus.end==end).first()
    if save_t_s_exist:
        db.session.delete(save_t_s_exist)
    db.session.add(save_t_s)
    db.session.commit()
    main(topic, start, end)
