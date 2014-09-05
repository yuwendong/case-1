# -*- coding: utf-8 -*-
import json
import time
from config import db
from model import TopicStatus, Topics, QuotaAttention, QuotaMediaImportance, QuotaGeoPenetration,\
                  QuotaQuickness, QuotaSentiment, QuotaDuration, QuotaSensitivity, QuotaImportance

def save_attention_quota(topic, start_ts, end_ts, domain, attention):
    # being used to test, it's should be modified
    item_topic = Topics(topic, start_ts, end_ts)
    item_topic_exist = db.session.query(Topics).filter(Topics.topic==topic, \
                                                       Topics.start_ts==start_ts, \
                                                       Topics.end_ts==end_ts).first()
    if item_topic_exist:
        db.session.delete(item_topic_exist)
    db.session.add(item_topic)

    db.session.commit()
    
    
    item = QuotaAttention(topic, start_ts, end_ts, domain, attention)
    item_exist = db.session.query(QuotaAttention).filter(QuotaAttention.topic==topic, \
                                                         QuotaAttention.start_ts==start_ts, \
                                                         QuotaAttention.end_ts==end_ts, \
                                                         QuotaAttention.domain==domain).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

# save_penetration_quota弃用
# 分为两个:save_meidia_importance_quota, save_geo_pentration

def save_media_importance_quota(topic, start_ts, end_ts, media_importance): # 重要媒体参与度
    item = QuotaMediaImportance(topic, start_ts, end_ts, media_importance)
    item_exist = db.session.query(QuotaMediaImportance).filter(QuotaMediaImportance.topic==topic ,\
                                                               QuotaMediaImportance.start_ts==start_ts ,\
                                                               QuotaMediaImportance.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

def save_geo_penetration(topic, start_ts, end_ts, geo_penetration): # 地域渗透度
    item = QuotaGeoPenetration(topic, start_ts, end_ts, geo_penetration)
    item_exist = db.session.query(QuotaGeoPenetration).filter(QuotaGeoPenetration.topic==topic ,\
                                                              QuotaGeoPenetration.start_ts==start_ts ,\
                                                              QuotaGeoPenetration.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()
   
    
def save_quickness_quota(topic, start_ts, end_ts, domain, quickness):
    item = QuotaQuickness(topic, start_ts, end_ts, domain, quickness)
    print 'topic:', topic
    item_exist = db.session.query(QuotaQuickness).filter(QuotaQuickness.topic==topic, \
                                                   QuotaQuickness.start_ts==start_ts, \
                                                   QuotaQuickness.end_ts==end_ts, \
                                                   QuotaQuickness.domain==domain).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()


def save_sentiment_quota(topic, start_ts, end_ts, emotion_ratio_dict): 
    item = QuotaSentiment(topic, start_ts, end_ts, json.dumps(emotion_ratio_dict))
    item_exist = db.session.query(QuotaSentiment).filter(QuotaSentiment.topic==topic, \
                                                   QuotaSentiment.start_ts==start_ts, \
                                                   QuotaSentiment.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

def save_duration_quota(topic, start_ts, end_ts, duration):
    item = QuotaDuration(topic, start_ts, end_ts, duration)
    item_exist = db.session.query(QuotaDuration).filter(QuotaDuration.topic==topic, \
                                                        QuotaDuration.start_ts==start_ts, \
                                                        QuotaDuration.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

def save_sensitivity_quota(topic, start_ts, end_ts, classfication, score):
    item = QuotaSensitivity(topic, start_ts, end_ts, classfication, score)
    item_exist = db.session.query(QuotaSensitivity).filter(QuotaSensitivity.topic==topic, \
                                                           QuotaSensitivity.start_ts==start_ts, \
                                                           QuotaSensitivity.end_ts==end_ts, \
                                                           QuotaSensitivity.classfication==classfication).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

def save_importance_quota(topic, start_ts, end_ts, score):
    item = QuotaImportance(topic, start_ts, end_ts, score)
    item_exist = db.session.query(QuotaImportance).filter(QuotaImportance.topic==topic, \
                                                          QuotaImportance.start_ts==start_ts, \
                                                          QuotaImportance.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

