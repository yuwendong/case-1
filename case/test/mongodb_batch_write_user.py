#-*-coding=utf-8-*-

import md5
import time
import pymongo
from pprint import pprint
from pymongo.errors import BulkWriteError
from datetime import datetime
from xapian_case.xapian_backend import XapianSearch

MASTER_TIMELINE_54API_MONGOD_HOST = "219.224.135.46"
MASTER_TIMELINE_54API_MONGOD_PORT = 27019
MASTER_TIMELINE_54API_WEIBO_DB = "54api_weibo_v2"
XAPIAN_USER_FIELDS = ['_id', 'province', 'city', 'verified', 'name', 'friends_count', \
        'gender', 'profile_image_url', 'verified_type', 'followers_count', 'followers', \
        'location', 'statuses_count', 'friends', 'description', 'created_at']
MONGODB_USER_KEYS = ['id', 'name', 'gender', 'province', 'city', 'location', \
        'description', 'verified', 'followers_count', \
        'statuses_count', 'friends_count', 'profile_image_url', \
        'bi_followers_count', 'verified_reason', 'verified_type', 'created_at']

XAPIAN_USER_DATA_PATH = "/mnt/mfs/xapian_user/"
XAPIAN_FLUSH_DB_SIZE = 10000
MONGODB_BATCH_SIZE = 10000
MYSQL_BATCH_SIZE = 10000


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print '%r args: %s %2.2f sec' % (method.__name__, args, te - ts)
        return result
    return timed

@timeit
def _default_mongo(host=MASTER_TIMELINE_54API_MONGOD_HOST, \
    port=MASTER_TIMELINE_54API_MONGOD_PORT, usedb=MASTER_TIMELINE_54API_WEIBO_DB):
    # 强制写journal，并强制safe
    connection = pymongo.MongoClient(host=host, port=port, j=True, w=1)
    db = connection.admin
    # db.authenticate('root', 'root')
    db = getattr(connection, usedb)
    return db

@timeit
def init_xapian_user():
    xapian_search_user = XapianSearch(path=XAPIAN_USER_DATA_PATH, name='master_timeline_user', schema_version=1)
    return xapian_search_user

@timeit
def test_xapian_user_iter_all_docs(xapian_search_user):
    count = 0
    tb = time.time()
    ts = tb
    docs = xapian_search_user.iter_all_docs(fields=XAPIAN_USER_FIELDS)
    for doc in docs:
        for field in XAPIAN_USER_FIELDS:
            doc[field]

        count += 1
        if count % XAPIAN_FLUSH_DB_SIZE == 0:
            te = time.time()
            print '[%s] deliver speed: %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), te - ts, XAPIAN_FLUSH_DB_SIZE)
            if count % (XAPIAN_FLUSH_DB_SIZE * 10) == 0:
                print '[%s] total deliver %s, cost: %s sec [avg: %sper/sec]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, te - tb, count / (te - tb))
            ts = te


def itemXapian2Mongo(item):
    result = dict()
    for key in MONGODB_USER_KEYS:
        if key == 'id':
            result[key] = item['_id']
        elif key == 'bi_followers_count':
            result[key] = None
        elif key == 'verified_reason':
            result[key] = None
        elif key in ['friends_count', 'statuses_count', 'followers_count']:
            result[key] = int(item[key])
        elif key == 'created_at':
            result['timestamp'] = item[key]
        else:
            result[key] = item[key]
        result['_id'] = item['_id']
        result['domain'] = None
        result['followers'] = []
        result['friends'] = []
        result['allow_all_act_msg'] = None
        result['geo_enabled'] = None
        result['favourites_count'] = None
        result['url'] = None

    return result

@timeit
def test_xapian_user_write2mongo(xapian_search_user):
    collection_name = "master_timeline_user"
    mongo = _default_mongo()

    count = 0
    tb = time.time()
    ts = tb
    docs = xapian_search_user.iter_all_docs(fields=XAPIAN_USER_FIELDS)
    for doc in docs:
        doc = itemXapian2Mongo(doc)

        if mongo[collection_name].find({"_id": doc["_id"]}).count():
            pass
        else:
            doc['last_modify'] = time.time()
            doc['first_in'] = doc['last_modify']
            mongo[collection_name].insert(doc)

        count += 1
        if count % XAPIAN_FLUSH_DB_SIZE == 0:
            te = time.time()
            print '[%s] deliver speed: %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), te - ts, XAPIAN_FLUSH_DB_SIZE)
            if count % (XAPIAN_FLUSH_DB_SIZE * 10) == 0:
                print '[%s] total deliver %s, cost: %s sec [avg: %sper/sec]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, te - tb, count / (te - tb))
            ts = te

@timeit
def test_xapian_user_save2mongo(xapian_search_user):
    collection_name = "master_timeline_user"
    mongo = _default_mongo()

    count = 0
    tb = time.time()
    ts = tb
    docs = xapian_search_user.iter_all_docs(fields=XAPIAN_USER_FIELDS)
    for doc in docs:
        doc = itemXapian2Mongo(doc)

        doc['last_modify'] = time.time()
        doc['first_in'] = doc['last_modify']
        mongo[collection_name].save(doc)

        count += 1
        if count % XAPIAN_FLUSH_DB_SIZE == 0:
            te = time.time()
            print '[%s] deliver speed: %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), te - ts, XAPIAN_FLUSH_DB_SIZE)
            if count % (XAPIAN_FLUSH_DB_SIZE * 10) == 0:
                print '[%s] total deliver %s, cost: %s sec [avg: %sper/sec]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, te - tb, count / (te - tb))
            ts = te

mongos_host_port = ['219.224.135.46:27019', '219.224.135.47:27019', \
        '219.224.135.48:27019', '219.224.135.60:27019', \
        '219.224.135.126:27019']

mongos_list = []
for mongo in mongos_host_port:
    mongo_host = mongo.split(":")[0]
    mongo_port = int(mongo.split(":")[1])
    mongos = _default_mongo(host=mongo_host, port=mongo_port, usedb=MASTER_TIMELINE_54API_WEIBO_DB)
    mongos_list.append(mongos)


def mongos_hash(idstr):
    key = gen_key(idstr)
    mongos = mongos_list[key % len(mongos_list)]

    return mongos

@timeit
def test_xapian_user_hash_write2mongo(xapian_search_user):
    collection_name = "master_timeline_user"

    count = 0
    tb = time.time()
    ts = tb
    docs = xapian_search_user.iter_all_docs(fields=XAPIAN_USER_FIELDS)
    for doc in docs:
        doc = itemXapian2Mongo(doc)

        mongo = mongos_hash(str(doc["id"]))
        if mongo[collection_name].find({"_id": doc["_id"]}).count():
            pass
        else:
            doc['last_modify'] = time.time()
            doc['first_in'] = doc['last_modify']
            mongo[collection_name].insert(doc)

        count += 1
        if count % XAPIAN_FLUSH_DB_SIZE == 0:
            te = time.time()
            print '[%s] deliver speed: %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), te - ts, XAPIAN_FLUSH_DB_SIZE)
            if count % (XAPIAN_FLUSH_DB_SIZE * 10) == 0:
                print '[%s] total deliver %s, cost: %s sec [avg: %sper/sec]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, te - tb, count / (te - tb))
            ts = te

@timeit
def test_xapian_user_batch_save2mongo(xapian_search_user):
    collection_name = "master_timeline_user"
    mongo = _default_mongo()

    count = 0
    tb = time.time()
    ts = tb
    bulk = mongo[collection_name].initialize_unordered_bulk_op()
    docs = xapian_search_user.iter_all_docs(fields=XAPIAN_USER_FIELDS)
    for doc in docs:
        doc = itemXapian2Mongo(doc)
        doc['last_modify'] = time.time()
        doc['first_in'] = doc['last_modify']

        bulk.find({"id": doc["_id"]}).upsert().update({"$set": doc})
        if count % XAPIAN_FLUSH_DB_SIZE == 0:
            te = time.time()
            print '[%s] deliver speed: %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), te - ts, XAPIAN_FLUSH_DB_SIZE)
            if count % (XAPIAN_FLUSH_DB_SIZE * 10) == 0:
                print '[%s] total deliver %s, cost: %s sec [avg: %sper/sec]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, te - tb, count / (te - tb))
            ts = te

        if count % MONGODB_BATCH_SIZE == 0:
            try:
                result = bulk.execute()
            except BulkWriteError as bwe:
                pprint(bwe.details)
            bulk = mongo[collection_name].initialize_unordered_bulk_op()

        count += 1

    try:
        result = bulk.execute()
    except BulkWriteError as bwe:
        pprint(bwe.details)


def gen_key(key):
    """Given a string key it returns a long value,
       this long value represents a place on the hash ring.

       md5 is currently used because it mixes well.
    """
    m = md5.new()
    m.update(key)
    return long(m.hexdigest(), 16)

from sqlalchemy import Table, Column, BigInteger, String, Float, MetaData, create_engine

MYSQL_USER = 'root'
MYSQL_HOST = '219.224.135.46'
#MYSQL_PORT = 8066
MYSQL_PORT = 3306
#MYSQL_DB = 'production_cobar_schema'
MYSQL_DB = 'weibo'
engine = create_engine('mysql+mysqldb://%s:@%s:%s/%s?charset=utf8' % (MYSQL_USER, MYSQL_HOST, MYSQL_PORT, MYSQL_DB),
        echo=False, convert_unicode=True)
metadata = MetaData()
users = Table('master_timeline_user', metadata,
        Column('id', BigInteger, primary_key=True, autoincrement=False),
        Column('_id', BigInteger),
        Column('name', String(30)),
        Column('gender', String(10)),
        Column('province', String(10)),
        Column('city', String(10)),
        Column('location', String(40)),
        Column('description', String(140)),
        Column('verified', String(10)),
        Column('followers_count', BigInteger),
        Column('statuses_count', BigInteger),
        Column('friends_count', BigInteger),
        Column('profile_image_url', String(50)),
        Column('bi_followers_count', BigInteger),
        Column('verified_reason', String(200)),
        Column('verified_type', String(10)),
        Column('created_at', String(20)),
        Column('domain', String(10)),
        Column('last_modify', Float),
        Column('first_in', Float),
        Column('timestamp', BigInteger),
        Column('allow_all_act_msg', String(10)),
        Column('geo_enabled', String(10)),
        Column('favourites_count', BigInteger),
        Column('url', String(50)),
        Column('friends', String(10)),
        Column('followers', String(10))
)

def create_mysql_table():
    metadata.create_all(engine)

def test_xapian_user2cobar(xapian_search_user):
    conn = engine.connect()

    count = 0
    tb = time.time()
    ts = tb
    docs = xapian_search_user.iter_all_docs(fields=XAPIAN_USER_FIELDS)
    batches = []
    for doc in docs:
        doc = itemXapian2Mongo(doc)
        doc['last_modify'] = time.time()
        doc['first_in'] = doc['last_modify']
        doc['friends'] = None
        doc['followers'] = None

        batches.append(doc)
        if count % XAPIAN_FLUSH_DB_SIZE == 0:
            te = time.time()
            print '[%s] deliver speed: %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), te - ts, XAPIAN_FLUSH_DB_SIZE)
            if count % (XAPIAN_FLUSH_DB_SIZE * 10) == 0:
                print '[%s] total deliver %s, cost: %s sec [avg: %sper/sec]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, te - tb, count / (te - tb))
            ts = te

        if count % MYSQL_BATCH_SIZE == 0:
            conn.execute(users.insert(), batches)
            batches = []

        count += 1


if __name__ == '__main__':
    xapian_search_user = init_xapian_user()

    #test_xapian_user_iter_all_docs(xapian_search_user)

    #test_xapian_user_write2mongo(xapian_search_user)

    #test_xapian_user_hash_write2mongo(xapian_search_user)

    #test_xapian_user_save2mongo(xapian_search_user)

    #test_xapian_user_batch_save2mongo(xapian_search_user)

    create_mysql_table()

    test_xapian_user2cobar(xapian_search_user)
