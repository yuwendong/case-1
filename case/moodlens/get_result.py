# -*- coding: utf-8 -*-

import case.model
from case.model import SentimentKeywords, SentimentWeibos , SentimentPoint, SentimentCount, SentimentCountRatio
from case.extensions import db

def getKeywords(topic, ts, module):
    if module == 'whole':#搜索全部的关键词
        items = db.session.query(SentimentKeywords).filter(SentimentKeywords.topic==topic).all()
        keyword = []
        for item in items:
            row = dict()
            row['word'] = item.keyword
            row['weight'] = item.count
            row['type'] = item.stype
            row['ts'] = item.ts
            keyword.append(row)
    elif module == 'happy':#搜索高兴对应时间点的关键词
        items = db.session.query(SentimentKeywords).filter((SentimentKeywords.topic==topic)&(SentimentKeywords.ts==ts)&(SentimentKeywords.stype==module)).all()
        keyword = []
        for item in items:
            row = dict()
            row['word'] = item.keyword
            row['weight'] = item.count
            row['type'] = item.stype
            row['ts'] = item.ts
            keyword.append(row)
    elif module == 'angry':#搜索愤怒对应时间点的关键词
        items = db.session.query(SentimentKeywords).filter((SentimentKeywords.topic==topic)&(SentimentKeywords.ts==ts)&(SentimentKeywords.stype==module)).all()
        keyword = []
        for item in items:
            row = dict()
            row['word'] = item.keyword
            row['weight'] = item.count
            row['type'] = item.stype
            row['ts'] = item.ts
            keyword.append(row)
    else:#搜索悲伤对应时间点的关键词
        items = db.session.query(SentimentKeywords).filter((SentimentKeywords.topic==topic)&(SentimentKeywords.ts==ts)&(SentimentKeywords.stype==module)).all()
        keyword = []
        for item in items:
            row = dict()
            row['word'] = item.keyword
            row['weight'] = item.count
            row['type'] = item.stype
            row['ts'] = item.ts
            keyword.append(row)

    return keyword

def getWeibo(topic, ts, module):
    if module == 'whole':#搜索全部的关键词
        items = db.session.query(SentimentWeibos).filter(SentimentWeibos.topic==topic).all()
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
    elif module == 'happy':#搜索高兴对应时间点的关键词
        items = db.session.query(SentimentWeibos).filter((SentimentWeibos.topic==topic)&(SentimentWeibos.posttime==ts)&(SentimentWeibos.stype==module)).all()
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
    elif module == 'angry':#搜索愤怒对应时间点的关键词
        items = db.session.query(SentimentWeibos).filter((SentimentWeibos.topic==topic)&(SentimentWeibos.posttime==ts)&(SentimentWeibos.stype==module)).all()
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
    else:#搜索悲伤对应时间点的关键词
        items = db.session.query(SentimentWeibos).filter((SentimentWeibos.topic==topic)&(SentimentWeibos.posttime==ts)&(SentimentWeibos.stype==module)).all()
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

def getPoint(topic, module):#提取某种情绪的拐点
    items = db.session.query(SentimentPoint).filter((SentimentPoint.topic==topic)&(SentimentPoint.stype==module)).all()
    point = []
    for item in items:
        point.append(item.ts)

    return point

def getCount(topic, ts):#提取三种情绪在某个时间点的绝对数量
    items = db.session.query(SentimentCount).filter((SentimentCount.topic==topic)&(SentimentCount.ts==ts)).all()
    row = dict()
    for item in items:        
        row[item.stype] = item.count

    return row

        
