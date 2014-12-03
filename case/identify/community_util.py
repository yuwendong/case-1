# -*- coding: utf-8 -*-
import os
from xapian_case.xapian_backend import XapianSearch
from case.time_utils import ts2date
from neighbor_util import get_neighbor_info

weibo_fields_list = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
               'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
               'comments_count', 'sentiment', 'topics', 'message_type']
emotions_kv = {0:u'无倾向', 1:u'高兴', 2:u'愤怒', 3:u'悲伤', 4:u'新闻'}

def getXapianWeiboByTopic(topic_id='54635178e74050a373a1b939'):
    XAPIAN_WEIBO_TOPIC_DATA_PATH = '/home/xapian/xapian_weibo_topic/'
    stub_file = XAPIAN_WEIBO_TOPIC_DATA_PATH + 'stub/xapian_weibo_topic_stub_' + str(topic_id)
    if os.path.exists(stub_file):
        print 'stub exist'
        xapian_search_weibo = XapianSearch(stub=stub_file, schema_version='5')
        return xapian_search_weibo
    else:
        print 'stub not exist'
        return None

def read_uid_weibos(topic, date, windowsize, uid):
    # topic_id = get_topic_id(topic, start_ts, end_ts) 这里需要补充通过话题名称、时间范围获取topic id的代码
    xapian_search_weibo = getXapianWeiboByTopic()
    query_dict = {
        'user':uid
            }
    count, results = xapian_search_weibo.search(query=query_dict, fields=weibo_fields_list)
    if count==0:
        weibo_list = []
    else:
        weibo_list = []
        for weibo in results():
            text = weibo['text']
            geo = weibo['geo']
            source = weibo['source']
            timestamp = weibo['timestamp']
            date = ts2date(timestamp)
            reposts_count = weibo['reposts_count']
            comments_count = weibo['comments_count']
            sentiment = weibo['sentiment']
            sentiment = emotions_kv[sentiment]
            row = [date , sentiment, text, geo, source, reposts_count, comments_count]
            weibo_list.append(row)
    sort_weibo_list = sorted(weibo_list, key=lambda x:x[0])
    return sort_weibo_list

'''
邻居信息详情：基本统计信息、深度分析
基本统计信息：人数、 名单、 微博信息
深度分析：微博关键词、 情感比例
'''
def read_uid_neighbors(topic, date, windowsize, uid, network_type):
    # network_type="source_graph" or 'direct_superior_graph'
    '''
    neighbor_num, neighbor_list, u_neighbor_list, neighbor_user= get_neighbor_userinfo(topic, date, windowsize, uid, network_type)
    neighbor_weibo_num, neighbor_weibo, top_keyword, sentiment_dict = get_neighbor_weiboinfo(topic, date, windowsize, neighbor_list)
    new_neighbor_weibo = get_new_neighbor_weibo(neighbor_weibo, neighbor_user)
    '''
    neighbor_weibo, top_keyword, sentiment_list = get_neighbor_info(topic, date, windowsize, uid, network_type)
    results = [neighbor_weibo, top_keyword, sentiment_list]
    return results

    

            
        
    
