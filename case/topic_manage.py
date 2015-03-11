#-*- coding:utf-8 -*-

from case.global_utils import mongo
from case.time_utils import ts2datetimestr

def topics_name_start_end():
    """获取话题的名称、起始时间、终止时间
    """
    topics_list = []
    topic_collection = 'master_timeline_topic'
    results = mongo[topic_collection].find()
    for r in results:
        try:
            topics = (r['name'], ts2datetimestr(r['start']), ts2datetimestr(r['end']))
            topics_list.append(topics)
        except:
            pass

    return topics_list

