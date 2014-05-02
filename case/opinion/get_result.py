# -*- coding: utf-8 -*-

import case.model
from case.model import OpinionTopic, OpinionWeibos , Opinion, OpinionHot
from case.extensions import db

def getOpinion(topic):#提取话题下的所有观点
    items = db.session.query(OpinionTopic).filter(OpinionTopic.topic==topic).all()
    opinion = []
    for item in items:
        row = dict()
        row['id'] = item.id
        row['word'] = item.opinion
        opinion.append(row)

    return opinion

def getRelation(topic, opinion):#提取话题-观点的对应关系 
    items = db.session.query(OpinionTopic).filter((OpinionTopic.topic==topic)&(OpinionTopic.opinion==opinion)).all()
    for item in items:
        relation = item.id

    return relation

def getWeibo(opinionTopic):#提取某个观点的重要微博
    items = db.session.query(OpinionWeibos).filter(OpinionWeibos.opinionTopic==opinionTopic).all()
    weibo = []
    for item in items:
        row = dict()
        row['mid'] = item.mid
        row['text'] = item.weibos
        row['user'] = item.user
        row['uid'] = item.userid
        row['posttime'] = item.posttime
        row['weibourl'] = item.weibourl
        row['userurl'] = item.userurl
        row['repost'] = item.repost
        row['stype'] = item.stype
        weibo.append(row)    
    return weibo

def getPoint(opinionTopic):#提取某个观点的基本信息
    items = db.session.query(Opinion).filter(Opinion.opinionTopic==opinionTopic).all()
    point = dict()
    for item in items:
        point['start'] = item.start
        point['end'] = item.end
        point['count'] = item.count
        point['opinionWord'] = item.opinionWord
        point['positive'] = item.positive
        point['nagetive'] = item.nagetive

    return point

def getHot(opinionTopic):#提取某个观点的热度
    items = db.session.query(OpinionHot).filter(OpinionHot.opinionTopic==opinionTopic).all()
    hot = []
    for item in items:        
        row = dict()
        row['time'] = item.ts
        row['count'] = count
        hot.append(row)

    return hot

        
