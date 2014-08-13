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


def search_topic_counts(end_ts, during, sentiment, unit=MinInterval, query=None, domain=None, customized='1'):
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        if customized == '0':
            item = db.session.query(SentimentCountRatio).filter(SentimentCountRatio.end==upbound, \
                                              SentimentCountRatio.sentiment==sentiment, \
                                              SentimentCountRatio.range==unit, \
                                              SentimentCountRatio.query==query).first()
        else:
            item = db.session.query(SentimentCount).filter(SentimentCount.end==upbound, \
                                              SentimentCount.sentiment==sentiment, \
                                              SentimentCount.range==unit, \
                                              SentimentCount.query==query).first()
        if item:
            count = [end_ts * 1000, item.count]
        else:
            count = [end_ts * 1000, 0]

    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        if customized == '0':
            count = db.session.query(func.sum(SentimentCountRatio.count)).filter(SentimentCountRatio.end>lowbound, \
                                            SentimentCountRatio.end<=upbound, \
                                            SentimentCountRatio.sentiment==sentiment, \
                                            SentimentCountRatio.range==unit, \
                                            SentimentCountRatio.query==query).all()

        else:
            count = db.session.query(func.sum(SentimentCount.count)).filter(SentimentCount.end>lowbound, \
                                                SentimentCount.end<=upbound, \
                                                SentimentCount.sentiment==sentiment, \
                                                SentimentCount.range==unit, \
                                                SentimentCount.query==query).all()

        if count and count[0] and count[0][0]:
            count = [end_ts * 1000, int(count[0][0])]
        else:
            count = [end_ts * 1000, 0]

    return count


if __name__ == '__main__':
    emotions_kv = {'happy': 1, 'angry': 2, 'sad': 3}
    end_ts = datetime2ts('2013-09-18')
    during = 1 * Day

    for k, v in emotions_kv.iteritems():
        count = search_topic_counts(end_ts, during, v, domain=0)
