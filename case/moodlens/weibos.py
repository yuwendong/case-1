# -*- coding: utf-8 -*-

import json
import math
import operator
from case.extensions import db
from case.model import SentimentWeibos 
from time_utils import datetime2ts,ts2date
from utils import weiboinfo2url
from config import xapian_search_user as user_search


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
    results_list_new = []

    if weibos_dict != {}:
        results = sorted(weibos_dict.iteritems(), key=lambda(k,v): v[0], reverse=False)
        results = results[len(results) - top:]
        #print 'len_results',len(results)-top
        for k, v in results:
            results_list.append(v[1])
        for i in range(len(results_list)):
            results_list_new.append(results_list[len(results_list)-1-i])
    #print 'lens_results_list:', len(results_list)
    return results_list_new


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
      #print 'there there there', weibo['user']
      username, profileimage = getuserinfo(weibo['user']) # get username and profile_image_url
      #print '99999:',username, profileimage
      reposts_count = weibo['reposts_count']
      weibo['weibo_link'] = weiboinfo2url(weibo['user'], _id)
      weibo['username'] = username
      weibo['profile_image_url'] = profileimage
      weibo['timestamp'] = ts2date(weibo['timestamp'])
      weibo_dict[_id] = [reposts_count, weibo]
      #print '#####:', weibo_dict
    except:
      continue

  return weibo_dict

def acquire_user_by_id(uid):
    user_result = user_search.search_by_id(uid, fields=['name', 'profile_image_url'])
    user = {}
    if user_result:
        user['name'] = user_result['name']
        user['image'] = user_result['profile_image_url']
    #print 'user', user
    return user


def getuserinfo(uid):
    #print 'uid:',uid, type(uid)
    user = acquire_user_by_id(uid)
    if not user:
        username = 'Unkonwn'
        profileimage = ''
    else:
        username = user['name']
        profileimage = user['image']
    return username, profileimage



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

