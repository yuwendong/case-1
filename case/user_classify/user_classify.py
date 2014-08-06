#!/usr/bin/env python
#-*-coding:utf-8-*-
"""用户领域分类
"""

import os
import csv
import sys
import json
import leveldb
import datetime
from consts import Schema
from xapian_case.utils import load_scws, cut


def load_admin_words(fr):
    """加载政府职位相关词汇
    """
    admin_words = []
    with open(fr, 'r') as f:
        for line in f:
            admin_words.append(_decode_utf8(line.strip().split()[0]))

    return admin_words


def load_media_words(fr):
    """加载媒体相关词汇
    """
    media_words = []
    with open(fr, 'r') as f:
        for line in f:
            media_words.append(_decode_utf8(line.strip().split()[0]))

    return media_words


def csvrow2json(csvrow, schema_version):
    """将csv数组中的一行转化为json格式
    """
    item = dict()
    schema = getattr(Schema, 'v%s' % schema_version)
    fields = schema['fields']
    for idx, field in enumerate(fields):
        item[field] = csvrow[idx]

    return item


def _encode_utf8(value):
    """utf-8编码
    """
    if isinstance(value, unicode):
        return value.encode('utf-8', 'ignore')
    else:
        return value


def _decode_utf8(value):
    """utf-8解码为unicode
    """
    if isinstance(value, str):
        return value.decode('utf-8', 'ignore')
    else:
        return value


def user_classify_v1(item, s):
    """v1根据verified_type进行用户领域分类
       item: v1版本user item
       s: load_scws()对象
    """

    verified_type = int(item['verified_type'])
    location = item['location']
    text = ''
    for key in ['name', 'description', 'verified_reason']:
        try:
            text += _encode_utf8(item[key])
        except KeyError:
            pass
    followers_count = int(item['followers_count'])
    statuses_count = int(item['statuses_count'])

    # 初始化将label设置成'other'
    label = 'other'

    if verified_type == 4:
        label = 'university' # 高校微博

    elif verified_type == 1:
        province = _decode_utf8(location.split()[0])
        if province not in out_words:
            label = 'homeadmin' # 境内机构
        else:
            label = 'abroadadmin' # 境外机构

    elif verified_type == 3:
        province = _decode_utf8(location.split()[0])
        if province not in out_words:
            label = 'homemedia'# 境内媒体
        else:
            label = 'abroadmedia' # 境外媒体

    elif verified_type == 7:
        label = 'folkorg' # 民间组织

    elif verified_type == 0:
        words = [_decode_utf8(w) for w in cut(s, text)]
        cover_words_count = 0

        select_candidate_idx = -1
        for idx, candidate in enumerate(verified_words_candidates):
            candidate_count = len(set(words) & set(candidate))
            if cover_words_count < candidate_count:
                cover_words_count = candidate_count
                select_candidate_idx = idx

        label = verified_label_candidates[select_candidate_idx]

    elif followers_count >= FOLLOWERS_COUNT_THRESHOLD and statuses_count >= STATUSES_COUNT_THRESHOLD:
        # verified_type取其他值时，用followers_count和statuses_count作分类依据
        label = 'grassroot'

    return label


def user_classify_v2(leveldbpath, domain_list, fw):
    """用户领域分类v2
       leveldbpath: 用户分类v2 leveldb目录
       domain_list: 用户分类v2 领域列表
       fw: 用户分类v2结果文件路径
    """
    global_user_field_bucket = leveldb.LevelDB(os.path.join(leveldbpath, 'linhao_global_user_field_20131012'),
                                                   block_cache_size=8 * (2 << 25), write_buffer_size=8 * (2 << 25))
    count = 0
    for uid, domains_str in global_user_field_bucket.RangeIter():
        domains = [domain_list[int(idx)] for idx in domains_str.split(',') if idx != '']
        fw.write('%s\t%s\n' % (uid, ','.join(domains)))

        if count % 10000 == 0:
            print 'extract user domains from leveldb ', count
        count += 1


def user_classify_v3(fr, fw):
    """用户领域分类v3
       fr: 用户领域分类v1 v2结果合并文件
       fw: 用户领域分类v123 结果文件
    """
    count = 0
    for line in fr:
        uid, domain_str = line.strip().split('\t')
        domain_dict = json.loads(domain_str)
        v1 = domain_dict['v1']
        v2 = domain_dict['v2']
        v3 = 'other'
        if v2 == 'media' or v1 in ['mediaworker', 'homemedia']:
            v3 = 'media'
        elif v1 in ['folkorg', 'grassroot']:
            v3 = 'folk'
        elif v1 in ['politicain', 'activer']:
            v3 = 'opinion_leader'
        elif v1 in ['abroadadmin', 'abroadmedia']:
            v3 = 'oversea'

        domain_dict['v3'] = v3
        fw.write('%s\t%s\n' % (uid, json.dumps(domain_dict)))

        if count % 10000 == 0:
            print 'merge v1 v2 v3 results ', count
        count += 1


if __name__ == '__main__':
    from consts import DOMAIN_V1_LIST, DOMAIN_V2_LIST, \
            ADMIN_WORDS_FILE, MEDIA_WORDS_FILE, OVERSEA_WORDS, LAWYER_WORDS, \
            STATUSES_COUNT_THRESHOLD, FOLLOWERS_COUNT_THRESHOLD, \
            MASTER_TIMELINE_USER_CSV_V1, USER_CLASSIFY_V1_RESULT, \
            USER_CLASSIFY_V2_RESULT, DOMAIN_V2_LEVELDBPATH, \
            USER_CLASSIFY_V12_RESULT, USER_CLASSIFY_V123_RESULT

    # 政府官员词汇
    admin_words = set(load_admin_words(ADMIN_WORDS_FILE))

    # 媒体人士词汇
    media_words = set(load_media_words(MEDIA_WORDS_FILE))

    verified_words_candidates = [LAWYER_WORDS, admin_words, media_words]
    verified_label_candidates = ['lawyer', 'politician', 'mediaworker', 'activer'] # 活跃人士activer 始终放在最后一个，其他与verified_words_candidates一一对应

    # v1 user classify
    s = load_scws() # 初始化分词对象

    count = 0
    schema_version = '1'
    reader = csv.reader(file(MASTER_TIMELINE_USER_CSV_V1, 'r'))
    fw = open(USER_CLASSIFY_V1_RESULT, 'w')
    for line in reader:
        item = csvrow2json(line, schema_version)

        uid = int(item['_id'])
        label = user_classify_v1(item, s)
        fw.write('%s\t%s\n' % (uid, label))

        if count % 10000 == 0:
            print 'write user classify result: ', count
        count += 1
    fw.close()

    # v2 user classify
    fw = open(USER_CLASSIFY_V2_RESULT, 'w')
    user_classify_v2(DOMAIN_V2_LEVELDBPATH, DOMAIN_V2_LIST, fw)
    fw.close()

    # merge v1 and v2 classify results
    f1 = open(USER_CLASSIFY_V1_RESULT, 'r')
    uid_domain = dict()
    count = 0
    for line in f1:
        uid, domain = line.strip().split('\t')
        uid_domain[uid] = {'v1': domain, 'v2':[]}

        if count % 10000 == 0:
            print 'v1 classify result read ', count
        count += 1
    f1.close()

    f2 = open(USER_CLASSIFY_V2_RESULT, 'r')
    count = 0
    for line in f2:
        uid, domains_str = line.strip().split('\t')
        domains = domains_str.split(',')
        try:
            uid_domain[uid]['v2'] = domains
        except KeyError:
            uid_domain[uid] = {'v1': 'other', 'v2': domains}

        if count % 10000 == 0:
            print 'v2 classify result merged ', count
        count += 1
    f2.close()

    with open(USER_CLASSIFY_V12_RESULT, 'w') as fw:
        count = 0
        for uid, domain in uid_domain.iteritems():
            fw.write('%s\t%s\n' % (uid, json.dumps(domain)))

            if count % 10000 == 0:
                print 'write classify merged result ', count
            count += 1

    # user classify v3
    fr = open(USER_CLASSIFY_V12_RESULT, 'r')
    fw = open(USER_CLASSIFY_V123_RESULT, 'w')
    user_classify_v3(fr, fw)
    fr.close()
    fw.close()

