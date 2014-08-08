#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import os
from BeautifulSoup import BeautifulSoup
from city_color import province_color_map    #根据count不同，给不同的城市不同的颜色
import json
from city_count import Pcount
#from get_result import *


mod = Blueprint('evolution', __name__, url_prefix='/evolution')

#mtype_kv={'original': 1, 'forward': 2, 'comment': 3,'sum':4}

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

province_list = [u'安徽', u'北京', u'重庆', u'福建', u'甘肃', u'广东', u'广西', u'贵州', u'海南', \
                 u'河北', u'黑龙江', u'河南', u'湖北', u'湖南', u'内蒙古', u'江苏', u'江西', u'吉林', \
                 u'辽宁', u'宁夏', u'青海', u'山西', u'山东', u'上海', u'四川', u'天津', u'西藏', u'新疆', \
                 u'云南', u'浙江', u'陕西', u'台湾', u'香港', u'澳门']


def info2map(infos):
    count = {}
    rank = {}
    ratio = {}
    top10 = {}
    for info in infos:
        map_dict = infos[info]
        count[info] = [0] * 34
        rank[info] = [0] * 34
        ratio[info] = [0] *34
        for p in range(34):
            try:
                pcount = map_dict['count'][province_list[p]][0]
                prank = map_dict['count'][province_list[p]][1]
                pratio = map_dict['count'][province_list[p]][2]
            except:
                continue
            count[info][p] = pcount
            rank[info][p] = prank
            ratio[info][p] = pratio

        top10[info] = map_dict['summary']
    
    
    data = {'count':count, 'rank':rank, 'ratio':ratio, 'top10':top10}

    return data


def readPropagateSpatial(stylenum, topic, end_ts , during):   #将从数据库中读取的数据转化为map_data
    city_count = {}
    city_count = Pcount(end_ts, during, stylenum, topic)  #PCount从db中计算各个省市地区的总数
    map_data = province_color_map(city_count)
    return map_data	

@mod.route("/topic_ajax_spatial/")  #地域演化的页面,从database获取数据返回topic_spatial.html
def ajax_spatial():
    tmp = request.args.get('style', '')                   #stylenum表示返回count是origin：1,forward：2,comment：3,sum：4 
    stylenum = int(tmp)
   # print stylenum
    topic = request.args.get('topic','')                  #???这里的topic是怎么传过来的？！
    during = request.args.get('during',2* 900)              #默认查询时间段为900秒
    during = int(during)
    ts = request.args.get('ts','')
    ts = long(ts)
    end_ts = ts
    codenum = request.args.get('codenum', '')
    codenum = int(codenum)
    spatial_dict = {}
    for i in range(codenum):
        end_ts = end_ts + i * during
        topic_spatial_info = readPropagateSpatial(stylenum, topic, end_ts , during)  #查询在一定时间范围内，某个topic的stylenum信息各个省市的数量
        print 'topic_spatial_info:'
        print topic_spatial_info
        spatial_dict[str(end_ts)] = topic_spatial_info
    map_data = info2map(spatial_dict)
    print 'map_data:'
    print map_data
    return json.dumps(map_data)
