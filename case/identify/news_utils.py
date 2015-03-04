# -*- coding: utf-8 -*-'''
'''
identify/news_utils
'''
import sys
import json
from case.time_utils import ts2date
reload(sys)
sys.setdefaultencoding('utf-8')
from case.extensions import db
from case.model import FirstUserNews, TrendMakerNews, TrendPusherNews

# 早期新闻
# 排序方式：timestamp(default),weight
def get_news_first_user(topic, start_ts, end_ts, rank_method, news_skip, news_limit_count):
    results = []
    
    print 'topic, start_ts, end_ts, rank_method:', topic.encode('utf-8'), ts2date(start_ts), ts2date(end_ts), rank_method
    items = db.session.query(FirstUserNews).filter(FirstUserNews.topic==topic ,\
                                                                               FirstUserNews.start_ts==start_ts ,\
                                                                               FirstUserNews.end_ts==end_ts).all()
    if not items or items==[]:
        return []
    for item in items:
        row = []
        timestamp = item.timestamp
        news_info = json.loads(item.news_info)
        news_id = news_info['id']
        url = news_info['url']
        summary = news_info['summary']
        datetime = news_info['datetime']
        source_from_name = news_info['source_from_name']
        content168 = news_info['source_info']
        title = news_info['title']
        same_news_num = news_info['same_news_num']
        transmit_name = news_info['transmit_name']
        weight = news_info['weight']
        row = [news_id, url, summary, timestamp ,datetime, source_from_name, content168, title, same_news_num, transmit_name, weight]
        results.append(row)
    if rank_method=='timestamp':
        sort_results = sorted(results, key=lambda x:x[3]) # 时间戳正序排列
    elif rank_method == 'weight':
        sort_results = sorted(results, key=lambda x:x[10], reverse=True) # 相关度逆序
        
    return sort_results[news_skip:news_limit_count+news_skip]

# 趋势制造者
#排序方式: timestamp,weight(default)
def get_news_trend_maker(topic, start_ts, end_ts, rank_method, news_skip, news_limit_count):
    results = []
    print 'topic, start_ts, end_ts, rank_method:', topic.encode('utf-8'), ts2date(start_ts), ts2date(end_ts), rank_method

    items = db.session.query(TrendMakerNews).filter(TrendMakerNews.topic==topic ,\
                                                                                    TrendMakerNews.start_ts==start_ts ,\
                                                                                    TrendMakerNews.end_ts==end_ts).all()
    if not items or items==[]:
        return []
    for item in items:
        row = []
        news_id = item.news_id
        timestamp = item.timestamp
        weight = item.weight
        news_info = json.loads(item.news_info)

        url = news_info['url']
        summary = news_info['summary']
        datetime = news_info['datetime']
        source_from_name = news_info['source_from_name']
        content168 = news_info['source_info']
        title = news_info['title']
        same_news_num = news_info['same_news_num']
        transmit_name = news_info['transmit_name']       
        row = [news_id, url, summary, timestamp ,datetime, source_from_name, content168, title, same_news_num, transmit_name, weight]
        results.append(row)
        
    if rank_method == 'timestamp':
        sort_results = sorted(results, key=lambda x:x[3]) # 时间戳正序排列
    elif rank_method == 'weight':
        sort_results = sorted(results, key=lambda x:x[10]) # 相关度排序

    return sort_results[news_skip:news_limit_count+news_skip]

# 趋势推动者
# 排序方式 : comments_count(default), timestamp,weight 
def get_news_trend_pusher(topic, start_ts, end_ts, rank_method, news_skip, news_limit_count):
    results = []
    print 'topic, start_ts, end_ts, rank_method:', topic.encode('utf-8'), ts2date(start_ts), ts2date(end_ts), rank_method

    items = db.session.query(TrendPusherNews).filter(TrendPusherNews.topic==topic ,\
                                                                                     TrendPusherNews.start_ts==start_ts ,\
                                                                                     TrendPusherNews.end_ts==end_ts),all()
    if not items or items==[]:
        return []
    
    for item in items:
        row = []
        news_id = item.news_id
        timestamp = item.timestamp
        same_news_num = item.same_news_num
        comments_count = item.comments_count
        news_info = json.loads(item.news_info)

        url = news_info['url']
        summary = news_info['summary']
        datetime = news_info['datetime']
        source_from_name = news_info['source_from_name']
        content168 = news_info['source_info']
        title = news_info['title']
        weight = news_info['weight']
        transmit_name = news_info['transmit_name']
        same_news_num = news_info['same_news_num']
        row = [news_id, url, summary, timestamp ,datetime, source_from_name, content168, title, same_news_num, transmit_name, weight, comments_count]
        results.append(row)

    if rank_method =='comments_count':
        sort_results = sorted(results, key=lambda x:x[11],reverse=True) # 评论数逆序排列
    elif rank_method=='timestamp':
        sort_results = sorted(results, key=lambda x:x[3]) # 时间戳正序排列
    elif rank_method=='weight':
        sort_results = sorted(results, key=lambda x:x[10], reverse=True) # 相关度逆序排序

    return sort_results[news_skip:news_limit_count+news_skip]
