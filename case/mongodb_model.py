# -*- coding: utf-8 -*-
"""Define mongoengine documents
"""

from extensions import mongo_engine as db

__all__ = ['MasterTimelineTopic']


class MasterTimelineTopic(db.Document):
    name = db.StringField(max_length=40)
    start = db.StringField(max_length=40)
    end = db.StringField(max_length=40)

    def __unicode__(self):
        return self.name

