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
            result = []
            uid = item.uid
            timestamp = item.timestamp
            user_info = item.user_info
            uname = user_info['name']
            location = user_info['location']
            weibo_info = item.weibo_info
            text = weibo_info['text']
            user_domain = item.user_domain
            row = [uid, uname, location, user_domain, timestamp, text]
            results.append(row)
    #print 'results:', results
    results = sorted(results, key=lambda x:x[4])
    new_results = []
    for i in range(len(items)):
        new_row = [i+1]
        for j in len(results[0]):
            new_row.append(results[i][j])
        new_results.append(new_row)
    return new_results

def time_domain_top_user(topic, date, windowsize, domain):
    #results = {'folk':[], 'media':[], 'opinion_leader':[], 'oversea':[], 'other':[]}
    print 'topic, date, windowsize:', topic.encode('utf-8'), date, windowsize
    #domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
    items = db.session.query(FirstDomainUser).filter(FirstDomainUser.topic==topic ,\
                                                     FirstDomainUser.date==date ,\
                                                     FirstDomainUser.windowsize==windowsize ,\
                                                     FirstDomainUser.domain_user==domain).all()
    results = []
    for item in items:
        domain = item.user_domain
        timestamp = item.timestamp
        weibo_info = item.weibo_info
        text = weibo_info['text']
        user_info = item.user_info
        uid = item.uid
        uname = user_info['name']
        location = user_info['location']
        rank = item.rank
        row = [rank, uid, uname, location, domain, timestamp, text]
        results.append(row)
        
    new_results = sorted(results, key=lambda x:x[0])

    return new_results

        
