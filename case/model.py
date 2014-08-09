# -*- coding: utf-8 -*-

from extensions import db

__all__ = ['Topics', 'SentimentKeywords', 'SentimentWeibos', 'SentimentPoint', 'SentimentCount', 'SentimentCountRatio',\
          'IndexTopic', 'OpinionTopic', 'OpinionWeibos', 'Opinion', 'OpinionHot', 'CityTopicCount', 'PropagateCount', 'AttentionCount', 'QuicknessCount']


class Topics(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(20))
    topic = db.Column(db.Text)
    iscustom = db.Column(db.Boolean)
    expire_date = db.Column(db.BigInteger(10, unsigned=True))

    def __init__(self, user, topic, iscustom, expire_date):
        self.user = user
        self.topic = topic
        self.iscustom = iscustom
        self.expire_date = expire_date  #实际上这一部分是需要重新修改的，但是在此次测试中用不到，就先不动。
#sentiment部分
class SentimentKeywords(db.Model):#情绪关键词---已改
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query = db.Column(db.String(20))
    end = db.Column(db.BigInteger(10, unsigned=True))
    range = db.Column(db.BigInteger(10, unsigned=True))
    limit = db.Column(db.BigInteger(10, unsigned=True))
    sentiment = db.Column(db.Integer(1, unsigned=True))
    kcount = db.Column(db.Text)

    def __init__(self, query, range, limit, end, sentiment, kcount):
        self.query = query 
        self.range = range
        self.limit = limit
        self.end = end
        self.sentiment = sentiment
        self.kcount = kcount

class SentimentWeibos(db.Model):#情绪微博--已改
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query = db.Column(db.String(20))
    end = db.Column(db.BigInteger(10, unsigned=True))
    range = db.Column(db.BigInteger(10, unsigned=True))
    limit = db.Column(db.BigInteger(10, unsigned=True))
    sentiment = db.Column(db.Integer(1, unsigned=True))
    weibos = db.Column(db.Text)

    def __init__(self, query, range, limit, end, sentiment, weibos):
        self.query = query 
        self.range = range
        self.limit = limit
        self.end = end
        self.sentiment = sentiment
        self.weibos = weibos

class SentimentPoint(db.Model):#情绪拐点
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(20))#话题名
    stype = db.Column(db.String(20))#拐点情绪类型标签（'happy','angry','sad'）
    ts = db.Column(db.BigInteger(20, unsigned=True))#拐点时间

    def __init__(self, topic, stype, ts):
        self.topic = topic
        self.stype = stype
        self.ts = ts

class SentimentCount(db.Model):#情绪绝对数量曲线--已改
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query = db.Column(db.String(20))
    end = db.Column(db.BigInteger(10, unsigned=True))
    range = db.Column(db.BigInteger(10, unsigned=True))
    sentiment = db.Column(db.Integer(1, unsigned=True))
    count = db.Column(db.BigInteger(20, unsigned=True))

    def __init__(self, query, range, end, sentiment, count):
        self.query = query 
        self.range = range
        self.end = end
        self.sentiment = sentiment
        self.count = count

class SentimentCountRatio(db.Model):#情绪相对比例曲线--已改
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(20))#话题名
    end = db.Column(db.BigInteger(20, unsigned=True))#时间
    range = db.Column(db.BigInteger(10, unsigned=True))
    count = db.Column(db.BigInteger(20, unsigned=True))
    allcount = db.Column(db.BigInteger(20, unsigned=True))
    sentiment = db.Column(db.Integer(1, unsigned=True))#情绪类型（'happy','angry','sad'）

    def __init__(self, query, end, range, sentiment, count, allcount):
        self.query = query
        self.end = end
        self.ts = ts
        self.count = count
        self.allcount = allcount
        self.sentiment = sentiment

# Index 模块

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

    def __init__(self, topic, count, user_count, begin, end, area, key_words, opinion):
        self.topic = topic
        self.count = count
        self.user_count = user_count
        self.begin = begin
        self.end = end
        self.area = area
        self.key_words = key_words
        self.opinion = opinion

#city模块
class CityTopicCount(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    end = db.Column(db.BigInteger(10, unsigned=True))
    range = db.Column(db.BigInteger(10, unsigned=True))
    mtype = db.Column(db.Integer(1, unsigned=True))  #message_type:原创-1、转发-2、评论-3
    ccount = db.Column(db.Text)                      #city_count:{city:count}

    def __init__(self, topic, range, end, mtype, ccount):
        self.topic = query 
        self.range = range
        self.end = end
        self.mtype = mtype
        self.ccount = ccount

#时间分析模块
class PropagateCount(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    end = db.Column(db.BigInteger(10, unsigned=True))
    range = db.Column(db.BigInteger(10, unsigned=True))
    mtype = db.Column(db.Integer(1, unsigned=True))   
    dcount = db.Column(db.Text) # dcount={domain:count}领域对应的count                      

    def __init__(self, topic, range, end, mtype, dcount):
        self.topic = topic 
        self.range = range
        self.end = end
        self.mtype = mtype
        self.dcount = dcount

class AttentionCount(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    end = db.Column(db.BigInteger(10, unsigned=True))
    range = db.Column(db.BigInteger(10, unsigned=True))
    mtype = db.Column(db.Integer(1, unsigned=True))   
    domain = db.Column(db.String(20))
    covernum = db.Column(db.BigInteger(20, unsigned=True))
    allnum = db.Column(db.BigInteger(20, unsigned=True))

    def __init__(self, topic, range, end, mtype, domain, covernum, allnum):
        self.topic = topic
        self.range = range
        self.end = end
        self.mtype = mtype
        self.domain = domain
        self.covernum = covernum
        self.allnum = allnum

class QuicknessCount(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    end = db.Column(db.BigInteger(10, unsigned=True))
    range = db.Column(db.BigInteger(10, unsigned=True))
    mtype = db.Column(db.Integer(1, unsigned=True))   
    domain = db.Column(db.String(20))
    topnum = db.Column(db.BigInteger(20, unsigned=True))
    allnum = db.Column(db.BigInteger(20, unsigned=True))

    def __init__(self, topic, range, end, mtype, domain, topnum, allnum):
        self.topic = topic
        self.range = range
        self.end = end
        self.mtype = mtype
        self.domain = domain
        self.topnum = topnum
        self.allnum = allnum
    
    
class TopicStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module = db.Column(db.String(10))# 显示是哪个模块---moodlens/evolution/propagate/identify
    status = db.Column(db.Integer)# 1: completed 0: computing, -1:not compute, -2:delete
    topic = db.Column(db.Text)
    start = db.Column(db.BigInteger(10, unsigned=True))#起始时间
    end = db.Column(db.BigInteger(10, unsigned=True))#终止时间
    db_date = db.Column(db.BigInteger(10, unsigned=True))#入库时间❯

    def __init__(self, module, status, topic, start, end, db_date):
        self.module = module
        self.status = status
        self.topic = topic
        self.start = start
        self.end = end
        self.db_date = db_date

#网络模块--存放pagerank的计算结果
class TopicIdentification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(20))
    rank = db.Column(db.Integer)
    userId = db.Column(db.BigInteger(11, unsigned=True))
    identifyDate = db.Column(db.Date)
    identifyWindow = db.Column(db.Integer, default=1)
    identifyMethod = db.Column(db.String(20), default='pagerank')

    def __init__(self, topic, rank, userId, identifyDate, identifyWindow, identifyMethod):
        self.topic = topic
        self.rank = rank
        self.userId = userId
        self.identifyDate = identifyDate
        self.identifyWindow = identifyWindow
        self.identifyMethod = identifyMethod


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

