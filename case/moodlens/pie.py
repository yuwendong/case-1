# -*- coding: utf-8 -*-


import json
import math
import operator
from sqlalchemy import func
from case.extensions import db
from time_utils import datetime2ts
from case.model import SentimentCountRatio
from case.global_config import emotions_kv


Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes


def search_topic_pie(end_ts, during, unit=MinInterval, query=None):
    ratio ={}
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        for sentiment in emotions_kv:
            item1 = db.session.query(SentimentCountRatio).filter(SentimentCountRatio.end==upbound, \
                                              SentimentCountRatio.sentiment==emotions_kv[sentiment], \
                                              SentimentCountRatio.range==unit, \
                                              SentimentCountRatio.query==query).first()
            item2 = db.session.query(SentimentCountRatio).filter(SentimentCountRatio.end==upbound, \
                                              SentimentCountRatio.sentiment==emotions_kv[sentiment], \
                                              SentimentCountRatio.range==unit, \
                                              SentimentCountRatio.query==query).first()
            if item1 and item2:
                ratio[sentiment] = '%.4f' % (float(item1.count) / float(item2.allcount))
            else:
                ratio[sentiment] =0

    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        for sentiment in emotions_kv:
            count = db.session.query(func.sum(SentimentCountRatio.count)).filter(SentimentCountRatio.end>lowbound, \
                                                SentimentCountRatio.end<=upbound, \
                                                SentimentCountRatio.sentiment==emotions_kv[sentiment], \
                                                SentimentCountRatio.range==unit, \
                                                SentimentCountRatio.query==query).all()
            allcount = db.session.query(func.sum(SentimentCountRatio.allcount)).filter(SentimentCountRatio.end>lowbound, \
                                                SentimentCountRatio.end<=upbound, \
                                                SentimentCountRatio.sentiment==emotions_kv[sentiment], \
                                                SentimentCountRatio.range==unit, \
                                                SentimentCountRatio.query==query).all()

            if count and allcount and count[0] and count[0][0] and allcount[0] and allcount[0][0]:
                ratio[sentiment] ='%.4f' % (float(count[0][0]) / float(allcount[0][0]))
            else:
                ratio[sentiment] = 0

    return ratio


