# -*- coding: utf-8 -*-
import os
import json
import redis
import networkx as nx
from xapian_case.xapian_backend import XapianSearch
from xapian_case.utils import top_keywords, gen_mset_iter
from case.time_utils import ts2date, datetime2ts
from case.model import Topics
from case.extensions import db
from case.global_config import xapian_search_user as user_search
from case.global_config import GRAPH_PATH
from utils import weiboinfo2url
from parameter import getXapianWeiboByTopic
from parameter import weibo_fields_list, user_fields_list, emotions_kv, REDIS_HOST, REDIS_PORT,\
                    USER_DOMAIN, DOMAIN_LIST, Minute, Fifteenminutes, Hour, Day


#GRAPH_PATH = '/home/ubuntu4/huxiaoqian/mcase/graph/'
'''
Minute = 60
Fifteenminutes = 15 *Minute
Hour = 3600
Day = Hour * 24
user_fields_list = ['_id', 'name', 'gender', 'profile_image_url', 'friends_count', \
                            'followers_count', 'location', 'created_at','statuses_count']
weibo_fields_list = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
                               'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
                               'comments_count', 'sentiment', 'topics', 'message_type', 'terms']
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

def get_community_info(topic, date, windowsize, uid, cid, network_type):
    real_topic_id = acquire_real_topic_id(topic, date, windowsize)
    # test
    real_topic_id = 282
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
    
    u_community_user_list = community_user_list.append(uid) # uid type str
    community_user_num = len(community_user_list)

    community_info, top_keyword, sentiment_dict , query_dict= community_result(community_user_list, topic, date, windowsize)
    community_t_c = get_timestamp_count(query_dict, topic, date, windowsize)
    return community_user_list, community_info, top_keyword, sentiment_dict, community_t_c

def community_result(community_user_list, topic, date, windowsize):
    #change
    end_ts = datetime2ts(date)
    start_ts = end_ts - windowsize * Day
    xapian_search_weibo = getXapianWeiboByTopic(topic, start_ts ,end_ts)
    query_dict = {
        '$or' : []
        }
    for uid in community_user_list:
        query_dict['$or'].append({'user': int(uid)})
    community_info = []
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
        domain = uid2domain(uid)

        try:
            sentiment_count[sentiment] += 1
        except KeyError:
            sentiment_count[sentiment] = 1
        community_info.append([_id, name, location, friends_count, followers_count, created_at, statuses_count, profile_image_url, text, date, reposts_count, source, geo, comments_count, sentiment_name,weibo_link, domain])
    
    sort_community_info = sorted(community_info, key=lambda x:x[10], reverse=True) #以转发量排序
    
    mset = xapian_search_weibo.search(query=query_dict, max_offset=50, mset_direct=True)
    top_keyword = top_keywords(gen_mset_iter(xapian_search_weibo, mset, fields=['terms']), top=50)

    sort_top_keyword = sorted(top_keyword, key=lambda x:x[1], reverse=True)

    new_sentiment_list = []
    for sentiment in sentiment_count:
        sentiment_ch = emotions_kv[int(sentiment)]
        num = sentiment_count[sentiment]
        ratio = float(num) / float(count)
        new_sentiment_list.append([sentiment_ch, num, ratio])
   
    return sort_community_info, sort_top_keyword, new_sentiment_list, query_dict
'''
# 公共函数 parameter
def getXapianWeiboByTopic(topic_id='54ccbfab5a220134d9fc1b37'):
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
def get_community_user(g, uid, cid):
    # 中间存储的graph结构与后面进行生成xml文件的图结构不同
    # 中间存储结构是完整的图结构，而xml文件的图结构去除了零度节点、自环
    # 这里的计算还是针对完整图结构计算----但这样会产生差异吧？？比如说社区划分有所差异
    #???Q???所有的指标计算都是针对处理图结构----但是pagerank却是完整的？
    import community
    partition = community.best_partition(g)
    #print 'partition:', partition
    community_user_list = []
    for node in g.nodes():
        node_cid = partition[node]
        if node_cid == cid:
            #print 'node:', node, type(node)
            community_user_list.append(node)
    #print 'community_user_list:', community_user_list
    return community_user_list

def get_timestamp_count(query_dict, topic, date, windowsize):
    during = 3600
    day = 24 * 3600
    end_ts = datetime2ts(date)
    start_ts = end_ts - windowsize * day
    xapian_search_weibo = getXapianWeiboByTopic(topic, start_ts, end_ts)
    interval = (end_ts - start_ts) / during # 以小时作为统计粒度
    time_count = []
    #query_dict['timestamp'] = {'$gt':start_ts, '$lt':end_ts}
    #print 'query_dict:', query_dict
    #count, results = xapian_search_weibo.search(query=query_dict, fields=['_id'])
    #print 'query_dict  count:', count
    for i in range(interval, 0, -1):
        begin = end_ts - during * i
        end = begin + during

        query_dict['timestamp'] = {'$gt':begin, '$lt':end}
        #print 'query_dict:', query_dict
        #print 'begin, end:', begin, end
        count, result = xapian_search_weibo.search(query=query_dict, fields = ['_id'])
        #print 'end, count:', end, count
        #new_end = ts2date(end)
        time_count.append([end, count])
    print 'time_count:', time_count
    return time_count

    
        
        
        
        
    
    
    
    
