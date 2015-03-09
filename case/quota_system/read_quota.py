# -*- coding: utf-8 -*-
import json
from case.extensions import db
from case.model import  Topics, QuotaIndex, QuotaFSensitivity, QuotaFSentiment, QuotaFTransmission ,\
                        QuotaFInvolved, QuotaSensitivity, QuotaSentiment, QuotaDuration, QuotaCoverage ,\
                        QuotaQuickness, QuotaMediaImportance, QuotaPersonSensitivity

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
    items = db.session.query(Topics).filter(Topics.topic==topic).all()
    if not items:
        return None
    all_end = 0

    for item in items:
        start_ts = item.start_ts
        end_ts = item.end_ts
        if all_end < end_ts:
            all_end = end_ts

    compute_day = (all_end - start_ts) / Day + 1
    index_evolution = {'end_ts':[], 'index':[]}
    f_quota_evolution = {'end_ts':[], 'f_sensitivity':[], 'f_sentiment':[], 'f_transmission':[], 'f_involved':[]}
    for i in range(compute_day-1):
        end_ts = start_ts + (i+1) * Day
        f_sensitivity = ReadFSensitivity(topic, start_ts, end_ts)
        f_sentiment = ReadFSentiment(topic, start_ts, end_ts)
        f_transmission = ReadFTransmission(topic, start_ts, end_ts)
        f_involved = ReadFInvolved(topic, start_ts, end_ts)
        index = ReadIndex(topic, start_ts, end_ts)
        index_evolution['end_ts'].append(end_ts) # index_evolution={'end_ts':[], 'index':[],...}
        index_evolution['index'].append(index)
        f_quota_evolution['end_ts'].append(end_ts)
        f_quota_evolution['f_sensitivity'].append(f_sensitivity)
        f_quota_evolution['f_sentiment'].append(f_sentiment)
        f_quota_evolution['f_transmission'].append(f_transmission)
        f_quota_evolution['f_involved'].append(f_involved)  # f_quota_evolution = {end_ts:[], quota1:[],.....}

    last_index = index  # float
    system_dict = {} 
    class_sensitivity, word_sensitivity = ReadQuotaSensitivity(topic, start_ts ,end_ts)
    sentiment_sad ,sentiment_angry = ReadQuotaSentiment(topic, start_ts ,end_ts)
    duration = ReadQuotaDuration(topic, start_ts ,end_ts)
    quickness = ReadQuotaQuickness(topic, start_ts, end_ts)
    coverage = ReadQuotaCoverage(topic, start_ts, end_ts)
    person_involved = ReadQuotaPerson(topic, start_ts, end_ts)
    media_involved = ReadQuotaMedia(topic, start_ts, end_ts)

    system_dict['index'] = ['low', last_index] # system_dict = {quota1:[weight, value],...}
    system_dict['f_sensitivity'] = [0.25, f_sensitivity]
    system_dict['f_sentiment'] = [0.25, f_sentiment]
    system_dict['f_transmission'] = [0.25, f_transmission]
    system_dict['f_invovled'] = [0.25, f_transmission]
    system_dict['class_sensitivity'] = [0.5, 0.2]
    system_dict['word_sensitivity'] = [0.5, 0.4]
    system_dict['sentiment_sad'] = [0.5, sentiment_sad]
    system_dict['sentiment_angry'] = [0.5, sentiment_angry]
    system_dict['duration'] = [(1.0 / 3.0) , duration]
    system_dict['quickness'] = [(1.0 / 3.0), quickness]
    system_dict['coverage'] = [(1.0 / 3.0), coverage]
    system_dict['person_involved'] = [0.5, person_involved]
    system_dict['media_involved'] = [0.5, media_involved]

    quota_system_dict= {'last_index': last_index,\
                        'now_system': system_dict,\
                        'index_evolution': index_evolution ,\
                        'f_quota_evolution': f_quota_evolution}

    return quota_system_dict

def ReadIndex(topic, start_ts, end_ts):
    item = db.session.query(QuotaIndex).filter(QuotaIndex.topic==topic ,\
                                               QuotaIndex.start_ts==start_ts ,\
                                               QuotaIndex.end_ts==end_ts).first()
    if item:
        index = item.index
    else:
        index = 'None'

    return index

def ReadFSensitivity(topic, start_ts, end_ts):
    item = db.session.query(QuotaFSensitivity).filter(QuotaFSensitivity.topic==topic ,\
                                                      QuotaFSensitivity.start_ts==start_ts ,\
                                                      QuotaFSensitivity.end_ts==end_ts).first()
    if item:
        f_sensitivity = item.f_sensitivity
    else:
        f_sensitivity = 'None'

    return f_sensitivity

def ReadFSentiment(topic, start_ts, end_ts):
    item = db.session.query(QuotaFSentiment).filter(QuotaFSentiment.topic==topic ,\
                                                    QuotaFSentiment.start_ts==start_ts ,\
                                                    QuotaFSentiment.end_ts==end_ts).first()
    if item:
        f_sentiment = item.f_sentiment
    else:
        f_sentiment = 'None'

    return f_sentiment

def ReadFTransmission(topic, start_ts, end_ts):
    item = db.session.query(QuotaFTransmission).filter(QuotaFTransmission.topic==topic ,\
                                                       QuotaFTransmission.start_ts==start_ts ,\
                                                       QuotaFTransmission.end_ts==end_ts).first()
    if item:
        f_transmission = item.f_transmission
    else:
        f_transmission = 'None'

    return f_transmission

def ReadFInvolved(topic, start_ts, end_ts):
    item = db.session.query(QuotaFInvolved).filter(QuotaFInvolved.topic==topic ,\
                                                   QuotaFInvolved.start_ts==start_ts ,\
                                                   QuotaFInvolved.end_ts==end_ts).first()
    if item:
        f_involved = item.f_involved
    else:
        f_involved = 'None'

    return f_involved

def ReadQuotaSensitivity(topic, start_ts, end_ts):
    item_class = db.session.query(QuotaSensitivity).filter(QuotaSensitivity.topic==topic, \
                                                           QuotaSensitivity.start_ts==start_ts, \
                                                           QuotaSensitivity.end_ts==end_ts ,\
                                                           QuotaSensitivity.classfication==1).first()
    item_word = db.session.query(QuotaSensitivity).filter(QuotaSensitivity.topic==topic, \
                                                          QuotaSensitivity.start_ts==start_ts, \
                                                          QuotaSensitivity.end_ts==end_ts ,\
                                                          QuotaSensitivity.classfication==2).first()
    if item_class:
        class_sensitivity = item_class.score
    else:
        class_sensitivity = 'None'
    if item_word:
        word_sensitivity = item_word.score
    else:
        word_sensitivity = 'None'
    
    return class_sensitivity, word_sensitivity


def ReadQuotaCoverage(topic, start_ts, end_ts):
    item = db.session.query(QuotaCoverage).filter(QuotaCoverage.topic==topic, \
                                                  QuotaCoverage.start_ts==start_ts, \
                                                  QuotaCoverage.end_ts==end_ts).first()
    if item:
        coverage = item.coverage
    else:
        coverage = 'None'
    
    return coverage

def ReadQuotaMedia(topic, start_ts, end_ts):
    item = db.session.query(QuotaMediaImportance).filter(QuotaMediaImportance.topic==topic ,\
                                                         QuotaMediaImportance.start_ts==start_ts ,\
                                                         QuotaMediaImportance.end_ts==end_ts).first()
    if item:
        media_involved = item.media_importance
    else:
        media_involves = 'None'

    return media_involved



def ReadQuotaQuickness(topic, start_ts, end_ts):
    item = db.session.query(QuotaQuickness).filter(QuotaQuickness.topic==topic, \
                                                   QuotaQuickness.start_ts==start_ts, \
                                                   QuotaQuickness.end_ts==end_ts ,\
                                                   QuotaQuickness.domain=='all').first()
    if item:
        quickness = item.quickness
    else:
        quickness = 'None'

    return quickness

def ReadQuotaDuration(topic, start_ts, end_ts):
    item = db.session.query(QuotaDuration).filter(QuotaDuration.topic==topic, \
                                                  QuotaDuration.start_ts==start_ts, \
                                                  QuotaDuration.end_ts==end_ts).first()
    if item:
        duration = item.duration
    else:
        duration = 'None'

    return duration

def ReadQuotaSentiment(topic, start_ts, end_ts):
    item = db.session.query(QuotaSentiment).filter(QuotaSentiment.topic==topic, \
                                                   QuotaSentiment.start_ts==start_ts, \
                                                   QuotaSentiment.end_ts==end_ts).first()
    if item:
        sentiment_dict = json.loads(item.sratio)
        sentiment_sad = sentiment_dict['sad']
        sentiment_angry = sentiment_dict['angry']
    else:
        sentiment_sad = 'None'
        sentiment_angry = 'None'

    return sentiment_sad, sentiment_angry

def ReadQuotaPerson(topic, start_ts, end_ts):
    item = db.session.query(QuotaPersonSensitivity).filter(QuotaPersonSensitivity.topic==topic, \
                                                           QuotaPersonSensitivity.start_ts==start_ts, \
                                                           QuotaPersonSensitivity.end_ts==end_ts).first()
    if item:
        person_involved = item.pr
    else:
        person_involved = 'None'

    return person_involved


