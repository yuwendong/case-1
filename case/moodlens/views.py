#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import os
import json
from get_result import *

#constants
emotions_kv = {'happy': 1, 'angry': 2, 'sad': 3}

mod = Blueprint('moodlens', __name__, url_prefix='/moodlens')

@mod.route('/index')
def index():
    return render_template('root/index.html')

@mod.route('/weibo')
def weibo():
    return render_template('moodlens/weibo.html')

'''
@mod.route('/news')
def weibo():
    return render_template('moodlens/news.html')

@mod.route('/blog')
def weibo():
    return render_template('moodlens/blog.html')

@mod.route('/forum')
def weibo():
    return render_template('moodlens/forum.html')
'''
@mod.route('/data/')
def data():
    query = request.args.get('query',None)
    if query:
        query = query.strip()
    ts = request.args.get('ts','')
    ts=long(ts)
    print ts,query
    results = getCount(query,ts)
    
    return json.dumps(results)

@mod.route('/emotionpeak/')
def emotionpeak():
    query = request.args.get('query',None)
    if query:
        query = query.strip()
        
    emotion = request.args.get('emotion',None)
    if emotion:
        results = getPoint(query, emotion)

    return json.dumps(results)

@mod.route('/keywords_data/')
def keywords_data():
    query = request.args.get('query',None)
    if query:
        topic = query.strip()
    ts = request.args.get('ts','')
    ts = long(ts)
    module = request.args.get('emotion','whole')
    print topic,ts,module
    results = getKeywords(topic, ts, module)

    return json.dumps(results)

@mod.route('/weibos_data/')
def weibos_data():
    """关键微博
    """
    
    query = request.args.get('query', None)
    if query:
        query = query.strip()
    
    ts = request.args.get('ts', '')
    ts = long(ts)
    #begin_ts = ts - during
    #end_ts = ts
    emotion = request.args.get('emotion','whole')

    
    results = getWeibo(query,ts,emotion)

    return json.dumps(results)


