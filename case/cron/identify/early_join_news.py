# -*- coding: utf-8 -*-
import json
import pymongo
from config import db
from model import FirstUserNews
from parameter import all_fields, filter_fields, first_news_count
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
    first_user_list = collection.find({},filter_fields_dict).sort('timestamp').limit(first_news_count)
    rank = 0
    for item in first_user_list:
        rank += 1
        timestamp = item['timestamp']
        save_item = FirstUserNews(topicname, start_ts, end_ts,timestamp, json.dumps(item))
        save_first_news(save_item)
    print 'success save_first_news'

def save_first_news(item):
    topic = item.topic
    start_ts = item.start_ts
    end_ts = item.end_ts
    timestamp = item.timestamp
    news_info = item.news_info
    item_exist = db.session.query(FirstUserNews).filter(FirstUserNews.topic==topic ,\
                                                        FirstUserNews.start_ts==start_ts ,\
                                                        FirstUserNews.end_ts==end_ts).first() # 建表
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()
    
    
        
        
    
    
    

