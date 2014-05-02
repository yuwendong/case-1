#-*- coding:utf-8 -*-
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import os

mod = Blueprint('moodlens', __name__, url_prefix='/moodlens')

@mod.route('/')
def weibo():
    return render_template('moodlens/weibo.html')
