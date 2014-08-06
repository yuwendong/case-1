# -*- coding: utf-8 -*-
import time
from config import db # 在mysql中存储topic是否计算的状态标注
from model import TopicStatus

NOT_CALC_STATUS = -1 # 未计算
IN_CALC_STATUS = 0 # 正在计算
COMPLETED_STATUS = 1 # 已计算


def _topic_not_calc(status=NOT_CALC_STATUS, module='identify'): # 查询未计算的topic
    topics_list = []
    topics = db.session.query(TopicStatus).filter(TopicStatus.status==status, \
                                                  TopicStatus.module==module).all()
    for topic in topics:
        topics_list.append(topic)

    return topics_list


def _topic_calculating(status=IN_CALC_STATUS, module='identify'): # 查询正在计算的topic
    topics_list = []
    topics = TopicStatus.query.filter_by(status=status, module=module).all()
    for topic in topics:
        topics_list.append(topic.topic)

    return topics_list


def _topic_completed(status=COMPLETED_STATUS, module='identify'): # 查询已计算的topic
    topics_list = []
    topics = TopicStatus.query.filter_by(status=status, module=module).all()
    for topic in topics:
        topics_list.append(topic.topic)

    return topics_list


def _update_topic_status2Computing(topic, start, end, db_date, module='identify'): # 更新：未计算>>正在计算的topic
    item = TopicStatus(module, IN_CALC_STATUS, topic, start, end, db_date)
    item_exist = db.session.query(TopicStatus).filter(TopicStatus.module==module, \
                                                      TopicStatus.status==NOT_CALC_STATUS, \
                                                      TopicStatus.topic==topic, \
                                                      TopicStatus.start==start, \
                                                      TopicStatus.end==end, \
                                                      TopicStatus.db_date==db_date).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()


def _update_topic_status2Completed(topic, start, end, db_date, module='identify'): # 更新：正在计算>>已完成计算
    item = TopicStatus(module, COMPLETED_STATUS, topic, start, end, db_date)
    item_exist = db.session.query(TopicStatus).filter(TopicStatus.module==module, \
                                                      TopicStatus.status==IN_CALC_STATUS, \
                                                      TopicStatus.topic==topic, \
                                                      TopicStatus.start==start, \
                                                      TopicStatus.end==end, \
                                                      TopicStatus.db_date==db_date).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()

'''
def _drop_item(topic, start, end, db_date, status, module='identify'): # 记录并不存在删除，这个应该不要
    item_exist = db.session.query(TopicStatus).filter(TopicStatus.module==module, \
                                                      TopicStatus.status==IN_CALC_STATUS, \
                                                      TopicStatus.topic==topic, \
                                                      TopicStatus.start==start, \
                                                      TopicStatus.end==end, \
                                                      TopicStatus.db_date==db_date).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.commit()
'''

if __name__ == '__main__':
    _update_topic_status2Completed('高考', 1377964800, 1378051200)
    #_drop_item('日本', 1377964800, 1378310400, IN_CALC_STATUS)
    #_add_not_start_topic('开学')
