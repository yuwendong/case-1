# -*- coding: utf-8 -*-
import json
import math
from case.extensions import db
from time_utils import datetime2ts
from case.model import PropagateCount # , AttentionCount, QuicknessCount # 需要查询的表

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

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
    for item in items:
        results['topic'] = item.topic
        results['mtype'] = item.mtype
        results['end'] = item.end
        results['dcount'] = {'folk':0, 'media':0, 'opinion_leader':0, 'oversea':0, 'other':0}
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
    #print '====',results
    return results

def ReadIncrement(topic, end, during, mtype, unit=MinInterval):
    items1 = ReadPropagate(topic, end, during, mtype)
    items2 = ReadPropagate(topic, end-during, during, mtype) # attent the exist of the end-during and end-during*2
    print 'items1:', items1
    print 'items2:', items2
    results = {}
    results['topic'] = topic
    results['end'] = end
    results['during'] = during
    results['mtype'] = mtype
    results['dincrement'] = {}
    for k in domain_list:
        try:
            results['dincrement'][k] = float(items1['dcount'][k]) / float(items2['dcount'][k]) - 1
        except:
            results['dincrement'][k] = None


    return results

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
