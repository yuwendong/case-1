#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-28 14:00:00
# Version: 0.3.0
"""MONGODB数据库操作的封装
"""

import time
from global_utils import _default_mongo, _default_mongo_db
from global_config import OPINION_MONGODB_NAME, EVENTS_COLLECTION, \
        EVENTS_NEWS_COLLECTION_PREFIX, SUB_EVENTS_COLLECTION, \
        SUB_EVENTS_FEATURE_COLLECTION


class EventManager(object):
    """话题管理类
    """
    def __init__(self):
        self.mongo = _default_mongo(usedb=OPINION_MONGODB_NAME)

    def getEvents(self):
        """获取话题
        """
        results = self.mongo[EVENTS_COLLECTION].find()
        return [r for r in results]

    def getActiveEventIDs(self, timestamp):
        """获取活跃话题的ID
           input:
               timestamp: 检测的时间点, 话题的创建时间要小于检测的时间点
           output:
               活跃的话题ID
        """
        results = self.mongo[EVENTS_COLLECTION].find({"status": "active", "startts": {"$lte": timestamp}})
        return [r['_id'] for r in results]

    def terminateEvent(self, eventid, endts=int(time.time())):
        """终止事件
           input:
               eventid: 事件ID
               endts: 终止时间
        """
        event = Event(eventid)
        event.terminate()
        event.setEndts(endts)

    def getEventIDByName(self, name):
        result = self.mongo[EVENTS_COLLECTION].find_one({"topic": name})
        if result:
            return result['_id']
        else:
            return None

    def checkActive(self, timestamp):
        """根据话题新文本数检查话题的活跃性, 更新不再活跃的话题的status
           input:
               timestamp: 检测的时间点
           output:
               活跃的话题ID
        """
        active_ids = []
        ids = self.getActiveEventIDs(timestamp)
        for id in ids:
            event = Event(id)
            if event.check_ifactive(timestamp):
                active_ids.append(id)
            else:
                event.terminate()
                event.setEndts(timestamp)

        return active_ids

    def getInitializingEventIDs(self, timestamp):
        """获取正在初始化的话题ID
           input:
               timestamp: 检测的时间点
           output:
               正在初始化的话题ID
        """
        results = self.mongo[EVENTS_COLLECTION].find({"status": "initializing", "startts": {"$lte": timestamp}})
        return [r['_id'] for r in results]

class Event(object):
    """话题类
    """
    def __init__(self, id):
        """初始化话题实例，输入为话题ID，ObjectID
        """
        self.id = id
        self.other_subeventid = self.getOtherSubEventID()
        self.news_collection = EVENTS_NEWS_COLLECTION_PREFIX + str(id)
        self.sub_events_collection = SUB_EVENTS_COLLECTION
        self.events_collection = EVENTS_COLLECTION
        self.mongo = _default_mongo(usedb=OPINION_MONGODB_NAME)

    def getOtherSubEventID(self):
        """获取其他类ID，该ID是预留的
           规则为eventid + '_other'
        """
        return str(self.id) + '_other'

    def get_subevent_addsize(self, subeventid):
        """获取子事件的增幅
        """
        result = self.mongo[SUB_EVENTS_COLLECTION].find_one({"_id": subeventid})
        if result:
            if "addsize" in result:
                return result["addsize"]

        return 0

    def get_subevent_tfidf(self, subeventid):
        """获取子事件的tfidf
        """
        result = self.mongo[SUB_EVENTS_COLLECTION].find_one({"_id": subeventid})
        if result:
            if "tfidf" in result:
                return result["tfidf"]

        return 0

    def get_subevent_startts(self, subeventid):
        """获取子事件的创建时间
        """
        result = self.mongo[SUB_EVENTS_COLLECTION].find_one({"_id": subeventid})
        if result:
            return result['timestamp']

    def getEventRiverData(self, startts, endts, topk_keywords=5, sort="weight"):
        """获取echarts event river的数据
           input:
               startts: 起时间戳
               endts: 止时间戳
               topk_keywords: 取每个子事件的topk keywords
               sort: 子事件排序的依据, 默认是weight，热度，可选的包括"addweight", "created_at", "tfidf"
        """
        results = self.mongo[self.news_collection].find({"timestamp": {"$gte": startts, "$lt": endts}, "$and": \
                [{"subeventid": {"$ne": self.other_subeventid}}, \
                {"subeventid": {"$exists": True}}]})

        cluster_date = dict()
        cluster_news = dict()
        global_dates_set = set()
        for r in results:
            label = r['subeventid']
            timestamp = r['timestamp']
            date = time.strftime('%Y-%m-%d', time.localtime(timestamp))
            global_dates_set.add(date)
            try:
                cluster_date[label].append(date)
            except KeyError:
                cluster_date[label] = [date]

            try:
                cluster_news[label].append(r)
            except KeyError:
                cluster_news[label] = [r]

        from collections import Counter
        results = []
        total_weight = 0
        for label, dates in cluster_date.iteritems():
            news_list = cluster_news[label]
            subevent_news = sorted(news_list, key=lambda news: news['weight'], reverse=True)[0]

            feature = Feature(label)
            fwords = feature.get_newest()
            counter = Counter(fwords)
            top_words_count = counter.most_common(topk_keywords)
            cluster_keywords = ','.join([word for word, count in top_words_count])

            counter = Counter(dates)
            date_count_dict = dict(counter.most_common())
            sorted_date_count = sorted(date_count_dict.iteritems(), key=lambda(k, v): k, reverse=False)
            evolution_list = [{"time": date, "value": count, "detail": {"text": str(count), "link": "#"}} for date, count in sorted_date_count]
            added_count = self.get_subevent_addsize(label)
            tfidf = self.get_subevent_tfidf(label)
            created_at = self.get_subevent_startts(label)
            total_weight += len(dates)
            cluster_result = {"id": label, "news": subevent_news, "name": cluster_keywords, "weight": len(dates), "addweight": added_count, "created_at": created_at, 'tfidf': tfidf, "evolution": evolution_list}
            results.append(cluster_result)

        results = sorted(results, key=lambda k: k[sort], reverse=True)
        sorted_dates = sorted(list(global_dates_set))

        return results, sorted_dates, total_weight

class Feature(object):
    """特征词类, 按子事件组织
    """
    def __init__(self, subeventid):
        """初始化特征词类
           input
               subeventid: 子事件ID
        """
        self.subeventid = subeventid
        self.mongo = _default_mongo(usedb=OPINION_MONGODB_NAME)

    def upsert_newest(self, words):
        """存储子事件最新存量的特征词，pattern为"newest", top100, 为新文本分类服务, upsert模式
        """
        self.mongo[SUB_EVENTS_FEATURE_COLLECTION].update({"subeventid": self.subeventid, "pattern": "newest"}, \
                {"subeventid": self.subeventid, "pattern": "newest", "feature": words}, upsert=True)

    def get_newest(self):
        """获取子事件最新存量的特征词, pattern为"newest", top100, 为新文本分类服务
        """
        result = self.mongo[SUB_EVENTS_FEATURE_COLLECTION].find_one({"subeventid": self.subeventid, "pattern": "newest"})
        if result:
            return result["feature"]
        else:
            return {}

    def set_range(self, words, start_ts, end_ts):
        """计算子事件某时间范围的特征词并存储
        """
        pass

    def get_range(self):
        """获取子事件某时间范围的特征词
        """
        pass

    def clear_all_features(self):
        """清除pattern为regular和newest的特征词
        """
        self.mongo[SUB_EVENTS_FEATURE_COLLECTION].remove({"subeventid": self.subeventid})
