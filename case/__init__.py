# -*- coding: utf-8 -*-

import model
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from extensions import db, admin, mongo
from global_config import MYSQL_HOST, MYSQL_USER, MYSQL_DB, MONGODB_HOST, MONGODB_PORT
from model_view import SQLModelView
from case.root.views import mod as rootModule
from case.moodlens.views import mod as moodlensModule
from case.opinion.views import mod as opinionModule
from case.propagate.views import mod as propagateModule
from case.index.views import mod as indexModule
from case.evolution.views import mod as evolutionModule
from case.identify.views import mod as identifyModule
from case.quota_system.views import mod as quota_systemModule
from case.dataout.views import mod as dataoutModule

def create_app():
    app = Flask(__name__)

    # Create modules
    app.register_blueprint(rootModule)
    app.register_blueprint(moodlensModule)
    app.register_blueprint(opinionModule)
    app.register_blueprint(propagateModule)
    app.register_blueprint(indexModule)
    app.register_blueprint(evolutionModule)
    app.register_blueprint(identifyModule)
    app.register_blueprint(quota_systemModule)
    app.register_blueprint(dataoutModule)

    # the debug toolbar is only enabled in debug mode
    app.config['DEBUG'] = True

    app.config['ADMINS'] = frozenset(['youremail@yourdomain.com'])
    app.config['SECRET_KEY'] = 'SecretKeyForSessionSigning'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://%s:@%s/%s?charset=utf8' % (MYSQL_USER, MYSQL_HOST, MYSQL_DB)
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['DATABASE_CONNECT_OPTIONS'] = {}

    app.config['THREADS_PER_PAGE'] = 8

    app.config['CSRF_ENABLED'] = True
    app.config['CSRF_SESSION_KEY'] = 'somethingimpossibletoguess'

    # Enable the toolbar?
    app.config['DEBUG_TB_ENABLED'] = app.debug
    # Should intercept redirects?
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
    # Enable the profiler on all requests, default to false
    app.config['DEBUG_TB_PROFILER_ENABLED'] = True
    # Enable the template editor, default to false
    app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
    # debug toolbar
    # toolbar = DebugToolbarExtension(app)

    app.config['MONGO_HOST'] = MONGODB_HOST
    app.config['MONGO_PORT'] = MONGODB_PORT

    # Create mysql database
    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    # # Create mysql database admin, visit via url: http://HOST:PORT/admin/
    admin.init_app(app)
    for m in model.__all__:
        m = getattr(model, m)
        n = m._name()
        admin.add_view(SQLModelView(m, db.session, name=n))
    
    # init mongo
    mongo.init_app(app)

    return app
