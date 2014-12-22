# -*- coding: utf-8 -*-

import os
import csv
import scws
import time
import re
import datetime
from datetime import datetime
from datetime import date
import heapq
import math
import Levenshtein
from model import *
from config import db
import json

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

def load_scws():#加载分词工具
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

def load_lable(flag):
    lable = []
    with open('./lable/lable%s.txt' % flag) as f:
        for line in f:
            lable.append(str(line[0]))
    return lable

def get_s(text,weibo):#计算相似度，剔除重复文本

    max_r = 0
    n = 0
    for i in range(0,len(text)):
        r = Levenshtein.ratio(str(text[i][3]), str(weibo))
        if max_r < r:
            max_r = r
            n = i
    return max_r,n

def get_text_net(word, weibo_text,word_weight):

    c = dict()
    weight = dict()
    for k,v in weibo_text.iteritems():
        c[str(k)] = 0
        w_list = []
        for w in word:
            k1,k2 = w.split('_')
            c[str(k)] = c[str(k)] + str(v[1]).count(str(k1))*word_weight[str(w)] + str(v[1]).count(str(k2))*word_weight[str(w)]
            if w not in w_list:
                w_list.append(str(w))
        weight[str(k)] = float(len(w_list))/float(len(word))#c[str(k)]*(float(len(w_list))/float(len(word)))

    r_weibo = TopkHeap(5000)
    for k,v in weight.iteritems():
        r_weibo.Push((v,k))#分类

    data = r_weibo.TopK()

    f_weibo = TopkHeap(1000)
    for i in range(0,len(data)):
        k = data[i][1]
        f_weibo.Push((c[k],k))#排序

    data = f_weibo.TopK()
    return data

def get_text_notin(word, weibo_text,word_weight):

    c = dict()
    for k,v in weibo_text.iteritems():
        c[str(k)] = 0
        w_list = []
        for w in word:
            k1,k2 = w.split('_')
            c[str(k)] = c[str(k)] + str(v[1]).count(str(k1))*word_weight[str(w)] + str(v[1]).count(str(k2))*word_weight[str(w)]
            if w not in w_list:
                w_list.append(str(w))
        c[str(k)] = c[str(k)]*(float(len(w_list))/float(len(word)))

    r_weibo = TopkHeap(5000)
    for k,v in c.iteritems():
        r_weibo.Push((v,k))#分类

    data = r_weibo.TopK()
    return data

def get_count(word,text):

    count = 0
    for w in word:
        k1,k2 = w.split('_')
        if k1 in str(text):
            count = count + 1
        if k2 in str(text):
            count = count + 1

    return float(count)/float(len(word)*2)

def count_rate(topic,title,t0,w_dict,flag,n1,n2):

    total = 0
    for k,v in w_dict.iteritems():
        total = total + v

    item_exist = db.session.query(OpinionTestRatio).filter(OpinionTestRatio.topic==topic.encode('utf-8')).all()
    if item_exist:
        for item in item_exist:
            db.session.delete(item)
                
    for k,v in w_dict.iteritems():
        r = (float(v)/float(total))*(float(n1)/float(n1+n2))
        str_title = json.dumps(title[k][0:3])
        new_item = OpinionTestRatio(str(topic.encode('utf-8')),str_title,r)
        db.session.add(new_item)
        db.session.commit()

    if t0:
        r = float(n2)/float(n1+n2)
        str_title = json.dumps(t0[0:3])
        new_item = OpinionTestRatio(str(topic.encode('utf-8')),str_title,r)
        db.session.add(new_item)
        db.session.commit()

def write_keyword(topic,title,title0,data,word_weight,data0):

    item_exist = db.session.query(OpinionTestKeywords).filter(OpinionTestKeywords.topic==topic.encode('utf-8')).all()
    if item_exist:
        for item in item_exist:
            db.session.delete(item)
            
    for k,v in title.iteritems():
        row = []
        for i in range(0,len(data[k])):
            row.append([data[k][i],word_weight[str(data[k][i])]])
        str_title = json.dumps(title[k][0:3])
        row = json.dumps(row)
        new_item = OpinionTestKeywords(str(topic.encode('utf-8')),str_title,row)        
        db.session.add(new_item)
        db.session.commit()

    if title0:
        row = []
        for i in range(0,len(data0)):
            row.append([data0[i][1],data0[i][0]])
        str_title = json.dumps(title0[0:3])
        row = json.dumps(row)
        new_item = OpinionTestKeywords(str(topic.encode('utf-8')),str_title,row)
        db.session.add(new_item)
        db.session.commit()
    

def write(topic,weibo_text,text_c,flag,lable,title,dur_time,f):

    if f == 0:
        item_exist = db.session.query(OpinionTestTime).filter(OpinionTestTime.topic==topic.encode('utf-8')).all()
        if item_exist:
            for item in item_exist:
                db.session.delete(item)
        item_exist = db.session.query(OpinionWeibosNew).filter(OpinionWeibosNew.topic==topic.encode('utf-8')).all()
        if item_exist:
            for item in item_exist:
                db.session.delete(item)
    str_title = []
    str_title = json.dumps(title[0:3])
    new_item = OpinionTestTime(str(topic.encode('utf-8')),str_title,dur_time[0],dur_time[1])
    db.session.add(new_item)
    db.session.commit()

    text = []
    number = dict()
    for i in range(0,len(text_c)):
        r,n = get_s(text,weibo_text[str(text_c[i][1])][1])#计算相似度，剔除重复文本
        if r < 0.8:
            text.append([text_c[i][0],text_c[i][1],weibo_text[str(text_c[i][1])][0],weibo_text[str(text_c[i][1])][1],weibo_text[str(text_c[i][1])][2],weibo_text[str(text_c[i][1])][3],weibo_text[str(text_c[i][1])][4]])
        else:
            if number.has_key(str(n)):
                number[str(n)] = number[str(n)] + 1
            else:
                number[str(n)] = 1
    for i in range(0,len(text)):
        if number.has_key(str(i)):
            pass
        else:
            number[str(i)] = 0
        #print topic.encode('utf-8'),str_title,float(text[i][0]),text[i][1],text[i][2],text[i][3].decode('utf-8'),text[i][4],int(text[i][5]),int(text[i][6]),number[str(i)]
        new_item = OpinionWeibosNew(str(topic.encode('utf-8')),str_title,float(text[i][0]),text[i][1],text[i][2],text[i][3].decode('utf-8'),text[i][4],int(text[i][5]),int(text[i][6]),number[str(i)])
        db.session.add(new_item)
        db.session.commit()

def word_net(notin,flag):#词频词网

    black = load_black_words()
    sw = load_scws()
    n = 0
    ts = time.time()

    f_dict = dict()#频数字典
    total = 0#词的总数
    weibo_word = []
    weibo_text = dict()
    weibo_mid = []
    for k,v in notin.iteritems():
        mid = k
        text = v[1]
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

    keyword = TopkHeap(100)
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
                if j-1 >= 0:
                    if word_net.has_key(str(row[j]+'_'+row[j-1])):
                        word_net[str(row[j]+'_'+row[j-1])] = word_net[str(row[j]+'_'+row[j-1])] + 1
                    else:
                        word_net[str(row[j]+'_'+row[j-1])] = 1
                if j+1 < len(row):
                    if word_net.has_key(str(row[j]+'_'+row[j+1])):
                        word_net[str(row[j]+'_'+row[j+1])] = word_net[str(row[j]+'_'+row[j+1])] + 1
                    else:
                        word_net[str(row[j]+'_'+row[j+1])] = 1
    end = time.time()
    print 'net use %s s' % (end-ts)
    weight = TopkHeap(10)
    for k,v in word_net.iteritems():#计算权重
        k1,k2 = k.split('_')
        p = v*k_value[k1]
        weight.Push((p,k))#排序

    data = weight.TopK()
    word = []
    weight = dict()
    for i in range(0,len(data)):
        word.append(str(data[i][1]))
        weight[str(data[i][1])] = data[i][0]
    return word,weight,data

def get_title(words):#子话题名称

    word_dict = dict()
    for i in range(0,len(words)):
        k1,k2 = words[i].split('_')
        if word_dict.has_key(str(k1)):
            word_dict[str(k1)] = word_dict[str(k1)] + words[i][0]
        else:
            word_dict[str(k1)] = words[i][0]
        if word_dict.has_key(str(k2)):
            word_dict[str(k2)] = word_dict[str(k2)] + words[i][0]
        else:
            word_dict[str(k2)] = words[i][0]
    
    f_weibo = TopkHeap(10)
    for k,v in word_dict.iteritems():
        f_weibo.Push((v,k))#排序

    data = f_weibo.TopK()
    title = []
    for i in range(0,len(data)):
        if i > 3:
            break
        word = data[i][1]#.decode('utf-8')
        title.append(word)
    return title

def get_time(weibo,mid_list):#获取子话题开始时间和结束时间
    
    n = len(mid_list)
    top = TopkHeap(n)
    for i in range(0,len(mid_list)):
        top.Push((weibo[mid_list[i][1]][2],i))
    
    top_data = top.TopK()
    end_ts = top_data[0][0]
    start_ts = top_data[n-1][0]

    return [start_ts,end_ts]
    

def text_net(topic,weibo,weibo_dict,lable,ind,word,flag):#提取代表性微博_词网
    
    ts = time.time()
    data = dict()
    word_weight = dict()
    for i in range(0,len(word)):
        f = filter(lambda ch: ch in '0123456789.', str(word[i][0]))
        word_weight[str(word[i][1])] = float(f)
        l = str(ind[0][i])
        if data.has_key(l):
            item = data[l]
            item.append(word[i][1])
        else:
            item = []
            item.append(word[i][1])
            data[l] = item

    weibo_text = dict()
    notin = dict()
    w_dict = dict()
    for k,v in data.iteritems():
        w_dict[k] = 0
    n = 0
    start = time.time()
    for j in range(0,len(weibo)):
        mid = weibo[j]
        text = weibo_dict[weibo[j]][1]
        if lable[j] == 0:
            if '//@' in str(text):
                m = re.finditer('//@', str(text))
                for i in m:
                    if i.start()<10:
                        pass
                    else:
                        total = 0
                        ratio = dict()
                        for k,v in data.iteritems():
                            w = get_count(v,text)
                            ratio[k] = w
                            total = total + w
                        if total == 0:
                            notin[str(mid)] = weibo_dict[weibo[j]]
                        else:
                            for k,v in w_dict.iteritems():
                                w_dict[k] = w_dict[k] + float(ratio[k])/float(total)
                            weibo_text[str(mid)] = weibo_dict[weibo[j]]
                    break
            else:
                total = 0
                ratio = dict()
                for k,v in data.iteritems():
                    w = get_count(v,text)
                    ratio[k] = w
                    total = total + w
                if total == 0:
                    notin[str(mid)] = weibo_dict[weibo[j]]
                else:
                    for k,v in w_dict.iteritems():
                        w_dict[k] = w_dict[k] + float(ratio[k])/float(total)
                    weibo_text[str(mid)] = weibo_dict[weibo[j]]
        n = n + 1
        if n%10000 == 0:
            end = time.time()
            print "%s takes %s s" % (n,end-start)
            start = end

    if len(notin) > 0:
        word,w,data0 = word_net(notin,flag)#提取其他类微博的关键词
        text0 = get_text_notin(word,notin,w)
        title0 = get_title(word)#提取子话题名称
        dur_time0 = get_time(notin,text0)#提取子话题起始时间和终止时间
    else:
        title0 = ''
        data0 = []

    #以下是提取每一类的代表性文本
    text = dict()
    start = time.time()
    title = dict()
    dur_time = dict()
    for k,v in data.iteritems():
        text[k] = get_text_net(v,weibo_text,word_weight)
        title[k] = get_title(v)#提取子话题名称
        dur_time[k] = get_time(weibo_text,text[k])#提取子话题起始时间和终止时间
        end = time.time()
        print "lable %s takes %s" % ((int(k)+1),(end-start))
        start = end

    count_rate(topic,title,title0,w_dict,flag,len(weibo_text),len(notin))#写每类比例
    write_keyword(topic,title,title0,data,word_weight,data0)#写每一类的关键词
    
    #以下是写入每一类代表性文本
    
    n = 0
    start = time.time()
    for k,v in text.iteritems():
        if n == 0:
            write(topic,weibo_text,v,flag,(int(k)+1),title[k],dur_time[k],0)
            n = 1
        else:
            write(topic,weibo_text,v,flag,(int(k)+1),title[k],dur_time[k],1)
        end = time.time()
        print "lable %s takes %s" % ((int(k)+1),(end-start))
        start = end

    if len(notin) > 0:
        start = time.time()
        write(topic,notin,text0,flag,'0',title0,dur_time0,1)
        end = time.time()
        print "lable 0 takes %s" % (end-start)

    print "total takes %s" % (end-ts)


if __name__ == '__main__':
    #text_net('0522')#博鳌论坛
    text_net('maoming')#复旦投毒
