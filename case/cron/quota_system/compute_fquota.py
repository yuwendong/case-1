# -*- coding: utf-8 -*-
import json
from config import db
from model import QuotaSensitivity, QuotaSentiment, QuotaDuration, QuotaQuickness, \
                  QuotaCoverage, QuotaMediaImportance, QuotaPersonSensitivity
from model import QuotaFSensitivity, QuotaFSentiment,QuotaFSensitivity, QuotaFTransmission, QuotaFInvolved, QuotaIndex


def ComputeFSensitivity(topic, start_ts, end_ts):
    items = db.session.query(QuotaSensitivity).filter(QuotaSensitivity.topic==topic ,\
                                                     QuotaSensitivity.start_ts==start_ts ,\
                                                     QuotaSensitivity.end_ts==end_ts).all()
    for item in items:
        if item.classfication==1:
            quota_class_sensitivity = item.score
        elif item.classfication==2:
            quota_word_sensitivity = item.score
    f_sensitivity = 0.5 * quota_class_sensitivity + 0.5 * quota_word_sensitivity
    save_sensitivity(topic, start_ts, end_ts, f_sensitivity)
    return f_sensitivity

def ComputeFSentiment(topic, start_ts, end_ts):
    item = db.session.query(QuotaSentiment).filter(QuotaSentiment.topic==topic ,\
                                                    QuotaSentiment.start_ts==start_ts ,\
                                                    QuotaSentiment.end_ts==end_ts).first()

    sentiment_dict = json.loads(item.sratio)
    quota_angry = sentiment_dict['angry']
    quota_sad = sentiment_dict['sad']
    f_sentiment = 0.7 * quota_angry + 0.3 * quota_sad
    sentiment_exp = 0.4
    x = float(f_sentiment) / float(sentiment_exp)
    print 'x:', x
    if x>1:
        x = 1
    save_sentiment(topic, start_ts, end_ts, x)
    return f_sentiment

def ComputeFTransmission(topic, start_ts, end_ts):
    item_duration = db.session.query(QuotaDuration).filter(QuotaDuration.topic==topic ,\
                                                           QuotaDuration.start_ts==start_ts ,\
                                                           QuotaDuration.end_ts==end_ts).first()
    quota_duration = item_duration.duration
    item_quickness = db.session.query(QuotaQuickness).filter(QuotaQuickness.topic==topic ,\
                                                             QuotaQuickness.start_ts==start_ts ,\
                                                             QuotaQuickness.end_ts==end_ts ,\
                                                             QuotaQuickness.domain=='all').first()
    quota_quickness = item_quickness.quickness
    item_coverage = db.session.query(QuotaCoverage).filter(QuotaCoverage.topic==topic ,\
                                                           QuotaCoverage.start_ts==start_ts ,\
                                                           QuotaCoverage.end_ts==end_ts).first()
    quota_coverage = item_coverage.coverage
    f_transmission = (1.0 / 3.0) * quota_duration + (1.0 / 3.0) * quota_quickness + (1.0 / 3.0) * quota_coverage
    save_transmission(topic, start_ts, end_ts, f_transmission)
    return f_transmission

def ComputeFInvolved(topic, start_ts, end_ts):
    item_media = db.session.query(QuotaMediaImportance).filter(QuotaMediaImportance.topic==topic ,\
                                                               QuotaMediaImportance.start_ts==start_ts ,\
                                                               QuotaMediaImportance.end_ts==end_ts).first()
    quota_media_involved = item_media.media_importance
    print 'quota_media_involved:',quota_media_involved, type(quota_media_involved)
    item_person = db.session.query(QuotaPersonSensitivity).filter(QuotaPersonSensitivity.topic==topic ,\
                                                                  QuotaPersonSensitivity.start_ts==start_ts ,\
                                                                  QuotaPersonSensitivity.end_ts==end_ts).first()
    quota_person_involved = item_person.pr
    print 'quota_person_involved:', quota_person_involved, type(quota_person_involved)
    f_involved = 0.5 * (quota_media_involved+0.0) + 0.5 * (quota_person_involved+0.0)
    save_involved(topic, start_ts, end_ts, f_involved)
    return f_involved

def ComputeIndex(topic, start_ts, end_ts):
    f_sensitivity = ComputeFSensitivity(topic, start_ts, end_ts)
    f_sentiment = ComputeFSentiment(topic, start_ts, end_ts)
    f_transmission = ComputeFTransmission(topic, start_ts, end_ts)
    f_involved = ComputeFInvolved(topic, start_ts, end_ts)
    '''
    item_fweight = db.session.query(FWeight).filter(FWeight.topic==topic ,\
                                                    FWeight.start_ts==start_ts ,\
                                                    FWeight.end_ts==end_ts).first()
    weight_dict = item_fweight.weight
    index = weight_dict['sensitivity']*f_sensitivity+weight_dict['sentiment']*f_sentiment\
            +weight_dict['transimission']*f_transmission+weight_dict['involved']*f_involved
    '''
    index = 0.25 * f_sensitivity + 0.25 * f_sentiment\
            + 0.25 * f_transmission + 0.25 * f_involved
    save_index(topic, start_ts, end_ts, index)

def save_index(topic, start_ts, end_ts, index):
    item = QuotaIndex(topic, start_ts, end_ts, index)
    item_exist = db.session.query(QuotaIndex).filter(QuotaIndex.topic==topic ,\
                                                     QuotaIndex.start_ts==start_ts ,\
                                                     QuotaIndex.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()
    print 'save index success'

def save_sensitivity(topic, start_ts, end_ts, f_sensitivity):
    f_sensitivity = 0.25
    item = QuotaFSensitivity(topic, start_ts, end_ts, f_sensitivity)
    item_exist = db.session.query(QuotaFSensitivity).filter(QuotaFSensitivity.topic==topic ,\
                                                            QuotaFSensitivity.start_ts==start_ts ,\
                                                            QuotaFSensitivity.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()
    print 'save f_sensitivity success'

def save_sentiment(topic,start_ts, end_ts, f_sentiment):
    item = QuotaFSentiment(topic, start_ts, end_ts, f_sentiment)
    item_exist = db.session.query(QuotaFSentiment).filter(QuotaFSentiment.topic==topic ,\
                                                         QuotaFSentiment.start_ts==start_ts ,\
                                                         QuotaFSentiment.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()
    print 'save f_sentiment success'

def save_transmission(topic, start_ts, end_ts, f_transmission):
    item = QuotaFTransmission(topic, start_ts, end_ts, f_transmission)
    item_exist = db.session.query(QuotaFTransmission).filter(QuotaFTransmission.topic==topic ,\
                                                            QuotaFTransmission.start_ts==start_ts ,\
                                                            QuotaFTransmission.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()
    print 'save f_transmission success'

def save_involved(topic, start_ts, end_ts, f_involved):
    item = QuotaFInvolved(topic, start_ts, end_ts, f_involved)
    item_exist = db.session.query(QuotaFInvolved).filter(QuotaFInvolved.topic==topic ,\
                                                        QuotaFInvolved.start_ts==start_ts ,\
                                                        QuotaFInvolved.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()
    print 'save f_involved success'
    
    
