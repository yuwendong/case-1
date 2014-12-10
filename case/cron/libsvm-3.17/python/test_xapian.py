# -*- coding: utf-8 -*-

import csv
import time
from dynamic_xapian_weibo import getXapianWeiboByDuration,getXapianWeiboByDate
from time_utils import datetime2ts, ts2HourlyTime
from ad import ad_main
from model import *
from config import db
from global_utils import getWeiboById, getTopicByName
from dynamic_xapian_weibo import getXapianWeiboByTopic

fields_list=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'comments_count']

def main(topic,start_time,end_time):
    start_ts = datetime2ts(start_time)
    end_ts = datetime2ts(end_time)+24*3600
##    datestrlist = []
##    for datestr in datestr_list:
##        datestr_new = datestr.replace('-', '')
##        datestrlist.append(datestr_new)
    query_dict = {
        'timestamp': {'$gt': start_ts, '$lt': end_ts},
    }
##    t = topic.split(',')
##    for ctopic in t:
##        query_dict['$and'].append({'topics': ctopic})
    start = time.time()
##    statuses_search = getXapianWeiboByDuration(datestrlist)
##    count, get_results = statuses_search.search(query=query_dict, fields=fields_list)
    topic_id = getTopicByName(topic)['_id']
    xapian_search_weibo = getXapianWeiboByTopic(topic_id)
    count, get_results = xapian_search_weibo.search(query=query_dict, fields=fields_list)
    end = time.time()
    
    #print count
    print 'search takes %s s' % (end-start)
    weibo = []
    for r in get_results():
        weibo.append([r['_id'],r['user'],r['text'].encode('utf-8'),r['timestamp'],r['reposts_count'],r['comments_count']])
    
    ad_main(topic,weibo,'0914',10)#开始进行微博数据的观点挖掘  

if __name__ == '__main__':
##    datestr_list = ['2013-10-02', '2013-09-03', '2013-09-04',\
##                    '2013-09-05', '2013-09-06', '2013-09-07']
    # xapian_search_weibo = getXapianWeiboByDate(datestr)
    topic = u"全军政治工作会议"
    main(topic,'2014-10-28','2014-11-15')
