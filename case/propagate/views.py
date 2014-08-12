#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import os
import json
from read_quota import ReadPropagate, ReadIncrement # ,ReadAttention, ReadPenetration, ReadQuickness 


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
