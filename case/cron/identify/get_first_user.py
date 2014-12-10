# -*- coding: utf-8 -*-

import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import redis
from config import db
sys.path.append('../')
from time_utils import ts2datetime, datetime2ts
from dynamic_xapian_weibo import getXapianWeiboByTopic
from config import xapian_search_user as user_search
from utils import acquire_user_by_id
from model import FirstUser, FirstDomainUser# 时间在前20的user及其对应的微博信息


fields_list = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
               'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
               'comments_count', 'sentiment', 'topics', 'message_type', 'terms']

user_fields_list = ['_id', 'name', 'gender', 'profile_image_url', 'friends_count', \
                    'followers_count', 'location', 'created_at','statuses_count']

REDIS_HOST = '219.224.135.48'
REDIS_PORT = 6379
USER_DOMAIN = 'user_domain' # user domain hash
DOMAIN_LIST = ['folk', 'media', 'opinion_leader', 'oversea', 'other']

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
    



def get_first_node(topic, start_date, date, windowsize):
    '''
    根据timestamp,获取top20的用户----微博可能就不只20条了
    根据微博获取对应的用户信息------可能会出现用户重复的情况，这里只取时间最早的那一个
    将其保存
    '''
    if topic and topic != '':
        datestr = start_date.replace('-','')
        xapian_search_weibo = getXapianWeiboByTopic(topic_id='545f4c22cf198b18c57b8014')
        begin_ts = datetime2ts(start_date)
        end_ts = datetime2ts(date)
        topics = topic.strip().split(',')
        query_dict = {
            'timestamp': {'$gt': begin_ts, '$lt': end_ts},
            '$or': [{'message_type':1},{'message_type':3}],
            '$and': []
            }
        # 这里只选取原创和转发微博进行计算
        for c_topic in topics:
            query_dict['$and'].append({'topics': c_topic})
    
        time_top_nodes = xapian_search_weibo.search(query=query_dict, sort_by=['-timestamp'], fields=fields_list)
        user_list = []
        if not time_top_nodes:
            print 'search error'
        else:
            s = 0
            domain_count_list = {'folk':0, 'media':0, 'opinion_leader':0, 'oversea':0, 'other':0}
            domain_user_list = {'folk':[], 'media':[], 'opinion_leader':[], 'oversea':[], 'other':[]}
            for node in time_top_nodes[1]():
                uid = node['user']
                user_domain = uid2domain(uid)
                timestamp = node['timestamp']
                user_info = get_user_info(uid) # 获取top_time微博对应的用户信息
                if s < 20:
                    if user_info and (not (uid in user_list)):
                        s += 1
                        weibo_info = node
                        user_list.append(uid)
                        save_first_nodes(topic, date, windowsize, uid, timestamp, user_info, weibo_info, user_domain)
                if domain_count_list == {'folk':20, 'media':20, 'opinion_leader':20, 'oversea':20, 'other':20}:
                    break
                for domain in DOMAIN_LIST:
                    if domain_count_list[domain] >= 20:
                        continue
                    elif user_domain==domain:
                        if user_info and (not(uid in domain_user_list[domain])):
                            domain_user_list[domain].append(uid)
                            domain_count_list[domain] += 1
                            rank = domain_count_list[domain]
                            save_domain_nodes(topic, date, windowsize, uid, timestamp, user_info, weibo_info, user_domain, rank)
                            
                    

def save_domain_nodes(topic, date, windowsize, uid, timestamp, user_info, weibo_info, user_domain, rank):
    item = FirstDomainUser(topic, date, windowsize, uid, timestamp, json.dumps(user_info), json.dumps(weibo_info), user_domain, rank)
    item_exist = db.session.query(FirstDomainUser).filter(FirstDomainUser.topic==topic ,\
                                                          FirstDomainUser.date==date ,\
                                                          FirstDomainUser.windowsize==windowsize ,\
                                                          FirstDomainUser.uid==uid).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()
        
def get_user_info(uid):
    user_info = {}
    result = user_search.search_by_id(int(uid), fields=user_fields_list)
    if result:
        user_info['name'] = result['name']
        user_info['location'] = result['location']
        #user_info['gender'] = result['gender']
        user_info['friends_count'] = result['friends_count']
        user_info['followers_count'] = result['followers_count']
        user_info['profile_image_url'] = result['profile_image_url']
        user_info['friends_count'] = result['friends_count']
        user_info['followers_count'] = result['followers_count']
        user_info['created_at'] = result['created_at']
        user_info['statuses_count'] = result['statuses_count']
    else:
        user_info['name'] = u'未知'
        user_info['location'] = u'未知'
        user_info['friends_count'] = u'未知'
        user_info['followers_count'] = u'未知'
        user_info['profile_image_url'] = 'no'
        user_info['friends_count'] = u'未知'
        user_info['followers_count'] = u'未知'
        user_info['created_at'] = u'未知'
        user_info['statuses_count'] = u'未知'      
        
    return user_info
        
def save_first_nodes(topic, date, windowsize, uid, timestamp, user_info, weibo_info, user_domain):
    item = FirstUser(topic, date, windowsize, uid, timestamp, json.dumps(user_info), json.dumps(weibo_info), user_domain)
    item_exist = db.session.query(FirstUser).filter(FirstUser.topic==topic ,\
                                                    FirstUser.date==date ,\
                                                    FirstUser.windowsize==windowsize, \
                                                    FirstUser.uid==uid).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()


if __name__=='__main__':
    topic = u'全军政治工作会议'
    windowsize = 17
    end_ts = datetime2ts('2014-11-16')
    date = ts2datetime(end_ts)
    start_ts = datetime2ts('2014-10-30')
    start_date = ts2datetime(start_ts) # 确定topic的start_ts和end_ts是怎么得来的
    get_first_node(topic, start_date, date, windowsize) # 如果start_ts就是第一条微博出现的时间，不能只查询前15分钟的数据。要考虑极端情况，必须查询所有数据
    
