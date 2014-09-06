# -*- coding: utf-8 -*-
import json
from config import db
from model import QuotaWeight


def save_quota_weight_dict(weight_dict):
    item = QuotaWeight(json.dumps(weight_dict))
    item_exist = db.session.query(QuotaWeight).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

if __name__=='__main__':
    weight = 1.0 / 7.0
    quota_weight_dict = {'attention': weight ,\
                         'geo_penetration': weight ,\
                         'media_importance': weight ,\
                         'quickness': weight ,\
                         'duration': weight ,\
                         'sensitivity': weight ,\
                         'sentiment': weight}
    save_quota_weight_dict(quota_weight_dict)
    
