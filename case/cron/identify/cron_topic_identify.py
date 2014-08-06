# -*- coding: utf-8 -*-

from time_utils import ts2datetime
from area import pagerank_rank, degree_rank, make_network_graph 
from utils import acquire_topic_name, acquire_topic_id, save_rank_results, save_gexf_results
from topicStatus import _topic_not_calc, _update_topic_status2Computing, _update_topic_status2Completed
import networkx as nx 


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
        
        start_ts = topic.start
        end_ts = topic.end
        db_date = topic.db_date
        topicname = topic.topic
        _update_topic_status2Computing(topicname, start_ts, end_ts, db_date)
        topic_id = acquire_topic_id(topicname, start_ts, end_ts) # 重新获取id是因为TopicStatus中id是自增加的，进行更新后，id就不是原来的那一个了
        windowsize = (end_ts - start_ts) / Day # 确定时间跨度的大小
        date = ts2datetime(end_ts)
        if windowsize > 7:
            degree_rank(TOPK, date, topic_id, windowsize) # topic的时间跨度大，就选择典型的几个点进行计算
        else:
            pagerank_rank(TOPK, date, topic_id, windowsize) # topic的时间跨度小，进行pagerank
        topic_id = int(topic_id)
        windowsize = int(windowsize)
        if not topic_id:
            gexf = ''
        else:
            gexf = make_network_graph(date, topic_id, topicname, windowsize) # 绘制gexf图--返回值是序列化字符串

        save_gexf_results(topicname, date, windowsize, gexf) 

        _update_topic_status2Completed(topicname, start_ts, end_ts, db_date) 


if __name__ == '__main__':
    main()
