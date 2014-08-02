# -*- coding: utf-8 -*-
import json
import math
from case.extensions import db
from time_utils import datetime2ts
from case.model import PropagateCount, APCount, QuicknessCount # 需要查询的表

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

expr = 100 # 经验值的计算


def Merge_Acount(item): # 计算指标值 
    results = {}
    s = 0
    for r in item:
        s += r.covernum

    results = s / expr # 这里需要写一个方法，确定expr。先默认为100的常值
    return results

def Merge_Pcount(item):
    results = {}
    cover = 0
    total = 0
    for r in item:
        cover += r.covernum
        total += r.allnum
        
    results = cover / total
    return results

def Merge_Qcount(item):
    results = {}
    top = 0
    total = 0
    for r in item:
        top += r.topnum
        total += r.allnum
        
    results = top / total
    return results




def ReadAttention(topic, domain, mtype, ts, durng):
    if during <= unit:
        upbound int(math.ceil(end_ts / (unit * 1.0)) * unit)
        if mtype == 4:
            item = db.session.query(APCount).filter(Apcount.end==upbound, \
                                                    Apcount.range==unit,  \
                                                    Apcount.topic==topic, \
                                                    Apount.domain==domain).all()                  
        else:
            item = db.session.query(APcount).filter(Apcount.end==upbound, \
                                                    Apound.range==unit, \
                                                    Apound.topic==topic, \
                                                    Apound.mtype==mtype, \
                                                    Apound.domain==domain).first()  
        if item:
            results = Merge_Acount(item) # 合并指标计算，分子和分母
        else:
            results = None
            
    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        if stylenum == 4:
            item = db.session.query(Apcount).filter(Apcount.end>lowbound, \
                                                    Apcount.end<=upbound, \
                                                    Apcount.range==unit, \
                                                    Apcount.topic==topic, \
                                                    Apound.domain==domain).all()
        else:
            item = db.session.query(Apcount).filter(Apcount.end>lowbound, \
                                                    Apcount.end<=upbound, \
                                                    Apcount.mtype==stylenum, \
                                                    Apcount.range==unit, \
                                                    Apcount.topic==topic, \
                                                    Apound.domain==domain).all()
        if item:
            results = Merge_Acount(item)
        else:
            results = None
                    
    return resluts

def ReadPenetration(topic, domain, mtype, ts, durng):
    if during <= unit:
        upbound int(math.ceil(end_ts / (unit * 1.0)) * unit)
        if mtype == 4:
            item = db.session.query(APCount).filter(Apcount.end==upbound, \
                                                    Apcount.range==unit,  \
                                                    Apcount.topic==topic, \
                                                    Apount.domain==domain).all()                  
        else:
            item = db.session.query(APcount).filter(Apcount.end==upbound, \
                                                    Apound.range==unit, \
                                                    Apound.topic==topic, \
                                                    Apound.mtype==mtype, \
                                                    Apound.domain==domain).first()  
        if item:
            results = Merge_Pcount(item) # 合并指标计算，分子和分母
        else:
            results = None
            
    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        if stylenum == 4:
            item = db.session.query(Apcount).filter(Apcount.end>lowbound, \
                                                    Apcount.end<=upbound, \
                                                    Apcount.range==unit, \
                                                    Apcount.topic==topic, \
                                                    Apound.domain==domain).all()
        else:
            item = db.session.query(Apcount).filter(Apcount.end>lowbound, \
                                                    Apcount.end<=upbound, \
                                                    Apcount.mtype==stylenum, \
                                                    Apcount.range==unit, \
                                                    Apcount.topic==topic, \
                                                    Apound.domain==domain).all()
        if item:
            results = Merge_Pcount(item)
        else:
            results = None    
    
    return results

def ReadQuickness(topic, domain, mtype, ts, durng):
    if during <= unit:
        upbound int(math.ceil(end_ts / (unit * 1.0)) * unit)
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
        if item:
            results = Merge_Qcount(item) # 合并指标计算，分子和分母
        else:
            results = None
            
    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        if stylenum == 4:
            item = db.session.query(QuicknessCount).filter(QuicknessCount.end>lowbound, \
                                                    QuicknessCount.end<=upbound, \
                                                    QuicknessCount.range==unit, \
                                                    QuicknessCount.topic==topic, \
                                                    QuicknessCount.domain==domain).all()
        else:
            item = db.session.query(QuicknessCount).filter(QuicknessCount.end>lowbound, \
                                                    QuicknessCount.end<=upbound, \
                                                    QuicknessCount.mtype==stylenum, \
                                                    QuicknessCount.range==unit, \
                                                    QuicknessCount.topic==topic, \
                                                    QuicknessCount.domain==domain).all()
        if item:
            results = Merge_Acount(item)
        else:
            results = None
    
    return results
