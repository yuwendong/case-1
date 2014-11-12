# -*- coding: utf-8 -*-
import json
import math
import operator
from case.extensions import db
from utils import weiboinfo2url
from case.time_utils import datetime2ts, ts2date
from case.global_config import xapian_search_user as user_search
from case.model import PropagateCount, PropagateKeywords, PropagateWeibos# , AttentionCount, QuicknessCount  需要查询的表

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

TOP_KEYWORDS_LIMIT = 50
TOP_READ =10
TOP_WEIBOS_LIMIT = 50

expr = 100 # 经验值的计算
domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']

'''
def Merge_Acount(item): # 计算指标值 
    results = {}
    s = 0
    print 'item:',item
    for r in item:
        s += r.covernum

    results =float(s) / expr # 这里需要写一个方法，确定expr。先默认为100的常值
    return results

def Merge_Pcount(item):
    results = {}
    cover = 0
    total = 0
    for r in item:
        cover += r.covernum
        total += r.allnum
        
    results = float(cover) / total
    return results

def Merge_Qcount(item):
    results = {}
    top = 0
    total = 0
    # print 'item:',item
    for r in item:
        top += r.topnum
        total += r.allnum
        
    results = float(top) / total
    return results
'''

# domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
def Merge_propagate(items):
    results = {}
    results['dcount'] = {'folk':0, 'media':0, 'opinion_leader':0, 'oversea':0, 'other':0}
    for item in items:
        results['topic'] = item.topic
        results['mtype'] = item.mtype
        results['end'] = item.end
        for k in domain_list:
            #print '*'*10,json.loads(item.dcount)
            try:
                dcount = json.loads(item.dcount)
                #print '*'*10, dcount[k]
                #print '-'*10, results['dcount'][k]
                results['dcount'][k] += dcount[k]
                #print '-'*10,results['dcount'][k]
            except KeyError:
                continue

    return results


def ReadPropagate(topic, end, during, mtype, unit=MinInterval):
    if during <= unit:
        upbound = int(math.ceil(end / (unit * 1.0)) * unit)
        item = db.session.query(PropagateCount).filter(PropagateCount.topic==topic, \
                                                       PropagateCount.end==upbound, \
                                                       PropagateCount.range==unit, \
                                                       PropagateCount.mtype==mtype).all()
    else:
        start = end - during
        upbound = int(math.ceil(end / (unit * 1.0)) * unit)
        lowbound = (start / unit) * unit
        item = db.session.query(PropagateCount).filter(PropagateCount.topic==topic, \
                                                       PropagateCount.range==unit, \
                                                       PropagateCount.end<=upbound, \
                                                       PropagateCount.end>lowbound, \
                                                       PropagateCount.mtype==mtype).all()
    if item:
        results = Merge_propagate(item)
    else:
        results = None

    return results

def ReadIncrement(topic, end, during, mtype, unit=MinInterval):
    items1 = ReadPropagate(topic, end, during, mtype)
    items2 = ReadPropagate(topic, end-during, during, mtype) # attent the exist of the end-during and end-during*2
    results = {}
    results['topic'] = topic
    results['end'] = end
    results['during'] = during
    results['mtype'] = mtype
    results['dincrement'] = {}
    total1=0
    total2=0
    for k in domain_list:
        try:
            results['dincrement'][k] = float(items1['dcount'][k]) / float(items2['dcount'][k]) - 1
            total1 += items1['dcount'][k]
            total2 += items2['dcount'][k]
        except:
            results['dincrement'][k] = None

    if total2 == 0:
        results['dincrement']['total'] = None
    else:
        results['dincrement']['total'] = float(total1) / float(total2) -1
    return results


def parseKcount(kcount):
    kcount_dict = {}
    kcount = json.loads(kcount)

    for k ,v in kcount:
        kcount_dict[k] = v

    return kcount_dict

def _top_keywords(kcount_dict, top=TOP_READ):
    results_dict = {}

    if kcount_dict != {}:
        results = sorted(kcount_dict.iteritems(), key=operator.itemgetter(1), reverse=False)
        results = results[len(results) - top:]

        for k, v in results:
            results_dict[k] = v

    return results_dict


def ReadPropagateKeywords(topic, end_ts, during, mtype, limit=TOP_KEYWORDS_LIMIT, unit=MinInterval, top=TOP_READ):
    kcounts_dict = {}
    print '*'*5
    print topic, end_ts, during, mtype
    print during-unit
    if during <= unit:
        print '*'*10
        print topic, end_ts, during, mtype
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        item = db.session.query(PropagateKeywords).filter(PropagateKeywords.end==upbound, \
                                                          PropagateKeywords.topic==topic, \
                                                          PropagateKeywords.range==unit, \
                                                          PropagateKeywords.mtype==mtype, \
                                                          PropagateKeywords.limit==limit).first()
        if item:
            #print '*'*10, item
            kcounts_dict = parseKcount(item.kcount)

    else:
        #print '---'*10
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        items = db.session.query(PropagateKeywords).filter(PropagateKeywords.end>lowbound, \
                                                         PropagateKeywords.end<=upbound, \
                                                         PropagateKeywords.topic==topic, \
                                                         PropagateKeywords.range==unit, \
                                                         PropagateKeywords.mtype==mtype, \
                                                         PropagateKeywords.limit==limit).all()
        for item in items:
            kcount_dict = parseKcount(item.kcount)
            for k, v in kcount_dict.iteritems():
                try:
                    kcounts_dict[k] += v
                except KeyError:
                    kcounts_dict[k] = v

    kcounts_dict = _top_keywords(kcounts_dict, top)

    return kcounts_dict

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
        #print 'user', user
    return user


def _top_weibos(weibos_dict, top=TOP_READ):
    results_list =[]
    results_list_new = []
    if weibos_dict != {}:
        results = sorted(weibos_dict.iteritems(), key=lambda(k,v): v[0], reverse=False)
        #print '_top_weibos_results_orgin:', len(results)
        #print '_top_weibos_results:', len(results)-top
        results = results[len(results) - top:]
        
        for k, v in results:
            #print '@@@@@@@@:',v[1]
            results_list.append(v[1])
        for i in range(len(results_list)):
            results_list_new.append(results_list[len(results_list)-1-i])
    #print 'list:', results_list
    #print 'list_lens:', len(results_list)
    return results_list_new

def _json_loads(weibos):
    try:
        return json.loads(weibos)
    except ValueError:
        if isinstance(weibos, unicode):
            return json.loads(json.dumps(weibos))
        else:
            return None

def parseWeibos(weibos):
    weibo_dict = {}
    weibos = _json_loads(weibos)

    if not weibos:
        return {}

    for weibo in weibos:
        try:
            _id = weibo['_id']
            username, profileimage = getuserinfo(weibo['user'])
            #print 'username', profileimage
            reposts_count = weibo['reposts_count']
            #print 'reposts_count', reposts_count
            weibo['weibo_link'] = weiboinfo2url(weibo['user'],_id)
            weibo['username'] = username
            weibo['profile_image_url'] = profileimage
            weibo['timestamp'] = ts2date(weibo['timestamp'])
            #print 'weibo:', weibo
            weibo_dict[_id] = [reposts_count, weibo]
        except:
            continue
    #print 'there :', weibo_dict
    return weibo_dict


def ReadPropagateWeibos(topic, end_ts, during, mtype, limit=TOP_WEIBOS_LIMIT, unit=MinInterval, top=TOP_READ):
    weibos_dict = {}
    #print '*'*5
    #print topic, end_ts, during, mtype, limit
    if during <= unit:
        #print '-'*5
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        item =db.session.query(PropagateWeibos).filter(PropagateWeibos.end==upbound, \
                                                       PropagateWeibos.topic==topic, \
                                                       PropagateWeibos.mtype==mtype, \
                                                       PropagateWeibos.range==unit, \
                                                       PropagateWeibos.limit==limit).first()
        if item:
            #print '$$'*5
            #print item.weibos
            weibos_dict = parseWeibos(item.weibos)
            #print '-------', weibos_dict

    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        items = db.session.query(PropagateWeibos).filter(PropagateWeibos.end>lowbound, \
                                                         PropagateWeibos.end<=upbound, \
                                                         PropagateWeibos.topic==topic, \
                                                         PropagateWeibos.mtype==mtype, \
                                                         PropagateWeibos.range==unit, \
                                                         PropagateWeibos.limit==limit).all()
        for item in items:
            weibo_dict = parseWeibos(item.weibos)
            #print 'weibo_dict:', weibo_dict
            for k ,v in weibo_dict.iteritems():
                try:
                    weibos_dict[k] += v
                except KeyError:
                    weibos_dict[k] = v
                #print 'weibos_dict:', weibos_dict
    weibos_dict = _top_weibos(weibos_dict, top)
    return weibos_dict



'''
def ReadAttention(topic, domain, mtype, end_ts, during, unit=MinInterval):
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        if mtype == 4:
            item = db.session.query(AttentionCount).filter(AttentionCount.end==upbound, \
                                                    AttentionCount.range==unit,  \
                                                    AttentionCount.topic==topic, \
                                                    AttentionCount.domain==domain).all()                  
        else:
            item = db.session.query(AttentionCount).filter(AttentionCount.end==upbound, \
                                                    AttentionCount.range==unit, \
                                                    AttentionCount.topic==topic, \
                                                    AttentionCount.mtype==mtype, \
                                                    AttentionCount.domain==domain).first()  
        #print '*'*10
        #print item
        if item:
            if not isinstance(item, list):
                item = [item]
            results = Merge_Acount(item) # 合并指标计算，分子和分母
        else:
            results = None
            
    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        if stylenum == 4:
            item = db.session.query(AttentionCount).filter(AttentionCount.end>lowbound, \
                                                    AttentionCount.end<=upbound, \
                                                    AttentionCount.range==unit, \
                                                    AttentionCount.topic==topic, \
                                                    AttentionCount.domain==domain).all()
        else:
            item = db.session.query(AttentionCount).filter(AttentionCount.end>lowbound, \
                                                    AttentionCount.end<=upbound, \
                                                    AttentionCount.mtype==stylenum, \
                                                    AttentionCount.range==unit, \
                                                    AttentionCount.topic==topic, \
                                                    AttentionCount.domain==domain).all()
        if item:
            if not isinstance(item, list):
                item = [item]
            results = Merge_Acount(item)
        else:
            results = None
                    
    return results

def ReadPenetration(topic, domain, mtype, end_ts, during, unit=MinInterval):
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        if mtype == 4:
            item = db.session.query(AttentionCount).filter(AttentionCount.end==upbound, \
                                                    AttentionCount.range==unit,  \
                                                    AttentionCount.topic==topic, \
                                                    AttentionCount.domain==domain).all()                  
        else:
            item = db.session.query(AttentionCount).filter(AttentionCount.end==upbound, \
                                                    AttentionCount.range==unit, \
                                                    AttentionCount.topic==topic, \
                                                    AttentionCount.mtype==mtype, \
                                                    AttentionCount.domain==domain).all()  
        if item:
            if not isinstance(item, list):
                item = [item]
            results = Merge_Pcount(item) # 合并指标计算，分子和分母
        else:
            results = None
            
    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        if stylenum == 4:
            item = db.session.query(AttentionCount).filter(AttentionCount.end>lowbound, \
                                                    AttentionCount.end<=upbound, \
                                                    AttentionCount.range==unit, \
                                                    AttentionCount.topic==topic, \
                                                    AttentionCount.domain==domain).all()
        else:
            item = db.session.query(AttentionCount).filter(AttentionCount.end>lowbound, \
                                                    AttentionCount.end<=upbound, \
                                                    AttentionCount.mtype==stylenum, \
                                                    AttentionCount.range==unit, \
                                                    AttentionCount.topic==topic, \
                                                    AttentionCount.domain==domain).all()
        if item:
            if not isinstance(item, list):
                 item = [item]
            results = Merge_Pcount(item)
        else:
            results = None    
    
    return results

def ReadQuickness(topic, domain, mtype, end_ts, during, unit=MinInterval):
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        if mtype == 4:
            item = db.session.query(QuicknessCount).filter(QuicknessCount.end==upbound, \
                                                    QuicknessCount.range==unit,  \
                                                    QuicknessCount.topic==topic, \
                                                    QuicknessCount.domain==domain).all()                  
        else:
            item = db.session.query(QuicknessCount).filter(QuicknessCount.end==upbound, \
                                                    QuicknessCount.range==unit, \
                                                    QuicknessCount.topic==topic, \
                                                    QuicknessCount.mtype==mtype, \
                                                    QuicknessCount.domain==domain).first()  
        print '*'*10
        print item
        if item:
            if not isinstance(item, list):
                item = [item]
            results = Merge_Qcount(item) # 合并指标计算，分子和分母
        else:
            results = None
            
    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        if mtype == 4:
            item = db.session.query(QuicknessCount).filter(QuicknessCount.end>lowbound, \
                                                    QuicknessCount.end<=upbound, \
                                                    QuicknessCount.range==unit, \
                                                    QuicknessCount.topic==topic, \
                                                    QuicknessCount.domain==domain).all()
        else:
            item = db.session.query(QuicknessCount).filter(QuicknessCount.end>lowbound, \
                                                    QuicknessCount.end<=upbound, \
                                                    QuicknessCount.mtype==mtype, \
                                                    QuicknessCount.range==unit, \
                                                    QuicknessCount.topic==topic, \
                                                    QuicknessCount.domain==domain).all()
        print '*'*10
        print item
        if item:
            if not isinstance(item, list):
                item = [item]
            results = Merge_Qcount(item)
        else:
            results = None
    
    return results
'''
