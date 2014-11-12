# -*- coding: utf-8 -*-

import json
import case.model
from case.model import OpinionTestTime, OpinionTestRatio, OpinionTestKeywords, OpinionWeibosNew
from case.extensions import db

def get_opinion_time(topic):
    items = db.session.query(OpinionTestTime).filter(OpinionTestTime.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        topic_term = json.loads(item.child_topic)
        start_ts = item.start_ts
        end_ts = item.end_ts
        results.append([topic_term,start_ts,end_ts])
    
    return results

def get_opinion_ratio(topic):
    items = db.session.query(OpinionTestRatio).filter((OpinionTestRatio.id>=11)&(OpinionTestRatio.id<=20)).all()#ratio表有问题，话题存不进去
    if not items:
        return None
##    items = db.session.query(OpinionTestRatio).filter(OpinionTestRatio.topic==topic).all()
##    if not items:
##        return None
    results = []
    for item in items:
        child_topic = json.loads(item.child_topic)
        ratio = item.ratio
        results.append([child_topic,ratio])

    return results

def get_opinion_keywords(topic):
    items = db.session.query(OpinionTestKeywords).filter(OpinionTestKeywords.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        child_topic = json.loads(item.child_topic)
        keywords_weight = json.loads(item.keywords)
        results.append([child_topic,keywords_weight])
    
    return results

def get_opinion_weibos(topic):
    items = db.session.query(OpinionWeibosNew).filter(OpinionWeibosNew.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        child_topic = json.loads(item.child_topic)
        weight = item.weight
        mid = item.mid
        uid = item.uid
        weibos = item.weibos
        time = item.time
        r_count = item.r_count
        c_count = item.c_count
        repeat = item.repeat
        results.append([child_topic,weight,mid,uid,weibos,time,r_count,c_count,repeat])
    return results


        
