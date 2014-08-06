# -*- coding: utf-8 -*-

import os
import re
import sys
import math
import time
import base62
import random
import datetime
import buchheim_weibospread
from gen_weibospread import Tree
from gexf import Gexf
from lxml import etree
from xapian_weibo.xapian_backend import XapianSearch
from dynamic_xapian_weibo import target_whole_xapian_weibo, target_whole_xapian_user

weibo_fields = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
                'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
                'comments_count', 'sentiment']
user_fields = ['_id', 'province', 'city', 'verified', 'name', 'friends_count', \
               'gender', 'profile_image_url', 'verified_type', 'followers_count', \
               'followers', 'location', 'statuses_count', 'friends', 'description', \
               'created_at']

def reposts2tree(source_weibo, reposts, per_page, page_count):
    # root
    tree_nodes = []
    tree_stats = {}
    node = source_weibo['user']['name']
    extra_infos = {
        'location': source_weibo['user']['location'],
        'datetime': source_weibo['created_at'],
        'wid': source_weibo['id'],
        'img_url': source_weibo['user']['profile_image_url'],
        'weibo_url': base62.weiboinfo2url(source_weibo['user']['id'], source_weibo['mid'])
    }

    tree_nodes.append(Tree(node, extra_infos))
    created_at = source_weibo['created_at']
    created_at = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S +0800 %Y')
    tree_stats['spread_begin'] = created_at
    tree_stats['spread_end'] = created_at
    tree_stats['reposts_count'] = source_weibo['reposts_count']
    tree_stats['repost_peoples'] = set([source_weibo['user']['id']])

    # sort reposts
    reposts = sorted(reposts, key=lambda x: x['id'])
    reposts = reposts[: per_page * page_count]

    # genarate tree
    for repost in reposts:
        node = repost['user']['name']
        extra_infos = {
            'location': repost['user']['location'],
            'datetime': repost['created_at'],
            'wid': repost['id'],
            'img_url': repost['user']['profile_image_url'],
            'weibo_url': base62.weiboinfo2url(repost['user']['id'], repost['mid'])
        }

        tree_nodes.append(Tree(node, extra_infos))

        repost_users = re.findall(u'/@([a-zA-Z-_\u0391-\uFFE5]+)', repost['text'])
        parent_idx = 0
        while parent_idx < len(repost_users):
            flag = False
            for node in tree_nodes[-2::-1]:
                if node.node == repost_users[parent_idx]:
                    node.append_child(tree_nodes[-1])
                    flag = True
                    break

            if flag:
                break
            parent_idx += 1
        else:
            tree_nodes[0].append_child(tree_nodes[-1])

        created_at = repost['created_at']
        created_at = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S +0800 %Y')
        if created_at > tree_stats['spread_end']:
            tree_stats['spread_end'] = created_at
        tree_stats['repost_peoples'].add(repost['user']['id'])

    tree_stats['repost_people_count'] = len(tree_stats['repost_peoples'])
    del tree_stats['repost_peoples']

    return tree_nodes, tree_stats


class Count:
    def __init__(self, count=0):
        self.count = count


def add_node_and_edge(drawtree, graph, ct, parent=None, max_width=0):
    length = len(drawtree.children)
    size = math.log((math.pow(length, 0.3) + math.sqrt(4)), 4)
    b, r, g = '217', '254', '240'
    if length > 6:
        b = str(random.randint(0, 255))
        r = str(random.randint(100, 255))
        g = str(random.randint(0, 255))

    scale_y = max_width / 200 + 1
    node = graph.addNode(drawtree.tree.extra_infos['wid'], drawtree.tree.node,
                         b=b, r=r, g=g, x=str(drawtree.x), y=str(drawtree.y * scale_y * 10), z='0.0',
                         size=str(size))

    node.addAttribute('img_url', drawtree.tree.extra_infos['img_url'])
    node.addAttribute('name', drawtree.tree.node)
    node.addAttribute('location', drawtree.tree.extra_infos['location'])
    node.addAttribute('datetime', drawtree.tree.extra_infos['datetime'])
    node.addAttribute('repost_num', str(length))
    node.addAttribute('weibo_url', drawtree.tree.extra_infos['weibo_url'])

    if parent is not None:
        ct.count += 1
        graph.addEdge(ct.count, str(drawtree.tree.extra_infos['wid']), str(parent.tree.extra_infos['wid']))

    for child in drawtree.children:
        add_node_and_edge(child, graph, ct, drawtree, max_width)


def tree2graph(tree_nodes):
    dt, max_depth, max_width = buchheim_weibospread.buchheim(tree_nodes[0])

    gexf = Gexf('MOON_CLJ', 'simple')
    graph = gexf.addGraph('directed', 'static', 'weibo graph')
    graph.addNodeAttribute('img_url', type='URI', force_id='img_url')
    graph.addNodeAttribute('name', type='string', force_id='name')
    graph.addNodeAttribute('location', type='string', force_id='location')
    graph.addNodeAttribute('datetime', type='string', force_id='datetime')
    graph.addNodeAttribute('repost_num', type='integer', force_id='repost_num')
    graph.addNodeAttribute('weibo_url', type='URI', force_id='weibo_url')

    add_node_and_edge(dt, graph, Count(), max_width=max_width)

    return etree.tostring(gexf.getXML(), pretty_print=False, encoding='utf-8', xml_declaration=True), max_depth, max_width


whole_xapian_weibo = target_whole_xapian_weibo()
whole_xapian_user = target_whole_xapian_user()


def getWeiboByMid(mid):
    weibo = whole_xapian_weibo.search_by_id(int(mid), fields=weibo_fields)
    status = {}
    if weibo:
        for field in weibo_fields:
            if field == 'user':
                status['user'] = getUserByUid(weibo['user'])
            elif field == 'timestamp':
                status['timestamp'] = weibo['timestamp']
                status['created_at'] = time.strftime("%a %b %d %H:%M:%S +0800 %Y", time.localtime(weibo['timestamp']))
            else:
                status[field] = weibo[field]
    else:
        status['text'] = ''
    
    status['id'] = int(mid)
    status['mid'] = str(mid)

    return status

def getUserByUid(uid):
    user = whole_xapian_user.search_by_id(int(uid), fields=user_fields)
    user_dict = {}
    if user:
        for field in user_fields:
            user_dict[field] = _utf_8_decode(user[field])
    else:
        user_dict['name'] = str(uid)
        user_dict['location'] = 'unknown'
        user_dict['profile_image_url'] = u''
        user_dict['followers_count'] = 0
        user_dict['friends_count'] = 0
        user_dict['statuses_count'] = 0
        user_dict['description'] = ''

    result_dict = {}
    for k, v in user_dict.iteritems():
        result_dict[k] = v
    result_dict['id'] = int(uid)

    return result_dict


def getWeiboRepostsByMid(mid, begin_ts, end_ts, limit=100000):
    query_dict = {
        'timestamp': {'$gt': begin_ts, '$lt': end_ts},
        'retweeted_mid': int(mid)
    }
    print '---', limit
    count, get_results = whole_xapian_weibo.search(query=query_dict, fields=weibo_fields, max_offset=limit)
    statuses = []
    
    count = 0
    ts = te = time.time()
    for r in get_results():
        if count % 10000 == 0:
            te = time.time()
            print count, '%s sec' % (te - ts), ' search reposts'
            ts = te 

        status = {}
        for field in weibo_fields:
            if field == 'user':
                status['user'] = getUserByUid(r['user'])
            elif field == 'timestamp':
                status['timestamp'] = r['timestamp']
                status['created_at'] = time.strftime("%a %b %d %H:%M:%S +0800 %Y", time.localtime(r['timestamp']))
            else:
                status[field] = r[field]

        status['id'] = status['_id']
        status['mid'] = str(status['_id'])
        statuses.append(status)

        count += 1

    return statuses


def getSubWeiboRepostsByMid(mid, name, retweeted_mid, begin_ts, end_ts, limit=100000):
    query_dict = {
        'timestamp': {'$gt': begin_ts, '$lt': end_ts},
        'retweeted_mid': int(retweeted_mid)
    }

    count, get_results = whole_xapian_weibo.search(query=query_dict, fields=weibo_fields, max_offset=limit)
    statuses = []
    
    count = 0
    ts = te = time.time()
    for r in get_results():
        if count % 10000 == 0:
            te = time.time()
            print count, '%s sec' % (te - ts), ' search reposts'
            ts = te

        repost_users = re.findall(u'/@([a-zA-Z-_\u0391-\uFFE5]+)', r['text'])
        if name not in repost_users:
            count += 1
            continue

        status = {}
        for field in weibo_fields:
            if field == 'user':
                status['user'] = getUserByUid(r['user'])
            elif field == 'timestamp':
                status['timestamp'] = r['timestamp']
                status['created_at'] = time.strftime("%a %b %d %H:%M:%S +0800 %Y", time.localtime(r['timestamp']))
            else:
                status[field] = r[field]

        status['id'] = status['_id']
        status['mid'] = str(status['_id'])
        statuses.append(status)

        count += 1

    return statuses


def _utf_8_decode(stri):
    if isinstance(stri, str):
        return unicode(stri, 'utf-8')
    return stri


def local2ts(time_str):
    time_format = '%a %b %d %H:%M:%S +0800 %Y'
    return int(time.mktime(time.strptime(time_str, time_format)))


def graph(mid):
    # weibo
    weibo = getWeiboByMid(mid)
    if 'retweeted_mid' not in weibo or 'retweeted_uid' not in weibo:
        sys.exit('weibo not found from the whole xapian db')
    retweeted_mid = weibo['retweeted_mid']
    retweeted_uid = weibo['retweeted_uid']

    # source_weibo
    repost_flag = False # 该微博为非转发微博
    if retweeted_mid != 0:
        repost_flag = True # 该微博为原创微博
        source_weibo = getWeiboByMid(retweeted_mid)
    else:
        source_weibo = weibo

    if 'created_at' not in source_weibo or 'created_at' not in weibo:
        sys.exit('source weibo or weibo not exist created_at')

    # 完整树的reposts
    begin_ts = local2ts(source_weibo['created_at'])
    end_ts = begin_ts + 24 * 3600

    per_page = 100#10000
    page_count = 10
    reposts = getWeiboRepostsByMid(source_weibo['id'], begin_ts, end_ts, per_page * page_count)
    print 'search source weibo reposts completely ', source_weibo['id'], 'total reposts count : ', len(reposts), \
    ' source user name: ', source_weibo['user']['id']#source_weibo['user']['name'], source_weibo['user']['id']

    # 完整转发树绘制
    print 'start draw whole tree'
    tree, tree_stats = reposts2tree(source_weibo, reposts, per_page, page_count)
    graph, max_depth, max_width = tree2graph(tree)
    tree_stats['max_depth'] = max_depth
    tree_stats['max_width'] = max_width
    try:
        tree_stats['spread_begin'] = time.mktime(tree_stats['spread_begin'].timetuple())
        tree_stats['spread_end'] = time.mktime(tree_stats['spread_end'].timetuple())
    except Exception, e:
        tree_stats['spread_begin'] = 'unknown'
        tree_stats['spread_end'] = 'unknown'
        print e

    whole_graph_stats = {'graph': graph, 'stats': tree_stats, 'reposts': reposts, 'ori': source_weibo}
    print tree_stats
    print 'end draw whole tree'

    sub_graph_stats = {'graph': '', 'stats': '', 'reposts': [], 'ori': None}
    if repost_flag:
        # 转发微博需要进行子树计算
        print 'start draw sub tree'

        # 子树的reposts，从该条微博往下
        sub_reposts = []
        begin_ts = local2ts(weibo['created_at'])
        end_ts = begin_ts + 24 * 3600

        reposts = getSubWeiboRepostsByMid(weibo['id'], weibo['user']['name'], source_weibo['id'], begin_ts, end_ts, per_page * page_count)
        print 'search sub weibo reposts completely ', weibo['id'], 'total reposts count : ', len(reposts), \
        ' source user name: ', weibo['user']['id']# weibo['user']['name']
        
        # 子树转发树绘制
        tree, tree_stats = reposts2tree(weibo, reposts, per_page, page_count)
        graph, max_depth, max_width = tree2graph(tree)
        tree_stats['max_depth'] = max_depth
        tree_stats['max_width'] = max_width
        try:
            tree_stats['spread_begin'] = time.mktime(tree_stats['spread_begin'].timetuple())
            tree_stats['spread_end'] = time.mktime(tree_stats['spread_end'].timetuple())
        except Exception, e:
            tree_stats['spread_begin'] = 'unknown'
            tree_stats['spread_end'] = 'unknown'
            print e

        sub_graph_stats['graph'] = graph
        sub_graph_stats['stats'] = tree_stats
        sub_graph_stats['reposts'] = reposts
        sub_graph_stats['ori'] = weibo
        print tree_stats
        print 'end draw sub tree'

    else:
        # 原创微博不需要进行子树计算
        print 'original need not draw sub tree'

    return {'whole': whole_graph_stats, 'sub': sub_graph_stats}


if __name__ == '__main__':
    # repost: 3618204893345603
    #3618476080282985   3617726042418839    3618201981966170    3617841875854702
    source_mid = 3618204893345603
    graph(source_mid)
