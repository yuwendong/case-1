# -*- coding: utf-8 -*-

from flask import Blueprint

mod = Blueprint('index', __name__, url_prefix='')

@mod.route('/')
def loading():
    return 'hello world'
