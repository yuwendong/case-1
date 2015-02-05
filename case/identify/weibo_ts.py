# -*- coding: utf-8 -*-
import os
import redis
import networkx as nx
from xapian_case.xapian_backend import XapianSearch
from utils import weiboinfo2url
from case.time_utils import ts2date, datetime2ts
from case.extensions import db
from case.model import Topics
from case.global_config import xapian_search_user as user_search
from case.global_config import GRAPH_PATH
from community_information import get_community_user
from parameter import getXapianWeiboByTopic
from parameter import user_fields_list, weibo_fields_list, emotions_kv

Minute = 60
Fifteenminutes = 15 *Minute
Hour = 3600
Day = Hour * 24
'''
user_fields_list = ['_id', 'name', 'gender', 'profile_image_url', 'friends_count', \
                            'followers_count', 'location', 'created_at','statuses_count']
weibo_fields_list = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
                               'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
                               'comments_count', 'sentiment', 'topics', 'message_type', 'terms']
emotions_kv = {0:u'无倾向', 1:u'高兴', 2:u'愤怒', 3:u'悲伤', 4:u'新闻'}
'''
def acquire_real_topic_id(topic, date, windowsize):
    end_ts = datetime2ts(date)
    start_ts = end_ts - windowsize * Day
    item = db.session.query(Topics).filter(Topics.topic==topic ,\
                                                                Topics.start_ts==start_ts ,\
                                                                Topics.end_ts==end_ts).first()
    if item:
        real_topic_id = item.id
    else:
        real_topic_id = None

    return real_topic_id

'''
def getXapianWeiboByTopic(topic_id='545f4c22cf198b18c57b8014'):
    XAPIAN_WEIBO_TOPIC_DATA_PATH = '/home/xapian/xapian_weibo_topic/'
    stub_file = XAPIAN_WEIBO_TOPIC_DATA_PATH + 'stub/xapian_weibo_topic_stub_' + str(topic_id)
    if os.path.exists(stub_file):
        print 'stub exist'
        xapian_search_weibo = XapianSearch(stub=stub_file, schema_version='5')
        return xapian_search_weibo
    else:
        print 'stub not exist'
        return None
'''

def c_weibo_by_ts(topic, date, windowsize, uid, network_type, cid, rank_method):
    real_topic_id = acquire_real_topic_id(topic, date, windowsize)
    if not real_topic_id:
        return None, None, None
        # 该话题存在进行下面的计算
    key_pre = str(real_topic_id) + '_' + str(date) + '_' + str(windowsize)
    # 选择有向图进行社区信息的计算
    if network_type=='source_graph':
        key = str(GRAPH_PATH)+key_pre + '_gg_graph.gexf'
    elif network_type=='direct_superior_graph':
        key = str(GRAPH_PATH)+key_pre + '_ds_udg_graph.gexf'
    g = nx.read_gexf(key)
    # 获取图结构中节点uid对应的社区包括的节点list
    community_user_list = get_community_user(g, uid, cid)
    # 考虑节点社区属性存放的位置

    # change
    end_ts = datetime2ts(date)
    start_ts = end_ts - Day * windowsize
    xapian_search_weibo = getXapianWeiboByTopic(topic, start_ts, end_ts)
    query_dict = {
        '$or' : []
        }
    for uid in community_user_list:
        query_dict['$or'].append({'user': int(uid)})
    community_info = []
    count, weibo_results = xapian_search_weibo.search(query=query_dict, fields= weibo_fields_list)
    if count==0:
        return None

    for weibo in weibo_results():
        uid = weibo['user']
        _id = weibo['_id']
        result = user_search.search_by_id(uid, fields=user_fields_list)
        if result:
            name = result['name']
            location = result['location']
            friends_count = result['friends_count']
            followers_count = result['followers_count']
            created_at = result['created_at']
            statuses_count = result['statuses_count']
            profile_image_url = result['profile_image_url']
        else:
            name = u'未知'
            location = u'未知'
            friends_count = u'未知'
            followers_count = u'未知'
            created_at = u'未知'
            statuses_count = u'未知'
            profile_image_url = u'no'
            
        text = weibo['text']
        timestamp = weibo['timestamp']
        date = ts2date(timestamp)
        reposts_count = weibo['reposts_count']
        source = weibo['source']
        geo = weibo['geo']
        comments_count = weibo['comments_count']
        sentiment = weibo['sentiment']
        sentiment_name = emotions_kv[sentiment]
        weibo_link = weiboinfo2url(uid, _id)
 
        community_info.append([_id, name, location, friends_count, followers_count, created_at, statuses_count, profile_image_url, text, date, reposts_count, source, geo, comments_count, sentiment_name,weibo_link, uid, timestamp])
      
    if rank_method == 'reposts_count':
        sort_community_info = sorted(community_info, key=lambda x:x[10], reverse=True) #以转发量排序
    else:
        sort_community_info = sorted(community_info, key=lambda x:x[17]) # 以时间戳排序
        
    return sort_community_info


def n_weibo_by_ts(topic, date, windowsize, uid, network_type, rank_method):
    # 为读取graph结构，需要获取topic对应id
    real_topic_id = acquire_real_topic_id(topic, date, windowsize)
    if not real_topic_id:
        return None, None, None
    # 该话题存在进行下面的计算
    key_pre = str(real_topic_id) + '_' + str(date) + '_' + str(windowsize)
    # 选择无向图进行邻居信息的计算
    if network_type=='source_graph':
        key = str(GRAPH_PATH)+key_pre + '_gg_graph.gexf'
    elif network_type=='direct_superior_graph':
        key = str(GRAPH_PATH)+key_pre + '_ds_udg_graph.gexf'
    g = nx.read_gexf(key)
    neighbor_list = g.neighbors(str(uid)) # 纯邻居节点组成的list

    # change
    end_ts = datetime2ts(date)
    start_ts = end_ts - Day * windowsize
    xapian_search_weibo = getXapianWeiboByTopic(topic , start_ts, end_ts)
    query_dict = {
        '$or' : []
        }
    for uid in neighbor_list:
        query_dict['$or'].append({'user': int(uid)})
    neighbor_info = []
    count, weibo_results = xapian_search_weibo.search(query=query_dict, fields= weibo_fields_list)
    if count==0:
        return None, None, None
    sentiment_count = {}
    for weibo in weibo_results():
        uid = weibo['user']
        _id = weibo['_id']
        result = user_search.search_by_id(uid, fields=user_fields_list)
        if result:
            name = result['name']
            location = result['location']
            friends_count = result['friends_count']
            followers_count = result['followers_count']
            created_at = result['created_at']
            statuses_count = result['statuses_count']
            profile_image_url = result['profile_image_url']
        else:
            name = u'未知'
            location = u'未知'
            friends_count = u'未知'
            followers_count = u'未知'
            created_at = u'未知'
            statuses_count = u'未知'
            profile_image_url = u'no'
            
        text = weibo['text']
        timestamp = weibo['timestamp']
        date = ts2date(timestamp)
        reposts_count = weibo['reposts_count']
        source = weibo['source']
        geo = weibo['geo']
        comments_count = weibo['comments_count']
        sentiment = weibo['sentiment']
        sentiment_name = emotions_kv[sentiment]
        weibo_link = weiboinfo2url(uid, _id)
        neighbor_info.append([_id, name, location, friends_count, followers_count, created_at, statuses_count, profile_image_url, text, date, reposts_count, source, geo, comments_count, sentiment_name,weibo_link, uid, timestamp])

    if rank_method == 'reposts_count':
        sort_neighbor_info = sorted(neighbor_info, key=lambda x:x[10], reverse=True) #以转发量排序
    else:
        sort_neighbor_info = sorted(neighbor_info, key=lambda x:x[17]) # 以时间戳排序
            
    return sort_neighbor_info
    
