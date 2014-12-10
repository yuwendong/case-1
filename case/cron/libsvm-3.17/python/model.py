# -*- coding: utf-8 -*-

from extensions import db

__all__ = ['Topics', 'OpinionTestRatio','OpinionTestTime',\
           'OpinionTestKeywords', 'OpinionTestWeibos', 'IndexTopic', 'OpinionWeibosNew']

class Topics(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    start_ts = db.Column(db.BigInteger(20, unsigned=True))
    end_ts = db.Column(db.BigInteger(20, unsigned=True))

    def __init__(self, topic, start_ts, end_ts):
        self.topic = topic
        self.start_ts = start_ts
        self.end_ts = end_ts
#实际上这一部分是需要重新修改的，但是在此次测试中用不到，就先不动。

class IndexTopic(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    topic = db.Column(db.Text)
    count = db.Column(db.Integer) # 微博数
    user_count = db.Column(db.Integer) # 用户数
    begin = db.Column(db.BigInteger(10,unsigned = True)) # 起始时间
    end = db.Column(db.BigInteger(10,unsigned = True)) # 终止时间
    area = db.Column(db.Text) # 地理区域
    key_words = db.Column(db.Text) # 关键词
    opinion = db.Column(db.Text) # 代表文本
    media_opinion = db.Column(db.Text) # 媒体观点

    def __init__(self, topic, count, user_count, begin, end, area, key_words, opinion, media_opinion):
        self.topic = topic
        self.count = count
        self.user_count = user_count
        self.begin = begin
        self.end = end
        self.area = area
        self.key_words = key_words
        self.opinion = opinion
        self.media_opinion = media_opinion

# opinion module used in test
class OpinionTestTime(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    child_topic = db.Column(db.Text)
    start_ts = db.Column(db.BigInteger(20, unsigned=True))
    end_ts = db.Column(db.BigInteger(20, unsigned=True))

    def __init__(self, topic, child_topic, start_ts, end_ts):
        self.topic = topic
        self.child_topic = child_topic
        self.start_ts = start_ts
        self.end_ts = end_ts

class OpinionTestRatio(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    #ts = db.clumns(db.BigInteger(10),unsigned=True)
    child_topic = db.Column(db.String(20))
    ratio = db.Column(db.Float)

    def __init__(self, topic, child_topic, ratio):
        self.topc = topic
        self.child_topic = child_topic
        self.ratio = ratio

class OpinionTestKeywords(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    child_topic = db.Column(db.String(20))
    keywords = db.Column(db.Text)

    def __init__(self, topic, child_topic, keywords):
        self.topic = topic
        self.child_topic = child_topic
        self.keywords = keywords

class OpinionTestWeibos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    child_topic = db.Column(db.String(20))
    weibos = db.Column(db.Text)

    def __init__(self, topic, child_topic, weibos):
        self.topic = topic
        self.child_topic = child_topic
        self.weibos = weibos

class OpinionWeibosNew(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    child_topic = db.Column(db.Text)
    weight = db.Column(db.Float)
    mid = db.Column(db.String(20))
    uid = db.Column(db.String(20))
    weibos = db.Column(db.Text)
    time = db.Column(db.String(20))    
    r_count = db.Column(db.Integer)
    c_count = db.Column(db.Integer)
    repeat = db.Column(db.Integer)

    def __init__(self, topic, child_topic, weight, mid, uid, weibos, time, r_count, c_count, repeat):
        self.topic = topic
        self.child_topic = child_topic
        self.weight = weight
        self.mid = mid
        self.uid = uid
        self.weibos = weibos
        self.time = time        
        self.r_count = r_count
        self.c_count = c_count
        self.repeat = repeat

# Quota_system Module
class QuotaAttention(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    start_ts = db.Column(db.BigInteger(10, unsigned=True))
    end_ts = db.Column(db.BigInteger(10, unsigned=True))
    domain = db.Column(db.String(20))
    attention = db.Column(db.Float)

    def __init__(self, topic, start_ts, end_ts, domain, attention):
        self.topic = topic
        self.start_ts = start_ts
        self.end_ta = end_ts
        self.domain = domain
        self.attention = attention

class QuotaPenetration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    start_ts = db.Column(db.BigInteger(10, unsigned=True))
    end_ts = db.Column(db.BigInteger(10, unsigned=True))
    domain = db.Column(db.String(20))
    penetration = db.Column(db.Float)

    def __init__(self, topic, start_ts, end_ts, domain, penetration):
        self.topic = topic
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.domain = domain
        self.penetration = penetration

class QuotaQuickness(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    start_ts = db.Column(db.BigInteger(10, unsigned=True))
    end_ts = db.Column(db.BigInteger(10, unsigned=True))
    domain = db.Column(db.String(20))
    quickness = db.Column(db.Float)

    def __init__(self, topic, start_ts, end_ts, domain, quickness):
        self.topic = topic
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.domain = domain
        self.quickness = quickness

class QuotaSentiment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    start_ts = db.Column(db.BigInteger(10, unsigned=True))
    end_ts = db.Column(db.BigInteger(10, unsigned=True))
    sentiment = db.Column(db.Integer(1, unsigned=True))
    ratio = db.Column(db.Float)

    def __init__(self, topic, start_ts, end_ts, sentiment, ratio):
        self.topic = topic
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.sentiment = sentiment
        self.ratio = ratio

class QuotaDuration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    start_ts = db.Column(db.BigInteger(10, unsigned=True))
    end_ts = db.Column(db.BigInteger(10, unsigned=True))
    duration = db.Column(db.Float)

    def __init__(self, topic, start_ts, end_ts, duration):
        self.topic = topic
        self. start_ts = start_ts
        self.end_ts = end_ts
        self.duration = duration

class QuotaSensitivity(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    start_ts = db.Column(db.BigInteger(10, unsigned=True))
    end_ts = db.Column(db.BigInteger(10, unsigned=True))
    classfication = db.Column(db.Integer(1, unsigned=True)) # ['category':1, 'word':2, 'place':3]
    score = db.Column(db.Float) # 1<=score<=5

    def __init__(self, topic, start_ts, end_ts, classfication, score):
        self.topic = topic
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.classfication = classfication
        self.score = score

class QuotaImportance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    start_ts = db.Column(db.BigInteger(10, unsigned=True))
    end_ts = db.Column(db.BigInteger(10, unsigned=True))
    score = db.Column(db.Float)

    def __init__(self, topic, start_ts, end_ts, score):
        self.topic = topic
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.score = score # 0<=score<1



