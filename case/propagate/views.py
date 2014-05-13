#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import os
import json
from utils import *

mod = Blueprint('propagate', __name__, url_prefix='/propagate')

@mod.route('/weibo')
def weibo():
    return render_template('propagate/ajax_contents.html')

@mod.route('/ajax_contents')
def contents():
    return render_template('propagate/ajax_contents.html')

@mod.route('/ajax_path')
def path():
    return render_template('propagate/ajax_path.html')

@mod.route('/ajax_track_source')
def track_source():
    return render_template('propagate/ajax_track_source.html')

@mod.route('/ajax_key_person')
def key_person():
    return render_template('propagate/ajax_key_person.html')

@mod.route('/ajax_media')
def media():
    return render_template('propagate/ajax_media.html')

@mod.route('/test')
def test():
    return render_template('propagate/test.html')


   





