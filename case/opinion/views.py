#-*- coding:utf-8 -*-
import os
import json
from get_result import get_opinion_time, get_opinion_ratio, get_opinion_keywords, get_opinion_weibos
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect


mod = Blueprint('opinion', __name__, url_prefix='/opinion')

@mod.route('/time/')
def opinion_time():
    topic = request.args.get('topic', '')
    results = get_opinion_time(topic) # results=[{childtopic:[start_ts, end_ts]},....]
    return json.dumps(results)

@mod.route('/ratio/')
def opinion_ratio():
    topic = request.args.get('topic', '')
    results = get_opinion_ratio(topic) # results=[{childtopic:ratio},....]
    return json.dumps(results)

@mod.route('/keywords/')
def opinion_keywords():
    topic = request.args.get('topic', '')
    results = get_opinion_keywords(topic) # results=[{childtopic:[(keywords,weight)]},.....]
    return json.dumps(results)

@mod.route('/weibos/')
def opinion_weibos():
    topic = request.args.get('topic', '')
    results = get_opinion_weibos(topic) # results=[{childtopic:[{weibos,weight}]},.....]
    return json.dumps(results)
    
