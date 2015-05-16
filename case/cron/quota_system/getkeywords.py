# -*- coding: utf-8 -*-
import sys
import json
import operator
#from config import db
from model import PropagateKeywords

sys.path.append('../../')
from global_config import db

Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24


def parseKcount(kcount):
    kcount_dict = {}
    kcount = json.loads(kcount)

    for k, v in kcount:
        kcount_dict[k] = v

    return kcount_dict

def _top_keywords(kcount_dict, top):
    results_dict = {}

    if kcount_dict != {}:
        results = sorted(kcount_dict.iteritems(), key=operator.itemgetter(1), reverse=False)
        results = results[len(results)-top: ]

        for k, v in results:
            results_dict[k] = v

    return results_dict
        

def get_keywords(topic, start_ts, end_ts, all_limit):
    unit = Fifteenminutes
    limit = 50
    kcount_dict = {}
    upbound = int(start_ts / Fifteenminutes) * Fifteenminutes
    lowbound = (int(end_ts / Fifteenminutes) + 1) * Fifteenminutes
    items = db.session.query(PropagateKeywords).filter(PropagateKeywords.end>=upbound ,\
                                                       PropagateKeywords.end<=lowbound ,\
                                                       PropagateKeywords.topic==topic ,\
                                                       PropagateKeywords.range==unit ,\
                                                       PropagateKeywords.limit==limit).all()
    kcounts_dict = {}
    for item in items:
        kcount_dict = parseKcount(item.kcount)
        for k ,v in kcount_dict.iteritems():
            try:
                kcounts_dict[k] += v
            except KeyError:
                kcounts_dict[k] = v
    kcounts_dict = _top_keywords(kcounts_dict, all_limit)
    keywords_set = set()
    for keyword in kcounts_dict:
        keywords_set.add(keyword)

    return keywords_set
    
