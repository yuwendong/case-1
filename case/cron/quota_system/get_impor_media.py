# -*- coding: utf-8 -*-
import sys
import csv
import redis
#from config import xapian_search_user as user_search # 修改对应的config

sys.path.append('../../')
from global_config import xapian_search_user as user_search

REDIS_HOST = '219.224.135.48'
REDIS_PORT = 6379

def get_impor_media():
    reader = csv.reader(file('media.csv', 'rb'))
    media_dict = {} # media_dict = {uid1:followers_count1}
    for line in reader:
        uid = line[0]
        results = user_search.search_by_id(int(uid), fields=['followers_count'])
        if results:
            followers_count = results['followers_count']
            media_dict[uid] = followers_count
        else:
            continue
    
    sort_media = sorted(media_dict.iteritems(), key=lambda a:a[1], reverse=False)
    topmedia = sort_media[len(sort_media)-500:] # topmedia = [(uid1, followers1),(uid2, followers2)]
    write_impor_media(topmedia)

def write_impor_media(topmedia):
    writer = csv.writer(file('impor_media.csv', 'wb'))
    for uid in topmedia:
        followers_count = uid[1]
        writer.writerow([uid[0], followers_count])

def impor_media2redis(fr, r, set_name): # 将impor_media.csv文件中的media的uid存入redis中
    for line in fr:
        uid = line.strip().split(',')[0]
        #print 'uid:', uid
        r.sadd(set_name, int(uid))

def _default_redis(host, port, db=0):
    return redis.StrictRedis(host, port, db)


if __name__=='__main__':
    # get_impor_media()
    fr = open('impor_media.csv', 'r')
    r = _default_redis(REDIS_HOST, REDIS_PORT)
    set_name = 'ImporMedia'
    impor_media2redis(fr, r, set_name)
    fr.close()
