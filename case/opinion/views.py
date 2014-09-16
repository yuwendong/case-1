#-*- coding:utf-8 -*-
import os
import json
from get_result import get_opinion_time, get_opinion_ratio, get_opinion_keywords, get_opinion_weibos
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import heapq

mod = Blueprint('opinion', __name__, url_prefix='/opinion')

class TopkHeap(object):
    def __init__(self, k):
        self.k = k
        self.data = []
 
    def Push(self, elem):
        if len(self.data) < self.k:
            heapq.heappush(self.data, elem)
        else:
            topk_small = self.data[0][0]
            if elem[0] > topk_small:
                heapq.heapreplace(self.data, elem)
 
    def TopK(self):
        return [x for x in reversed([heapq.heappop(self.data) for x in xrange(len(self.data))])]

@mod.route('/time/')
def opinion_time():
    topic = request.args.get('topic', '')
    results = get_opinion_time(topic) # results=[{childtopic:[start_ts, end_ts]},....]
    if not results:
        return 'no data in mysql'
    
    time_list = []
    for i in range(0,len(results)):
        if len(results[i][0])>=3:
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
        elif len(results[i][0]) ==2:
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')
        else:
            k = results[i][0][0].encode('utf-8')
        time_list.append([k,results[i][1],results[i][2]])
    return json.dumps(time_list)

@mod.route('/ratio/')
def opinion_ratio():
    topic = request.args.get('topic', '')
    results = get_opinion_ratio(topic) # results=[{childtopic:ratio},....]
    if not results:
        return 'no data in mysql'
    ratio = dict()
    for i in range(0,len(results)):
        if len(results[i][0])>=3:
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
        elif len(results[i][0]) ==2:
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')
        else:
            k = results[i][0][0].encode('utf-8')
        ratio[k] = results[i][1]
    return json.dumps(ratio)

@mod.route('/keywords/')
def opinion_keywords():
    topic = request.args.get('topic', '')
    results = get_opinion_keywords(topic) # results=[{childtopic:[(keywords,weight)]},.....]
    if not results:
        return 'no data in mysql'

    ratio = dict()
    for i in range(0,len(results)):
        if len(results[i][0])>=3:
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
        elif len(results[i][0]) ==2:
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')
        else:
            k = results[i][0][0].encode('utf-8')
        ratio[k] = results[i][1]
    return json.dumps(ratio)

@mod.route('/weibos/')
def opinion_weibos():
    topic = request.args.get('topic', '')
    results = get_opinion_weibos(topic) # results=[{childtopic:[{weibos,weight}]},.....]
    if not results:
        return 'no data in mysql'

    f_news = TopkHeap(20)
    for i in range(0,len(results)):
        if len(results[i][0])>=3:
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
        elif len(results[i][0]) ==2:
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')
        else:
            k = results[i][0][0].encode('utf-8')
        row = {'c_topic':k,'weight':results[i][1],'_id':results[i][2],'title':results[i][3],'content':results[i][4],'user':results[i][5],'time':results[i][6],'source':results[i][7],'c_source':results[i][8],'repeat':results[i][9]}
        f_news.Push((results[i][1],row))

    data = f_news.TopK()
    return json.dumps(data)
    
