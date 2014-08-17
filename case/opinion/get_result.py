# -*- coding: utf-8 -*-

import json
import case.model
from case.model import OpinionTestTime, OpinionTestRatio, OpinionTestKeywords, OpinionTestWeibos
from case.extensions import db

def get_opinion_time(topic):
    items = db.session.query(OpinionTestTime).filter(OpinionTestTime.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        topic_term = json.loads(item.child_topic)
        child_topic = topic_term.keys()[0]
        term_list = topic_term[child_topic]
        start_ts = item.start_ts
        end_ts = item.end_ts
        # 缺少子话题名称--name
        results.append({child_topic:[start_ts, end_ts, term_list[:2]]})
    
    return results

def get_opinion_ratio(topic):
    items = db.session.query(OpinionTestRatio).filter(OpinionTestRatio.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        child_topic = item.child_topic
        ratio = item.ratio
        results.append({child_topic:item.ratio})
    return results

def get_opinion_keywords(topic):
    items = db.session.query(OpinionTestKeywords).filter(OpinionTestKeywords.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        child_topic = item.child_topic
        keywords_weight = json.loads(item.keywords)
        results.append({child_topic:keywords_weight})
    
    return results

def get_opinion_weibos(topic):
    items = db.session.query(OpinionTestWeibos).filter(OpinionTestWeibos.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        child_topic = item.child_topic
        weibos_weight = json.loads(item.weibos)
        results.append({child_topic:weibos_weight})
    return results


        
