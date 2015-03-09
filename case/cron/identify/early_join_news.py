# -*- coding: utf-8 -*-
import json
import pymongo
import sys
#from config import db
#from model import FirstUserNews
from parameter import all_fields, filter_fields, first_news_count
sys.path.append('../../')
from global_config import db
from model import FirstUserNews
from time_utils import datetime2ts, ts2datetime
'''
all_fields = ['id', '_id', 'title', 'url', 'summary', 'timestamp', \
                   'datetime', 'date', 'thumbnail_url', 'user_id', 'user_url', \
                   'user_image_url', 'user_name', 'source_website', \
                   'category', 'same_news_num', 'more_same_link', \
                   'relative_news', 'key', 'key', 'tplid', 'classid', 'title1', \
                   'content168','isV', 'Pagesize', 'Showurl', 'source_from_name' ,\
                   'Replies', 'last_modify', 'first_in', 'news_author', 'transmit_name', 'weight']
filter_fields = ['user_id', 'user_url', 'user_image_url', 'user_name',\
                      'relative_news', 'key', 'tplid', 'classid', 'isV', 'Pagesize', 'Showurl' ,\
                      'Replies', 'last_modify', 'first_in','news_author']
'''
def get_filter_dict():
    filter_dict = {}
    for field in filter_fields:
        filter_dict[field] = 0
        
    return filter_dict

def early_join(topicname, start_ts, end_ts, collection):
    filter_fields_dict = get_filter_dict() # 筛选掉部分字段需要的字典的形成
    # pay attention
    query_dict = {'timestamp':{'$gte':start_ts, '$lte':end_ts}}
    print 'query_dict, first_news_count:', query_dict, first_news_count
    #first_user_list = collection.find(query_dict, filter_fields_dict).sort('timestamp').limit(first_news_count)
    first_user_list = collection.find(query_dict, filter_fields_dict).sort('timestamp')
    rank = 0
    # deal with the start_ts/end_ts is not the whole day
    if start_ts - datetime2ts(ts2datetime(start_ts)) != 0:
        start_ts = datetime2ts(ts2datetime(start_ts))
    if end_ts - datetime2ts(ts2datetime(end_ts)) != 0:
        end_ts = datetime2ts(ts2datetime(end_ts)) + 3600 * 24
    
    items_exist = db.session.query(FirstUserNews).filter(FirstUserNews.topic==topicname, \
                                                         FirstUserNews.start_ts==start_ts ,\
                                                         FirstUserNews.end_ts==end_ts).all()
    for item_exist in items_exist:
        db.session.delete(item_exist)
    db.session.commit()
    # 媒体去重
    media_list = []
    for item in first_user_list:
        
        meida_name = ''
        transmit_name = item['transmit_name']
        source_from_name = item['source_from_name']
        if not transmit_name:
            media_name = source_from_name
        else:
            media_name = transmit_name
        if media_name in media_list:
            continue
        rank += 1
        media_list.append(media_name)
        
        timestamp = item['timestamp']
        save_item = FirstUserNews(topicname, start_ts, end_ts,timestamp, json.dumps(item))
        db.session.add(save_item)
        print 'rank:', rank
    db.session.commit()
    print 'success save_first_news'
