# -*- coding: utf-8 -*-
"""
将微博用户的bson文件转化成json格式数据

@version: 1.0 (2014-08-05)
@author: linhaobuaa
"""

import os
from xapian_case.bs_input import KeyValueBSONInput


class Schema:
    """定义用户的结构，分别是新浪微博V1和V2接口的字段
    """

    v1 = {
        'fields': [u'domain', u'last_modify', u'id', u'city', u'verified', u'followers_count', u'followers', u'location', u'verified_type', u'province', u'statuses_count', u'description', u'friends_count', u'first_in', u'timestamp', u'allow_all_act_msg', u'profile_image_url', u'geo_enabled', u'friends', u'favourites_count', u'name', u'url', u'gender', u'created_at', u'_id']
    }

    v2 = {
        'fields': [u'active', u'last_modify', u'id', u'city', u'verified', u'followers_count', u'followers', u'location', u'verified_type', u'province', u'statuses_count', u'description', u'friends_count', u'first_in', u'profile_image_url', u'friends', u'name', u'gender', u'_id', u'bi_followers_count', u'verified_reason']
    }


def _encode_utf8(value):
    """utf-8编码
    """
    if isinstance(value, unicode):
        return value.encode('utf-8', 'ignore')
    else:
        return value


def json2csvrow(item, schema_version):
    """将json结构的item转化为数组
       item: json数据
       schema_version: 字段类型，取‘1’或‘2’
    """
    schema = getattr(Schema, 'v%s' % schema_version)
    fields = schema['fields']

    csvrow = [_encode_utf8(item[field]) if field in item else '' for field in fields]

    return csvrow


def load_items(bs_filepath):
    """将bson文件转化为可迭代的对象，以供读取
       bs_filepath: BSON文件路径
    """
    print 'bson file mode: read user from bson file ', bs_filepath
    bs_input = KeyValueBSONInput(open(bs_filepath, 'rb'))
    return bs_input


def duplicate_rm(itema, itemb):
    """根据两个item的最后修改时间去重，保留较新的那个
    """
    ma = itema['last_modify']
    mb = itemb['last_modify']
    if ma < mb:
        return itemb
    else:
        return itema


if __name__ == '__main__':
    from consts import BSON_FILE_FOLDER, \
            MASTER_TIMELINE_V1_BSON, \
            MASTER_TIMELINE_V2_BSON,
            MASTER_TIMELINE_V1_CSV,
            MASTER_TIMELINE_V2_CSV

    # 解析并写入csv
    import csv
    bson_csv_version = [(MASTER_TIMELINE_V1_BSON, MASTER_TIMELINE_V1_CSV, '1'), \
            (MASTER_TIMELINE_V2_BSON, MASTER_TIMELINE_V2_CSV, '2')]

    for bson_file, master_timeline_user_csv, schema_version in bson_csv_version:
        count = 0
        writer = csv.writer(file(master_timeline_user_csv, 'wb'))

        for bson_file in master_timeline_bson:
            f = os.path.join(bson_file_folder, bson_file)
            bs_input = load_items(f)

            for _id, item in bs_input:
                writer.writerow(json2csvrow(item, schema_version))

                if count % 10000 == 0:
                    print 'parse bson and write csv %s' % count
                count += 1

