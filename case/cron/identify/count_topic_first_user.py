# -*- coding: utf-8 -*-

import time
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from config import db
from model import NewTopicStatus, FirstUser, FirstDomainUser, AllFrequentUser # NewTopicStatus AllFrequentUser需要在model文件中建立
from time_uitls import datetime2ts
from collections import Counter

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour *6
Day = Hour * 24
Topk = 10
Categories = ['反腐', '自然灾害', '城管']
# 仅作为测试使用---但实际应该存在数据库中允许能够进行修改和增加，但是修改会影响话题与category的对应。这里需要进行考虑！！

'''
将话题分别对应语料库分进不同的类别（机制是每新加一个话题，就将其对应存放在一个类别之下）
在存入NewTopicStauts之前进行处理，增加一个category字段
通过语料库进行处理
'''
def add_topic(topic, start_ts, end_ts):
    module = 'identify'
    status = '-1'
    category = topic2category(topic)
    db_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    item = NewTopicStatus(module, topic, start_ts, end_ts, category, db_date, status)
    item_exist = db.session.query(NewTopicStatus).filter(NewTopicStatus.topic==topic ,\
                                                         NewTopicStatus.start_ts==start_ts ,\
                                                         NewTopicStatus.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()

'''
与语料库进行映射对比，将话题打上category字段性质
'''
def topic2category(topic):
    return category

 
'''
根据统计结果形成的字典，以value进行排序
'''
def sort_by_value(d):
    items = d.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort()
    print 'sort_by_vlue_cnt:', backitems
    return backitems # 用例[[1, 'b'], [2, 'a'], [7, 'f'], [12, 'p']]
    

'''
统计每一类话题中first user出现的频率
话题的类别暂定作为一个全局的固定变量
'''
def frequent_first_user():
    db_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    items = db.session.query(FirstUser).filter(FirstUser.db_time<=db_time).all()
    if not items:
        return None
    user_list = []
    for item in items:
        uid = item.uid
        user_list.append(uid)
    cnt = Counter()
    for user in user_list:
        cnt[user] += 1
    count_user = sort_by_value(cnt[0])
    top_user = count_user[len(count_user)-Topk:]
    ffu_kind = 'all'
    save_all_ffu(top_user, ffu_kind)
    return 'success save_all_ffu'
        
      
def save_all_ffu(top_user, ffu_kind): # ??!!是否需要进行时间快照的数据记录？
    # 时间快照数据在一段时间范围内产生的变化能否说明一些什么内容？！！！
    db_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    user_frequent = json.dumps(top_user)
    item = AllFrequentUser(db_time, ffu_kind, json.dumps(user_frequent))
    item_exist = db.session.query(AllFrequentUser).filter(AllFrequentUser.ffu_kind==ffu_kind).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()


'''
统计每一类话题中各个领域的first user出现的频率
'''
def frequent_domain_first_user():
    for category in categories:
        user_list = []
        topics = db.session.query(NewTopicStatus).filter(NewTopicStatus.category==category ,\
                                                        NewTopicStatus.module=='identify' ,\
                                                        NewTopicStatus.status==1).all() # 获取某一类话题，并且identify这一模块计算已经完成
        for topic_item in topics:
            topic = topic_item.topic
            items = db.session.query(FirstDomainUser).filter(FirstDomainUser.topic==topic).all()
            for item in items:
                uid = item.uid
                user_list.append(uid)
        cnt = Counter()
        for user in user_list:
            cnt[user] += 1
        print 'category:', category
        print 'id_count:', cnt # 生成字典({uid:count})
        count_user = sort_by_value(cnt[0]) # 根据统计结果抽取频率前10的用户，然后保存。结果为正序排列
        top_user = count_user[len(count_user)-Topk:]
        # 数据库中不存储对应的微博信息和用户信息， 在展示时，再进行查询，在view中要写
        ffu_kind = category
        save_all_ffu(top_user, ffu_kind)
        return 'save_all_domain_ffu'

if __name__=='__main__':
    topic = '东盟,博览会'
    start_ts = datetime2ts('2013-09-02')
    end_ts = datetime2ts('2013-09-07')+Day
    addtopic()
    result1 = frequent_first_user()
    print result1
    result2 = frequent_domain_fisrt_user()
    print result2
