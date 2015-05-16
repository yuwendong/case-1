# -*- coding: utf-8 -*-

import os

SPIDER_MODULES = ['dogapi.spiders']
NEWSPIDER_MODULE = 'dogapi.spiders'
# BOT_NAME = 'weibo'


# enables scheduling storing requests queue in redis
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# don't cleanup redis queues, allows to pause/resume crawls
# SCHEDULER_PERSIST = True

# Schedule requests using a priority queue. (default)
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'

# Schedule requests using a queue (FIFO).
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderQueue'

# Schedule requests using a stack (LIFO).
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderStack'

# Max idle time to prevent the spider from being closed when distributed crawling.
# This only works if queue class is SpiderQueue or SpiderStack,
# and may also block the same time when your spider start at the first time (because the queue is empty).

# SCHEDULER_IDLE_BEFORE_CLOSE = 10

# The amount of time (in secs) that the downloader should wait 
# before downloading consecutive pages from the same spider
DOWNLOAD_DELAY = 0.5 # 50 ms of delay

# If enabled, Scrapy will wait a random amount of time 
# (between 0.5 and 1.5 * DOWNLOAD_DELAY) while fetching requests 
# from the same spider.
# This randomization decreases the chance of the crawler 
# being detected (and subsequently blocked) by sites which analyze 
# requests looking for statistically significant similarities in 
# the time between their requests.
# RANDOMIZE_DOWNLOAD_DELAY = True


# 期望减少mongodb的压力
# Maximum number of concurrent items (per response) to process in parallel in ItemPipeline, Default 100
CONCURRENT_ITEMS = 100
# The maximum number of concurrent (ie. simultaneous) requests that will be performed by the Scrapy downloader, Default 16.
CONCURRENT_REQUESTS = 2
# The maximum number of concurrent (ie. simultaneous) requests that will be performed to any single domain, Default: 8.
CONCURRENT_REQUESTS_PER_DOMAIN = 1


# 不需要默认的180秒,更多的机会留给重试
# The amount of time (in secs) that the downloader will wait before timing out, Default: 180.
DOWNLOAD_TIMEOUT = 15

AUTOTHROTTLE_ENABLED = True # Enables the AutoThrottle extension.
AUTOTHROTTLE_START_DELAY = 2.0 # The initial download delay (in seconds).Default: 5.0
AUTOTHROTTLE_MAX_DELAY = 60.0 # The maximum download delay (in seconds) to be set in case of high latencies.
AUTOTHROTTLE_CONCURRENCY_CHECK_PERIOD = 100 # How many responses should pass to perform concurrency adjustments.
AUTOTHROTTLE_DEBUG = True


# middlewares 的意思是在engine和download handler之间有一层，包括进入download
# handler之前和从download handler出来之后，同理spider (handler)
# retry 直接在downloader middlewares这一层处理
# 将400 403等有用的预知的错误留给spider middlewares处理

# ** ** ** ** ** ** ** ** ** **
# downloadermiddleware 1 process_request
# ** ** ** ** ** ** ** ** ** **
# downloadermiddleware 2 process_request
# ** ** ** ** ** ** ** ** ** **
# downloadermiddleware 2 process_response
# ** ** ** ** ** ** ** ** ** **
# downloadermiddleware 1 process_response
# ** ** ** ** ** ** ** ** ** **
# spidermiddleware 1 process_spider_input
# ** ** ** ** ** ** ** ** ** **
# spidermiddleware 2 process_spider_input
# spider parse
# ** ** ** ** ** ** ** ** ** **
# spidermiddleware 2 process_spider_output
# ** ** ** ** ** ** ** ** ** **
# spidermiddleware 1 process_spider_output

RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

SPIDER_MIDDLEWARES = {
    'dogapi.middlewares.middlewares.ErrorRequestMiddleware': 40,
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None,
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': None,
    'scrapy.contrib.spidermiddleware.urllength.UrlLengthMiddleware': None,
    'scrapy.contrib.spidermiddleware.depth.DepthMiddleware': None,
    # 如果process_spider_input或spider里抛出错误，
    # process_spider_exception是反向执行的，即要想记录错误得先过sentry，在捕获重试
    'dogapi.middlewares.middlewares.RetryErrorResponseMiddleware': 940,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': None,
    'scrapy.contrib.downloadermiddleware.httpauth.HttpAuthMiddleware': None,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'scrapy.contrib.downloadermiddleware.defaultheaders.DefaultHeadersMiddleware': None,
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': None,
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': None,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,
    'scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware': None,
}

ITEM_PIPELINES = [
    'dogapi.pipelines.mongodbPipeline.MongodbPipeline',
    # '54api.scrapy_weibo.pipelines.jsonWriterPipeline.JsonWriterPipeline',
]

EXTENSIONS = {
    'scrapy.webservice.WebService': None,
    'scrapy.telnet.TelnetConsole': None
}

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

#dev
#REDIS_HOST = 'localhost'
#REDIS_PORT = 6379
MONGOD_HOST = 'localhost'
MONGOD_PORT = 27017
MASTER_TIMELINE_54API_MONGOD_HOST = '219.224.135.47'
MASTER_TIMELINE_54API_MONGOD_PORT = 27019
MASTER_TIMELINE_54API_WEIBO_DB = '54api_weibo_v2'
MASTER_TIMELINE_54API_USER_COLLECTION = 'master_timeline_user'
#MASTER_TIMELINE_54API_WEIBO_COLLECTION = 'master_timeline_weibo'
#MASTER_TIMELINE_54API_WEIBO_DAILY_COLLECTION_PREFIX = 'master_timeline_weibo_weekly_'
API_SERVER_HOST = '219.224.135.47'
API_SERVER_PORT = 9115
API_SERVER_80_PORT = 80
SEARCH_SPIDER_SEARCH_TYPE = 1
WEIBO_USER_SPIDER_SEARCH_TYPE = 2
#RE_LIST_SPIDER_SEARCH_TYPE = 4
#CMT_LIST_SPIDER_SEARCH_TYPE = 5
#CMT_STATUS_SEARCH_TYPE = 6
#SHOW_BATCH_SPIDER_SEARCH_TYPE = 8
#USER_WEIBO_SPIDER_SEARCH_TYPE = 9
PER_IP_HOURS_LIMIT = 40000
BUFFER_SIZE = 20
RETRY_TIMES = 3 - 1
