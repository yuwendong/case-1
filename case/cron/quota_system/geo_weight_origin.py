# -*- coding: utf-8 -*-
import sys
import json
#from config import db
from model import GeoWeight, QuotaGeoPenetration
from config import xapian_search_user as user_search

sys.path.append('../../')
from global_config import db

province_dict = {'34':'安徽','11':'北京', '50':'重庆', '35':'福建', '62':'甘肃', '44':'广东', '45':'广西',\
                 '52':'贵州', '46':'海南', '13':'河北', '23':'黑龙江', '41':'河南', '42':'湖北', '43':'湖南',\
                 '15':'内蒙古', '32':'江苏', '36':'江西', '22':'吉林', '21':'辽宁', '64':'宁夏', '63':'青海',\
                 '14':'山西', '37':'山东', '31':'上海', '51':'四川', '12':'天津', '54':'西藏', '65':'新疆',\
                 '53':'云南', '33':'浙江', '61':'陕西', '71':'台湾', '81':'香港', '82':'澳门',\
                 '400':'海外', '100':'其他'}


def save_weight_dict(weight_dict):
    item = GeoWeight(json.dumps(weight_dict))
    item_exist = db.session.query(GeoWeight).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()
    print 'success save default weight_dict'

def get_geo_register(N):
    geo_weight_dict = {}
    for province in province_dict:
        query_dict = {'province': province}
        counts = user_search.search(query=query_dict, count_only=True)
        geo_weight_dict[province] = float(counts) / float(N)
        print 'provice, count:',province_dict[province], counts
    return geo_weight_dict

'''
def get_weight_geo():
    item_weight_dict = db.session.query(GeoWeight).first()
    item_geo_count = db.session.query(QuotaGeoPenetration).filter(QuotaGeoPenetration.id==1).first()
    weight_dict = json.loads(item_weight_dict.weight_dict)
    geo_count = json.loads(item_geo_count.pcount)
    geo_weight = {}
    s = 0
    for province in province_dict:
        if geo_count[province] >= weight_dict[province]:
            geo_weight[province] = 1
        else:
            geo_weight[province] = 0
        s += geo_weight[province]
        print province_dict[province], geo_count[province], weight_dict[province], geo_weight[province]
    print 's:', s
    print 'avg_s:', float(s) / float(36)
    
'''

if __name__=='__main__':
    N = 200 # N be used to generate weight of geo
    weight_dict = get_geo_register(N)
    print 'geo_weight_dict:', weight_dict
    save_weight_dict(weight_dict)
    # get_weight_geo()
