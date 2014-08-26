# -*- coding: utf-8 -*-
import os
import sys
import json
import time
reload(sys)
sys.setdefaultencoding('utf-8')

from datetime import datetime
from SSDB import SSDB 
from case.global_config import SSDB_PORT, SSDB_HOST, db
from case.model import TopicStatus
from time_utils import datetimestr2ts, ts2datetime
from flask import Blueprint, url_for, render_template, request, abort, flash, make_response, session, redirect

from utils import read_topic_rank_results

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
    windowsize = (end_ts - start_ts+900)/Day
    windowsize = int(windowsize)
    #strat_ts = datetimestr2ts(start_ts)
    #end_ts = datetimestr2ts(end_ts)
    #start_ts = ts2datetime(start_ts)
    end = ts2datetime(end_ts)
  
    topic_status = get_topic_status(topic, start_ts, end_ts, module)

    if topic_status == COMPLETED_STATUS:  
        query_key =_utf8_unicode(topic) + '_' + str(end) + '_' + str(windowsize)
        key = str(query_key)
       
        try:
            ssdb = SSDB(SSDB_HOST, SSDB_PORT)
           
            results = ssdb.request('get', [key])
           
        
            if results.code == 'ok' and results.data:
               
               
            
                response = make_response(results.data)
                response.headers['Content-Type'] = 'text/xml'
                #return results.data
                return response
            return None
        except Exception, e:
            print e
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
    windowsize = (end_ts - start_ts+900) / Day
    topn = request.args.get('topn', 10)
    topn = int(topn)
    date = ts2datetime(end_ts)
    if windowsize > 7:
        rank_method = 'degreerank'
    else:
        rank_method = 'pagerank'

    results = read_topic_rank_results(topic, topn, rank_method, date, windowsize)
    return json.dumps(results)

def _utf8_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, 'utf-8')

@mod.route("/quota/")
def network_quota():
    quota = request.args.get('quota','')
    topic = request.args.get('topic','')
    start_ts = request.args.get('start_ts','')
    start_ts = int(start_ts)
    end_ts = request.args.get('end_ts','')
    end_ts = int(end_ts)
    date = ts2datetime(end_ts)
    windowsize = (end_ts - start_ts+900) / Day
    key = _utf8_unicode(topic)+'_'+str(date)+'_'+str(windowsize)+'_'+quota
    try:
        ssdb = SSDB(SSDB_HOST, SSDB_PORT)
        print 'ssdb yes'
        value = ssdb.request('get',[key])
        print 'value yes'
        if value.code == 'ok' and value.data:
            print 'code yes'
            print value.data
            response = make_response(value.data)
            return response
        return None
    except Exception, e:
        print e
        return None
