# -*- coding: utf-8 -*-

import os
import time
import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from SSDB import SSDB
from case.global_config import db, SSDB_HOST, SSDB_PORT
from case.model import TopicStatus, TopicIdentification 
from time_utils import ts2datetime, datetime2ts, window2time
from case.global_config import xapian_search_user as user_search




def acquire_topic_id(name, start_ts, end_ts, module="identify"):
    item = db.session.query(TopicStatus).filter_by(topic=name, start=start_ts, end=end_ts, module=module).first()
    if not item: # 若item不存在TopicStatus说明是新插入的，进行插入-----完成通过前端用户提交的要计算的topic数据
        item = TopicStatus(module, -1, topic, start_ts, end_ts, int(time.time()))
        db.session.add(item)
        db.session.commit()
    return item.id


def acquire_topic_name(tid, module='identify'): # 将topic_id转化成对应的topic_name，以便映射到user
    item = db.session.query(TopicStatus).filter_by(id=tid).first()
    if not item:
        return None
    return item.topic


def acquire_user_by_id(uid):
    result = user_search.search_by_id(int(uid), fields=['name', 'location', 'followers_count', 'friends_count'])
    user = {}
    if result:
        user['name'] = result['name']
        user['location'] = result['location']
        user['count1'] = result['followers_count']
        user['count2'] = result['friends_count']
            
    return user


def user_status(uid):  # 暂时未做处理，原文件中涉及到knowledgelist，此处无
    return 1


def is_in_trash_list(uid):
    '''之后增加判断是否为垃圾用户的判断
    '''
    return False

def read_topic_rank_results(topic, top_n, method, date, window):
    data = []
    items = db.session.query(TopicIdentification).filter_by(topic=topic, identifyMethod=method, \
                                                            identifyWindow=window, identifyDate=date).order_by(TopicIdentification.rank.asc()).limit(top_n)
    print items.count()
    if items.count():
        for item in items:
            rank = item.rank
            uid = item.userId
            user = acquire_user_by_id_v2(uid)
            if not user:
                continue
            name = user['name']
            location = user['location']
            count1 = user['count1']
            count2 = user['count2']
            #read from external knowledge database
            status = user_status(uid)
            row = (rank, uid, name, location, count1, count2, status)
            data.append(row)
    return data

def acquire_user_by_id_v2(uid):
    result = user_search.search_by_id(int(uid), fields=['name', 'location', 'followers_count', 'friends_count'])
    user = {}
    if result:
        user['name'] = result['name']
        user['location'] = result['location']
        user['count1'] = result['followers_count']
        user['count2'] = result['friends_count']
            
    return user


def save_rank_results(sorted_uids, identifyRange, method, date, window, topicname):
    '''存放pagerank的计算结果
    '''
    data = []
    rank = 1
    count = 0
    exist_items = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topicname, \
                                                               TopicIdentification.identifyWindow==window, \
                                                               TopicIdentification.identifyDate==date, \
                                                               TopicIdentification.identifyMethod==method).all()
    for item in exist_items:
        db.session.delete(item)
    db.session.commit()
    for uid in sorted_uids:
        user = acquire_user_by_id(uid)
        if not user:
            continue
        count = count + 1
        name = user['name']
        location = user['location']
        count1 = user['count1']
        count2 = user['count2']
        #read from external knowledge database
        status = user_status(uid)
        row = (rank, uid, name, location, count1, count2, status)
        data.append(row)
        if identifyRange == 'topic':
            item = TopicIdentification(topicname, rank, uid, date, window, method)
        else:
            break
        db.session.add(item)
        rank += 1
    db.session.commit()
    print 'done'
    return data


def read_key_users(date, window, topicname, top_n=10):
    '''获取一个话题中的关键用户--即读取pagerank的计算结果
    '''
    items = db.session.query(TopicIdentification).filter_by(topic=topicname, identifyWindow=window, identifyDate=date).order_by(TopicIdentification.rank.asc()).limit(top_n)
    users = []
    if items.count():
        for item in items:
            uid = item.userId
            users.append(uid)
    return users


def _utf8_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, 'utf-8')


def save_gexf_results(topic, identifyDate, identifyWindow, identifyGexf):
    '''保存gexf图数据到SSDB
    '''
    #try:
    ssdb = SSDB(SSDB_HOST, SSDB_PORT)
    if ssdb:
        print 'ssdb yes'
    else:
        print 'ssdb no'
    key = _utf8_unicode(topic) + '_' + str(identifyDate) + '_' + str(identifyWindow)
    print 'key', key
    key = str(key)
    value = identifyGexf
    result = ssdb.request('set',[key,value])
    if result.code == 'ok':
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),'save success',  _utf8_unicode(topic), str(identifyDate), str(identifyWindow)
    else:
        print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'Gexf save into SSDB failed'

    #except Exception, e:
    #    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'SSDB ERROR'
        
