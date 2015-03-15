#-*- coding:utf-8 -*-
import csv
import json
import pymongo
from flask import Blueprint , url_for, render_template, request, abort, flash, make_response, session, redirect

from case.propagate.read_quota import ReadPropagate, ReadPropagateKeywords
from case.propagate.peak_detection import detect_peaks
from case.propagate.read_quota_news import ReadPropagateNews

from case.identify.first_user import read_table_fu
from case.identify.trend_user import read_trend_user_table
from case.identify.utils import read_topic_rank_results

from case.evolution.city_count import Pcount

from case.moodlens.counts import  search_topic_counts
from case.moodlens.keywords import search_topic_keywords
from case.moodlens.peak_detection import detect_peaks

from case.time_utils import ts2datetime, datetime2ts, ts2date
from case.global_config import MONGODB_HOST, MONGODB_PORT
from util import get_info_num, get_dynamic_mongo, json2str

conn = pymongo.Connection(host=MONGODB_HOST, port=MONGODB_PORT)
mongodb = conn['54api_weibo_v2']
#collection = 'master_timeline_topic'

sentiment_class = {'news': u'中性', 'happy': u'积极', 'sad':u'悲伤', 'angry':u'愤怒'}
Fifteenminutes = 15 * 60
Hour = 60 * 60
Day = 3600 * 24
MinInterval = Fifteenminutes
During = Day
mtype_kv = {'origin':1, 'comment':2, 'forward':3}
emotions_kv = {'happy': 1, 'angry': 2, 'sad': 3, 'news': 4}
excel_line = ['topic_id', 'topic_status', 'topic_name', 'propagate_keywords' ,'start_ts', 'end_ts', 'topic_area',\
                     'topic_subject', 'identify_firstuser', 'identify_trendpusher', 'identify_pagerank',\
                     'moodlens_sentiment', 'topic_abstract', 'propagate_peak', 'propagate_peak_news']

mod = Blueprint('dataout', __name__, url_prefix='/dataout')

def get_propagate_peak(topic, start_ts, end_ts):
    lis = []
    ts_lis = []
    total_days = (end_ts - start_ts) / During
    for i in range(total_days+1):
        ts = start_ts + During * i
        count = 0
        for k, v in mtype_kv.iteritems():
            dcount = ReadPropagate(topic, ts, During, v)
            if dcount:
                count += sum(dcount['dcount'].values())
        lis.append(float(count))
        ts_lis.append(ts2date(ts))

    if not lis or not len(lis):
        return {}

    new_zeros = detect_peaks(lis)
    time_lis = {}
    for idx, point_idx in enumerate(new_zeros):
        timestamp = ts_lis[point_idx]
        time_lis[idx] = {
            'ts': timestamp,
            'title': 'E'+str(idx)
            }
    return {'ts':ts_lis, 'count_list':lis, 'peak': time_lis}

def get_propagate_peak_news(topic, start_ts, end_ts):
    lis = []
    ts_lis = []
    total_days = (end_ts - start_ts) / During
    for i in range(total_days+1):
        ts = start_ts + During * i
        count = 0
        for k, v in mtype_kv.iteritems():
            dcount = ReadPropagateNews(topic, ts, During, v)
            if dcount:
                count += sum(dcount['dcount'].values())
        lis.append(float(count))
        ts_lis.append(ts2date(ts))

    if not lis or not len(lis):
        return {}

    new_zeros = detect_peaks(lis)
    time_lis = {}
    for idx, point_idx in enumerate(new_zeros):
        timestamp = ts_lis[point_idx]
        time_lis[idx] = {
            'ts': timestamp,
            'title': 'E'+str(idx)
            }
    return {'ts':ts_lis, 'count_list':lis, 'peak': time_lis}

def get_propagate_keywords(topic, start_ts, end_ts):
    results = {}
    time_range = end_ts - start_ts
    limit = 50
    for k, v in mtype_kv.iteritems():
        m_results = ReadPropagateKeywords(topic, end_ts, time_range, v, limit)
        if not m_results:
            return {}
        for keyword, count in m_results.iteritems():
            try:
                results[keyword] += count
            except:
                results[keyword] = count

    return results

def get_identify_firstuser(topic, start_ts, end_ts):
    results = []
    windowsize = (end_ts - start_ts) / Day
    date = ts2datetime(end_ts)
    top_n = 20
    firstuser_table = read_table_fu(topic, date, windowsize, top_n)
    if len(firstuser_table)==1:
        return []
    results = firstuser_table[0]
    
    return results

def get_identify_trendpusher(topic, start_ts, end_ts):
    results = []
    windowsize = (end_ts - start_ts) / Day
    date = ts2datetime(end_ts)
    trenduser_table = read_trend_user_table(topic, date, windowsize)
    if not trenduser_table:
        return []
    results = trenduser_table[1][1:]

    return results

def get_identify_pagerank(topic, start_ts, end_ts):
    results = {}
    topn = 10
    rank_method = 'spark_pagerank'
    domain = 'all'
    windowsize = (end_ts - start_ts) / Day
    date = ts2datetime(end_ts)
    results = read_topic_rank_results(topic, topn, rank_method, date, windowsize, domain)
    
    return results

def get_evolution_topcity(topic, start_ts, end_ts):
    results = []
    stylenum = 4
    during = end_ts - start_ts
    first_item, pcount = Pcount(end_ts, during, stylenum, topic, unit=MinInterval)
    sort_pcount = sorted(pcount.items(), key=lambda x:x[1], reverse=True)
    if len(sort_pcount)>=10:
        results = sort_pcount[:10]
    else:
        results = sort_pcount
        
    return results

def get_moodlens_sentiment(topic, start_ts, end_ts):
    results = {}
    during = end_ts - start_ts
    domain = None
    for k, v in emotions_kv.iteritems():
        results[k] = search_topic_counts(end_ts, during, v, MinInterval,topic, domain, '1')[1]
    
    return results

def get_moodlens_keywords(topic, start_ts, end_ts):
    results = {}
    limit = 50
    top = 10
    emotion = 'global'
    keywords_data = {}
    emotion_result = {}
    domain = None
    during = end_ts - start_ts
    for k, v in emotions_kv.iteritems():
        emotion_results = search_topic_keywords(end_ts, during, v, MinInterval, top, limit, topic, domain, '1')
        keywords_data = {}

        for keyword, count in emotion_results.iteritems():
            try:
                keywords_data[keyword] += count
            except:
                keywords_data[keyword] = count

        kcount_tuple = sorted(keywords_data.iteritems(), key=lambda (k, v): v, reverse=True)
        for w, c in kcount_tuple[len(kcount_tuple)-top:]:
            results[w] = c
        emotion_results[k] = results

    return emotion_results

def get_moodlens_peak(topic, start_ts, end_ts):
    results = []
    time_range = end_ts - start_ts
    windowsize = time_range / Day
    if windowsize * Day != time_range:
        windowsize += 1
    interval = windowsize
    during = Day
    domain = None
    ts_list = []
    time_lis = {}
    emotion_list_dict = {} # emotion_list_dict = {'happy':[1,2,3...], 'sad':[2,4,3...], 'angry':[...], 'news':[...]}
    for i in range(interval, 0 ,-1):
        end = end_ts - i * during
        ts_list.append(end)

        for k, v in emotions_kv.iteritems():
            try:
                emotion_list_dict[k].append(search_topic_counts(end, during, v, MinInterval,topic, domain, '1')[1])
            except:
                emotion_list_dict[k] = [search_topic_counts(end, during, v, MinInterval, topic, domain, '1')[1]]
    results = {}
    title = {'happy':'A', 'angry':'B', 'sad':'C', 'news':'D'}
    for senti in emotion_list_dict:
        lis = emotion_list_dict[senti]
        new_zeros = detect_peaks(lis)
        for idx, point_idx in enumerate(new_zeros):
            ts = ts_list[point_idx]
            end_ts = ts
            v = senti

            time_lis[idx] = {
                'ts': end_ts,
                'title': title[senti] + str(idx)
                }
        results[senti] = time_lis

    return {'ts':ts_list, 'count':emotion_list_dict ,'peak':results}

# case下没有该数据,opinion_news中得数据
'''
from opinion.Database import Event, EventManager
em = EventManager()
'''
def get_news_fishbone(topic, start_ts, end_ts):
    results = {} # results = {'dates':dates, 'name':topic_name, 'type':'eventRiver', 'weight':total_weight, 'eventList':subeventlist}
    during = end_ts - start_ts
    sort = 'tfidf'
    '''
    topic_id = em.getEventIDByName(topic)
    event = Event(topicid)
    subeventlist, dates, total_weight = event.getEventRiverData(start_ts, end_ts, sort=sort)
    '''
    return results

def get_topic_abstract(topic_name, start_ts, end_ts, sentiment, keywords, city):
    results = {} # 没有数据--js中写进去的数据
    # 事件发生时间、事件发生地点
    # compute: 舆情信息起止时间、参与人数、舆情信息累积数、参与人群集中地点、关键词、网民情绪占比
    start_date = ts2datetime(start_ts)
    results['info_start'] = start_date
    end_date = ts2datetime(end_ts)
    results['info_end'] = end_date
    user_count, weibo_count = get_info_num(topic_name)
    results['user_count'] = user_count
    results['weibo_count'] = weibo_count
    sentiment_allcount = 0
    sentiment_ratio = {}
    for sentiment_item in sentiment:
        sentiment_allcount += sentiment[sentiment_item]
    for item in sentiment:
        sentiment_ratio[item] = sentiment[item] / (float(sentiment_allcount))
    results['sentiment_ratio'] = sentiment_ratio
    sort_keywords = sorted(keywords.iteritems(), key=lambda x:x[1], reverse=True)
    results['keywords'] = sort_keywords
    city_list = []
    for k in city:
        city_list.append(k[0])
    results['city'] = city_list
    abstract = creat_abstract(results)
    return abstract

def creat_abstract(results):
    abstract = u'该事件的舆情信息起始于' + results['info_start'] + u'，终止于' + results['info_end']
    abstract += u'，共' + str(results['user_count']).decode('utf-8') + u'人参与信息发布与传播，舆情信息累计' + str(results['weibo_count']).decode('utf-8') + u'条。'
    abstract += u'参与人群集中于'
    for index in range(len(results['city'])):
        if index==(len(results['city'])-1):
            abstract += results['city'][index]
            abstract += '。'
        else:
            abstract += results['city'][index]
            abstract += '，'
    abstract += u'前10个关键词是：'
    for index in range(len(results['keywords'])):
        if index==(len(results['city'])-1):
            abstract += results['keywords'][index][0]
            abstract += '。'
        else:
            abstract += results['keywords'][index][0]
            abstract += '，'
    abstract += u'网民的情绪分布情况为：'
    count = 0
    for senti in sentiment_class:
        count += 1
        ratio = results['sentiment_ratio'][senti]
        senti_zh = sentiment_class[senti]
        if count==4:
            abstract += senti_zh
            abstract += '：'
            abstract += str(round(ratio * 100, 2))
            abstract += '%。'
        else:
            abstract += senti_zh
            abstract += '：'
            abstract += str(round(ratio * 100, 2))
            abstract += '%，'
    return {'abstract':abstract}

@mod.route('/get_topic_list/')
def get_topic_list():
    topic_collection = mongodb.master_timeline_topic
    topic_items = topic_collection.find()
    topic_list = []
    if not topic_items:
        print 'there is no topic'
    else:
        for item in topic_items:
            topic_name = item['name']
            topic_list.append(topic_name)

    return json.dumps(topic_list)
        
@mod.route('/get_data_out/')
def get_data():
    # start_ts 和 end_ts 为舆情信息的起止时间，均为整天数的时间
    topic = request.args.get('topic', '')
    start_ts = request.args.get('start_ts', '')
    end_ts = request.args.get('end_ts', '')
    start_ts = int(start_ts)
    end_ts = int(end_ts)
    result = {}
    result['propagate_peak'] = get_propagate_peak(topic, start_ts, end_ts)
    result['propagate_keywords'] = get_propagate_keywords(topic, start_ts, end_ts)
    result['identify_firstuser'] = get_identify_firstuser(topic, start_ts, end_ts)
    result['identify_trendpusher'] = get_identify_trendpusher(topic, start_ts, end_ts)
    result['identify_pagerank'] = get_identify_pagerank(topic, start_ts, end_ts)
    result['evolution_topcity'] = get_evolution_topcity(topic, start_ts, end_ts)
    result['moodlens_sentiment'] = get_moodlens_sentiment(topic, start_ts, end_ts)
    result['moodlens_keywords'] = get_moodlens_keywords(topic, start_ts, end_ts)
    result['moodlens_peak'] = get_moodlens_peak(topic, start_ts, end_ts)
    #result['news_fishbone'] = get_news_fishbone()
    result['topic_abstract'] = get_topic_abstract(topic, start_ts, end_ts, result['moodlens_sentiment'], result['propagate_keywords'], result['evolution_topcity'])
    return json.dumps(result)

def get_topic_data(topic, start_ts, end_ts):
    result = {}
    if topic=='APEC':
        result['topic_name'] = 'APEC2014'
    else:
        result['topic_name'] = topic
    result['start_ts'] = ts2datetime(start_ts)
    result['end_ts'] = ts2datetime(end_ts - 3600 * 24)
    result['propagate_peak'] = get_propagate_peak(topic, start_ts, end_ts)
    result['propagate_peak_news'] = get_propagate_peak_news(topic, start_ts, end_ts)
    propagate_keywords = get_propagate_keywords(topic, start_ts, end_ts)
    result['propagate_keywords'] = json2str('propagate_keywords' , propagate_keywords)
    identify_firstuser = get_identify_firstuser(topic, start_ts, end_ts)
    result['identify_firstuser'] = json2str('identify_firstuser', identify_firstuser)
    identify_trendpusher = get_identify_trendpusher(topic, start_ts, end_ts)
    result['identify_trendpusher'] = json2str('identify_trendpusher', identify_trendpusher)
    identify_pagerank = get_identify_pagerank(topic, start_ts, end_ts)
    result['identify_pagerank'] = json2str('identify_pagerank', identify_pagerank)
    result['evolution_topcity'] = get_evolution_topcity(topic, start_ts, end_ts)
    result['moodlens_sentiment'] = get_moodlens_sentiment(topic, start_ts, end_ts)
    result['moodlens_keywords'] = get_moodlens_keywords(topic, start_ts, end_ts)
    result['moodlens_peak'] = get_moodlens_peak(topic, start_ts, end_ts)
    #result['news_fishbone'] = get_news_fishbone()
    topic_abstract = get_topic_abstract(topic, start_ts, end_ts, result['moodlens_sentiment'], propagate_keywords, result['evolution_topcity'])
    result['topic_abstract'] = topic_abstract['abstract']
    return result

@mod.route('/get_all_data/')
def get_all_data():
    topic_list = [u'东盟,博览会', u'全军政治工作会议', u'外滩踩踏', u'高校思想宣传', u'APEC', u'张灵甫遗骨疑似被埋羊圈']
    time_range_list = [('2013-09-08', 6), ('2014-11-16', 17), ('2015-01-10', 10), ('2015-02-01', 9), ('2014-11-20', 15), ('2015-02-02', 10)]
    result = {}
    result_list = []
    for i in range(len(topic_list)):
        topic_name = topic_list[i]
        end_date = time_range_list[i][0]
        windowsize = time_range_list[i][1]
        end_ts = datetime2ts(end_date)
        start_ts = end_ts - Day * windowsize
        print 'start compute topic:', topic_name
        result = get_topic_data(topic_name, start_ts, end_ts)
        result_list.append(result)
        
    return json.dumps(result_list)

def write_topic_excel(topic, start_ts, end_ts):
    result = get_topic_data(topic, start_ts, end_ts)
    result['topic_id'] = get_dynamic_mongo(topic)
    result['topic_status'] = '1'
    result['topic_area'] = u'北京'
    result['topic_subject'] = u'习近平'
    identify_firstuser = get_identify_firstuser(topic, start_ts, end_ts)
    result['identify_firstuser'] = json2str('identify_firstuser', identify_firstuser)
    if topic==u'APEC':
        topic = u'APEC2014'
    csvfile = file(topic + '.csv', 'wb')
    count = 0
    
    for item in excel_line:
        line = [item]
        write_cell = result[item]
        line.append(write_cell)
        count += 1
        writer = csv.writer(csvfile)
        #writer.writerow(excel_line)
        writer.writerow(line)
    csvfile.close()

@mod.route('/save_csv/')
def save_csv():
    topic_list = [u'东盟,博览会', u'全军政治工作会议', u'外滩踩踏', u'高校思想宣传', \
                       u'APEC', u'张灵甫遗骨疑似被埋羊圈']
    time_range_list = [('2013-09-02', '2013-09-07'), ('2014-10-31', '2014-11-15'), ('2014-12-31', '2015-01-09'),\
                                 ('2015-01-23', '2015-02-02'), ('2014-11-01', '2014-11-10'), ('2015-01-23', '2015-02-02')]
    for i in range(len(topic_list)):
        topic = topic_list[i]
        start_date = time_range_list[i][0]
        start_ts = datetime2ts(start_date)
        end_date = time_range_list[i][1]
        end_ts = datetime2ts(end_date) + 3600 * 24
        write_topic_excel(topic, start_ts, end_ts)
        print 'success write topic:', topic
    return 'success save'

