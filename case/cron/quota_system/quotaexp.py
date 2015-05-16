# -*- coding: utf-8 -*-
import sys
import json
#from config import db
from model import QuotaAttentionExp, QuotaDurationExp, CoverageExp

sys.path.append('../../')
from global_config import db

Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24


def save_exp(topic, start_ts, end_ts, attention_exp, duration_exp, coverage_exp):
    item_attention = QuotaAttentionExp(topic, start_ts, end_ts, json.dumps(attention_exp))
    item_attention_exist = db.session.query(QuotaAttentionExp).filter(QuotaAttentionExp.topic==topic, \
                                                                      QuotaAttentionExp.start_ts==start_ts ,\
                                                                      QuotaAttentionExp.end_ts==end_ts).first()
    if item_attention_exist:
        db.session.delete(item_attention_exist)
    db.session.add(item_attention)

    db.session.commit()
    
    item_duration = QuotaDurationExp(topic, start_ts, end_ts, duration_exp)
    item_duration_exist = db.session.query(QuotaDurationExp).filter(QuotaDurationExp.topic==topic ,\
                                                                    QuotaDurationExp.start_ts==start_ts ,\
                                                                    QuotaDurationExp.end_ts==end_ts).first()
    if item_duration_exist:
        db.session.delete(item_duration_exist)
    db.session.add(item_duration)

    db.session.commit()

    item_coverage = CoverageExp(topic, start_ts, end_ts, coverage_exp)
    item_coverage_exist = db.session.query(CoverageExp).filter(CoverageExp.topic==topic ,\
                                                               CoverageExp.start_ts==start_ts ,\
                                                               CoverageExp.end_ts==end_ts).first()
    if item_coverage_exist:
        db.session.delete(item_coverage_exist)
    db.session.add(item_coverage)

    db.session.commit()
    

if __name__=='__main__':
    attention_exp = {'folk':100, 'media':100, 'other':100, 'opinion_leader':100, 'oversea':100}
    duration_exp = 5 * Day
    coverage_exp = 3000 # 话题参与人数的经验值设为3000
    save_exp(topic, start, end, attention_exp, duration_exp, coverage_exp)
