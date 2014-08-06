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
    begin_ts = ts - during
    end_ts = ts 
    
    topic_spatial_info = readPropagateSpatial(stylenum, topic, end_ts , during)  #查询在一定时间范围内，某个topic的stylenum信息各个省市的数量
    
    return json.dumps({'map_data': topic_spatial_info})
