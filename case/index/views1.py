#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import json
from case.model import *
from case.extensions import db
mod = Blueprint('case', __name__, url_prefix='/index')

@mod.route('/')
def loading():
    return render_template('index/gl.html')

@mod.route('/detail/')
def detail():
    return render_template('index/detail.html')
