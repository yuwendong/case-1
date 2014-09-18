# -*- coding:utf-8 -*-


from dynamic_xapian_weibo import getXapianWeiboByTopic
from case.extensions import db
from xapian_case.xapian_backend import XapianSearch
from time_utils import datetime2ts, ts2datetime
from case.model import TopicIdentification, DegreeCentralityUser, BetweenessCentralityUser, ClosenessCentralityUser

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
    counts, results = s.search(fields=['user', 'retweeted_uid', 'reposts_count'], sort_by=['reposts_count'], reverse=False)
    k = 0
    origin_user_dict = {}
    origin_user_x = []
    for result in results():
        if k == 10:
            break
        uid = result['retweeted_uid']
        print 'uid', uid
        count = s.search(query={'user': uid}, count_only=True)
        print 'count:',count
        if count != 0:
            origin_user = {}
            #print 'exist:uid', uid
            k += 1
            user_info = acquire_user_by_id(uid)
            origin_user['uid'] = uid
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
            pagerank = get_user_pagerank(topic, uid, end_date, windowsize)
            d_centrality = get_user_dc(topic, uid, end_date, windowsize)
            b_centrality = get_user_bc(topic, uid, end_date, windowsize)
            c_centrality = get_user_cc(topic, uid, end_date, windowsize)
            origin_user['pr'] = pagerank
            origin_user['dc'] = d_centrality
            origin_user['bc'] = b_centrality
            origin_user['cc'] = c_centrality
            origin_user['rank'] = k
            try:
                if origin_user_dict[str(uid)]:
                    k = k - 1
                    continue
            except KeyError:
                if origin_user['count1'] != u'未知':
                    origin_user_dict[str(uid)] = origin_user
                    origin_user_x.append((str(uid), origin_user, origin_user['count1']))
                else:
                    k = k - 1
            
            #origin_user_list.add(origin_user)
        results = sorted(origin_user_x, key=lambda x:x[2], reverse=True) 


    return results
            
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
