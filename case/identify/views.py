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
from utils import read_ds_topic_rank_results, read_ds_degree_centrality_rank ,\
                  read_ds_betweeness_centrality_rank, read_ds_closeness_centrality_rank
from first_user import time_top_user, time_domain_top_user,read_table_fu
from trend_user import read_trend_maker, read_trend_pusher, read_trend_user_table
from community_util import read_uid_weibos, read_uid_neighbors, read_uid_community
from weibo_ts import c_weibo_by_ts, n_weibo_by_ts
from news_utils import get_news_first_user, get_news_trend_maker, get_news_trend_pusher
from parameter import TOPK, Minute, Fifteenminutes, Hour, sixHour, Day,\
        module, NOT_CALC_STATUS, IN_CALC_STATUS, COMPLETED_STATUS

'''
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
'''
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


@mod.route("/trend_maker/")
def trend_makers():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    rank_method = request.args.get('rank_method', '') # content, timestamp,reposts_count, friends_count, statuses_count 
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    results = read_trend_maker(topic, date, windowsize, rank_method)
    #print 'trend_maker:',results
    return json.dumps(results)

@mod.route('/trend_pusher/')
def trend_pushers():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    rank_method = request.args.get('rank_method', '')
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    results = read_trend_pusher(topic, date, windowsize, rank_method)
    #print 'trend_pusher:', results
    return json.dumps(results)

@mod.route('/trend_user/')
def trend_user():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts','')
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    results = read_trend_user_table(topic,  date, windowsize)
    #print 'trend_user:', results 
    return json.dumps(results)
    
    
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
    domain = request.args.get('domain', 'all')
    date = ts2datetime(end_ts)
    rank_method = 'spark_pagerank'
    results = read_topic_rank_results(topic, topn, rank_method, date, windowsize, domain)
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
    domain = request.args.get('domain','all')
    date = ts2datetime(end_ts)
    rank_method = 'spark_pagerank'
    results = read_ds_topic_rank_results(topic, topn, date, windowsize, domain, rank_method)
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
    domain = request.args.get('domain', 'all')
    results = read_ds_degree_centrality_rank(topic, topn, date, windowsize, domain)

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
    domain = request.args.get('domain','all')
    results = read_degree_centrality_rank(topic, topn, date, windowsize, domain)
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
    domain = request.args.get('domain', 'all')
    results = read_ds_betweeness_centrality_rank(topic, topn, date, windowsize, domain)
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
    domain = request.args.get('domain', 'all')
    results = read_betweeness_centrality_rank(topic, topn, date, windowsize, domain)
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
    domain = request.args.get('domain', 'all')
    results = read_ds_closeness_centrality_rank(topic, topn, date , windowsize, domain)
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
    domain = request.args.get('domain', 'all')
    results = read_closeness_centrality_rank(topic, topn, date, windowsize, domain)
    return json.dumps(results)

def _utf8_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, 'utf-8')  

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
    rank_method = request.args.get('rank_method','')
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    results = time_top_user(topic, date, windowsize, rank_method)
    #print 'view-len(results):', len(results)
    #print 'results[0]:', results[0]
    return json.dumps(results)

@mod.route('/table_first_user/')
def table_fu():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts','')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts','')
    end_ts = int(end_ts)
    top_n = request.args.get('topn','')
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    results = read_table_fu(topic, date, windowsize, top_n)

    return json.dumps(results)

@mod.route('/domain_first_user/')
def network_domain_first_user():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    domain = request.args.get('domain','')
    rank_method = request.args.get('rank_method','')
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    results = time_domain_top_user(topic, date, windowsize, domain, rank_method)
    return json.dumps(results)


@mod.route('/uid_weibo/')
def network_uid_weibos():
    uid = request.args.get('uid', '')
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    results = read_uid_weibos(topic, date, windowsize, uid)
    return json.dumps(results)

@mod.route('/uid_neighbor/')
def network_uid_neighbor():
    uid = request.args.get('uid', '')
    #print 'uid:', uid
    uid = int(uid)
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    network_type = request.args.get('network_type','source_graph')
    # network_type="source_graph" or 'direct_superior_graph'
    results = read_uid_neighbors(topic, date, windowsize , uid, network_type)
    return json.dumps(results)

@mod.route('/uid_community/')
def network_uid_community():
    uid = request.args.get('uid', '')
    # uid 在网络节点以str形式存放
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    network_type = request.args.get('network_type', 'source_graph')
    community_id = request.args.get('community_id', '')
    community_id = int(community_id)
    results = read_uid_community(topic, date, windowsize, uid, network_type, community_id)
    return json.dumps(results)

@mod.route('/uid_community_by_ts/')
def community_weibo_by_ts():
    uid = request.args.get('uid', '')
    # uid 在网络节点以str形式存放
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    network_type = request.args.get('network_type', 'source_graph')
    community_id = request.args.get('community_id', '')
    #print 'community_id:', community_id
    community_id = int(community_id)
    rank_method = request.args.get('rank_method', 'timestamp')
    results = c_weibo_by_ts(topic, date, windowsize, uid, network_type, community_id, rank_method)
    return json.dumps(results)

@mod.route('/uid_neighbor_by_ts/')
def neighbor_weibo_by_ts():
    uid = request.args.get('uid', '')
    # uid 在网络节点以str形式存放
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts) / Day
    network_type = request.args.get('network_type', 'source_graph')
    rank_method = request.args.get('rank_method', 'timestamp')
    results = n_weibo_by_ts(topic, date, windowsize, uid, network_type, rank_method)
    return json.dumps(results)

@mod.route('/news_first_user/')
def news_first_user():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    # rank_method:timestamp(default), weight
    rank_method = request.args.get('rank_method', 'timestamp')
    news_skip = request.args.get('news_skip', 0)
    news_skip = int(news_skip)
    news_limit_count = request.args.get('news_limit_count', 10)
    news_limit_count = int(news_limit_count)
    results = get_news_first_user(topic, start_ts, end_ts, rank_method, news_skip, news_limit_count)

    return json.dumps(results)

@mod.route('/news_trend_maker/')
def news_trend_maker():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    #rank_method:weight(default), timestamp
    rank_method = request.args.get('rank_method', 'weight')
    news_skip = request.args.get('news_skip', '0')
    news_skip = int(news_skip)
    news_limit_count = request.args.get('news_limit_count', '10')
    news_limit_count = int(news_limit_count)
    results = get_news_trend_maker(topic, start_ts, end_ts, rank_method, news_skip, news_limit_count)

    return json.dumps(results)

@mod.route('/news_trend_pusher/')
def news_trend_pusher():
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts', '')
    end_ts = int(end_ts)
    # rank_method:comment_count(default), timestamp, weight
    rank_method = request.args.get('rank_method', 'comments_count')
    news_skip = request.args.get('news_skip', '0')
    #print 'news_trend_pusher news_skip:', news_skip
    news_skip = int(news_skip)
    news_limit_count = request.args.get('news_limit_count', '10')
    news_limit_count = int(news_limit_count)
    results = get_news_trend_pusher(topic, start_ts, end_ts, rank_method, news_skip, news_limit_count)

    return json.dumps(results)
    

