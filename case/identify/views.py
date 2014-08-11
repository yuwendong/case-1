# -*- coding: utf-8 -*-
import os
import sys
import json
import time
reload(sys)
sys.setdefaultencoding('utf-8')

from datetime import datetime
from SSDB import SSDB 
from config import SSDB_PORT, SSDB_HOST, db
from case.model import TopicStatus
from time_utils import datetimestr2ts, ts2datetime
from flask import Blueprint, url_for, render_template, request, abort, flash, make_response, session, redirect

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
    print 'item',item
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
    print 'end_ts', end
    topic_status = get_topic_status(topic, start_ts, end_ts, module)
    print 'status:', topic_status
    if topic_status == COMPLETED_STATUS:  
        query_key =_utf8_unicode(topic) + '_' + str(end) + '_' + str(windowsize)
        key = str(query_key)
        print 'key', key
        try:
            ssdb = SSDB(SSDB_HOST, SSDB_PORT)
            print 'ssdb yes'
            results = ssdb.request('get', [key])
            print 'results yes'
            print 'r-code', results.code
            if results.code == 'ok' and results.data:
                print 'code yes'
                print '--'*10
                print results.data
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

@mod.route("/quota/")
def network_quota():
    key = request.args.get('quota_key','')
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
