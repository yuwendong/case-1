# -*- coding: utf-8 -*-
from case.extensions import db
from case.model import  Topics, QuotaAttention, QuotaPenetration, QuotaQuickness, \
                        QuotaDuration, QuotaSentiment, QuotaSensitivity, \
                        QuotaImportance# 需要查询的表

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

TOP_KEYWORDS_LIMIT = 50
TOP_READ =10
TOP_WEIBOS_LIMIT = 50

domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']


def ReadTopic(topic):
    item = db.session.query(Topics).filter(Topics.topic==topic).first()
    if not item:
        return None
    else:
        start_ts = item.start_ts
        end_ts = item.end_ts
        #print 'item:',item.topic, item.start_ts, item.end_ts
        attention_dict = ReadAttention(topic, start_ts, end_ts)
        penetration_dict = ReadPenetration(topic, start_ts, end_ts)
        quickness_dict = ReadQuickness(topic, start_ts, end_ts)
        duration_dict = ReadDuration(topic, start_ts, end_ts)
        sensitivity_dict = ReadSensitivity(topic, start_ts, end_ts)
        sentiment_dict = ReadSentiment(topic, start_ts, end_ts)
        importance_dict = ReadImportance(topic, start_ts, end_ts)
        quota_system_dict= {'attention': attention_dict, \
                            'penetration': penetration_dict, \
                            'quickness': quickness_dict, \
                            'duration': duration_dict, \
                            'sensitivity': sensitivity_dict, \
                            'sentiment': sentiment_dict, \
                            'importance': importance_dict}
        return quota_system_dict

def ReadAttention(topic, start_ts, end_ts):
    items = db.session.query(QuotaAttention).filter(QuotaAttention.topic==topic, \
                                                    QuotaAttention.start_ts==start_ts, \
                                                    QuotaAttention.end_ts==end_ts).all()
    attention_dict = {}
    for item in items:
        domain = item.domain
        attention = item.attention
        attention_dict[domain] = attention
    print 'attention:', attention_dict
    return attention_dict

def ReadPenetration(topic, start_ts, end_ts):
    items = db.session.query(QuotaPenetration).filter(QuotaPenetration.topic==topic, \
                                                      QuotaPenetration.start_ts==start_ts, \
                                                      QuotaPenetration.end_ts==end_ts).all()
    penetration_dict = {}
    for item in items:
        domain = item.domain
        penetration = item.penetration
        penetration_dict[domain] = penetration
    print 'penetration:', penetration_dict
    return penetration_dict

def ReadQuickness(topic, start_ts, end_ts):
    items = db.session.query(QuotaQuickness).filter(QuotaQuickness.topic==topic, \
                                                    QuotaQuickness.start_ts==start_ts, \
                                                    QuotaQuickness.end_ts==end_ts).all()
    quickness_dict = {}
    for item in items:
        domain = item.domain
        quickness = item.quickness
        quickness_dict[domain] = quickness
    
    print 'quickness:', quickness_dict
    return quickness_dict

def ReadDuration(topic, start_ts, end_ts):
    item = db.session.query(QuotaDuration).filter(QuotaDuration.topic==topic, \
                                                 QuotaDuration.start_ts==start_ts, \
                                                 QuotaDuration.end_ts==end_ts).first()
    duration_dict = item.duration
    print 'duration:', duration_dict
    return duration_dict

def ReadSensitivity(topic, start_ts, end_ts):
    items = db.session.query(QuotaSensitivity).filter(QuotaSensitivity.topic==topic, \
                                                     QuotaSensitivity.start_ts==start_ts, \
                                                     QuotaSensitivity.end_ts==end_ts).all()
    sensitivity_dict = {}
    for item in items:
        classfication = item.classfication
        score = item.score
        sensitivity_dict[classfication] = score
        
    return sensitivity_dict

def ReadSentiment(topic, start_ts, end_ts):
    items = db.session.query(QuotaSentiment).filter(QuotaSentiment.topic==topic, \
                                                  QuotaSentiment.start_ts==start_ts, \
                                                  QuotaSentiment.end_ts==end_ts).all()
    sentiment_dict = {}
    for item in items:
        sentiment = item.sentiment
        ratio = item.ratio
        sentiment_dict[sentiment] = ratio

    return sentiment_dict

def ReadImportance(topic, start_ts, end_ts):
    item = db.session.query(QuotaImportance).filter(QuotaImportance.topic==topic, \
                                                  QuotaImportance.start_ts==start_ts, \
                                                  QuotaImportance.end_ts==end_ts).first()
    importance_dict = item.score
    return importance_dict
    
        

