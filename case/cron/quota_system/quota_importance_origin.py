# -*- coding: utf-8 -*-
import sys
import json
import random
#from config import db
from model import QuotaImportance

sys.path.append('../../')
from global_config import db

# 若topic不存在，添加该话题的importance默认值；若topic存在，则不进行修改
def origin_quota_importance(topic, start_ts, end_ts):
    item_exist = db.session.query(QuotaImportance).filter(QuotaImportance.topic==topic ,\
                                                          QuotaImportance.start_ts==start_ts ,\
                                                          QuotaImportance.end_ts==end_ts).first()
    if not item_exist:
        score = 0
        weight = 0
        item = QuotaImportance(topic, start_ts, end_ts, score, weight)
        db.session.add(item)
        db.session.commit()
        print 'success save default quota_importance'
    else:
        print 'default value of quota_importance exist'

if __name__=='__main__':
    topic = u'中国'
    start_ts = 1377965700
    end_ts = 1378051200
    origin_quota_importance(topic, start_ts, end_ts)
