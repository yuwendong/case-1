#-*- coding:utf-8 -*-
import os
import json
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
# from read_quota import ReadTopic


mod = Blueprint('quota_system', __name__, url_prefix='/quota_system')


'''
实际上这一部分需要通过查询Topic这张表来获取相关指标，具体触发这一部分还需要与前台进行沟通。
目前这一部分仅作为测试后台数据显示用
'''

@mod.route('/topic/')
def system_topic():
    topic = request.args.get('topic', '')
    quota_system_dict = ReadTopic(topic)
    
    return json.dumps(quota_system_dict)

