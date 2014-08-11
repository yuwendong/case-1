# -*- coding: utf-8 -*-
from sqlalchemy import func
from case.extensions import db
from time_utils import datetime2ts
from case.model import TopicIdentification   #需要查询的表

def rank_results(topic, windowsize, date):
    item = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topic, \
                                                        TopicIdentification.identifyDate==date, \
                                                        TopicIdentification.identifyWindow==windowsize).first()
    if item:
        return item
    else:
        return None



