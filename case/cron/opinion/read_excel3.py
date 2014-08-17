# -*- coding: utf-8 -*-

import xlrd
import json
from config import db
from xapian_case.xapian_backend import XapianSearch
from config import xapian_search_user as user_search
from time_utils import datetime2ts,ts2date
from utils import weiboinfo2url
from model import OpinionTestTime, OpinionTestRatio, OpinionTestKeywords, OpinionTestWeibos


fields_list=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', \
             'source', 'bmiddle_pic', 'geo', 'attitudes_count', 'comments_count', 'sentiment', 'topics', 'message_type', 'terms']



def save_ts(topic): # '0' no means
    start_ts = [1396918800, 1396918800, 1396920000, 1396922400, 1396929600, 1396928400,\
                1397032200, 1397045700, 1397096100, 1397089200, 1397138400]
    end_ts = [1396918900,1996920300, 1396927000, 1396923400, 1396931000, 1396930000,\
              1397033200, 1397130000, 1397098000, 1397089900, 1397140000]
    for i in range(11):
        item = OpinionTestTime(topic, str(i), start_ts[i], end_ts[i])
        item_exist = db.session.query(OpinionTestTime).filter(OpinionTestTime.topic==topic, \
                                                              OpinionTestTime.child_topic==str(i), \
                                                              OpinionTestTime.start_ts==start_ts[i], \
                                                              OpinionTestTime.end_ts==end_ts[i]).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
    db.session.commit()


def save_ratio(excel_name, topic):
    data = xlrd.open_workbook(excel_name) # 打开excel文件
    table_ratio = data.sheet_by_name('ratio') # 获取工作表内容
    n_row_ratio = table_ratio.nrows # 工作表数据的行数
    child_topic_list = []
    for i in range(n_row_ratio):
        line = table_ratio.row_values(i)
        child_topic = line[0]
        child_topic_list.append(str(int(child_topic))) # 获取子话题名称的序列
        ratio = line[1]
        #topic = str(topic)
        #print 'topic:', topic
        item = OpinionTestRatio(topic, child_topic, ratio)
        item_exist = db.session.query(OpinionTestRatio).filter(OpinionTestRatio.topic==topic, \
                                                               OpinionTestRatio.child_topic==child_topic).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
    db.session.commit()
    return child_topic_list
        
    
def save_keywords(excel_name, topic, k_limit):
    data = xlrd.open_workbook(excel_name)
    table_keywords = data.sheet_by_name(u'关键词对聚类结果')
    n_row_keywords = table_keywords.nrows
    keywords_dict = {} # keywords_dict = {child_topic:[(keyword1：weight1),(keyword2:weight2)]} 
    for i in range(n_row_keywords):
        line = table_keywords.row_values(i)
        weight = line[0]
        keywords = line[1]
        child_topic = line[2]
        #print 'child_topic:',child_topic, type(child_topic)
        try:
            keywords_dict[str(int(child_topic))].append((keywords, weight))
        except:
            keywords_dict[str(int(child_topic))] = [(keywords, weight)]

    for child_topic in keywords_dict:
        keywords_dict[child_topic] = sorted(keywords_dict[child_topic], key=lambda x:x[1], reverse=False) 
        keywords_list = keywords_dict[child_topic][len(keywords_dict[child_topic]) - k_limit:]
        keywords_list_new = []
        for i in range(len(keywords_list)):
            keywords_list_new.append(keywords_list[len(keywords_list)-1-i]) # keywords_list_new=[(keywords:weight),()] 根据weight从大到小排列
            
        item = OpinionTestKeywords(topic, child_topic, json.dumps(keywords_list_new))
        item_exist = db.session.query(OpinionTestKeywords).filter(OpinionTestKeywords.topic==topic, \
                                                                  OpinionTestKeywords.child_topic==child_topic).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
    db.session.commit()

def getuserinfo(uid):
    #print 'uid:',uid, type(uid)
    user = acquire_user_by_id(uid)
    if not user:
        username = 'Unkonwn'
        profileimage = ''
    else:
        username = user['name']
        profileimage = user['image']
    return username, profileimage

def acquire_user_by_id(uid):
    user_result = user_search.search_by_id(uid, fields=['name', 'profile_image_url'])
    user = {}
    if user_result:
        user['name'] = user_result['name']
        user['image'] = user_result['profile_image_url']
   
    return user


def save_weibos(excel_name, topic, child_topic_list, w_limit): # 这里需要根据文本内容查询相关微博id等
    data = xlrd.open_workbook(excel_name)
    weibos_dict = {}
    for i in child_topic_list:
        #if i == '0':
        #    continue
        weibos_dict[i] = []
        table_weibos = data.sheet_by_name(str(int(i)))
        n_row_weibos = table_weibos.nrows
        if n_row_weibos <= w_limit:
            n_rows = n_row_weibo
        else:
            n_rows = w_limit  # 考虑到数据已经根据权重从大到小排列
        for j in range(n_rows):
            line = table_weibos.row_values(j)  # 缺少根据文本查询微博文本对应的其他微博内容
            weibo_text = line[1]
            weibo_weight = line[0]
            try:
                weibos_dict[i].append((weibo_text, weibo_weight)) # 实际上这里append的应该是weibo的完整内容，并且是将username等获取到的
            except:
                weibos_dict[i]=[(weibo_text, weibo_weight)]
    #print 'weibos_dict:', weibos_dict
    #获取微博具体数据，仅作测试用
    s = XapianSearch(path='/home/ubuntu3/huxiaoqian/case/20140724/20140804/', name='master_timeline_weibo',schema_version='5')
    begin_ts = 1378050300
    end_ts = 1378051200
    query_dict = {
        'timestamp': {'$gt':begin_ts, '$lt': end_ts},
        'message_type' : 2
    }
    weibos_dict_new = {}
    scount, weibo_results =s.search(query=query_dict, fields=fields_list)
    #print 'scount:', scount
    i = 0
    j = 0
    for weibo in weibo_results():
        if i==11:
            break
        #print 'i, j:', i, j
        weibo['text'] = weibos_dict[str(i)][j][0]
        #获取username，profileimage,weibourl
        username, profileimage = getuserinfo(weibo['user'])
        weibo['username'] = username
        weibo['profile_image_url'] = profileimage
        weibo['timestamp'] = ts2date(weibo['timestamp'])
        weibo['weibo_link'] = weiboinfo2url(weibo['user'],weibo['_id'])
        #获取username， profileimage,weibourl结束       
        weight = weibos_dict[str(i)][j][1]
        try:
            weibos_dict_new[i].append((weibo, weight))
        except:
            weibos_dict_new[i] = [(weibo, weight)]
        if j==4:
            j = 0
            i += 1
        else:
            j +=1
            
        #分割线
    print 'weibos_dict_new:', weibos_dict_new[6]
    for i in range(len(child_topic_list)):
        item = OpinionTestWeibos(topic, i, json.dumps(weibos_dict_new[i]))
        item_exist = db.session.query(OpinionTestWeibos).filter(OpinionTestWeibos.topic==topic, \
                                                                OpinionTestWeibos.child_topic==i).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
    db.session.commit()

if __name__=='__main__':
    topic = u'博鳌'
    excel_name = 'ba.xlsx'
    k_limit = 5
    w_limit = 5
    save_ts(topic)
    child_topic_list = save_ratio(excel_name, topic)
    #print 'child_topic_list:', child_topic_list
    save_keywords(excel_name, topic, k_limit)
    save_weibos(excel_name, topic, child_topic_list, w_limit)
    

           

        
