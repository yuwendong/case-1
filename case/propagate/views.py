#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import os
import json
from peak_detection import detect_peaks
from read_quota import ReadPropagate, ReadIncrement, ReadPropagateKeywords, ReadPropagateWeibos  # ,ReadAttention, ReadPenetration, ReadQuickness 

mtype_kv = {'origin':1, 'forward':2, 'comment':3}


mod = Blueprint('propagate', __name__, url_prefix='/propagate')

@mod.route('/total/')
def ajax_propagate():
    mtype = request.args.get('style', '')
    mtype = int(mtype)
    topic = request.args.get('topic', '')
    during = request.args.get('during', 900)
    during = int(during)
    end = request.args.get('end_ts', '')
    end = int(end)
    results = ReadPropagate(topic, end, during, mtype)

    return json.dumps(results)

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
    results = ReadPropagateKeywords(topic, end_ts, during, mtype, limit)
    

    return json.dumps(results)

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
    results = ReadPropagateWeibos(topic, end_ts, during, mtype, limit)
    return json.dumps(results)

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

    title_text = {'origin': [], 'forward': [], 'comment': []}
    title = {'1': 'A', '2': 'B', '3': 'C'}

    time_lis = {}
    for idx, point_idx in enumerate(new_zeros):
        print idx, point_idx
        ts = ts_lis[point_idx]
        begin_ts = ts - during
        end_ts = ts

        v = mtype_kv[mtype]

        time_lis[idx] = {
            'ts': end_ts * 1000,
            'title': title[str(mtype)] + str(idx+1),
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
