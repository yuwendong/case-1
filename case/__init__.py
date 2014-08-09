# -*- coding: utf-8 -*-

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from extensions import db, admin
from model_view import SQLModelView
from case.root.views import mod as rootModule
from case.moodlens.views import mod as moodlensModule
from case.opinion.views import mod as opinionModule
from case.propagate.views import mod as propagateModule
from case.index.views import mod as indexModule
from case.evolution.views import mod as evolutionModule
from case.identify.views import mod as identifyModule

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    # Create modules
    app.register_blueprint(rootModule)
    app.register_blueprint(moodlensModule)
    app.register_blueprint(opinionModule)
    app.register_blueprint(propagateModule)
    app.register_blueprint(indexModule)
    app.register_blueprint(evolutionModule)
    app.register_blueprint(identifyModule)

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

    # Create database
    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    # # Create admin
    # admin.init_app(app)
    # for m in model.__all__:
    #     m = getattr(model, m)
    #     n = m._name()
    #     admin.add_view(SQLModelView(m, db.session, name=n))

    return app
