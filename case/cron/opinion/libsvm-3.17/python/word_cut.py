# -*- coding: utf-8 -*-

import os
import scws
import csv
import time
import re
import datetime
from datetime import datetime
from datetime import date
import heapq
import math
import Levenshtein
import milk
import numpy as np

SCWS_ENCODING = 'utf-8'
SCWS_RULES = '/usr/local/scws/etc/rules.utf8.ini'
CHS_DICT_PATH = '/usr/local/scws/etc/dict.utf8.xdb'
CHT_DICT_PATH = '/usr/local/scws/etc/dict_cht.utf8.xdb'
IGNORE_PUNCTUATION = 1

ABSOLUTE_DICT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './dict'))
CUSTOM_DICT_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'userdic.txt')
EXTRA_STOPWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'stopword.txt')
EXTRA_EMOTIONWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'emotionlist.txt')
EXTRA_ONE_WORD_WHITE_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'one_word_white_list.txt')
EXTRA_BLACK_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'black.txt')

cx_dict = ['Ag','a','an','Ng','n','nr','ns','nt','nz','Vg','v','vd','vn','@']#关键词词性词典

class TopkHeap(object):
    def __init__(self, k):
        self.k = k
        self.data = []
 
    def Push(self, elem):
        if len(self.data) < self.k:
            heapq.heappush(self.data, elem)
        else:
            topk_small = self.data[0][0]
            if elem[0] > topk_small:
                heapq.heapreplace(self.data, elem)
 
    def TopK(self):
        return [x for x in reversed([heapq.heappop(self.data) for x in xrange(len(self.data))])]

def load_one_words():
    one_words = [line.strip('\r\n') for line in file(EXTRA_ONE_WORD_WHITE_LIST_PATH)]
    return one_words

def load_black_words():
    one_words = [line.strip('\r\n') for line in file(EXTRA_BLACK_LIST_PATH)]
    return one_words

single_word_whitelist = set(load_one_words())
single_word_whitelist |= set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')

def load_scws():
    s = scws.Scws()
    s.set_charset(SCWS_ENCODING)

    s.set_dict(CHS_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CHT_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CUSTOM_DICT_PATH, scws.XDICT_TXT)

    # 把停用词全部拆成单字，再过滤掉单字，以达到去除停用词的目的
    s.add_dict(EXTRA_STOPWORD_PATH, scws.XDICT_TXT)
    # 即基于表情表对表情进行分词，必要的时候在返回结果处或后剔除
    s.add_dict(EXTRA_EMOTIONWORD_PATH, scws.XDICT_TXT)

    s.set_rules(SCWS_RULES)
    s.set_ignore(IGNORE_PUNCTUATION)
    return s

def word_net(weibo,weibo_dict,lable,flag,k_cluster):#词频词网

    black = load_black_words()
    sw = load_scws()
    n = 0
    ts = time.time()

    f_dict = dict()#频数字典
    total = 0#词的总数
    weibo_word = []
    weibo_text = dict()
    weibo_mid = []
    for i in range(0,len(weibo)):
        mid = weibo[i]
        text = weibo_dict[weibo[i]]
        if lable[i] == 0:
            words = sw.participle(text)
            row = []
            for word in words:
                if (word[1] in cx_dict) and (3 < len(word[0]) < 30 or word[0] in single_word_whitelist) and (word[0] not in black):#选择分词结果的名词、动词、形容词，并去掉单个词
                    total = total + 1
                    if f_dict.has_key(str(word[0])):
                        f_dict[str(word[0])] = f_dict[str(word[0])] + 1
                    else:
                        f_dict[str(word[0])] = 1
                    row.append(word[0])
            weibo_word.append(row)
            weibo_mid.append(str(mid))
            weibo_text[str(mid)] = str(text)
        n = n + 1
        if n%10000 == 0:
            end = time.time()
            print '%s weibo takes %s s' %(n,(end-ts))
            ts = end

    #top_k = int(total*0.175) + 1#关键词数量
    keyword = TopkHeap(300)
    ts = time.time()
    print 'start to calculate information counting'
    n = 0
    for k,v in f_dict.iteritems():#计算单个词的信息量
        if v >= 2 and (float(v)/float(total)) <= 0.8:#去掉频数小于3，频率高于80%的词
            p = v#0 - math.log(v, 2)#计算信息量
            keyword.Push((p,k))#排序
        n = n + 1
        if n%10000 == 0:
            end = time.time()
            print '%s weibo takes %s s' %(n,(end-ts))
            ts = end
    
    keyword_data = keyword.TopK()#取得前100的高频词作为顶点
    ts = time.time()

    keyword = []
    k_value = dict()
    for i in range(0,len(keyword_data)):
        keyword.append(keyword_data[i][1])
        k_value[str(keyword_data[i][1])] = float(keyword_data[i][0])/float(total)

    word_net = dict()#词网字典
    for i in range(0,len(weibo_word)):
        row = weibo_word[i]
        for j in range(0,len(row)):
            if row[j] in keyword:
                if j-1 >= 0 and row[j] != row[j-1]:
                    if word_net.has_key(str(row[j]+'_'+row[j-1])):
                        word_net[str(row[j]+'_'+row[j-1])] = word_net[str(row[j]+'_'+row[j-1])] + 1
                    elif word_net.has_key(str(row[j-1]+'_'+row[j])):
                        word_net[str(row[j-1]+'_'+row[j])] = word_net[str(row[j-1]+'_'+row[j])] + 1
                    else:
                        word_net[str(row[j-1]+'_'+row[j])] = 1
                if j+1 < len(row) and row[j] != row[j+1]:
                    if word_net.has_key(str(row[j]+'_'+row[j+1])):
                        word_net[str(row[j]+'_'+row[j+1])] = word_net[str(row[j]+'_'+row[j+1])] + 1
                    elif word_net.has_key(str(row[j+1]+'_'+row[j])):
                        word_net[str(row[j+1]+'_'+row[j])] = word_net[str(row[j+1]+'_'+row[j])] + 1
                    else:
                        word_net[str(row[j]+'_'+row[j+1])] = 1
    end = time.time()
    print 'net use %s s' % (end-ts)
    weight = TopkHeap(500)
    for k,v in word_net.iteritems():#计算权重
        k1,k2 = k.split('_')
        if not k_value.has_key(k1):
            k_value[k1] = 0
        if not k_value.has_key(k2):
            k_value[k2] = 0
        if k_value[k1] > k_value[k2]:
            p = v*k_value[k1]
        else:
            p = v*k_value[k2]
        weight.Push((p,k))#排序

    data = weight.TopK()
    word = []
    for i in range(0,len(data)):
        if data[i][1] not in word:
            word.append(data[i])
            if len(word) == 300:#取前300的词对
                break

    #聚类
    feature = []
    for w in word:
        k1,k2 = w[1].split('_')
        c = []
        for i in range(0, len(weibo_word)):
            n1 = str(weibo_text[str(weibo_mid[i])]).count(str(k1))
            n2 = str(weibo_text[str(weibo_mid[i])]).count(str(k2))
            n = n1 + n2
            c.append(n)
        feature.append(c)
    features = np.array(feature)
    cluster_ids = milk.kmeans(features, k_cluster)

    return cluster_ids, word

if __name__ == '__main__':
    word_net('maoming')

