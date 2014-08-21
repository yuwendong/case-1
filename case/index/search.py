#-*- coding: utf-8 -*-

import json
from case.extensions import db
from case.model import IndexTopic


CITY_LIMIT = 3
KEY_WORDS_LIMIT = 3
OPINION_LIMIT = 100
MEDIA_OPINION_LIMIT = 10

def search_count(topic):
    item = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item:
        count = item.count
        print 'item,count'
        print item, count
    else:
        count = 0
    return count

def search_user_count(topic):
    item = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item:
        user_count = item.user_count
        print 'item,user_count'
        print item, user_count
    else:
        user_count = 0
    return user_count

def search_begin(topic):
    item = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item:
        begin = item.begin
        print 'item,begin'
        print item, begin
    else:
        begin = 0
    return begin

def search_end(topic):
    item = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item:
        end = item.end
        print 'item,end'
        print item, end
    else:
        end = 0
    return end

def search_area(topic, limit = CITY_LIMIT):
    item = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item:
        area_list = json.loads(item.area)
        area = area_list[len(area_list) - limit:]
        print 'item,area'
        print item, area
    else:
        area = []
    return area

def search_key_words(topic, limit = KEY_WORDS_LIMIT):
    item = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item:
        key_words_dict = json.loads(item.key_words)
        key_words_list = key_words_dict.items()
        key_words_sublist = key_words_list[len(key_words_list) - limit:]
        key_words = {}
        for k,v in key_words_sublist:
            key_words[k] = v
        print 'item,key_words'
        print item, key_words
    else:
        key_words = {}
    return key_words

def search_opinion(topic, limit = OPINION_LIMIT):
    item = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item:
        opinion_list = json.loads(item.opinion)
        opinion = opinion_list[len(opinion_list)-limit:]
        print 'item,opinion'
        print item, opinion
    else:
        opinion = []
    return opinion

def search_media_opinion(topic, limit = MEDIA_OPINION_LIMIT):
    item = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item:
        media_opinion_list = json.loads(item.media_opinion)
        media_opinion = media_opinion_list[len(media_opinion_list)-limit:]
        print 'item,media_opinion'
        print item, media_opinion
    else:
        media_opinion = []
    return media_opinion

if __name__ == '__main__':
    topic = u'中国'
    search_topic_count(topic)
