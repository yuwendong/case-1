# -*- coding: utf-8 -*-
import json
import time
from config import db
from time_utils import datetime2ts, ts2HourlyTime
from model import TopicStatus, QuotaAttention, QuotaPenetration, QuotaQuickness, \
                  QuotaSentiment, QuotaDuration, QuotaSensitivity, QuotaImportance #, QuotaTotal
# QuotaTotal怎么计算未知，待定---注：该表未建



def save_attention_quota(topic, start_ts, end_ts, domain, attention):
    item = QuotaAttention(topic, start_ts, end_ts, domain, attention)
    item_exist = db.session.query(QuotaAttention).filter(QuotaAttention.topic==topic, \
                                                         QuotaAttention.start_ts==start_ts, \
                                                         QuotaAttention.end_ts==end_ts, \
                                                         QuotaAttention.domain==domain).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

def save_penetration_quota(topic, start_ts, end_ts, domain, penetration):
    item = QuotaPenetration(topic, start_ts, end_ts, domain, penetration)
    item_exist = db.session.query(QuotaPenetration).filter(QuotaPenetration.topic==topic, \
                                                           QuotaPenetration.start_ts==start_ts, \
                                                           QuotaPenetration.end_ts==end_ts, \
                                                           QuotaPenetration.domain==domain).first()
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


def save_sentiment_quota(topic, start_ts, end_ts, sentiment, ratio):
    item = QuotaSentiment(topic, start_ts, end_ts, sentiment, ratio)
    item_exist = db.session.query(QuotaSentiment).filter(QuotaSentiment.topic==topic, \
                                                   QuotaSentiment.start_ts==start_ts, \
                                                   QuotaSentiment.end_ts==end_ts, \
                                                   QuotaSentiment.sentiment==sentiment).first()
    if item_exist:
        db.session.add(item_exist)
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

'''
QuotaTotal未知，待定
def save_total_quota():
'''
