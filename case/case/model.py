# -*- coding: utf-8 -*-

from extensions import db

__all__ = ['SentimentKeywords', 'SentimentWeibos', 'SentimentPoint', 'SentimentCount', 'SentimentCountRatio',\
           'OpinionTopic', 'OpinionWeibos', 'Opinion', 'OpinionHot']

#以下是情绪模块（岳耀猛看）
class SentimentKeywords(db.Model):#情绪关键词
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(20))#话题名
    keyword = db.Column(db.String(20))#关键词
    count = db.Column(db.Integer)#关键词权重（出现次数）
    stype = db.Column(db.String(20))#关键词的情绪类型（'happy','angry','sad'）
    ts = db.Column(db.BigInteger(20, unsigned=True))#关键词对应的时间（点击拐点时可根据拐点时间来匹配该项，提出关键词）

    def __init__(self, topic, keyword, count, stype, ts):
        self.topic = topic
        self.keyword = keyword
        self.count = count
        self.stype = stype
        self.ts = ts

class SentimentWeibos(db.Model):#情绪微博
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(20))#话题名
    mid = db.Column(db.String(20))#微博id
    weibos = db.Column(db.Text)#微博文本
    user = db.Column(db.String(20))#用户昵称
    userid = db.Column(db.String(20))#用户id
    posttime = db.Column(db.String(20))#发布时间（点击拐点时可根据拐点时间来匹配该项，提出微博）
    weibourl = db.Column(db.String(20))#微博url（目前没啥用，都是‘#’）
    userurl = db.Column(db.String(20))#用户url（目前没啥用，都是‘#’）
    repost = db.Column(db.Integer)#转发数
    stype = db.Column(db.String(20))#微博情绪类型（'happy','angry','sad'）

    def __init__(self, topic, mid, weibos, user, userid, posttime, weibourl, userurl, repost, stype):
        self.topic = topic
        self.mid = mid
        self.weibos = weibos
        self.user = user
        self.userid = userid
        self.posttime = posttime
        self.weibourl = weibourl
        self.userurl = userurl
        self.repost = repost
        self.stype = stype

class SentimentPoint(db.Model):#情绪拐点
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(20))#话题名
    stype = db.Column(db.String(20))#拐点情绪类型标签（'happy','angry','sad'）
    ts = db.Column(db.BigInteger(20, unsigned=True))#拐点时间

    def __init__(self, topic, stype, ts):
        self.topic = topic
        self.stype = stype
        self.ts = ts

class SentimentCount(db.Model):#情绪绝对数量曲线
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(20))#话题名
    ts = db.Column(db.BigInteger(20, unsigned=True))#时间
    count = db.Column(db.Integer)#绝对数量
    stype = db.Column(db.String(20))#情绪类型（'happy','angry','sad'）

    def __init__(self, topic, ts, count, stype):
        self.topic = topic
        self.ts = ts
        self.count = count
        self.stype = stype

class SentimentCountRatio(db.Model):#情绪相对比例曲线
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(20))#话题名
    ts = db.Column(db.BigInteger(20, unsigned=True))#时间
    ratio = db.Column(db.Float)#相对比例
    stype = db.Column(db.String(20))#情绪类型（'happy','angry','sad'）

    def __init__(self, topic, ts, ratio, stype):
        self.topic = topic
        self.ts = ts
        self.ratio = ratio
        self.stype = stype

#以下是语义模块（李文文看）
class OpinionTopic(db.Model):#话题、观点对应表
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(20))#话题
    opinion = db.Column(db.String(20))#观点

    def __init__(self, topic, opinion):
        self.topic = topic
        self.opinion = opinion

class OpinionWeibos(db.Model):#观点微博
    id = db.Column(db.Integer, primary_key=True)
    opinionTopic = db.Column(db.Integer)#话题、观点对应表中id字段
    mid = db.Column(db.String(20))#微博id
    weibos = db.Column(db.Text)#微博文本
    user = db.Column(db.String(20))#用户昵称
    userid = db.Column(db.String(20))#用户id
    posttime = db.Column(db.String(20))#发布时间
    weibourl = db.Column(db.String(20))#微博url（目前没啥用，都是‘#’）
    userurl = db.Column(db.String(20))#用户url（目前没啥用，都是‘#’）
    repost = db.Column(db.Integer)#转发数
    stype = db.Column(db.String(20))#情绪类型（'happy','angry','sad'）

    def __init__(self, opinionTopic, mid, weibos, user, userid, posttime, weibourl, userurl, repost, stype):
        self.opinionTopic = opinionTopic
        self.mid = mid
        self.weibos = weibos
        self.user = user
        self.userid = userid
        self.posttime = posttime
        self.weibourl = weibourl
        self.userurl = userurl
        self.repost = repost
        self.stype = stype

class Opinion(db.Model):#观点
    id = db.Column(db.Integer, primary_key=True)
    opinionTopic = db.Column(db.Integer)#话题、观点对应表中id字段
    start = db.Column(db.BigInteger(20, unsigned=True))#开始时间
    end = db.Column(db.BigInteger(20, unsigned=True))#结束时间
    count = db.Column(db.Integer)#所占微博数量
    opinionWord = db.Column(db.String(20))#关键词
    positive = db.Column(db.Float)#正极性情绪比例
    nagetive = db.Column(db.Float)#负极性情绪比例

    def __init__(self, opinionTopic, start, end, count, opinionWord, positive, nagetive):
        self.opinionTopic = opinionTopic
        self.start = start
        self.end = end
        self.count = count
        self.opinionWord = opinionWord
        self.positive = positive
        self.nagetive = nagetive

class OpinionHot(db.Model):#观点热度值
    id = db.Column(db.Integer, primary_key=True)
    opinionTopic = db.Column(db.Integer)#话题、观点对应表中id字段
    ts = db.Column(db.BigInteger(20, unsigned=True))#时间
    count = db.Column(db.Integer)#热度

    def __init__(self, opinionTopic, ts, count):
        self.opinionTopic = opinionTopic
        self.ts = ts
        self.count = count
