# -*- coding: utf-8 -*-
import os
import sys
import json
import time
reload(sys)
sys.setdefaultencoding('utf-8')

from datetime import datetime
from SSDB import SSDB 
from case.extensions import db
from case.global_config import SSDB_PORT, SSDB_HOST
from case.model import TopicStatus
from case.time_utils import datetimestr2ts, ts2datetime
from flask import Blueprint, url_for, render_template, request, abort, flash, make_response, session, redirect

from utils import read_topic_rank_results, read_degree_centrality_rank ,\
                  read_betweeness_centrality_rank, read_closeness_centrality_rank
from utils import read_ds_topic_rank_results, read_tr_rank_results, read_ds_degree_centrality_rank ,\
                  read_ds_betweeness_centrality_rank, read_ds_closeness_centrality_rank
from first_user import time_top_user, time_domain_top_user


TOPK = 1000
Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
module = 'identify'


NOT_CALC_STATUS = -1
IN_CALC_STATUS = 0
COMPLETED_STATUS = 1

mod = Blueprint('identify', __name__, url_prefix='/identify')

def _utf8_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, 'utf-8')

def get_topic_status(topic, start, end, module):
    '''判断该topic的状态
    '''
    item = db.session.query(TopicStatus).filter(TopicStatus.topic==topic, \
                                                TopicStatus.start==start, \
                                                TopicStatus.end==end, \
                                                TopicStatus.module==module).first()
  
    if item:
        return item.status
    else:
        return None


@mod.route("/graph/")
def network():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts)/Day
    windowsize = int(windowsize)
    end = ts2datetime(end_ts)
    network_type = request.args.get('network_type', '')
    module = 'identify'
    print 'topic, end_ts, windowsize, network_type:', topic.encode('utf-8'), end, windowsize,network_type  
    topic_status = get_topic_status(topic, start_ts, end_ts, module)
    print 'graph_status:', topic_status
    if topic_status == COMPLETED_STATUS:  
        query_key =_utf8_unicode(topic) + '_' + str(end) + '_' + str(windowsize) + '_' + network_type
        print 'key:', query_key.encode('utf-8')
        key = str(query_key)
        try:
            ssdb = SSDB(SSDB_HOST, SSDB_PORT)
            results = ssdb.request('get', [key])
            print 'results.code:', results.code
            if results.code == 'ok' and results.data:
                print 'result_code ok'
                response = make_response(results.data)
                response.headers['Content-Type'] = 'text/xml'
                return response
            return None
        except Exception, e:
            print 'error',e
            return None
    elif topic_status == IN_CALC_STATUS or topic_status == IN_CALC_STATUS:
        print 'The Topic is being computed......Just Waiting'
        return None
    else:
        print 'Topic is not in the topic_list'
        return None



@mod.route("/rank/")
def network_rank():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts) / Day
    topn = request.args.get('topn', 100)
    topn = int(topn)
    date = ts2datetime(end_ts)
    rank_method = 'pagerank'
    results = read_topic_rank_results(topic, topn, rank_method, date, windowsize)
    return json.dumps(results)

@mod.route('/ds_pr_rank/')
def ds_network_pr_rank():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts) / Day
    topn = request.args.get('topn', 100)
    topn = int(topn)
    date = ts2datetime(end_ts)

    results = read_ds_topic_rank_results(topic, topn, date, windowsize)
    return json.dumps(results)

@mod.route('/ds_tr_rank/')
def ds_network_tr_rank():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts' ,'')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts) / Day
    topn = request.args.get('topn', 100)
    topn = int(topn)
    date = ts2datetime(end_ts)

    results = read_tr_rank_results(topic, topn, date, windowsize)
    print 'results1:', results[0]
    return json.dumps(results)

@mod.route('/ds_degree_centrality_rank/')
def ds_node_degree_rank():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts ) / Day
    date = ts2datetime(end_ts)
    topn = request.args.get('topn', 100)
    topn = int(topn)
    results = read_ds_degree_centrality_rank(topic, topn, date, windowsize)

    return json.dumps(results)
    

@mod.route('/degree_centrality_rank/')
def node_degree_rank():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts ) / Day
    date = ts2datetime(end_ts)
    topn = request.args.get('topn', 100)
    topn = int(topn)
    results = read_degree_centrality_rank(topic, topn, date, windowsize)
    return json.dumps(results)


@mod.route('/ds_betweeness_centrality_rank/')
def ds_betweeness_degree_rank():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts) / Day
    date = ts2datetime(end_ts)
    topn = request.args.get('topn', 100)
    topn = int(topn)
    results = read_ds_betweeness_centrality_rank(topic, topn, date, windowsize)
    return json.dumps(results)

@mod.route('/betweeness_centrality_rank/')
def betweeness_degree_rank():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts) / Day
    date = ts2datetime(end_ts)
    topn = request.args.get('topn', 100)
    topn = int(topn)
    results = read_betweeness_centrality_rank(topic, topn, date, windowsize)
    return json.dumps(results)

@mod.route('/ds_closeness_centrality_rank/')
def ds_closeness_centrality_rank():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts) / Day
    date = ts2datetime(end_ts)
    topn = request.args.get('topn', 100)
    topn = int(topn)
    results = read_ds_closeness_centrality_rank(topic, topn, date , windowsize)
    return json.dumps(results)

@mod.route('/closeness_centrality_rank/')
def closeness_centrality_rank():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    windowsize = (end_ts - start_ts ) / Day
    date = ts2datetime(end_ts)
    topn = request.args.get('topn', 100)
    topn = int(topn)
    results = read_closeness_centrality_rank(topic, topn, date, windowsize)
    return json.dumps(results)

def _utf8_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, 'utf-8')
'''
@mod.route('/origin/')
def origin_user():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts','')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts','')
    end_ts = int(end_ts)
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts ) / Day
    
    results = get_origin_user(topic, date, windowsize)
    rank = 0
    results_list = []
    for uid, result, reposts_count in results[:10]:
        rank += 1
        results_list.append([rank, result['uid'], result['name'], \
                           result['location'], result['count1'], result['count2'], \
                           result['pr'], result['dc'], result['bc'], result['cc']])
    

    return json.dumps(results_list)
'''   

@mod.route("/quota/")
def network_quota():
    quota = request.args.get('quota','')
    print 'quota:', quota
    topic = request.args.get('topic','')
    start_ts = request.args.get('start_ts','')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts','')
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts ) / Day
    network_type = request.args.get('network_type', '')
    print 'network_type:', network_type
    key = _utf8_unicode(topic)+'_'+str(date)+'_'+str(windowsize)+'_'+quota+'_'+network_type
    print 'key:', key
    try:
        ssdb = SSDB(SSDB_HOST, SSDB_PORT)
        value = ssdb.request('get',[key])
        print 'value.code:', value.code
        if value.code == 'ok' and value.data:
            print 'ok'
            response = make_response(value.data)
            return response
        return None
    except Exception, e:
        print e
        return None

@mod.route('/first_user/')
def network_first_user():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    results = time_top_user(topic, date, windowsize)
    #print 'view-len(results):', len(results)
    #print 'results[0]:', results[0]
    return json.dumps(results)

@mod.route('/domain_first_user/')
def network_domain_first_user():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    domain = request.args.get('domain','')
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    results = time_domain_top_user(topic, date, windowsize, domain)
    return json.dumps(results)
