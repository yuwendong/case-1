#!/usr/bin/env python
#-*-coding:utf-8-*-
"""将用户领域分类结果更新入redis
"""

import json
from consts import DOMAIN_REDIS_HOST as REDIS_HOST, \
        DOMAIN_REDIS_PORT as REDIS_PORT, \
        USER_DOMAIN, _default_redis


def userDomainTxt2Redis(fr, r, hash_name):
    """将txt文件中用户领域分类结果读出来写入redis中
       fr: open(txt文件名)对象
       r: 写入的redis db对象
       hash_name: 使用hash结构存储，HASH名
    """
    count = 0
    for line in fr:
        uid, domain_str = line.strip().split('\t')
        domain_dict = json.loads(domain_str)

        r.hset(hash_name, str(uid), domain_str)

        if count % 10000 == 0:
            print 'user domain txt to redis ', count
        count += 1


if __name__ == '__main__':
    r = _default_redis(REDIS_HOST, REDIS_PORT)
    hash_name = USER_DOMAIN

    fr = open(USER_CLASSIFY_V123_RESULT, 'r')
    userDemainTxt2Redis(fr, r, hash_name)
    fr.close()

