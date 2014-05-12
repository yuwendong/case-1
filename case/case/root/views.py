# -*- coding: utf-8 -*-

from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
import json
from case.model import *
from case.extensions import db
mod = Blueprint('index', __name__, url_prefix='')

@mod.route('/')
def loading():
    return render_template('root/index.html')

    

    
    
