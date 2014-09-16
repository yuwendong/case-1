#-*-coding:utf-8-*-

import json
import math

def province_color_map(city_count):
    total_count = sum(city_count.values())
    city_sorted = sorted(city_count.iteritems(), key=lambda(k, v): v, reverse=True)
    city_color = {}
    city_count = {}
    city_summary = []
    #color = ['#000079', '#0f1486', '#1e2893', '#2d3ca1', '#3c51ae', '#4b65bc', '#5a79c9', '#698ed6', '#78a2e4', '#87b6f1', '#96cafe']
    color = ['#ff0000', '#ff1414', '#ff2727', '#ff3b3b', '#ff4e4e', '#ff6262', '#ff7676', '#ff8989', '#ff9d9d', '#ffb1b1', '#ffc4c4',
             '#ffd8d8', '#ffebeb', '#ffffff']
    if len(city_sorted) > len(color):
        n = int(math.ceil(len(city_sorted)*1.0/len(color)))
        for i in range(0, len(city_sorted), n):
            for j in range(n):
                if i+j < len(city_sorted):
                    city, count = city_sorted[i+j]
                    if count == 0:
                        continue
                    city_color[city] = color[i/n]
                    rank = i+j+1
                    percent = str(int(count*1000/total_count)/10.0)+'%'
                    if rank <= 10:
                        city_summary.append([rank, city, percent])
                    city_count[city] = [count, rank, percent]
    else:
        for index, x in enumerate(city_sorted):
            city, count = x
            if count:
                city_color[city] =  "%s" % color[index]
                percent = str(int(count*1000/total_count)/10.0)+'%'
                rank = index+1
                if rank <= 10:
                    city_summary.append([rank, city, percent])
                city_count[city] = [count, rank, percent]
    data = {'count': city_count,
            'color': city_color,
            'summary': city_summary}

    return data

def main():
    from BeautifulSoup import BeautifulSoup
    import random
    city_count = {}
    html = '''<select name="province" id="province" defvalue="11"><option value="34">安徽</option><option value="11">北京</option><option value="50">重庆</option><option value="35">福建</option><option value="62">甘肃</option>
                <option value="44">广东</option><option value="45">广西</option><option value="52">贵州</option><option value="46">海南</option><option value="13">河北</option>
                <option value="23">黑龙江</option><option value="41">河南</option><option value="42">湖北</option><option value="43">湖南</option><option value="15">内蒙古</option><option value="32">江苏</option>
                <option value="36">江西</option><option value="22">吉林</option><option value="21">辽宁</option><option value="64">宁夏</option><option value="63">青海</option><option value="14">山西</option><option value="37">山东</option>
                <option value="31">上海</option><option value="51">四川</option><option value="12">天津</option><option value="54">西藏</option><option value="65">新疆</option><option value="53">云南</option><option value="33">浙江</option>
                <option value="61">陕西</option><option value="71">台湾</option><option value="81">香港</option><option value="82">澳门</option><option value="400">海外</option><option value="100">其他</option></select>'''
    province_soup = BeautifulSoup(html)
    for province in province_soup.findAll('option'):
        pp = province.string
        if pp == u'海外' or pp == u'其他':
            continue
        city_count[pp] = random.randint(0, 20)
    city_count[u'内蒙古'] = 0
    city_count[u'北京'] = 100
    city_count[u'广东'] = 90
    city_count[u'上海'] = 80
    return province_color_map(city_count)

if __name__ == '__main__': main()
