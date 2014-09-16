# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from time_utils import ts2datetime, datetime2ts
from area import pagerank_rank, degree_rank, make_network_graph 
from utils import acquire_topic_name, acquire_topic_id, save_rank_results, save_gexf_results
from topicStatus import _topic_not_calc, _update_topic_status2Computing, _update_topic_status2Completed
import networkx as nx
from config import db #　用于测试期间，建立topicstatus这张表。待删
import time # 用于测试生成topicStatus入库时间，待删
from model import TopicStatus # 用于测试，待删
from lxml import etree

TOPK = 1000
Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24


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
        windowsize = (end_ts - start_ts) / Day # 确定时间跨度的大小,daixiuzheng
        date = ts2datetime(end_ts)
        print 'windowsize:',windowsize

        all_uid_pr = {}
        if windowsize > 7:
            print 'degree_rank'
            degree_rank(TOPK, date, topic_id, windowsize) # topic的时间跨度大，就选择典型的几个点进行计算
        else:
            print 'pagerank_rank'
            all_uid_pr = pagerank_rank(TOPK, date, topic_id, windowsize) # topic的时间跨度小，进行pagerank
        topic_id = int(topic_id)
        windowsize = int(windowsize)
        if not topic_id:
            gexf = ''
        else:
            gexf = make_network_graph(date, topic_id, topicname, windowsize, all_uid_pr) # 绘制gexf图--返回值是序列化字符串
        
        print 'save gexf'
        save_gexf_results(topicname, date, windowsize, gexf) 
        print 'uodate_topic_end'
        _update_topic_status2Completed(topicname, start_ts, end_ts, db_date) 


if __name__ == '__main__':
    module_t_s = 'identify'
    status = -1
    topic = u'东盟,博览会'
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
