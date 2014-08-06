# -*- coding: utf-8 -*-
import os
import sys
import time
from datetime import datetime
from SSDB import SSDB 
from config import SSDB_PORT, SSDB_HOST, db
from Model import TopicStatus
from cron.identify import main 
from time_utils import datetimestr2ts

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


def get_topic_status(topic, start, end, module):
    '''判断该topic的状态
    '''s
    item = db.session.query(TopicStatus).filter(TopicStatus.topic==topic, \
                                                TopicStatus.start==start, \
                                                TopicStatus.end==end, \
                                                TopicStatus.module==module)
    if item:
        return item['status']
    else:
        return None


@mod.route('/identify/')
def network()
    topic = request.args.get('topic', '')
    topic_status = get_topic_status(topic, start_ts, end_ts, module)
    if topic_status == COMPLETED_STATUS:
        start_ts = request.args.get('start_ts', '')
        end_ts = request.args.get('end_ts', '')
        windowsize = (end_ts - start_ts)/Day
        windowsize = int(windowsize)
        strat_ts = datetimestr2ts(start_ts)
        end_ts = datetimestr2ts(end_ts)
        start_ts = ts2datetime(start_ts)
        end_ts = ts2datetime(end_ts)
        query_key =_utf8_unicode(topic) + '_' + str(end_ts) + '_' + str(windowsize)
        try:
            ssdb = SSDB(SSDB_HOST, SSDB_PORT)
            results = ssdb.request('get', [key])
            if results.code == 'ok' and result.data:
                return result.data
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
        
    
