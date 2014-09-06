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

def title_count(data):

    title = dict()
    for k,v in data.iteritems():
        if title.has_key(v[0]):
            title[v[0]] = title[v[0]] + 1
        else:
            title[v[0]] = 1

    n = len(data)
    e = 0
    for k,v in title.iteritems():
        e = e + (float(v)/float(n))*math.log(float(v)/float(n), 2)
    e = -e
    return e

def keyword(flag,news,lable):#话题标志、新闻、类别标签

    data = dict()
    for i in range(0,len(lable)):
        l = str(lable[i])
        if data.has_key(l):
            item = data[l]
            item[str(news[i][0])] = [news[i][1],news[i][2]]
        else:
            item = dict()
            item[str(news[i][0])] = [news[i][1],news[i][2]]
            data[l] = item

    word = dict()
    count = dict()
    for k,v in data.iteritems():#根据词网提取关键词对
        item = word_net(v)
        number = title_count(v)
        count[k] = number
        word[k] = item
    

    rate = dict()
    number = dict()
    for k,v in word.iteritems():
        ts = time.time()
        rate[k]  = get_text_net(flag,str(k),v,data[k])#提取代表性文本并写入文件
        number[k] = len(data[k])
        end = time.time()
        print "%s takes %s s to find text" % (k,(end-ts))
        ts = end
        write(flag,v,str(k))#将关键词对写入文件
        end = time.time()
        print "%s takes %s s to write keywords into file" % (k,(end-ts))

    return count,rate,number        

def get_s(text,weibo):#计算相似度，剔除重复文本

    max_r = 0
    n = []
    for k,v in text.iteritems():
        r = Levenshtein.ratio(str(v), str(weibo))
        if max_r < r:
            n = []
            max_r = r
            n.append(k)
        elif max_r == r:
            n.append(k)
        else:
            pass
    return max_r,n

def get_text_net(flag,lable,word,weibo_text):

    c = dict()
    data = dict()
    number = dict()
    z_count = 0
    for k,v in weibo_text.iteritems():
        r,n = get_s(data,v[1])
        f = 0
        an = 0
        for i in range(0,len(n)):
            if weibo_text[n[i]][0] == v[0]:
                f = 1
                an = i
                break
        if (r < 0.8) or (f == 0):
            c[str(k)] = 0
            w_list = []
            for w in word:
                k1,k2 = w[1].split('_')
                c[str(k)] = c[str(k)] + str(v[1]).count(str(k1))*w[0] + str(v[1]).count(str(k2))*w[0] + str(v[0]).count(str(k1))*w[0] + str(v[0]).count(str(k2))*w[0]
                if w not in w_list:
                    w_list.append(str(w))
            c[str(k)] = c[str(k)] * float(len(w_list))/float(len(word))
            data[str(k)] = v[1]
        else:
            if number.has_key(str(n[an])):
                number[str(n[an])] = number[str(n[an])] + 1
            else:
                number[str(n[an])] = 1
    
    f_weibo = TopkHeap(30)
    for k,v in c.iteritems():
        f_weibo.Push((v,k))#排序
        if v == 0:
            z_count = z_count + 1

    data = f_weibo.TopK()

    with open('./result_comment/text%s_%s.csv' % (flag,lable), 'wb') as f:
        writer = csv.writer(f)
        for i in range(0,len(data)):
            if number.has_key(data[i][1]):
                writer.writerow((data[i][1],weibo_text[data[i][1]][0],weibo_text[data[i][1]][1],data[i][0],number[data[i][1]]))
            else:
                writer.writerow((data[i][1],weibo_text[data[i][1]][0],weibo_text[data[i][1]][1],data[i][0],0))
    
    return float(z_count)/len(weibo_text)

def word_net(data):
    black = load_black_words()
    sw = load_scws()
    n = 0
    ts = time.time()

    f_dict = dict()#频数字典
    total = 0#词的总数
    weibo_word = []
    weibo_text = dict()
    weibo_mid = []
    for k,v in data.iteritems():
        text = v[0] + '_' + v[1]
        mid = k
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
            print '%s comments takes %s s' %(n,(end-ts))
            ts = end

    #top_k = int(total*0.175) + 1#关键词数量
    keyword = TopkHeap(200)
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
            print '%s comments takes %s s' %(n,(end-ts))
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
    weight = TopkHeap(20)
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
    return data

def write(flag,data,lable):

    word = []
    print 'start to write in csv'
    with open('./result_comment/keyword%s_%s.csv' % (flag,lable), 'wb') as f:
        writer = csv.writer(f)
        for i in range(0,len(data)):
            if data[i][1] not in word:
                word.append(str(data[i][1]))
                writer.writerow((data[i][0],str(data[i][1])))

def cut_word(flag,cluster):#标题分类
   
    title = dict()
    title_count = dict()
    weibo_word = []
    black = load_black_words()
    sw = load_scws()
    word_count = []
    reader = csv.reader(file('./comment/data%s.csv' % flag, 'rb'))
    for mid,url,t,c,author,publish,site,board in reader:#按标题归类
        if title_count.has_key(str(t)):
            item = title_count[str(t)]
            item.append(mid)
            title_count[str(t)] = item
        else:
            item = []
            item.append(mid)
            title_count[str(t)] = item
        string = t + '_' + c
        words = sw.participle(string)
        for word in words:
            if (word[1] in cx_dict) and (3 < len(word[0]) < 30 or word[0] in single_word_whitelist) and (word[0] not in black):
                if word[0] not in weibo_word:
                    weibo_word.append(word[0])
                    word_count.append(0)
        title[str(mid)] = [str(t),str(c)]

    #保留文本大于20条的新闻标题
    lable = dict()
    n = 0
    for k,v in title_count.iteritems():
        if len(v) >= 20:
            n = n + 1
            lable[str(n)] = v

    big_data = []#进行分类的微博
    big_lable = []#分类的标签
    for k,v in lable.iteritems():
        for i in v:
            big_data.append([i,title[str(i)][0],title[str(i)][1]])
            big_lable.append((int(k)+cluster-1))
            del title[str(i)]
    
    #统计每个属性的值    
    for k,v in title.iteritems():
        string = v[0] + '_' + v[1]
        for i in range(0,len(weibo_word)):
            if weibo_word[i] in string:
                word_count[i] = word_count[i] + 1

    new_weibo = []
    for i in range(0,len(word_count)):
        if word_count[i] >= 5:
            new_weibo.append(weibo_word[i])

    notin = []
    data = dict()
    for k,v in title.iteritems():
        f = 0
        row = []
        string = v[0] + '_' + v[1]
        for i in new_weibo:
            if i in string:
                n = string.count(i)
                row.append(n)
                f = 1
            else:
                row.append(0)
        if f == 1:
            data[k] = row
        else:
            notin.append(k)

    #聚类
    feature = []
    word = []
    for k,v in data.iteritems():
        word.append([k,title[k][0],title[k][1]])
        feature.append((v))
    features = np.array(feature)
    cluster_ids = milk.kmeans(features, cluster)

    return word, cluster_ids, big_data, big_lable#新闻、聚类标签、分类的微博、分类的标签 

def write_rate(count1,count2,flag):

    max_e = -1
    min_e = 99999999
    for k,v in count1.iteritems():
        if v > max_e:
            max_e = v
        if v < min_e:
            min_e = v
    
    for k,v in count2.iteritems():
        if v > max_e:
            max_e = v
        if v < min_e:
            min_e = v

    with open('./result_comment/rate%s.csv' % flag, 'wb') as f:
        writer = csv.writer(f)
        for k,v in count1.iteritems():
            s = float(v - min_e)/float(max_e - min_e)
            writer.writerow((k,s))

        for k,v in count2.iteritems():
            s = float(v - min_e)/float(max_e - min_e)
            writer.writerow((k,s))

def write_z_count(total1,total2,flag):

    sum_count = 0
    for k,v in total1.iteritems():
        sum_count = sum_count + int(v)

    for k,v in total2.iteritems():
        sum_count = sum_count + int(v)
    
    with open('./result_comment/z_count%s.csv' % flag, 'wb') as f:
        writer = csv.writer(f)
        for k,v in total1.iteritems():
            writer.writerow((k,(float(v)/float(sum_count))))

        for k,v in total2.iteritems():
            writer.writerow((k,(float(v)/float(sum_count))))

if __name__ == '__main__':
    count1,rate1,n1 = keyword('lianghui')
    count2,rate2,n2 = keyword('lianghui_pre')
    write_rate(count1,count2,'lianghui')
    write_z_count(rate1,rate2,n1,n2,'lianghui')
    #cut_word('lianghui')

