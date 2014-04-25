# -*- coding: utf-8 -*-

from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import json
from case.model import *
from case.extensions import db
mod = Blueprint('index', __name__, url_prefix='')

@mod.route('/')
def loading():
    return render_template('demo.html')

@mod.route('/add_field')
def add():
##    topic = '九一八'
##    keyword = ['日本','钓鱼岛','悲痛']
##    count = [345,789,123]
##    stype = ['happy','angry','sad']
##    ts = 1396368000
##    for i in range(0,len(keyword)):
##        new_item = SentimentKeywords(topic, keyword[i], count[i], stype[i], ts)
##        db.session.add(new_item)
##    db.session.commit()
##
##    topic = '九一八'
##    keyword = ['小日本','买岛','哈哈']
##    count = [345,789,123]
##    stype = ['sad','angry','happy']
##    ts = 1396454400
##    for i in range(0,len(keyword)):
##        new_item = SentimentKeywords(topic, keyword[i], count[i], stype[i], ts)
##        db.session.add(new_item)
##    db.session.commit()
##
##    topic = '九一八'
##    stype = ['sad','angry','happy','sad','angry','happy']
##    ts = [1396368000,1396368000,1396368000,1396454400,1396454400,1396454400]
##    for i in range(0,len(stype)):
##        new_item = SentimentPoint(topic, stype[i], ts[i])
##        db.session.add(new_item)
##    db.session.commit()
##
##    topic = '九一八'
##    stype = ['sad','angry','happy','sad','angry','happy','sad','angry','happy','sad','angry','happy']
##    ts = [1396281600,1396281600,1396281600,1396368000,1396368000,1396368000,1396454400,1396454400,1396454400,1396540800,1396540800,1396540800]
##    count = [400,300,100,600,500,200,400,200,100,500,500,200]
##    for i in range(0,len(stype)):
##        new_item = SentimentCount(topic, ts[i], count[i], stype[i])
##        db.session.add(new_item)
##    db.session.commit()
##
##    topic = '九一八'
##    stype = ['sad','angry','happy','sad','angry','happy','sad','angry','happy','sad','angry','happy']
##    ts = [1396281600,1396281600,1396281600,1396368000,1396368000,1396368000,1396454400,1396454400,1396454400,1396540800,1396540800,1396540800]
##    count = [0.5,0.375,0.125,0.46,0.38,0.16,0.57,0.29,0.14,0.42,0.39,0.19]
##    for i in range(0,len(stype)):
##        new_item = SentimentCountRatio(topic, ts[i], count[i], stype[i])
##        db.session.add(new_item)
##    db.session.commit()
##
##    topic = '九一八'
##    mid = ['12345678990','3879098798','169876098797']
##    weibos = ['难过，这不是篮球范畴里的动作，这也间歇性缩短了他的运动寿命。','普京：互联网就是一个由CIA控制的项目','今日北京晚报，敬请多提宝贵意见。到app store 搜索下载安装“北京晚报”客户端，即可阅读晚报iphone版，欢迎您多提宝贵意见。']
##    user = ['123','356','adniukhn']
##    userid = ['8470987','8097897','90897134']
##    posttime = [1396281600,1396368000,1396454400]
##    weibourl = '#'
##    userurl = '#'
##    repost = 6798
##    stype = ['sad','angry','happy']
##    for i in range(0,len(mid)):
##        new_item = SentimentWeibos(topic, mid[i], weibos[i], user[i], userid[i], posttime[i], weibourl, userurl, repost, stype[i])
##        db.session.add(new_item)
##    db.session.commit()

##    topic = '九一八'
##    keyword = ['日本','钓鱼岛','悲痛']
##    for i in range(0,len(keyword)):
##        new_item = OpinionTopic(topic, keyword[i])
##        db.session.add(new_item)
##    db.session.commit()
##
##    topic = [1,2,3]
##    mid = ['12345678990','3879098798','169876098797']
##    weibos = ['难过，这不是篮球范畴里的动作，这也间歇性缩短了他的运动寿命。','普京：互联网就是一个由CIA控制的项目','今日北京晚报，敬请多提宝贵意见。到app store 搜索下载安装“北京晚报”客户端，即可阅读晚报iphone版，欢迎您多提宝贵意见。']
##    user = ['123','356','adniukhn']
##    userid = ['8470987','8097897','90897134']
##    posttime = [1396281600,1396368000,1396454400]
##    weibourl = '#'
##    userurl = '#'
##    repost = 6798
##    stype = ['sad','angry','happy']
##    for i in range(0,len(mid)):
##        new_item = OpinionWeibos(topic[i], mid[i], weibos[i], user[i], userid[i], posttime[i], weibourl, userurl, repost, stype[i])
##        db.session.add(new_item)
##    db.session.commit()
##
##    topic = [1,2,3]
##    start = [1396281600,1396368000,1396454400]
##    end = [1396368000,1396454400,1396713600]
##    count = 6798
##    opinionWord = ['难过,篮球','普京,互联网','北京,意见,宝贵']
##    positive = [0.3,0.4,0.35]
##    nagetive = [0.7,0.6,0.65]    
##    for i in range(0,len(topic)):
##        new_item = Opinion(topic[i], start[i], end[i], count, opinionWord[i], positive[i], nagetive[i])
##        db.session.add(new_item)
##    db.session.commit()

    topic = [1,1,2,2,2,3,3,3]
    ts = [1396281600,1396368000,1396368000,1396454400,1396454400,1396454400,1396627200,1396713600]
    count = [123,456,679,122,444,567,789,345]  
    for i in range(0,len(topic)):
        new_item = OpinionHot(topic[i], ts[i], count[i])
        db.session.add(new_item)
    db.session.commit()
    
    return json.dumps('Right')
    

    
    
