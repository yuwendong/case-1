# -*- coding: utf-8 -*-
import json
from config import db
from model import GeoWeight

def save_weight_dict(weight_dict):
    item = GeoWeight(json.dumps(weight_dict))
    item_exist = db.session.query(GeoWeight).first()
    if not item_exist:
        db.session.add(item)
        db.session.commit()
        print 'success save default weight_dict'
    else:
        print 'default weight_dict exist'


if __name__=='__main__':
    weight_dict = [(100000, 10000000, 1), (80000, 100000, 0.9),\
                   (60000, 80000, 0.7), (40000, 600000, 0.5), \
                   (20000, 40000, 0.3), (10000,20000, 0.1), \
                   (0,10000, 0)]
    save_weight_dict(weight_dict)
