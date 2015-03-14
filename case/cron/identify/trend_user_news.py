# -*- coding: utf-8 -*-
import sys
import json
import pymongo
#from config import db
#from model import TrendMakerNews, TrendPusherNews, PropagateCountNews
from peak_detection import detect_peaks
from bottom_detect import detect_bottom
from early_join_news import get_filter_dict
from time_utils import ts2date, ts2datetime, datetime2ts
from parameter import During, pusher_during, unit, interval_count_during ,\
                  maker_news_count, pusher_news_count
from parameter import Minute, Fifteenminutes, Hour, sixHour, Day
from news_keywords import  cut_news, get_news_keywords, get_news_weight, get_top_weight_news
sys.path.append('../../')
from global_config import db
from model import TrendMakerNews, TrendPusherNews, PropagateCountNews
'''
Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
During = Day # 计算波峰波谷的时间粒度
pusher_during = Hour # 计算推动者的时间粒度
unit = 900
'''
def trend_user(topic, start_ts, end_ts, news_collection, comment_collection):
    '''利用时间分析部分的计算结果
    '''
    ts_list, count_list = get_interval_count(topic, start_ts, end_ts)
    # 波峰
    new_peaks = detect_peaks(count_list)
    print 'news_peaks:', new_peaks
    # 波谷
    new_bottom = detect_bottom(count_list)
    print 'news_bottom:', new_bottom
    # trend_maker
    trend_maker = get_maker(topic, new_peaks, new_bottom, ts_list, news_collection)
    print 'len(trend_maker):', len(trend_maker)
    # trend_pusher
    trend_pusher = get_pusher(topic, new_peaks, new_bottom, ts_list, news_collection, comment_collection)
    print 'len(trend_pusher):', len(trend_pusher)

    save_trend_maker(topic, start_ts, end_ts, trend_maker)
    save_trend_pusher(topic, start_ts, end_ts, trend_pusher)
    
#趋势制造者----以weight作为排序标准,weight是以cover关键词的个数确定的
def get_maker(topic, new_peaks, new_bottom, ts_list, collection):
    begin_ts = ts_list[new_bottom[0]]
    end_ts = ts_list[new_peaks[0]]
    print 'get_maker news_bottom:', new_bottom[0]
    print 'get_maker news_peak:', new_peaks[0]
    print 'get_maker ts_list:', ts2date(ts_list[0])
    print 'get_maker start_ts:', ts2date(begin_ts)
    print 'get_maker end_ts:', ts2date(end_ts)
    if begin_ts > end_ts:
        begin_ts = ts_list[0]
    
    begin_ts = begin_ts - Hour
    filter_dict = get_filter_dict()
    query_dict = {'timestamp':{'$gte':begin_ts, '$lte':end_ts}}
    '''
    maker_list = collection.find(query_dict, filter_dict).sort('weight').limit(maker_news_count)
    if not maker_list:
        return []
    else:
        return maker_list
    '''
    input_news_list = collection.find(query_dict, filter_dict)
    # 第一个波段内所有新闻进行分词
    news_cut_list = cut_news(input_news_list)
    # 计算top50的关键词
    keywords_list = get_news_keywords(news_cut_list)
    # 计算波段内新闻的关键词占比weight
    weight_list = get_news_weight(news_cut_list, keywords_list)
    # 排序获取weight前20的news
    maker_list = get_top_weight_news(weight_list)
    
    if not maker_list:
        return []
    else:
        return maker_list

# 新闻数作为推动者的指标
def get_pusher(topic, new_peaks, new_bottom, ts_list, news_collection, comment_collection):
    start_ts = ts_list[new_bottom[0]]
    end_ts = ts_list[new_peaks[0]]
    p_ts_list = []
    results = []
    if start_ts > end_ts:
        start_ts = ts_list[0]

    interval = (end_ts - start_ts) / pusher_during
    for i in range(interval, 0, -1):
        begin_ts = end_ts - pusher_during * i
        over_ts = begin_ts + pusher_during
        p_ts_list.append(over_ts)
        items = db.session.query(PropagateCountNews).filter(PropagateCountNews.topic==topic ,\
                                                            PropagateCountNews.end<=over_ts ,\
                                                            PropagateCountNews.end>begin_ts ,\
                                                            PropagateCountNews.range==unit).all()
        if items:
            result = Merge_propagate(items)
        else:
            result = 0
        results.append(float(result))

    max_k_timestamp = get_max_k_timestamp(results , p_ts_list)

    start = max_k_timestamp
    end = max_k_timestamp + pusher_during
    query_dict = {'timestamp':{'$gte':start, '$lte':end}}
    #pusher的排序两种方案：相同新闻数/新闻评论数---前者没有数据，忽略
    # 下面按照相同新闻数进行倒叙排列
    #max_k_timestamp_news = news_collection.find(query_dict, filter_fields).sort({'same_news_num':-1})
    # 按照新闻评论数进行排序
    max_k_timestamp_news = sort_news_by_comment(query_dict, news_collection, comment_collection)
    trend_pusher = max_k_timestamp_news[:maker_news_count]
    
    return trend_pusher

# 利用时间分析部分的计算结果
def get_interval_count(topic, start_ts, end_ts):
    results = [0]
    ts_list = []
    #unit = 900
    #during = Day
    during = interval_count_during
    start_ts = datetime2ts(ts2datetime(start_ts))
    ts_list.append(start_ts)
    #end_ts = datetime2ts(ts2datetime(end_ts))
    # deal with the time is not the whole day
    print 'before deal end_ts:', ts2date(end_ts)
    if end_ts - datetime2ts(ts2datetime(end_ts))!= 0:
        end_ts = datetime2ts(ts2datetime(end_ts)) + 3600 * 24
    print 'get_interval_count start_ts:', ts2date(start_ts)
    print 'get_interval_count end_ts:', ts2date(end_ts)

    windowsize = (end_ts - start_ts) / Day
    interval = (end_ts - start_ts) / During
    for i in range(interval, 0, -1):
        begin_ts = end_ts - during * i
        over_ts = begin_ts + during
        ts_list.append(over_ts)

        items = db.session.query(PropagateCountNews).filter(PropagateCountNews.topic==topic ,\
                                                                                              PropagateCountNews.end<=over_ts ,\
                                                                                              PropagateCountNews.end>begin_ts ,\
                                                                                              PropagateCountNews.range==unit).all()
        if items:
            result = Merge_propagate(items)
        else:
            result = 0
        results.append(float(result))

    return ts_list, results

def save_trend_maker(topic, start_ts, end_ts, trend_maker):
    # deal with the start_ts/end_ts is not the whole day
    if start_ts - datetime2ts(ts2datetime(start_ts)) != 0:
        start_ts = datetime2ts(ts2datetime(start_ts))
    if end_ts - datetime2ts(ts2datetime(end_ts)) != 0:
        end_ts = datetime2ts(ts2datetime(end_ts)) + 3600 * 24
    items_exist = db.session.query(TrendMakerNews).filter(TrendMakerNews.topic==topic ,\
                                                          TrendMakerNews.start_ts==start_ts ,\
                                                          TrendMakerNews.end_ts==end_ts).all()
    if items_exist:
        for item in items_exist:
            db.session.delete(item)
        db.session.commit()
    # 媒体名称去重
    media_list = []
    for maker in trend_maker:
        if len(media_list)==maker_news_count:
            break
        meida_name = ''
        transmit_name = maker['transmit_name']
        source_from_name = maker['source_from_name']
        if not transmit_name:
            media_name = source_from_name
        else:
            media_name = transmit_name
        if media_name in media_list:
            continue
        media_list.append(media_name)
        
        news_id = maker['id']
        timestamp = maker['timestamp']
        #same_news_num = maker['same_news_num']
        weight = maker['weight'] # cover关键词得到的权重--由语义部分计算而得
        news_info = json.dumps(maker)
        item = TrendMakerNews(topic, start_ts, end_ts, news_id, timestamp, weight, news_info)
        db.session.add(item)
    db.session.commit()

def save_trend_pusher(topic, start_ts, end_ts, trend_pusher):
    #deal with the start_ts/end_ts is not the whole day
    if start_ts - datetime2ts(ts2datetime(start_ts)) != 0:
        start_ts = datetime2ts(ts2datetime(start_ts))
    if end_ts - datetime2ts(ts2datetime(end_ts)) != 0:
        end_ts = datetime2ts(ts2datetime(end_ts)) + 3600 * 24
    items_exist = db.session.query(TrendPusherNews).filter(TrendPusherNews.topic==topic ,\
                                                           TrendPusherNews.start_ts==start_ts ,\
                                                           TrendPusherNews.end_ts==end_ts).all()
    if items_exist:
        for item in items_exist:
            db.session.delete(item)
        db.session.commit()
    # 媒体名称去重
    media_list = []
    for pusher in trend_pusher:
        if len(media_list)==pusher_news_count:
            break
        media_name = ''
        transmit_name = pusher['transmit_name']
        source_from_name = pusher['source_from_name']
        if not transmit_name:
            media_name = source_from_name
        else:
            media_name = source_from_name
        if media_name in media_list:
            continue
        media_list.append(media_name)
        
        news_id = pusher['id']
        timestamp = pusher['timestamp']
        comments_count = pusher['comments_count']
        news_info = json.dumps(pusher)
        item = TrendPusherNews(topic, start_ts, end_ts, news_id, timestamp, comments_count ,news_info)
        db.session.add(item)
    db.session.commit()

# 如果新闻在时间分析中具有某种划分方法，merge还需要进行修改
def Merge_propagate(items):
    result = 0
    
    for item in items:
        dcount = json.loads(item.dcount)
        result += dcount['other']
    #print 'merge:', result
    return result

# 最大斜率
def get_max_k_timestamp(results, p_ts_list):
    # 最大斜率 且增量要大于平均增量
    length = len(results)
    smooth_results = []
    incre_dict = {}
    k_dict = {}
    # 平滑处理
    for i in range(length):
        if i>1:
            smooth = sum(results[i-2:i+1]) / 3.0
            smooth_results.append(smooth)
            #print 'smooth_results:',i ,results[i-2:i+1], smooth_results
        l = len(smooth_results)
        if l>=2:
            k = (smooth_results[l-1] - smooth_results[l-2]) / Hour
            k_dict[l-1] = k

    #print 'smooth_results:', smooth_results
    sort_k_list = sorted(k_dict.items(), key=lambda c:c[1], reverse=True)
    #print 'sort_k_list:', sort_k_list
    smooth_length = len(smooth_results)
    all_average = 0
    for j in range(smooth_length):
        if j>0:
            incre = float(smooth_results[j] - smooth_results[j-1])
            all_average += incre
            incre_dict[j-1] = incre
    average_incre = all_average / len(incre_dict)    
    remove_list = []
    #print 'incre_dict:', incre_dict
    # 筛掉增量小于平均增量的
    for k in incre_dict:
        if incre_dict[k]<=average_incre:
            remove_list.append(k)
    after_remove_k_list = []
    for sort_k in sort_k_list:
        if not sort_k[0] in remove_list:
            index = sort_k[0]
            timestamp = p_ts_list[index+1]
            k_value = sort_k[1]
            after_remove_k_list.append((index+1, timestamp, k_value))
    max_k_timestamp = after_remove_k_list[0][1]
    #print 'after_remove_k_list:', after_remove_k_list
    print 'max_k_timestamp:', max_k_timestamp
    print 'max_k_timestamp:', ts2date(max_k_timestamp)
    return max_k_timestamp


def sort_news_by_comment(query_dict, news_collection, comment_collection):
    results = []
    filter_dict = get_filter_dict()
    news_no_comment = news_collection.find(query_dict, filter_dict)
    for news in news_no_comment:
        #print 'news:', news
        news_id = news['id']
        comment_query_dict = {'news_id': news_id}
        news_comment = comment_collection.find(comment_query_dict) # 一条新闻对应的所有评论
        try:
            news['comments_count'] = len(news_comment) # news_id对应的评论数
        except:
            news['comments_count'] = 0
        results.append(news)

    sort_results = sorted(results, key=lambda x:x['comments_count'], reverse=True)
    
    return sort_results

