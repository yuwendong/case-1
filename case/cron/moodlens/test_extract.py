# -*- coding: utf-8 -*-

import sys
import json
from dynamic_xapian_weibo import getXapianWeiboByDate, getXapianWeiboByDuration
sys.path.append('../libsvm-3.17/python/')
from sta_ad import start

weibo_fields = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
                'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
                'comments_count', 'sentiment', 'topics', 'message_type']

def get_nad(rlist):
    flag = '0916'
    data = start(rlist, flag)
    return len(data), data

if __name__ == '__main__':
    datestr_list = ['20130902', '20130903', '20130904',\
                    '20130905', '20130906', '20130907']
    topics = u'东盟,博览会'
    xapian_search_weibo = getXapianWeiboByDuration(datestr_list)
    query_dict = {
        'topics':[]
    }
    for c_topic in topics.split(','):
        query_dict['topics'].append(c_topic)
    count, results = xapian_search_weibo.search(query=query_dict, fields=weibo_fields)
    print count
    
    mid_text = []
    mid_weibo_dict = {}
    for r in results():
        count += 1
        mid_text.append([r['_id'], r['text'].encode('utf-8')])
        mid_weibo_dict[r['_id']] = r

    count, mids = get_nad(mid_text)
    print count
    
    count = 0
    fw = open('items_filter.jl', 'wb')
    for mid in mids:
        r = mid_weibo_dict[int(mid)]
        fw.write(json.dumps(r) + '\n')
    fw.close()
