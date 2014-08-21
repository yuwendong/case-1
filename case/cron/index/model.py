# -*- coding: utf-8 -*-

from consts import db


class IndexTopic(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    topic = db.Column(db.Text)
    count = db.Column(db.Integer) # 微博数
    user_count = db.Column(db.Integer) # 用户数
    begin = db.Column(db.BigInteger(10,unsigned = True)) # 起始时间
    end = db.Column(db.BigInteger(10,unsigned = True)) # 终止时间
    area = db.Column(db.Text) # 地理区域
    key_words = db.Column(db.Text) # 关键词
    opinion = db.Column(db.Text) # 代表文本
    media_opinion = db.Column(db.Text) # 媒体观点

    def __init__(self, topic, count, user_count, begin, end, area, key_words, opinion, media_opinion):
        self.topic = topic
        self.count = count
        self.user_count = user_count
        self.begin = begin
        self.end = end
        self.area = area
        self.key_words = key_words
        self.opinion = opinion
        self.media_opinion = media_opinion
