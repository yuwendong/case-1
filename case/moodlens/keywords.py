# -*- coding: utf-8 -*-


import json
import math
import operator
from case.extensions import db
from case.model import SentimentKeywords
from time_utils import datetime2ts


TOP_KEYWORDS_LIMIT = 50
TOP_READ = 10

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes


def parseKcount(kcount):
    kcount_dict = {}
    kcount = json.loads(kcount)

    for k, v in kcount:
    	kcount_dict[k] = v

    return kcount_dict


def _top_keywords(kcount_dict, top=TOP_READ):
    results_dict = {}

    if kcount_dict != {}:
        results = sorted(kcount_dict.iteritems(), key=operator.itemgetter(1), reverse=False)
        results = results[len(results) - top:]

        for k, v in results:
            results_dict[k] = v

    return results_dict


def search_topic_keywords(end_ts, during, sentiment, unit=MinInterval, top=TOP_READ, limit=TOP_KEYWORDS_LIMIT, query=None, domain=None, customized='1'):
    kcounts_dict = {}
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        item = db.session.query(SentimentKeywords).filter(SentimentKeywords.end==upbound, \
                                              SentimentKeywords.sentiment==sentiment, \
                                              SentimentKeywords.range==unit, \
                                              SentimentKeywords.query==query, \
                                              SentimentKeywords.limit==limit).first()
        if item:
            kcounts_dict = parseKcount(item.kcount)

    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        items = db.session.query(SentimentKeywords).filter(SentimentKeywords.end>lowbound, \
                                                 SentimentKeywords.end<=upbound, \
                                                 SentimentKeywords.sentiment==sentiment, \
                                                 SentimentKeywords.range==unit, \
                                                 SentimentKeywords.query==query, \
                                                 SentimentKeywords.limit==limit).all()
        for item in items:
            kcount_dict = parseKcount(item.kcount)
            for k, v in kcount_dict.iteritems():
                try:
                    kcounts_dict[k] += v
                except KeyError:
                    kcounts_dict[k] = v

    kcounts_dict = _top_keywords(kcounts_dict, top)

    return kcounts_dict


if __name__ == '__main__':
    emotions_kv = {'happy': 1, 'angry': 2, 'sad': 3}
    end_ts = datetime2ts('2013-09-01')
    during = 5 * Day

            
    print 'topic'
    for k, v in emotions_kv.iteritems():
        print v
        keywords_with_count = search_topic_keywords(end_ts, during, v, query='钓鱼岛')
        for key, value in keywords_with_count.iteritems():
            print key, value
