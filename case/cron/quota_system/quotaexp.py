# -*- coding: utf-8 -*-
import json
from config import db
from model import QuotaAttentionExp, QuotaDurationExp

def save_exp(topic, start_ts, end_ts, attention_exp, duration_exp):
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
    
