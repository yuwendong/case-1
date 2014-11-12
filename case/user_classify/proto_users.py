#!/usr/bin/env python
#-*-coding:utf-8-*-
"""生成原型用户
"""

import csv
from collections import Counter


class Schema:
    v1 = {
        'fields': [u'domain', u'last_modify', u'id', u'city', u'verified', u'followers_count', u'followers', u'location', u'verified_type', u'province', u'statuses_count', u'description', u'friends_count', u'first_in', u'timestamp', u'allow_all_act_msg', u'profile_image_url', u'geo_enabled', u'friends', u'favourites_count', u'name', u'url', u'gender', u'created_at', u'_id']
    }

    v2 = {
        'fields': [u'active', u'last_modify', u'id', u'city', u'verified', u'followers_count', u'followers', u'location', u'verified_type', u'province', u'statuses_count', u'description', u'friends_count', u'first_in', u'profile_image_url', u'friends', u'name', u'gender', u'_id', u'bi_followers_count', u'verified_reason']
    }


def readSeedUidsByArea(area):
    uidlist = []
    with open("./seed_users/%s.txt" % area) as f:
    for line in f:
        uid = int(line.strip().split()[0])
        uidlist.append(uid)


def proto_users(reader, fw, seedusers):
    # generate seed set
    seed_pool = seedusers # seed users
    proto_pool = dict() # proto user pool, get from seed users' friends
    friends_dict = dict() # all user friends dict

    count = 0
    for line in reader:
        item = csvrow2json(line, schema_version)
        uid = int(item['_id'])

        friends_str = item['friends']
        friends = friends_str.rstrip(']').lstrip('[').strip().split(',')
        friends = [int(friend.strip('L')) for friend in friends if friend != '']
        if len(friends):
            friends_dict[uid] = friends

        if count % 10000 == 0:
            print 'iter item: ', count
        count += 1

    global_friends_list = []
    for domain, uids in seed_pool.iteritems():
        domain_friends = []

        for uid in uids:
            try:
                friends = friends_dict[uid]
                domain_friends.extend(friends)
            except KeyError:
                pass

        global_friends_list.extend(domain_friends)
        proto_pool[domain] = Counter(domain_friends)

    global_friends_counter = Counter(global_friends_list)

    # sort proto users by domain, get TopN, combine with seed users
    topN = 300
    for domain, counter in proto_pool.iteritems():
        uid_score = dict()
        for uid, freq in counter.iteritems():
            t_freq = global_friends_counter[uid]
            score = freq * 1.0 / t_freq
            uid_score[uid] = score

        sorted_uid_score = sorted(uid_score.iteritems(), key=lambda (k, v): v, reverse=True)
        top_sorted_users = [uid for uid, score in sorted_uid_score[:topN]]
        seed_proto_users = [str(uid) for uid in (top_sorted_users + seed_pool[domain])]

        fw.write('%s,%s\n' % (domain, ' '.join(seed_proto_users)))


if __name__ == '__main__':
    count = 0
    schema_version = '2'

    master_timeline_user_csv = '/home/ubuntu3/linhao/case/data/master_timeline_user_csv/master_timeline_user_20140802_v2.csv'
    reader = csv.reader(file(master_timeline_user_csv, 'r'))

    proto_users_file = 'proto_users.txt'
    fw = open(proto_users_file, 'w')

    DOMAIN_LIST = ["culture", "entertainment", "fashion", "education", "finance", "sports", "technology", "media"]
    seedusers = dict()
    for domain in DOMAIN_LIST:
        users = readSeedUidsByArea(domain)
        seedusers[domain] = users

    proto_users(reader, fw, seedusers)
    fw.close()
