# -*- coding: utf-8 -*-

import json
import math
import operator
from case.extensions import db
from case.model import SentimentWeibos 
from time_utils import datetime2ts
from utils import weiboinfo2url


TOP_WEIBOS_LIMIT = 50
TOP_READ = 10

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes


def _top_weibos(weibos_dict, top=TOP_READ):
    results_list = []

    if weibos_dict != {}:
        results = sorted(weibos_dict.iteritems(), key=lambda(k,v): v[0], reverse=False)
        results = results[len(results) - top:]

        for k, v in results:
            results_list.append(v[1])

    return results_list


def _json_loads(weibos):
  try:
    return json.loads(weibos)
  except ValueError:
    if isinstance(weibos, unicode):
      return json.loads(json.dumps(weibos))
    else:
      return None


def parseWeibos(weibos):
  weibo_dict = {}
  weibos = _json_loads(weibos)

  if not weibos:
    return {}

  for weibo in weibos:
    try:
      _id = weibo['_id']
      reposts_count = weibo['reposts_count']
      weibo['weibo_link'] = weiboinfo2url(weibo['user'], _id)
      weibo_dict[_id] = [reposts_count, weibo]
    except:
      continue

  return weibo_dict


def search_topic_weibos(end_ts, during, sentiment, unit=MinInterval, top=TOP_READ, limit=TOP_WEIBOS_LIMIT, query=None, domain=None, customized='1'):
    weibos_dict = {}
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        item = db.session.query(SentimentWeibos).filter(SentimentWeibos.end==upbound, \
                                                  SentimentWeibos.sentiment==sentiment, \
                                                  SentimentWeibos.range==unit, \
                                                  SentimentWeibos.query==query, \
                                                  SentimentWeibos.limit==limit).first()
        if item:
            weibos_dict = parseWeibos(item.weibos)

    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        items = db.session.query(SentimentWeibos).filter(SentimentWeibos.end>lowbound, \
                                                     SentimentWeibos.end<=upbound, \
                                                     SentimentWeibos.sentiment==sentiment, \
                                                     SentimentWeibos.range==unit, \
                                                     SentimentWeibos.query==query, \
                                                     SentimentWeibos.limit==limit).all()
        for item in items:
            weibo_dict = parseWeibos(item.weibos)
            for k, v in weibo_dict.iteritems():
                try:
                    weibos_dict[k] += v
                except KeyError:
                    weibos_dict[k] = v

    weibos_dict = _top_weibos(weibos_dict, top)

    return weibos_dict

