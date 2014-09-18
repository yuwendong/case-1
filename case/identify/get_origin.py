# -*- coding:utf-8 -*-

import pymongo
from case.extensions import db
from operator import itemgetter
from dynamic_xapian_weibo import getXapianWeiboByTopic
from xapian_case.xapian_backend import XapianSearch
from time_utils import datetime2ts, ts2datetime
from case.model import TopicIdentification, DegreeCentralityUser, BetweenessCentralityUser, ClosenessCentralityUser


DB_NAME = '54api_weibo_v2' 
TB_NAME = 'master_timeline_weibo' 

mongoclient =  pymongo.MongoClient('219.224.135.46')
mongodb = mongoclient[DB_NAME] 
mongotable = mongodb[TB_NAME]

SORT_FIELD = ['reposts_count']

top_weibos_limit = 10

def acquire_user_by_id(uid):
    XAPIAN_USER_DATA_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/user-datapath/'
    user_search = XapianSearch(path=XAPIAN_USER_DATA_PATH, name='master_timeline_user', schema_version=1)
    result = user_search.search_by_id(int(uid), fields=['name', 'location', 'followers_count', 'friends_count'])
    user = {}
    if result:
        user['name'] = result['name']
        user['location'] = result['location']
        user['count1'] = result['followers_count']
        user['count2'] = result['friends_count']
    
    return user

def get_origin_user(topic, end_date, windowsize):
    s = getXapianWeiboByTopic(topic)
    weibos = []
    get_results = s.iter_all_docs(fields=['_id', 'user', 'retweeted_uid', 'reposts_count', 'comments_count'])
    for r in get_results:
        w = dict()
        w['_id'] = r['_id']
        w['user'] = r['user']
        w['retweeted_uid'] = r['retweeted_uid']
        weibo = mongotable.find_one({'_id': int(r['_id'])})
        if weibo:
            w['reposts_count'] = int(weibo['reposts_count'])
            w['comments_count'] = int(weibo['comments_count'])

        weibos.append((r['reposts_count'],w))

    sorted_weibos = sorted(weibos, key=lambda k: k[0], reverse=False)
    #sorted_weibos = sorted_weibos[:]
    sorted_weibos.reverse()
    #print 'sorted_weibos:', sorted_weibos
    rank = 0
    origin_user_dict = {}
    origin_user_x = []
    user_list = []
    for weibo in sorted_weibos:
        retweeted_uid = weibo[1]['retweeted_uid']
        print 'retweeted_uid:', retweeted_uid
        count = s.search(query={'user': retweeted_uid}, count_only=True)
        print 'count:', count
        if count:
            rank += 1
            origin_user = {}
            user_info = acquire_user_by_id(retweeted_uid)
            origin_user['uid'] = retweeted_uid
            if user_info:
                origin_user['name'] = user_info['name']
                origin_user['location'] = user_info['location']
                origin_user['count1'] = user_info['count1']
                origin_user['count2'] = user_info['count2']
            else:
                origin_user['name'] = u'未知'
                origin_user['location'] = u'未知'
                origin_user['count1'] = u'未知'
                origin_user['count2'] = u'未知'

            pagerank = get_user_pagerank(topic, retweeted_uid, end_date, windowsize)
            d_centrality = get_user_dc(topic, retweeted_uid, end_date, windowsize)
            b_centrality = get_user_bc(topic, retweeted_uid, end_date, windowsize)
            c_centrality = get_user_cc(topic, retweeted_uid, end_date, windowsize)
            origin_user['pr'] = pagerank
            origin_user['dc'] = d_centrality
            origin_user['bc'] = b_centrality
            origin_user['cc'] = c_centrality
            origin_user['rank'] = rank
            try:
                if origin_user_dict[str(retweeted_uid)]:
                    rank = rank - 1
                    continue
            except KeyError:
                if origin_user['count1'] != u'未知':
                    origin_user_dict[str(retweeted_uid)] = origin_user
                    origin_user_x.append((str(retweeted_uid), origin_user, origin_user['count1']))
                else:
                    retweeted_uid = retweeted_uid - 1
            #print 'origin_user_x:', origin_user_x
        user_list = sorted(origin_user_x, key=lambda x:x[2], reverse=True) 
        #print 'user_list:', user_list
    return user_list
            
def get_user_pagerank(topic, uid, end_date, windowsize):
    item = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topic ,\
                                                     TopicIdentification.identifyDate==end_date ,\
                                                     TopicIdentification.userId==uid ,\
                                                     TopicIdentification.identifyWindow==windowsize).first()
    if item:
        pr = item.pr
    else:
        pr = 'None'

    return pr

def get_user_dc(topic, uid, end_date, windowsize):
    item = db.session.query(DegreeCentralityUser).filter(DegreeCentralityUser.topic==topic ,\
                                                         DegreeCentralityUser.date==end_date ,\
                                                         DegreeCentralityUser.windowsize==windowsize ,\
                                                         DegreeCentralityUser.userid==uid).first()
    if item:
        dc = item.dc
    else:
        dc = 'None'

    return dc

def get_user_bc(topic, uid, end_date, windowsize):
    item = db.session.query(BetweenessCentralityUser).filter(BetweenessCentralityUser.topic==topic ,\
                                                             BetweenessCentralityUser.date==end_date ,\
                                                             BetweenessCentralityUser.windowsize==windowsize ,\
                                                             BetweenessCentralityUser.userid==uid).first()
    if item:
        bc = item.bc
    else:
        bc = 'None'

    return bc

def get_user_cc(topic ,uid, end_date, windowsize):
    item = db.session.query(ClosenessCentralityUser).filter(ClosenessCentralityUser.topic==topic ,\
                                                            ClosenessCentralityUser.date==end_date ,\
                                                            ClosenessCentralityUser.windowsize==windowsize ,\
                                                            ClosenessCentralityUser.userid==uid).first()
    if item:
        cc = item.cc
    else:
        cc ='None'
    
    return cc
if __name__=='__main__':
    topic = u'东盟,博览会'
    start_ts = '2013-09-02'
    end_ts = '2013-09-07'
    end_time = datetime2ts(end_ts) + Day
    start_time = datetime2ts(start_ts)
    windowsize = (end_time - start_time) / Day
    end_date = ts2dateime(end_time)
    
    get_origin_user(topic, end_date, windowsize)
