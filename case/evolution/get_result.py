# -*- coding: utf-8 -*-

import case.model
from case.model import EvolutionTopicCount, EvolutionTopicKeywords, EvolutionTopicTopWeibos
from case.extensions import db
import json
from utils import weiboinfo2url

TOP_WEIBOS_LIMIT = 50
TOP_READ = 10
evolutions_kv = {'original': 1, 'forward': 2, 'comment': 3}
evolution_re = {1:'original', 2:'forward', 3:'comment'}

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
    
def _top_weibos(weibos_dict, top=TOP_READ):
    results_list = []

    if weibos_dict != {}:
        results = sorted(weibos_dict.iteritems(), key=lambda(k,v): v[0], reverse=False)
        results = results[len(results) - top:]

        for k, v in results:
            results_list.append(v[1])

    return results_list

def getKeywords(query, ts, module):
    if module == 'original':#搜索原创对应时间点的关键词
        item = db.session.query(EvolutionTopicKeywords).filter((EvolutionTopicKeywords.query==query)&(EvolutionTopicKeywords.end==ts)&(EvolutionTopicKeywords.evolution==1)).first()
        keyword = []
        if item:
            keywords_list = json.loads(item.kcount)
            for i in keywords_list:
                row = {}
                row['word'] = i[0]
                row['weight'] = i[1]
                row['type'] = 1
                row['ts'] =  ts
                keyword.append(row)
        else:
            pass
    elif module == 'forward':#搜索转发对应时间点的关键词
        item = db.session.query(EvolutionTopicKeywords).filter((EvolutionTopicKeywords.query==query)&(EvolutionTopicKeywords.end==ts)&(EvolutionTopicKeywords.evolution==2)).first()
        keyword = []
        if item:
            keywords_list = json.loads(item.kcount)
            for i in keywords_list:
                row = {}
                row['word'] = i[0]
                row['weight'] = i[1]
                row['type'] = 2
                row['ts'] =  ts
                keyword.append(row)
        else:
            pass
    else:#搜索评论对应时间点的关键词
        item = db.session.query(EvolutionTopicKeywords).filter((EvolutionTopicKeywords.query==query)&(EvolutionTopicKeywords.end==ts)&(EvolutionTopicKeywords.evolution==3)).first()
        keyword = []
        if item:
            keywords_list = json.loads(item.kcount)
            for i in keywords_list:
                row = {}
                row['word'] = i[0]
                row['weight'] = i[1]
                row['type'] = 3
                row['ts'] =  ts
                keyword.append(row)
        else:
            pass

    return keyword

def getWeibo(query, ts, module):
    if module == 'original':#搜索原创对应时间点的关键词
        item = db.session.query(EvolutionTopicTopWeibos).filter((EvolutionTopicTopWeibos.query==query)&(EvolutionTopicTopWeibos.end==ts)&(EvolutionTopicTopWeibos.evolution==1)).first()
        weibos_dict = {}
        if item:
            weibos_dict = parseWeibos(item.weibos)
        else:
            pass
        weibos_list = _top_weibos(weibos_dict, TOP_READ)
    elif module == 'forward':#搜索评论对应时间点的关键词
        item = db.session.query(EvolutionTopicTopWeibos).filter((EvolutionTopicTopWeibos.query==query)&(EvolutionTopicTopWeibos.end==ts)&(EvolutionTopicTopWeibos.evolution==2)).first()
        weibos_dict = {}
        if item:
            weibos_dict = parseWeibos(item.weibos)
        else:
            pass
        weibos_list = _top_weibos(weibos_dict, TOP_READ)
    else:#搜索转发对应时间点的关键词
        item = db.session.query(EvolutionTopicTopWeibos).filter((EvolutionTopicTopWeibos.query==query)&(EvolutionTopicTopWeibos.end==ts)&(EvolutionTopicTopWeibos.evolution==3)).first()
        weibos_dict = {}
        if item:
            weibos_dict = parseWeibos(item.weibos)
        else:
            pass
        weibos_list = _top_weibos(weibos_dict, TOP_READ)

    return weibos_list

def getPoint(topic, module):#提取某种情绪的拐点
    items = db.session.query(SentimentPoint).filter((SentimentPoint.topic==topic)&(SentimentPoint.stype==module)).all()
    point = []
    for item in items:
        point.append(item.ts)

    return point

def getCount(query, ts):#提取三种在某个时间点的绝对数量
    items = db.session.query(EvolutionTopicCount).filter((EvolutionTopicCount.end==ts)).all()
    row = {}
    for item in items:        
        row[evolution_re[item.evolution]] = item.count

    return row

        
