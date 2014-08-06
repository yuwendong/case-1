#-*-coding:utf-8-*-

import redis

"""dependence: 
   1. import redis (Redis Python Client)
      安装https://github.com/andymccurdy/redis-py.git
      用法参考https://github.com/andymccurdy/redis-py/blob/master/redis/client.py
"""

class Schema:
    """定义用户的结构
    """
    v1 = {
        'fields': [u'domain', u'last_modify', u'id', u'city', u'verified', u'followers_count', u'followers', u'location', u'verified_type', u'province', u'statuses_count', u'description', u'friends_count', u'first_in', u'timestamp', u'allow_all_act_msg', u'profile_image_url', u'geo_enabled', u'friends', u'favourites_count', u'name', u'url', u'gender', u'created_at', u'_id']
    }

    v2 = {
        'fields': [u'active', u'last_modify', u'id', u'city', u'verified', u'followers_count', u'followers', u'location', u'verified_type', u'province', u'statuses_count', u'description', u'friends_count', u'first_in', u'profile_image_url', u'friends', u'name', u'gender', u'_id', u'bi_followers_count', u'verified_reason']
    }

# user_classify
"""dependence:
   1. from xapian_case.utils import load_scws, cut
      安装https://github.com/linhaobuaa/xapian_case.git
"""
# 用户中文领域标签v1
DOMAIN_V1_ZH_LIST = [u'高校微博', u'境内机构', u'境外机构', u'媒体', \
        u'境外媒体', u'民间组织', u'律师', u'政府官员', \
        u'媒体人士', u'活跃人士', u'草根', u'其他']
# 用户英文领域标签v1
DOMAIN_V1_LIST = ['university', 'homeadmin', 'abroadadmin', 'homemedia', \
        'abroadmedia', 'folkorg', 'lawyer', 'politician', \
        'mediaworker', 'activer', 'grassroot', 'other']
# 用户英文领域标签v2
DOMAIN_V2_LIST = ["culture", "entertainment", "fashion", \
        "education", "finance", "sports", "technology", "media"]
# 用户中文领域标签v2
DOMAIN_V2_ZH_LIST = [u'文化', u'娱乐', u'时尚', \
        u'教育', u'财经', u'体育', u'科技', u'媒体']
# 用户英文领域标签v3
DOMAIN_V3_LIST = ['folk', 'media', 'opinion_leader', \
        'oversea', 'other']
# 用户中文领域标签v3
DOMAIN_V3_ZH_LIST = [u'民众', u'媒体', u'意见领袖', u'境外', u'其他']
# 根据location中的境外词汇判断
OVERSEA_WORDS = set([u'海外', u'香港', u'台湾', u'澳门'])
# 律师词汇
LAWYER_WORDS = set([u'律师', u'法律', u'法务', u'辩护'])
# 政府官员词汇
ADMIN_WORDS_FILE = 'admin_words.txt'
# 媒体人士词汇
MEDIA_WORDS_FILE = 'media_words.txt'
# 活跃人士阀值
STATUSES_COUNT_THRESHOLD = 4000
FOLLOWERS_COUNT_THRESHOLD = 1000
# 用户csv数据v1版
MASTER_TIMELINE_USER_CSV_V1 = '/home/ubuntu3/linhao/case/data/master_timeline_user_csv/master_timeline_user_20140802_v1.csv'
# 用户分类v1结果文件
USER_CLASSIFY_V1_RESULT = '/home/ubuntu3/linhao/case/data/user_classify_v1_result.txt'
# 用户分类LEVELDB文件目录
DOMAIN_V2_LEVELDBPATH = '/home/ubuntu3/linhao/case/case/user_classify/'
# 用户分类v2结果文件
USER_CLASSIFY_V2_RESULT = '/home/ubuntu3/linhao/case/data/user_classify_v2_result.txt'
# 用户分类v1和v2合并文件
USER_CLASSIFY_V12_RESULT = '/home/ubuntu3/linhao/case/data/user_classify_v12_result.txt'
# 用户分类v1 v2 v3合并文件
USER_CLASSIFY_V123_RESULT = '/home/ubuntu3/linhao/case/data/user_classify_v123_result.txt'


# user_classify2redis
DOMAIN_REDIS_HOST = '219.224.135.48' # 用户领域数据
DOMAIN_REDIS_PORT = 6379 # 用户领域数据
USER_DOMAIN = "user_domain"  # user domain hash, 用户所在领域的Hash结构
# 用户领域分类txt结果 sample: 2090398107	{"v1": "other", "v2": [], "v3": "other"}
USER_CLASSIFY_V123_RESULT = '/home/ubuntu3/linhao/case/data/user_classify_v123_result.txt'


def _default_redis(host, port, db=0):
    """返回redis的db对象
       host: redis db的主机地址
       port: redis db 端口号
       db: redis db number(一般令db＝0）
    """
    return redis.StrictRedis(host, port, db)

