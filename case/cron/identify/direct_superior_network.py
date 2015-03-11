# -*- coding: utf-8 -*-
import re
import json
import pymongo # 需要easy_install pymongo
import networkx as nx
import urllib2
from mongodb_connection import mongodb, collection
#from config import API_SERVER_HOST, API_SERVER_PORT
from items import UserItem_search
#from config import xapian_search_user as user_search
import sys
sys.path.append('../../')
from global_config import xapian_search_user as user_search
from global_config import API_HOST, API_PORT
'''
根据相关话题微博，通过正则表达式获取直接转发上级的昵称，并将其转化为userid
'''

BASE_URL_UID = 'http://%s:%s/queryWeiboUsers?users={user}&type=1' % (API_HOST, API_PORT)


def get_superior_userid(weibo):
    text = weibo['text']
    if isinstance(text, str):
        text = text.decode('utf-8', 'ignore')
    RE = re.compile(u'//@([a-zA-Z-_⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]+):', re.UNICODE)
    repost_chains = RE.findall(text)
    
    # 直接上级就是转发的源头节点，这种情况下在微博文本中不存正则表达匹配的内容
    
    '''
    # get direct_superior_name
    reposts_name = set()
    if repost_chains!=[]:
        repost_name = repost_chains[0]
    else:
        repost_name = None
    return repost_name
    
    '''

    if (weibo['retweeted_uid']!=0 and weibo['retweeted_uid']) and (repost_chains == []):
        direct_superior_id = weibo['retweeted_uid']
        return direct_superior_id
    
    if repost_chains!=[]:
        direct_superior_name = repost_chains[0]
        count, results = user_search.search(query={'name':direct_superior_name}, fields=['_id', 'name'])
        if count != 0:
            for result in results():
                direct_superior_id = result['_id']
        else:
            direct_superior_id = None
        #direct_superior_id = find_in_mongo(direct_superior_name) # 在mongodb中查询

        if not direct_superior_id:
            #direct_superior_id = find_by_scripy(direct_superior_name)
            direct_superior_id = None
    else:
        direct_superior_name = None
        direct_superior_id = None

    return direct_superior_id
    

def find_in_mongo(uname):
    user = collection.find_one({'name': uname})
    if user:
        uid = user['id']
        if uid==None or uid=='' or uid==0:
            print 'error uid in mongo:', uid
    else:
        uid = None
    
    return uid

def find_by_scripy(uname):
    '''
    通过api爬取数据
    存在mongodb--54api_weibo_v2---master_timeline_user
    在存之前，先要判断数据库中有没有已经存在的uid，一旦uid已经存在，说明用户更新了uname
    需要对数据库中该条数据进行更新，否则直接insert
    返回uid
    '''
    #print 'before scripy'
    item = get_item(uname) # 爬取数据
    if item==None:
        return None
    user = item.to_dict()
    #print 'type(user):', type(user)
    try:
        uid = user['id']
        user['_id'] = uid
        user_exist = collection.find_one({'_id': uid})
        #print 'user_exist:', user_exist
        if user_exist:
            collection.update({'_id': uid}, {'$set': user})
            #print 'mongodb update'
        else:
            #print 'user:', user
            collection.insert(user)
            #print 'mongodb insert'
        #print 'uid:', uid
    except KeyError:
        #print 'uname changed'
        uid = None
    #print 'uid:', uid
    #print 'after scripy'
    return uid
    
def get_item(uname):
    #print 'get_item'
    uname = uname.encode('utf-8')
    #print 'url:', BASE_URL_UID.format(user=uname)
    try:
        content_stream = urllib2.urlopen(BASE_URL_UID.format(user=uname), timeout=60)
    except:
        #file_name = 'fix_uname1.txt'
        #write_log_file(file_name)
        return None
    content = content_stream.read()
    #print 'uname:', uname
    #print 'type:content:', type(content)
    #print 'content:', content
    # 上述计数了能够从微薄文本中解析出用户昵称，但是在爬虫爬取过程中为能获取到的。即在一年的时间内修改了昵称的用户数量        
    resp = json.loads(content)
    #print 'resp:', resp
    #if 'error' in resp:
        #file_name = 'fix_uname2.txt'
        #write_log_file(file_name)
    
    if not resp:
        print 'failed scripy '
        item = None
    else:
        item = resp2item_search(resp)
    #print 'item:', item 
    return item

def write_log_file(file_name):
    log_file = open(file_name, 'r+')
    count = log_file.readlines()
    #print 'read_count:', count
    try:
        k = int(count[0]) + 1
        count[0] = str(k)
    except:
        count = ['1']
    log_file = open(file_name, 'w+')
    #print 'write_count:', count
    log_file.writelines(count)
    log_file.close()
    
def resp2item_search(resp):
    item = []
    user = UserItem_search()
    for key in user['RESP_ITER_KEYS']:
        if key in resp:
            if key == 'class_type':
                user[key] = resp['class']
            else:
                user[key] = resp[key]

    return user
        









    
    
    
    
    
        
