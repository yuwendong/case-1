#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import os
import json
from peak_detection import detect_peaks
from read_quota import ReadPropagate, ReadIncrement, ReadPropagateKeywords, ReadPropagateWeibos  # ,ReadAttention, ReadPenetration, ReadQuickness 

mtype_kv = {'origin': 1, 'comment': 2, 'forward': 3}


mod = Blueprint('propagate', __name__, url_prefix='/propagate')

@mod.route('/total/')
def ajax_propagate():
    mtype = request.args.get('style', '')
    mtype = int(mtype)
    topic = request.args.get('topic', '')
    during = request.args.get('during', 3600)
    during = int(during)
    end = request.args.get('end_ts', '')
    end = int(end)

    results_dict = {}
    incre_results_dict = {}
    if mtype == 5:
        count = 0
        for k, v in mtype_kv.iteritems():
            results = ReadPropagate(topic, end, during, v)
            # incr_results = ReadIncrement(topic, end, during, v)
            if results:
                results_dict[k] = sum(results['dcount'].values())
                count +=  results_dict[k]
        results_dict['total'] = count

    if mtype == 4:
        for k, v in mtype_kv.iteritems():
            results = ReadPropagate(topic, end, during, v)
            # incr_results = ReadIncrement(topic, end, during, v)
            if results:
                results_dict[k] = sum(results['dcount'].values())
            # if incr_results:
            #    incre_results_dict[k] = incr_results['dincrement']['total']

    return json.dumps({'count': results_dict, 'incre': incre_results_dict})

@mod.route('/increment/')
def increment():
    topic = request.args.get('topic', '')
    mtype = request.args.get('style', '')
    mtype = int(mtype)
    during = request.args.get('during', 900)
    during = int(during)
    end = request.args.get('end_ts', '')
    end = int(end)
    results = ReadIncrement(topic, end, during, mtype)
    return json.dumps(results)

@mod.route('/keywords/') 
def prpagate_keywords():
    topic = request.args.get('topic', '')
    mtype = request.args.get('style', '')
    mtype = int(mtype)
    during = request.args.get('during', 900)
    during = int(during)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    limit = request.args.get('limit', 50)
    limit = int(limit)

    results_dict = {}
    if mtype == 4 or mtype == 5:
        for k, v in mtype_kv.iteritems():
            results = ReadPropagateKeywords(topic, end_ts, during, v, limit)
            for keyword, count in results.iteritems():
                try:
                    results_dict[keyword] += count
                except KeyError:
                    results_dict[keyword] = count
    else:
        results_dict = ReadPropagateKeywords(topic, end_ts, during, mtype, limit)

    return json.dumps(results_dict)

@mod.route('/weibos/') 
def propagate_weibos():
    topic = request.args.get('topic', '')
    mtype = request.args.get('style', '')
    mtype = int(mtype)
    during = request.args.get('during', 900)
    during = int(during)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    limit = request.args.get('limit', 50)
    limit = int(limit)
    results_dict = {}

    if mtype == 4 or mtype == 5:
        weibos = []
        for k, v in mtype_kv.iteritems():
            results_dict[k] = ReadPropagateWeibos(topic, end_ts, during, v, limit)
            weibos.extend(results_dict[k])
        sorted_weibos = sorted(weibos, key=lambda k:k['reposts_count'], reverse=False)
        sorted_weibos = sorted_weibos[len(sorted_weibos)-50:]
        sorted_weibos.reverse()
        results_dict['total'] = sorted_weibos
    else:
        results_dict[mtype] = ReadPropagateWeibos(topic, end_ts, during, mtype, limit)
    return json.dumps(results_dict)

@mod.route('/propagatepeak/')
def PropagatePeak():
    limit = request.args.get('limit', 10)
    topic = request.args.get('topic', None)
    if topic:
        topic = topic.strip()
    during = request.args.get('during', 900)
    during = int(during)
    mtype = request.args.get('mtype', '')
    mtype = int(mtype)
    lis = request.args.get('lis', '')

    try:
        lis = [float(da) for da in lis.split(',')]
    except:
        lis =[]
    if not lis or not len(lis):
        return 'Null Data'

    ts_lis = request.args.get('ts', '')
    ts_lis = [float(da) for da in ts_lis.split(',')]

    new_zeros = detect_peaks(lis)

    title_text = {'origin': [], 'forward': [], 'comment': [], 'total': []}
    title = {'1': 'A', '2': 'B', '3': 'C', '5': 'D'}

    time_lis = {}
    for idx, point_idx in enumerate(new_zeros):
        # print idx, point_idx
        ts = ts_lis[point_idx]
        end_ts = ts

        v = mtype

        time_lis[idx] = {
            'ts': end_ts * 1000,
            'title': title[str(mtype)] + str(idx),
         }

    return json.dumps(time_lis)


'''

# 三个指标分别对应不同的页面url

@mod.route('/attention/') # 关注度曲线
def ajax_attention():
    mtype = request.args.get('style', '')
    mtype = int(mtype)
    topic = request.args.get('topic', '')
    during = request.args.get('during', 900)
    during = int(during)
    ts = request.args.get('ts', '')
    ts = long(ts)
    domain = request.args.get('domain','')
    begin_ts = ts - during
    end_ts = ts

    results = ReadAttention(topic, domain, mtype, ts, during)
    
    return json.dumps(results)
    
@mod.route('/penetration/')
def ajax_penetration():
    mtype = request.args.get('style', '')
    mtype = int(mtype)
    topic = request.args.get('topic', '')
    during = request.args.get('during', 900)
    during = int(during)
    ts = request.args.get('ts', '')
    ts = long(ts)
    domain = request.args.get('domain','')
    begin_ts = ts - during
    end_ts = ts

    results = ReadPenetration(topic, domain, mtype, ts, during)

    return json.dumps(results)

@mod.route('/quickness/')
def ajax_quickness():
    mtype = request.args.get('style', '')
    mtype = int(mtype)
    topic = request.args.get('topic', '')
    during = request.args.get('during', 2*900)
    during = int(during)
    ts = request.args.get('ts', '')
    ts = long(ts)
    domain = request.args.get('domain','')
    begin_ts = ts - during
    end_ts = ts

    results = ReadQuickness(topic, domain, mtype, ts, during)

    return json.dumps(results)
'''
