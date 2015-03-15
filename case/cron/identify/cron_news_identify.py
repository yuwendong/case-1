# -*- coding: utf-8 -*-
'''
news_identify的计算入口，主要由两部分组成：
1)最早参与者
2)趋势发起人计算
'''
import time
import pymongo
import sys
#from config import MONGODB_HOST, MONGODB_PORT, db
#from model import Topics, TopicStatus
from early_join_news import early_join
from trend_user_news import trend_user
from topicStatus import _topic_not_calc, _update_topic_status2Computing, \
        _update_topic_status2Completed
from parameter import NEWS_MODULE, NEWS_TOPIC, NEWS_START_TS, NEWS_END_TS
from parameter import get_dynamic_mongo
sys.path.append('../../')
from global_config import MONGODB_HOST, MONGODB_PORT, db
from model import Topics, TopicStatus
from time_utils import datetime2ts, ts2datetime

# host 46 port 27019
'''
conn = pymongo.Connection(host=MONGODB_HOST, port=MONGODB_PORT)
mongodb = conn['news']
'''
def main(topic, start_ts, end_ts):
    #在topic_status中获取还未进行计算的话题
    topics = _topic_not_calc(status='-1', module='i_news')
    topic_status_info = db.session.query(TopicStatus).filter(TopicStatus.topic==topic ,\
                                                             TopicStatus.start==start_ts ,\
                                                             TopicStatus.end==end_ts ,\
                                                             TopicStatus.module=='i_news' ,\
                                                             TopicStatus.status==-1).first()
    if topic_status_info:
        topic_id = topic_status_info.id
        start_ts = topic_status_info.start
        end_ts = topic_status_info.end
        topicname = topic_status_info.topic
        db_date = topic_status_info.db_date
            
        _update_topic_status2Computing(topicname, start_ts, end_ts, db_date, 'i_news')
        print 'update_status'
    
        #mongodb中topic对应的collection
        print 'get_dynamic_mongo'
        news_collection , comment_collection = get_dynamic_mongo(topicname, start_ts, end_ts)
        #早期参与者
        print 'start compute early_join'
        early_join(topicname, start_ts, end_ts, news_collection)
        #趋势发起人
        print 'start compute trend_user'
        trend_user(topicname, start_ts, end_ts, news_collection, comment_collection)

        print 'update_topic_end'
        _update_topic_status2Completed(topicname, start_ts, end_ts, db_date, 'i_news') 

'''    
#通过topic, start_ts, end_ts获取news_topic中对应的object_id，然后找到对应的collection
def get_dynamic_mongo(topic, start_ts, end_ts):
    topic_collection = mongodb.news_topic 
    topic_news = topic_collection.find_one({'topic':topic, 'startts':start_ts, 'endts':end_ts}) # 保证时间范围是在该数据
    if not topic_news:
        print 'this topic is not exist'
        return None
    else:
        topic_news_id = topic_news['_id']
        news_collection_name = 'post_' + str(topic_news_id) 
        topic_news_collection = mongodb[news_collection_name] # 这里的调用方法可能会有问题
        comment_collection_name = 'comment_' + str(topic_news_id)
        topic_comment_collection = mongodb[comment_collection_name]
    return topic_news_collection, topic_comment_collection
'''


if __name__=='__main__':
    #module = 'i-news'
    status = -1
    # end_ts 需要做处理，为最后一天的24点的时间戳
    #在调用主函数之前，时间起始点由外界给定
    '''
    topic = u'全军政治工作会议'
    start_ts = 1415030400
    end_ts = 1415750400
    '''
    module = NEWS_MODULE
    topic = NEWS_TOPIC
    start_ts = datetime2ts(NEWS_START_TS)
    end_ts = datetime2ts(NEWS_END_TS)
    # deal with the start_ts/end_ts is not the whole day
    if start_ts - datetime2ts(ts2datetime(start_ts)) != 0:
        start_ts = datetime2ts(ts2datetime(start_ts))
    if end_ts - datetime2ts(ts2datetime(end_ts)) != 0:
        end_ts = datetime2ts(ts2datetime(end_ts)) + 3600 * 24
    print 'start_ts, end_ts:', start_ts, end_ts
    db_date = int(time.time())
    # 创建topics中得话题
    '''
    save_t = Topics(topic, start_ts, end_ts)
    save_t_exist = db.session.query(Topics).filter(Topics.topic==topic ,\
                                                   Topics.start_ts==start_ts ,\
                                                   Topics.end_ts==end_ts).first()
    if save_t_exist:
        db.session.delete(save_t_exist)
    db.session.add(save_t)
    db.session.commit()
    '''
    save_t_s = TopicStatus(module, status, topic, start_ts, end_ts, db_date)
    save_t_s_exist = db.session.query(TopicStatus).filter(TopicStatus.module==module, \
                                                                                          TopicStatus.start==start_ts, \
                                                                                          TopicStatus.end==end_ts).first()
    if save_t_s_exist:
        db.session.delete(save_t_s_exist)
    db.session.add(save_t_s)
    db.session.commit()
    main(topic, start_ts, end_ts)
    
