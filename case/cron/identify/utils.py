# -*- coding: utf-8 -*-

import os
import time
import random
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from SSDB import SSDB
from config import db, SSDB_HOST, SSDB_PORT
from model import Topics, TsRank, TopicStatus, TopicIdentification, DsTopicIdentification
sys.path.append('../')
from time_utils import ts2datetime, datetime2ts, window2time
from config import xapian_search_user as user_search

def acquire_topic_id(name, start_ts, end_ts, module="identify"):
    item = db.session.query(TopicStatus).filter_by(topic=name, start=start_ts, end=end_ts, module=module).first()
    if not item: # 若item不存在TopicStatus说明是新插入的，进行插入-----完成通过前端用户提交的要计算的topic数据
        item = TopicStatus(module, -1, topic, start_ts, end_ts, int(time.time()))
        db.session.add(item)
        db.session.commit()
    return item.id

def acquire_real_topic_id(topicname, start_ts, end_ts):
    item = db.session.query(Topics).filter(Topics.topic==topicname ,\
                                           Topics.start_ts==start_ts ,\
                                           Topics.end_ts==end_ts).first()
    if item:
        real_topic_id = item.id
    else:
        real_topic_id = None
    
    return real_topic_id

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


def user_status(uid): 
    return 1


def is_in_trash_list(uid):
    '''之后增加判断是否为垃圾用户的判断
    '''
    return False


def save_rank_results(sorted_uids, identifyRange, method, date, window, topicname, all_uid_pr):
    '''存放源头转发网络pagerank的计算结果
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
        pr = all_uid_pr[uid]
        user = acquire_user_by_id(uid)
        count += 1
        if not user:
            name = 'Unknown'
            location = 'Unknown'
            count1 = 'Unknown'
            count2 = 'Unknown'
        else:
            name = user['name']
            location = user['location']
            count1 = user['count1']
            count2 = user['count2']
        #read from external knowledge database
        status = user_status(uid)
        row = (rank, uid, name, location, count1, count2, status)
        data.append(row)
        if identifyRange == 'topic':
            item = TopicIdentification(topicname, rank, uid, date, window, method, pr)
        else:
            break
        db.session.add(item)
        rank += 1
    db.session.commit()
    print 'done'
    print 'len(data):', len(data)
    return data

def save_ds_rank_results(sorted_uids, identifyRange, method, date, window, topicname, all_uid_pr):
    '''存放直接上级转发网络pagerank的计算结果
    '''
    data = []
    rank = 1
    count = 0
    exist_items = db.session.query(DsTopicIdentification).filter(DsTopicIdentification.topic==topicname, \
                                                                 DsTopicIdentification.identifyWindow==window, \
                                                                 DsTopicIdentification.identifyDate==date, \
                                                                 DsTopicIdentification.identifyMethod==method).all()
    for item in exist_items:
        db.session.delete(item)
    db.session.commit()
    for uid in sorted_uids:
        pr = all_uid_pr[uid]
        user = acquire_user_by_id(uid)
        count += 1
        if not user:
            name = 'Unknown'
            location = 'Unknown'
            count1 = 'Unknown'
            count2 = 'Unknown'
        else:
            name = user['name']
            location = user['location']
            count1 = user['count1']
            count2 = user['count2']
        #read from external knowledge database
        status = user_status(uid)
        row = (rank, uid, name, location, count1, count2, status)
        data.append(row)
        if identifyRange == 'topic':
            item = DsTopicIdentification(topicname, rank, uid, date, window, method, pr)
        else:
            break
        db.session.add(item)
        rank += 1
    db.session.commit()
    print 'done'
    print 'len(data):', len(data)
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

def ds_read_key_users(date, window, topicname, top_n=10):
    '''
    读取直接上级转发网络的pagerank值，区分于上面的源头转发网络
    直接上级转发网络的pagerank值存放在DsTopicIdentification中
    '''
    items = db.session.query(DsTopicIdentification).filter_by(topic=topicname, identifyWindow=window, identifyDate=date).order_by(DsTopicIdentification.rank.asc()).limit(top_n)
    users = []
    if items.count():
        for item in items:
            uid = item.userId
            users.append(uid)
    return users

def ds_tr_read_key_users(date, window, topicname, top_n=10):
    '''
    获取直接上级转发网络中trendsetter_rank排名前十的用户，主要用户画图时进行特殊点的显示
    '''
    items = db.session.query(TsRank).filter_by(topic=topicname, windowsize=window, date=date).order_by(TsRank.rank.asc()).limit(top_n)
    users = []
    if items.count():
        for item in items:
            uid = item.uid
            users.append(uid)
    return users

def _utf8_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, 'utf-8')


def save_gexf_results(topic, identifyDate, identifyWindow, identifyGexf, gexf_type):
    '''保存gexf图数据到SSDB
    '''
    #try:
    ssdb = SSDB(SSDB_HOST, SSDB_PORT)
    if ssdb:
        print 'ssdb yes'
    else:
        print 'ssdb no'
    if gexf_type == 1:
        key = _utf8_unicode(topic) +'_' + str(identifyDate) + '_' + str(identifyWindow) + '_' + 'source_graph'
    else:
        key = _utf8_unicode(topic) +'_' + str(identifyDate) + '_' + str(identifyWindow) + '_' + 'direct_superior_graph'
    print 'key', key.encode('utf-8')
    key = str(key)
    value = identifyGexf
    result = ssdb.request('set',[key,value])
    if result.code == 'ok':
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),'save Gexf success'
    else:
        print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'Gexf save into SSDB failed'

    #except Exception, e:
    #    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'SSDB ERROR'


def save_graph(topic, identifyDate, identifyWindow, graph, graph_type):
    '''
    保存make_network产生的没有增加attribute，以及未做cut和sampling的原始图结构
    '''
    ssdb = SSDB(SSDB_HOST, SSDB_PORT)
    if ssdb:
        print 'ssdb yes'
    else:
        print 'ssdb no'
    if graph_type == 'g':
        key = _utf8_unicode(topic) +'_' + str(identifyDate) + '_' + str(identifyWindow) + '_' + 'make_network_g'
    elif graph_type == 'ds_g':
        key = _utf8_unicode(topic) +'_' + str(identifyDate) + '_' + str(identifyWindow) + '_' + 'make_network_ds_g'
    elif graph_type == 'gg':
        key = _utf8_unicode(topic) +'_' + str(identifyDate) + '_' + str(identifyWindow) + '_' + 'make_network_gg'
    elif graph_type == 'ds_udg':
        key = _utf8_unicode(topic) +'_' + str(identifyDate) + '_' + str(identifyWindow) + '_' + 'make_network_ds_udg'
    print 'key:', key.encode('utf-8')
    key = str(key)
    value = graph
    result = ssdb.request('set', [key, value])
    if result_code == 'ok':
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), graph_type, 'save make_network_graph success'
    else:
        print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), graph_type, ' save make_network_graph into SSDB failed'
        
def read_graph(topic, identifyDate, identifyWindow, graph_type):
    '''
    读取make_network产生的原始图结构
    '''
    if graph_type:
        key = _utf8_unicode(topic) +'_' + str(identifyDate) + '_' + str(identifyWindow) + '_' + 'make_network_' + graph_type
    else:
        return None
    try:
        ssdb = SSDB(SSDB_HOST, SSDB_PORT)
        value = ssdb.request('get', [key])
        if value.code == 'ok' and value.data:
            response = value.data # ???!!这里还需要进行确定
            return response
        return None
    except Exception, e:
        print e
        return None

def save_attribute_dict(attribute_dict, graph_type):
    '''
    临时保存attribute_dict，所以不进行topic的唯一指定，使其每一次存储都会覆盖上一次的。
    '''
    ssdb = SSDB(SSDB_HOST, SSDB_PORT)
    if ssdb:
        print 'ssdb yes'
    else:
        print 'ssdb no'
    if graph_type == 'g':
        key = 'g_attribute_dict'
    elif graph_type == 'ds_g':
        key = 'ds_g_attribute_dict'
    print 'key:', key.encode('utf-8')
    value = json.dumps(attribute_dict)
    result = ssdb.request('set', [key, value])
    if result.code == 'ok':
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), key.encode('utf-8'), 'save success'
    else:
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), key.encode('utf-8'), 'save failed'

def read_attribute_dict(graph_type):
    '''
    读取临时保存的attribute_dict
    '''
    if graph_type:
        key = graph_type + '_attribute_dict'
    try:
        ssdb = SSDB(SSDB_HOST, SSDB_PORT)
        value = ssdb.request('get', [key])
        if value.code == 'ok' and value.data:
            response = value.data # 这里的读取数据应该是怎样的？！！！！但是views文件中的make_response是几个意思？！！
            return response
        return None
    except Exception, e:
        print e
        return None
