# -*- coding: utf-8 -*-
import json
from case.extensions import db
from case.model import  Topics, QuotaAttention, QuotaGeoPenetration, QuotaMediaImportance, \
                        QuotaQuickness, QuotaImportance ,QuotaWeight ,GeoWeight ,\
                        QuotaDuration, QuotaSentiment, QuotaSensitivity # 需要查询的表

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
province_dict = {'34':'安徽','11':'北京', '50':'重庆', '35':'福建', '62':'甘肃', '44':'广东', '45':'广西',\
                 '52':'贵州', '46':'海南', '13':'河北', '23':'黑龙江', '41':'河南', '42':'湖北', '43':'湖南',\
                 '15':'内蒙古', '32':'江苏', '36':'江西', '22':'吉林', '21':'辽宁', '64':'宁夏', '63':'青海',\
                 '14':'山西', '37':'山东', '31':'上海', '51':'四川', '12':'天津', '54':'西藏', '65':'新疆',\
                 '53':'云南', '33':'浙江', '61':'陕西', '71':'台湾', '81':'香港', '82':'澳门',\
                 '400':'海外', '100':'其他'}

def ReadTopic(topic):
    item = db.session.query(Topics).filter(Topics.topic==topic).first()
    if not item:
        return None
    else:
        start_ts = item.start_ts
        end_ts = item.end_ts
        #print 'item:',item.topic, item.start_ts, item.end_ts
        attention_dict = ReadAttention(topic, start_ts, end_ts)
        geo_penetration_dict = ReadGeoPenetration(topic, start_ts, end_ts)
        media_importance_dict = ReadMediaImportance(topic, start_ts, end_ts)
        quickness_dict = ReadQuickness(topic, start_ts, end_ts)
        duration_dict = ReadDuration(topic, start_ts, end_ts)
        sensitivity_dict = ReadSensitivity(topic, start_ts, end_ts)
        sentiment_dict = ReadSentiment(topic, start_ts, end_ts)
        importance_dict = ReadImportance(topic, start_ts, end_ts)
        quota_weight_dict = ReadQuotaWeight()
        # geo_weight_dict = ReadGeoWeight()
        quota_system_dict= {'attention': attention_dict, \
                            'geo_penetration': geo_penetration_dict, \
                            'media_importance': media_importance_dict ,\
                            'quickness': quickness_dict, \
                            'duration': duration_dict, \
                            'sensitivity': sensitivity_dict, \
                            'sentiment': sentiment_dict, \
                            'importance': importance_dict ,\
                            'quota_weight': quota_weight_dict ,\
                            }
        return quota_system_dict

def ReadGeoWeight():
    item = db.session.query(GeoWeight).first()
    weight_dict = json.loads(item.weight_dict)
    print 'geo_weight_dict:', weight_dict

    return weight_dict

def ReadQuotaWeight():
    item = db.session.query(QuotaWeight).first()
    weight_dict = json.loads(item.weight_dict)
    print 'quota_weight_dict:', weight_dict

    return weight_dict

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

def ReadGeoPenetration(topic, start_ts, end_ts):
    item = db.session.query(QuotaGeoPenetration).filter(QuotaGeoPenetration.topic==topic, \
                                                      QuotaGeoPenetration.start_ts==start_ts, \
                                                      QuotaGeoPenetration.end_ts==end_ts).first()
    pcount_dict = json.loads(item.pcount)
    print 'pcount_dict:', pcount_dict

    weight_dict = ReadGeoWeight()
    geo_weight_dict = {}
    s = 0
    for province in province_dict:
        if pcount_dict[province] >= weight_dict[province]:
            geo_weight_dict[province] = 1
        else:
            geo_weight_dict[province] = 0
        s =s + geo_weight_dict[province]
    avg_s = float(s) / float(36)
    print 's:', s
    print 'avg_s:', avg_s

    return avg_s

def ReadMediaImportance(topic, start_ts, end_ts):
    item = db.session.query(QuotaMediaImportance).filter(QuotaMediaImportance.topic==topic ,\
                                                         QuotaMediaImportance.start_ts==start_ts ,\
                                                         QuotaMediaImportance.end_ts==end_ts).first()
    media_importance_dict = item.media_importance
    print 'media_importance:', media_importance_dict
    return media_importance_dict

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
    print 'sensitivity_dict:', sensitivity_dict
    return sensitivity_dict

def ReadSentiment(topic, start_ts, end_ts):
    item = db.session.query(QuotaSentiment).filter(QuotaSentiment.topic==topic, \
                                                  QuotaSentiment.start_ts==start_ts, \
                                                  QuotaSentiment.end_ts==end_ts).first()
    sentiment_dict = {}
    sentiment_dict = json.loads(item.sratio)
    print 'sentiment_dict:', sentiment_dict

    return sentiment_dict

def ReadImportance(topic, start_ts, end_ts):
    item = db.session.query(QuotaImportance).filter(QuotaImportance.topic==topic, \
                                                  QuotaImportance.start_ts==start_ts, \
                                                  QuotaImportance.end_ts==end_ts).first()
    importance_dict = {}
    importance_dict['score'] = item.score
    importance_dict['weight'] = item.weight
    print 'importance_dict:', importance_dict

    return importance_dict
    
        



