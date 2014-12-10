# -*- coding: utf-8 -*-
from flask import Blueprint, session, redirect, url_for
from weibospread.utils import items2mongo, mongo, get_client
from dogapi.utils import resp2item_search
from weibospread.gen import Tree
import math
import re
import datetime
import networkx as nx

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
        'weibo_url': weiboinfo2url(source_weibo['user']['id'], source_weibo['mid'])
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
            'weibo_url': weiboinfo2url(repost['user']['id'], repost['mid'])
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

def add_node_edge(drawtree, graph, ct, parent=None, max_width=0):
    length = len(drawtree.children)
    '''
    node_children = {}
    id = drawtree.tree.extra_infos['wid']
    ts = drawtree.tree.extra_infos['datetime']
    node_children[id] = (length, ts)

    for child in drawtree.children:
        add_node_edge(child, drawtree, max_width)
    '''
    node_id = drawtree.tree.extra_infos['wid']
    timestamp = drawtree.tree.extra_infos['datetime']
    children_num = length(drawtree.children)
    node_attribute_dict = {'timestamp':timestamp, 'children':children_num}
    node = graph.add_node(node_id, node_attribute_dict)

    if parent is not None:
        ct.count += 1
        graph.add_edge(ct.count, str(parent.tree.extra_infos['wid']),str(drawtree.tree.extra_infos['wid']))

    for child in drawtree.children:
       tree_graph = add_node_edge(child, graph, ct, drawtree, max_width)

    return tree_graph
    
def sot_node_by_children(graph):
    children_num_dict = nx.get_node_attributes(graph, 'children')
    timestamp_dict = nx.get_node_attributes(graph, 'timestamp')
    sort_children_num_dict = sorted(children_num_dict, key=lambda x:x[1])
    # sort_children_num_dict = [(id1, children_num1), (id2, children_num2)...]
    count = 0
    result = {}
    for item in sort_children_num_dict:
        if count >= 10:
            break
        id = item[0]
        children_num = item[1]
        timestamp = timestamp_dict[id]
        count += 1
        result[id] = (children_num, timestamp)

    return result
               
def tree2graph(tree_nodes):
    dt, max_depth, max_width = buchheim.buchheim(tree_nodes[0])
    '''
    gexf = Gexf('MOON_CLJ', 'simple')
    graph = gexf.addGraph('directed', 'static', 'weibo graph')
    graph.addNodeAttribute('img_url', type='URI', force_id='img_url')
    graph.addNodeAttribute('name', type='string', force_id='name')
    graph.addNodeAttribute('location', type='string', force_id='location')
    graph.addNodeAttribute('datetime', type='string', force_id='datetime')
    graph.addNodeAttribute('repost_num', type='integer', force_id='repost_num')
    graph.addNodeAttribute('weibo_url', type='URI', force_id='weibo_url')

    add_node_and_edge(dt, graph, Count(), max_width=max_width)
    '''
    graph = nx.DiGraph()
    tree_graph = add_node_edge(dt, graph, Count(), max_width=max_width)
    results = sort_node_by_children(tree_graph) # 对每个节点的children数进行排序----综合考虑时间因素
    
    return results, max_depth, max_width


def index(mid, page=None):
    client = get_client()

    per_page = 200
    total_page = 0
    reposts_count = 0
    source_weibo = None
    if page is None:
        source_weibo = client.get('/showBatch', ids=mid)['statuses'][0]
        items = resp2item_search(source_weibo, 8)
        items2mongo(items, weibo_mode='REPOST')

        reposts_count = source_weibo['reposts_count']
        total_page = int(math.ceil(reposts_count * 1.0 / per_page))
        page = total_page
    else:
        source_weibo = mongo.db.master_timeline_weibo_repost.find_one({'id': mid})
        if source_weibo is None:
            return ''
        reposts_count = source_weibo['reposts_count']
        total_page = int(math.ceil(reposts_count * 1.0 / per_page))
    
    if page == 0:
        return ''
        
    # try:
    reposts = client.get('/queryReList', tweetId=mid, count=per_page, page=page)['reposts']

    # 如果reposts为空，且是最开始访问的一页，有可能是页数多算了一页,直接将页数减一页跳转
    if reposts == [] and total_page > 1 and page == total_page:
        return redirect(url_for('graph.index', mid=mid, page=page - 1))

    items = []
    for repost in reposts:
        items.extend(resp2item_search(repost, 4))
    items2mongo(items, weibo_mode='REPOST')

    for item in items:
        if isinstance(item, WeiboItem_search) and item['id'] != source_weibo['id']:
            item = item.to_dict()
            item['source_weibo'] = source_weibo['id']
            mongo.db.master_timeline_weibo_repost.update({'id': item['id']}, item, upsert=True)
    #except RuntimeError:
    #    pass
    
    reposts = list(mongo.db.master_timeline_weibo_repost.find({'source_weibo': source_weibo['id']}))
    if reposts == []:
        return ''

    page_count = total_page - page + 1 if total_page >= page else 0
    tree, tree_stats = reposts2tree(source_weibo, reposts, per_page, page_count)
    sort_results, max_depth, max_width = tree2graph(tree)
    
    tree_stats['max_depth'] = max_depth
    tree_stats['max_width'] = max_width

    # 存储转发状态
    tree_stats['id'] = mid
    tree_stats['page'] = page
    mongo.db.tree_stats.update({'id': mid, 'page': page}, tree_stats, upsert=True, w=1)
    
    return sort_results

if __name__=='__main__':
    mid = 1834719633
    sort_results = index(mid)
    print 'sort_results:', sort_results
