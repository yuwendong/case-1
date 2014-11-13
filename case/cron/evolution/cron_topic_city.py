# -*- coding: utf-8 -*-

import sys
import IP   #引入IP，对'geo'字段进行解析
import json
import datetime
from topics import _all_topics
sys.path.append('../')
from time_utils import datetime2ts, ts2HourlyTime
from dynamic_xapian_weibo import getXapianWeiboByDate, getXapianWeiboByDuration, getXapianWeiboByTopic #获取一定时间段内的微博
from config import mtype_kv, db
from model import CityTopicCount


Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24


RESP_ITER_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'bmiddle_pic', 'geo', 'comments_count', 'sentiment', 'terms']
fields_list=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', 'comments_count', 'sentiment', 'topics', 'message_type', 'terms']


def geo2city(geo): #将weibo中的'geo'字段解析为地址
    try:
        city=IP.find(str(geo))
        #print city
        if city:
            city=city.encode('utf-8')
        else:
            return None
    except Exception,e:
        print e
        return None
    
    return city



def save_rt_results(topic, mtype, results, during, first_item):
    for k, v in results.iteritems():
        mtype = k
        ts, ccount = v
        item = CityTopicCount(topic, during, ts, mtype, json.dumps(ccount), json.dumps(first_item))
        item_exist = db.session.query(CityTopicCount).filter(CityTopicCount.topic==topic, \
                                                                            CityTopicCount.range==during, \
                                                                            CityTopicCount.end==ts, \
                                                                            CityTopicCount.mtype==mtype).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
    db.session.commit()


def cityCronTopic(topic, xapian_search_weibo, start_ts, over_ts, during=Fifteenminutes):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)

        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        topics = topic.strip().split(',')
        for i in range(interval, 0, -1):
            mtype_ccount = {}  # mtype为message_type，ccount为{city：count}

            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            # print begin_ts, end_ts, 'topic %s starts calculate' % topic.encode('utf-8')

            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
                '$or': [],
            }

            for topic in topics:
                query_dict['$or'].append({'topics': topic})   #由于topic目前没有数据，所以测试阶段使用text中查询topic
            ''' 
            count, weibo_results = xapian_search_weibo.search(query={'message_type': 1}, fields=fields_list)
            for r in weibo_results():
                print datetime.datetime.utcfromtimestamp(r['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            '''
            for k, v in mtype_kv.iteritems():
                ccount={}
                first_timestamp = end_ts
                first_item = {}
                query_dict['message_type'] = v
                count,weibo_results = xapian_search_weibo.search(query=query_dict, fields=fields_list)# weibo_results是在指定时间段、topic、message_type的微博匹配集
                #for r in weibo_results():
                #    print r['_id']
                for weibo_result in weibo_results():
                    if (weibo_result['timestamp'] <= first_timestamp ):
                        first_timestamp = weibo_result['timestamp']
                        first_item = weibo_result

                    #print weibo_result['geo']
                    if geo2city(weibo_result['geo']):
                        try:
                            ccount[geo2city(weibo_result['geo'])] += 1   
                        except KeyError:
                            ccount[geo2city(weibo_result['geo'])] = 1    
                    else:
                        continue
                mtype_ccount[v] = [end_ts, ccount]
                #print mtype_ccount[v]
                #print '%s %s saved message_type city_count' % (begin_ts, end_ts)
                save_rt_results(topic,v, mtype_ccount, during, first_item)



def cal_topic_citycount_by_date(topic, datestr_list, duration):
    start_ts = datetime2ts(datestr_list[0])
    end_ts = datetime2ts(datestr_list[-1]) + Day
    datestrlist = []
    xapian_search_weibo = getXapianWeiboByTopic(topic)
    print 'step2----'
    if xapian_search_weibo:
        cityCronTopic(topic, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=duration)
   

def worker(topic, datestr_list):
    print 'topic: ', topic.encode('utf8'), 'datestr:', datestr_list, 'Fifteenminutes: '
    cal_topic_citycount_by_date(topic, datestr_list, Fifteenminutes)


if __name__ == '__main__':
    datestr = '2013-09-01'
    datestr_list = ['2013-09-02', '2013-09-03', '2013-09-04',\
                    '2013-09-05', '2013-09-06', '2013-09-07']
    # xapian_search_weibo = getXapianWeiboByDate(datestr)
    topic = u"东盟,博览会"
    worker(topic,datestr_list)
