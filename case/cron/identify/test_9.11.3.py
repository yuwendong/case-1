# -*- coding:utf-8 -*-

import sys
import time
import datetime

#sys.path.append('../xapian_case')
from xapian_case.xapian_backend import XapianSearch
from xapian_case.utils import top_keywords, not_low_freq_keywords, gen_mset_iter
from dynamic_xapian_weibo import getXapianWeiboByDate

# 默认schema_version为5
#datestr_list = ['20130901', '20130902', '20130903', '20130904', \
#                '20130905', '20130906', '20130907']
#s = getXapianWeiboByDate(datestr_list)

fields_list=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', 'comments_count', 'sentiment', 'topics', 'message_type', 'terms']

'''
# 测试八个测试字段
get_results = s.iter_all_docs(fields=fields_list)
begin_ts=time.mktime(datetime.datetime(2013,1,1).timetuple())
end_ts=time.mktime(datetime.datetime(2014,1,1).timetuple())
count=0
for r in get_results:
    count+=1
    if count>20000:
        break
    for f in fields_list:
        if f == '_id' or f == 'sentiment' or f == 'message_type' or f =='retweeted_mid' or f == 'user':
           scount, get_results=s.search(query={f:r[f]},fields=fields_list)
        elif f == 'timestamp':
           scount,get_results=s.search(query={'timestamp':{'$gt':begin_ts,'$lt':r[f]}},fields=fields_list)
        elif f == 'reposts_count' or f == 'comments_count':
           scount,get_results=s.search(query={f:{'$gt': r[f]-1, '$lt': r[f] + 1}},fields=fields_list)
        else:
            scount=1
        if scount == 0:
            print 'error'
            print count,f
print count

#测试text字段
count, get_results =  s.search(query={'message_type': 1}, fields=fields_list)
print 'query2:'
if count!=0:
    for r in get_results():
        print "** " * 10
        print r['message_type'], type(r['message_type'])
        print r['geo']
        print r['_id']
        print r['user']
        print r['text'].encode('utf-8')
        print r['timestamp']
        print r['terms']

    print 'hits: %s' % count
else:
    print 'no results'
'''

#测试topics字段
datestr_list = ['20130902', '20130903', '20130904', \
                '20130905', '20130906', '20130907']
# datestr_list = ['20130907']
k = 0
for datestr in datestr_list:
    s = getXapianWeiboByDate(datestr)
    count, results = s.search(query={'topics': [u'东盟', u'博览会']}, fields=['text'])#fields=fields_list)
    '''
    f = open(datestr+'.txt', 'wb')
    for result in results():
        save_line = result['text'].encode('utf-8')
        f.write(save_line+'\n')
    '''
    print 'count:', count
    k = k+count
print 'all_count:', k

'''
stopic=u'中国'

query_dict = {
    'timestamp': {'$gt': begin_ts, '$lt': end_ts},
    'topics':u'中国'
      }

count_dict={}
get_results = s.iter_all_docs(fields = fields_list)
for i in get_results:
    try:
        count_dict[i['timestamp']] += 1
    except KeyError:
        count_dict[i['timestamp']] = 1
print len(count_dict)
'''
