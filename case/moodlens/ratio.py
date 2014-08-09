# -*- coding: utf-8 -*-


import json
import math
import operator
from sqlalchemy import func
from case.extensions import db
from time_utils import datetime2ts
from case.model import SentimentCount, SentimentCountRatio


Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes


def search_topic_ratio(end_ts, during, sentiment, unit=MinInterval, query=None, domain=None, customized='1'):
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        item1 = db.session.query(SentimentCountRatio).filter(SentimentCountRatio.end==upbound, \
                                              SentimentCountRatio.sentiment==sentiment, \
                                              SentimentCountRatio.range==unit, \
                                              SentimentCountRatio.query==query).first()
        item2 = db.session.query(SentimentCountRatio).filter(SentimentCountRatio.end==upbound, \
                                              SentimentCountRatio.sentiment==sentiment, \
                                              SentimentCountRatio.range==unit, \
                                              SentimentCountRatio.query==query).first()
        if item1 and item2:
            print 'count',item1.count
            print 'allcount',item2.allcount
            ratio = float(item1.count) / item2.allcount
        else:
            ratio = 0

    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        count = db.session.query(func.sum(SentimentCountRatio.count)).filter(SentimentCountRatio.end>lowbound, \
                                                SentimentCountRatio.end<=upbound, \
                                                SentimentCountRatio.sentiment==sentiment, \
                                                SentimentCountRatio.range==unit, \
                                                SentimentCountRatio.query==query).all()
        allcount = db.session.query(func.sum(SentimentCountRatio.allcount)).filter(SentimentCountRatio.end>lowbound, \
                                                SentimentCountRatio.end<=upbound, \
                                                SentimentCountRatio.sentiment==sentiment, \
                                                SentimentCountRatio.range==unit, \
                                                SentimentCountRatio.query==query).all()

        if count and allcount and count[0] and count[0][0] and allcount[0] and allcount[0][0]:

            print 'count',count[0][0]
            print 'allcount',allcount[0][0]
            ratio = count[0][0] / allcount[0][0]
        else:
            ratio = 0

    return ratio

