# -*- coding: utf-8 -*-
import json
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from case.extensions import db
from case.model import TrendMaker, TrendPusher
from utils import weiboinfo2url
'''
domain_dict = {'folk':u'民众', 'media':u'媒体', 'opinion_leader':u'意见领袖', 'other':u'其他', 'oversea':u'海外'}
domain_list = ['folk', 'media', 'opinion_leader','oversea', 'other']
'''
def ts2date(ts):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))

def read_trend_maker(topic, date, windowsize, rank_method):
    results = []
    #print 'topic, date, windowsize:', topic.encode('utf-8'), date, windowsize
    items = db.session.query(TrendMaker).filter(TrendMaker.topic==topic ,\
                                                TrendMaker.date==date ,\
                                                TrendMaker.windowsize==windowsize).all()
    #print 'len(items):', len(items)
    if items:
        for item in items:
            uid= item.uid
            timestamp = item.timestamp
            timestamp = ts2date(timestamp)
            user_info = json.loads(item.user_info)
            uname = user_info['name']
            location = user_info['location']
            profile_image_url = user_info['profile_image_url']
            if profile_image_url == u'未知':
                profile_image_url = 'no'
            friends_count = user_info['friends_count']
            if friends_count == u'未知':
                friends_count = -1
            followers_count = user_info['followers_count']
            statuses_count = user_info['statuses_count']
            if statuses_count == u'未知':
                statuses_count = -1
            created_at = user_info['created_at']

            weibo_info = json.loads(item.weibo_info)
            text = weibo_info['text']
            geo = weibo_info['geo']
            source = weibo_info['source']
            _id = weibo_info['_id']
            reposts_count = weibo_info['reposts_count']
            weibo_link = weiboinfo2url(uid, _id)
            user_domain = item.domain
            domain_name = domain_dict[user_domain]
            rank = item.rank
            value = item.value # 关键词命中个数
            key_item = json.loads(item.key_item) # 命中关键词
            row = [rank, uid, uname, location, domain_name, timestamp, text, profile_image_url, friends_count, followers_count, statuses_count, created_at,geo, source, weibo_link, _id, reposts_count, value, key_item]
            results.append(row)
    sort_result = results
    if rank_method == 'content':
        rank_results = results
        sort_result = deal_rank(rank_results)
    elif rank_method == 'timestamp':
        sort_result = sorted(results, key=lambda x:x[5])
        sort_result = deal_rank(sort_result)
    elif rank_method == 'friends_count':
        sort_result = sorted(results, key=lambda x:x[8], reverse=True)
        sort_result = deal_rank(sort_result)
    elif rank_method == 'statuses_count':
        sort_result = sorted(results, key=lambda x:x[10], reverse=True)
        sort_result = deal_rank(sort_result)
    elif rank_method == 'reposts_count':
        sort_result = sorted(results, key=lambda x:x[16], reverse=True)
        sort_result = deal_rank(sort_result)
    #print 'results:', sort_result
    return sort_result

def deal_rank(result):
    new_result = []
    rank = 0
    for item in result:
        rank += 1
        row = [rank]
        for i in range(len(item)):
            element = item[i]
            if i == 0:
                continue
            if element==-1:
                element = u'未知'
            row.append(element)
        new_result.append(row)
    return new_result
            
        

def read_trend_pusher(topic, date, windowsize, rank_method):
    results = []
    #print 'topic, date, windowsize:', topic.encode('utf-8'), date, windowsize
    items = db.session.query(TrendPusher).filter(TrendPusher.topic==topic ,\
                                                 TrendPusher.date==date ,\
                                                 TrendPusher.windowsize==windowsize).all()
    #print 'len(items):', len(items)
    if items:
        for item in items:
            uid= item.uid
            timestamp = item.timestamp
            timestamp = ts2date(timestamp)
            user_info = json.loads(item.user_info)
            uname = user_info['name']
            location = user_info['location']
            profile_image_url = user_info['profile_image_url']
            if profile_image_url == u'未知':
                profile_image_url = 'no'
            friends_count = user_info['friends_count']
            if friends_count == u'未知':
                friends_count = -1
            followers_count = user_info['followers_count']
            statuses_count = user_info['statuses_count']
            if statuses_count == u'未知':
                statuses_count = -1
            created_at = user_info['created_at']

            weibo_info = json.loads(item.weibo_info)
            text = weibo_info['text']
            geo = weibo_info['geo']
            source = weibo_info['source']
            _id = weibo_info['_id']
            reposts_count = weibo_info['reposts_count']
            weibo_link = weiboinfo2url(uid, _id)
            user_domain = item.domain
            domain_name = domain_dict[user_domain]
            rank = item.rank
            row = [rank, uid, uname, location, domain_name, timestamp, text, profile_image_url, friends_count, followers_count, statuses_count, created_at,geo, source, weibo_link, _id, reposts_count]
            results.append(row)
    sort_result = results
    if rank_method == 'reposts_count':
        rank_results = results
        sort_result = deal_rank(rank_results)
    elif rank_method == 'timestamp':
        sort_result = sorted(results, key=lambda x:x[5])
        sort_result = deal_rank(sort_result)
    elif rank_method == 'friends_count':
        sort_result = sorted(results, key=lambda x:x[8], reverse=True)
        sort_result = deal_rank(sort_result)
    elif rank_method == 'statuses_count':
        sort_result = sorted(results, key=lambda x:x[10], reverse=True)
        sort_result = deal_rank(sort_result)

    #print 'results:', sort_result
    return sort_result

def read_trend_user_table(topic, date, windowsize):
    trend_user = []
    maker_items = db.session.query(TrendMaker).filter(TrendMaker.topic==topic ,\
                                                                                        TrendMaker.date==date ,\
                                                                                        TrendMaker.windowsize==windowsize).all()
    row_all = []
    if maker_items:
        for item in maker_items:
            uid = item.uid
            user_info = json.loads(item.user_info)
            uname = user_info['name']
            profile_image_url = user_info['profile_image_url']
            if profile_image_url == u'未知':
                profile_image_url = 'no'
            rank = item.rank
            row = [uid, uname, profile_image_url, rank]
            row_all.append(row)
        all_row= sorted(row_all, key=lambda x:x[3])
        row1 = [u'趋势制造者']
        for row in all_row:
            row1.append(row[:3])
    else:
        row1 = [u'趋势制造者']

    trend_user = [row1]

    pusher_items = db.session.query(TrendPusher).filter(TrendPusher.topic==topic ,\
                                                                                         TrendPusher.date==date ,\
                                                                                         TrendPusher.windowsize==windowsize).all()
    row_all = []
    if not pusher_items:
        row2 = []
    else:
        for item in pusher_items:
            uid = item.uid
            user_info = json.loads(item.user_info)
            uname = user_info['name']
            profile_image_url = user_info['profile_image_url']
            if profile_image_url==u'未知':
                profile_image_url = 'no'
            rank = item.rank
            row = [uid, uname, profile_image_url, rank]
            row_all.append(row)
        all_row = sorted(row_all, key=lambda x:x[3])
        row2 = [u'趋势推动者']
        for row in all_row:
            row2.append(row[:3])

    trend_user.append(row2)

    return trend_user

    
    

            
    
