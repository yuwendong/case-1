#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import os
from BeautifulSoup import BeautifulSoup
from city_color import province_color_map
import json
#from get_result import *
#from peak_detection import detect_peaks  


mod = Blueprint('evolution', __name__, url_prefix='/evolution')

#evolutions_kv = {'original': 1, 'forward': 2, 'comment': 3}

def readPropagateSpatial(stylenum):
    city_count = {}

    province_name = dict()
    html = '''<select name="province" id="province" defvalue="11"><option value="34">安徽</option><option value="11">北京</option><option value="50">重庆</option><option value="35">福建</option><option value="62">甘肃</option>
            <option value="44">广东</option><option value="45">广西</option><option value="52">贵州</option><option value="46">海南</option><option value="13">河北</option>
            <option value="23">黑龙江</option><option value="41">河南</option><option value="42">湖北</option><option value="43">湖南</option><option value="15">内蒙古</option><option value="32">江苏</option>
            <option value="36">江西</option><option value="22">吉林</option><option value="21">辽宁</option><option value="64">宁夏</option><option value="63">青海</option><option value="14">山西</option><option value="37">山东</option>
            <option value="31">上海</option><option value="51">四川</option><option value="12">天津</option><option value="54">西藏</option><option value="65">新疆</option><option value="53">云南</option><option value="33">浙江</option>
            <option value="61">陕西</option><option value="71">台湾</option><option value="81">香港</option><option value="82">澳门</option><option value="400">海外</option><option value="100">其他</option></select>'''
    province_soup = BeautifulSoup(html)
    #count is simply some numbers

    for province in province_soup.findAll('option'):
        pp = province.string
        if stylenum == 1:
            count = len(pp)
        elif stylenum == 20:
            count = 8
        else:
            count = 10
        key = province['value']
        province_name[key] = pp
        if pp == u'海外' or pp == u'其他':
            continue
        city_count[pp] = count

    map_data = province_color_map(city_count)

    return map_data	

@mod.route("/topic_ajax_spatial/", methods = ["GET","POST"])  #地域演化的页面,从database获取数据返回topic_spatial.html
def ajax_spatial():
    if request.method == "POST":
        tmp = request.form.get('style', '')
        stylenum = int(tmp)
        topic_info = readPropagateSpatial(stylenum)
	return json.dumps({'map_data': topic_info})
    else:
        return render_template('evolution/ajax/topic_spatial.html')
