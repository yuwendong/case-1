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
        r = Levenshtein.ratio(str(text[i][2]), str(weibo))
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
            c[str(k)] = c[str(k)] + str(v).count(str(k1))*word_weight[str(w)] + str(v).count(str(k2))*word_weight[str(w)]
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
            c[str(k)] = c[str(k)] + str(v).count(str(k1))*word_weight[str(w)] + str(v).count(str(k2))*word_weight[str(w)]
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

def count_rate(w_dict,flag,n1,n2):

    total = 0
    for k,v in w_dict.iteritems():
        total = total + v

    with open('./result_net/rate%s.csv' % flag, 'wb') as f:
        writer = csv.writer(f)
        for k,v in w_dict.iteritems():
            r = (float(v)/float(total))*(float(n1)/float(n1+n2))
            writer.writerow((k,r))

        r = float(n2)/float(n1+n2)
        writer.writerow(('0',r))

def write(weibo_text,text_c,flag,lable):
    
    with open('./result_net/weibo%s_%s.csv' % (flag,lable), 'wb') as f:
        writer = csv.writer(f)
        text = []
        number = dict()
        for i in range(0,len(text_c)):
            r,n = get_s(text,weibo_text[str(text_c[i][1])])#计算相似度，剔除重复文本
            if r < 0.8:
                text.append([text_c[i][0],text_c[i][1],weibo_text[str(text_c[i][1])]])
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
            writer.writerow((text[i][0],text[i][1],text[i][2],number[str(i)]))

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
    for mid,text in notin.iteritems():
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
    print 'start to write in csv'
    with open('./result_net/keyword0%s.csv' % flag, 'wb') as f:
        writer = csv.writer(f)
        for i in range(0,len(data)):
            writer.writerow((data[i][0],str(data[i][1])))
            word.append(str(data[i][1]))
            weight[str(data[i][1])] = data[i][0]
    return word,weight

def text_net(weibo,weibo_dict,lable,ind,word,flag):#提取代表性微博_词网

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
        text = weibo_dict[weibo[j]]
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
                            notin[str(mid)] = str(text)
                        else:
                            for k,v in w_dict.iteritems():
                                w_dict[k] = w_dict[k] + float(ratio[k])/float(total)
                            weibo_text[str(mid)] = str(text)
                    break
            else:
                total = 0
                ratio = dict()
                for k,v in data.iteritems():
                    w = get_count(v,text)
                    ratio[k] = w
                    total = total + w
                if total == 0:
                    notin[str(mid)] = str(text)
                else:
                    for k,v in w_dict.iteritems():
                        w_dict[k] = w_dict[k] + float(ratio[k])/float(total)
                    weibo_text[str(mid)] = str(text)

        n = n + 1
        if n%10000 == 0:
            end = time.time()
            print "%s takes %s s" % (n,end-start)
            start = end

    count_rate(w_dict,flag,len(weibo_text),len(notin))#写每类比例
    word,w = word_net(notin,flag)#提取其他类微博的关键词
    text0 = get_text_notin(word,notin,w)

    #以下是提取每一类的代表性文本
    text = dict()
    start = time.time()
    for k,v in data.iteritems():
        text[k] = get_text_net(v,weibo_text,word_weight)
        end = time.time()
        print "lable %s takes %s" % ((int(k)+1),(end-start))
        start = end

    #以下是写入每一类代表性文本
    start = time.time()
    write(notin,text0,flag,'0')
    end = time.time()
    print "lable 0 takes %s" % (end-start)

    start = time.time()
    for k,v in text.iteritems():
        write(weibo_text,v,flag,(int(k)+1))
        end = time.time()
        print "lable %s takes %s" % ((int(k)+1),(end-start))
        start = end

    print "total takes %s" % (end-ts)


if __name__ == '__main__':
    #text_net('0522')#博鳌论坛
    text_net('maoming')#复旦投毒
