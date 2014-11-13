# -*- coding: utf-8 -*-
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from case.extensions import db
from case.model import FirstUser, FirstDomainUser

def time_top_user(topic, date, windowsize):
    results = []
    print 'topic, date, windowsize:', topic.encode('utf-8'), date, windowsize
    items = db.session.query(FirstUser).filter(FirstUser.topic==topic ,\
                                               FirstUser.date==date ,\
                                               FirstUser.windowsize==windowsize).all()
    print 'len(items):', len(items)
    if items:
        for item in items:
            result = {}
            result['uid'] = item.uid
            result['timestamp'] = item.timestamp
            result['user_info'] = json.loads(item.user_info)
            result['weibo_info'] = json.loads(item.weibo_info)
            result['user_domain'] = item.user_domain
            results.append(result)
    #print 'results:', results
    return results

def time_domain_top_user(topic, date, windowsize):
    results = {'folk':[], 'media':[], 'opinion_leader':[], 'oversea':[], 'other':[]}
    print 'topic, date, windowsize:', topic.encode('utf-8'), date, windowsize
    domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
    items = db.session.query(FirstDomainUser).filter(FirstDomainUser.topic==topic ,\
                                                     FirstDomainUser.date==date ,\
                                                     FirstDomainUser.windowsize==windowsize).all()
    for item in items:
        domain = item.user_domain
        timestamp = item.timestamp
        weibo_info = item.weibo_info
        user_info = item.user_info
        rank = item.rank
        row = (rank, timestamp, domain, user_info, weibo_info)
        results[domain].append(row)
    '''
    sort for each domain
    '''
    for domain_info in results():
        user_list = results[domain_info]
        if not user_list==[]:
            sort_user_list = sorted(user_list, key=lambda x:x[0])
        results[domain] = sort_user_list

    return results

        
