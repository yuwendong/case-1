# -*- coding: utf-8 -*-
import json
import os
import redis
from xapian_case.xapian_backend import XapianSearch
from case.time_utils import ts2date
from neighbor_util import get_neighbor_info
from community_information import get_community_info, getXapianWeiboByTopic
from case.global_config import xapian_search_user as user_search
from utils import weiboinfo2url
from parameter import weibo_fields_list, user_fields_list, emotions_kv, REDIS_HOST, REDIS_PORT
from parameter import  USER_DOMAIN, DOMAIN_LIST, getXapianWeiboByTopic
'''
weibo_fields_list = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
               'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
               'comments_count', 'sentiment', 'topics', 'message_type']
user_fields_list = ['_id', 'name', 'gender', 'profile_image_url', 'friends_count', \
                            'followers_count', 'location', 'created_at','statuses_count']
emotions_kv = {0:u'无倾向', 1:u'高兴', 2:u'愤怒', 3:u'悲伤', 4:u'新闻'}
REDIS_HOST = '219.224.135.48'
REDIS_PORT = 6379
USER_DOMAIN = 'user_domain' # user domain hash
DOMAIN_LIST = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
'''
def _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)

r = _default_redis()

def uid2domain(user):
    domain_str = r.hget(USER_DOMAIN, str(user))
    if not domain_str:
        return 'other'

    domain_dict = json.loads(domain_str)
    domain = domain_dict['v3']

    return domain

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

def read_uid_weibos(topic, date, windowsize, uid):
    # change
    end_ts = datetime2ts(date)
    start_ts = end_ts - Day * windowsize
    xapian_search_weibo = getXapianWeiboByTopic(topic, start_ts ,end_ts)
    
    query_dict = {
        'user':uid
            }
    count, results = xapian_search_weibo.search(query=query_dict, fields=weibo_fields_list)
    if count==0:
        weibo_list = []
    else:
        weibo_list = []
        for weibo in results():
            wid = weibo['_id']
            uid = weibo['user']
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
            geo = weibo['geo']
            source = weibo['source']
            timestamp = weibo['timestamp']
            date = ts2date(timestamp)
            reposts_count = weibo['reposts_count']
            comments_count = weibo['comments_count']
            weibo_link = weiboinfo2url(uid, wid)
            domain = uid2domain(uid)
            
            row = [wid, uid, name, location, friends_count, followers_count, created_at, statuses_count, profile_image_url, date , text, geo, source, reposts_count, comments_count, weibo_link]
            weibo_list.append(row)
            
    sort_weibo_list = sorted(weibo_list, key=lambda x:x[9])
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
    neighbor_list, neighbor_weibo, top_keyword, sentiment_list ,timestamp_count= get_neighbor_info(topic, date, windowsize, uid, network_type)
    neighbor_user_info = get_u_info(neighbor_list) # 获取用户列表
    results = [neighbor_weibo, top_keyword, sentiment_list, neighbor_user_info, timestamp_count]
    return results

def read_uid_community(topic, date, windowsize, uid, network_type, cid):
    # cid: the id of the uid's community
    community_user, community_weibo, top_keyword, sentiment_list , timestamp_count= get_community_info(topic, date, windowsize, uid, cid, network_type)
    community_user_info = get_u_info(community_user) # 获取用户列表
    results = [community_weibo, top_keyword, sentiment_list, community_user_info, timestamp_count]
    return results

def get_u_info(uid_list):
    user_info_list = []
    row = []
    for uid in uid_list:
        user = user_search.search_by_id(uid, fields=['_id', 'name', 'profile_image_url', 'friends_count'])
        if user:
             name = user['name']
             profile_image_user = user['profile_image_url']
             friends_count = user['friends_count']
        else:
            name = u'未知'
            profile_image_user = u'no'
            friends_count = -1
            
        row.append([uid, name, profile_image_user, friends_count])
    sort_row = sorted(row, key=lambda x:x[3], reverse=True)
    user_info_list = [user[:3] for user in sort_row]

    return user_info_list
        
        
    

            
        
    
