# -*- coding: utf-8 -*-
import json
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from case.extensions import db
from case.model import FirstUser, FirstDomainUser
from utils import weiboinfo2url

domain_dict = {'folk':u'民众', 'media':u'媒体', 'opinion_leader':u'意见领袖', 'other':u'其他', 'oversea':u'海外'}
domain_list = ['folk', 'media', 'opinion_leader','oversea', 'other']

def ts2date(ts):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))

def time_top_user(topic, date, windowsize, rank_method):
    results = []
    print 'topic, date, windowsize:', topic.encode('utf-8'), date, windowsize
    items = db.session.query(FirstUser).filter(FirstUser.topic==topic ,\
                                               FirstUser.date==date ,\
                                               FirstUser.windowsize==windowsize).all()
    print 'len(items):', len(items)
    if items:
        for item in items:
            uid = item.uid
            timestamp = item.timestamp
            timestamp = ts2date(timestamp)
            user_info = json.loads(item.user_info)
            uname = user_info['name']
            location = user_info['location']
            profile_image_url = user_info['profile_image_url']
            if profile_image_url == u'未知':
                profile_image_url = ''
            friends_count = user_info['friends_count']
            followers_count = user_info['followers_count']
            statuses_count = user_info['statuses_count']

            if friends_count==u'未知':
                friends_count = -1
            if statuses_count==u'未知':
                statuses_count = -1
            
            created_at = user_info['created_at']

            weibo_info = json.loads(item.weibo_info)
            text = weibo_info['text']
            geo = weibo_info['geo']
            source = weibo_info['source']
            _id = weibo_info['_id']
            weibo_link = weiboinfo2url(uid, _id)
            user_domain = item.user_domain
            domain_name = domain_dict[user_domain]
            row = [uid, uname, location, domain_name, timestamp, text, profile_image_url, friends_count, followers_count, statuses_count, created_at,geo, source, weibo_link, _id]
            results.append(row)
    print 'results:', results
    sorted_results = []
    print 'rank_method:', rank_method
    if rank_method=='timestamp':
        sorted_results = sorted(results, key=lambda x:x[4])
    elif rank_method=='friends_count':
        sorted_results = sorted(results, key=lambda x:x[7], reverse=True)
    elif rank_method=='statuses_count':
        sorted_results = sorted(results, key=lambda x:x[9], reverse=True)
    print 'sorted_results',sorted_results
    #print 'sorted_results[0]:', sorted_results[0]
    new_results = []
    for i in range(len(items)):
        new_row = [i+1]
        for j in range(len(sorted_results[0])):
            if j==7 and sorted_results[i][j]==-1:
                new_row.append(u'未知')
            elif j==9 and sorted_results[i][j]==-1:
                new_row.append(u'未知')
            else:
                new_row.append(sorted_results[i][j])
        new_results.append(new_row)
    return new_results

def time_domain_top_user(topic, date, windowsize, domain, rank_method):
    #results = {'folk':[], 'media':[], 'opinion_leader':[], 'oversea':[], 'other':[]}
    print 'topic, date, windowsize:', topic.encode('utf-8'), date, windowsize
    #domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
    items = db.session.query(FirstDomainUser).filter(FirstDomainUser.topic==topic ,\
                                                     FirstDomainUser.date==date ,\
                                                     FirstDomainUser.windowsize==windowsize ,\
                                                     FirstDomainUser.user_domain==domain).all()
    results = []
    for item in items:
        domain = item.user_domain
        domain_name = domain_dict[domain]
        timestamp = item.timestamp
        timestamp = ts2date(timestamp)
        uid = item.uid

        weibo_info = json.loads(item.weibo_info)
        text = weibo_info['text']
        geo = weibo_info['geo']
        source = weibo_info['source']
        _id = weibo_info['_id']
        weibo_link = weiboinfo2url(uid, _id)

        user_info = json.loads(item.user_info)
        uname = user_info['name']
        location = user_info['location']
        profile_image_url = user_info['profile_image_url']
        if profile_image_url == u'未知':
            profile_image_url = ''
        friends_count = user_info['friends_count']
        followers_count = user_info['followers_count']
        statuses_count = user_info['statuses_count']

        if friends_count==u'未知':
            friends_count = -1
        if statuses_count==u'未知':
            statuses_count = -1
        
        created_at = user_info['created_at']

        #rank = item.rank
        row = [uid, uname, location, domain_name, timestamp, text, profile_image_url, friends_count, followers_count, statuses_count, created_at,geo, source, weibo_link, _id]
        results.append(row)
    sorted_results = []   
    if rank_method=='timestamp':
        sorted_results = sorted(results, key=lambda x:x[4])
    elif rank_method=='friends_count':
        sorted_results = sorted(results, key=lambda x:x[7], reverse=True)
    elif rank_method=='statuses_count':
        sorted_results = sorted(results, key=lambda x:x[9], reverse=True)

    new_results = []
    for i in range(len(items)):
        new_row = [i+1]
        for j in range(len(sorted_results[0])):
            if j==7 and sorted_results[i][j]==-1:
                new_row.append(u'未知')
            elif j==9 and sorted_results[i][j]==-1:
                new_row.append(u'未知')
            else:
                new_row.append(sorted_results[i][j])
        new_results.append(new_row)

    return new_results


def read_table_fu(topic, date, windowsize, top_n):
    results = []
    items_all = db.session.query(FirstUser).filter(FirstUser.topic==topic ,\
                                                   FirstUser.date==date ,\
                                                   FirstUser.windowsize==windowsize).all()
    row_all = []
    for item in items_all:
        uid = item.uid
        timestamp = item.timestamp
        user_info = json.loads(item.user_info)
        uname = user_info['name']
        profile_image_url = user_info['profile_image_url']
        if profile_image_url == u'未知':
            profile_image_url = ''
        row = [uid, uname, profile_image_url, timestamp]
        row_all.append(row)
    all_row = sorted(row_all, key=lambda x:x[3])
    row1 = [u'所有']
    for row in all_row:
        row1.append(row[:3])
    # row1为第一行--整体的首发用户信息
    results = [row1]
    for domain in domain_list:
        items = db.session.query(FirstDomainUser).filter(FirstDomainUser.topic==topic ,\
                                                         FirstDomainUser.date==date ,\
                                                         FirstDomainUser.windowsize==windowsize ,\
                                                         FirstDomainUser.user_domain==domain).all()
        domain_name = domain_dict[domain]
        rows = [domain_name]
        for item in items:
            uid = item.uid
            user_info = json.loads(item.user_info)
            uname = user_info['name']
            profile_image_url = user_info['profile_image_url']
            if profile_image_url == u'未知':
                profile_image_url = ''
            row = [uid, uname, profile_image_url]
            rows.append(row)
        results.append(rows)

    return results

    
    
      
