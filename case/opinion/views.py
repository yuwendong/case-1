#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import os

mod = Blueprint('opinion', __name__, url_prefix='/opinion')

@mod.route('/')
def index():
    return render_template('opinion/index.html')

@mod.route('/weibo')
def weibo():
    return render_template('opinion/meaning.html')
