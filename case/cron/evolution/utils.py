# -*- coding:utf-8 -*-

import IP   #引入IP，对'geo'字段进行解析


def geo2city(geo): #将weibo中的'geo'字段解析为地址
    try:
        province, city = geo.split()
        if province in [u'内蒙古自治区', u'黑龙江省']:
            province = province[:3]
        else:
            province = province[:2]

        city = city.strip(u'市').strip(u'区')

        geo = province + ' ' + city
    except:
        pass

    if isinstance(geo, unicode):
        geo = geo.encode('utf-8')

    if geo.split()[0] not in ['海外', '其他']:
        geo = '中国 ' + geo
    geo = '\t'.join(geo.split())

    return geo

def IP2city(geo):
    try:
        city=IP.find(str(geo))
        if city:
            city=city.encode('utf-8')
        else:
            return None
    except Exception,e:
        return None

    return city
