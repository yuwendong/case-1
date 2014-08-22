# -*- coding: utf-8 -*-

import os
import scws
import csv
import time
import re
from svmutil import *
import datetime
from datetime import datetime
from datetime import date
import heapq
import math
from word_cut import load_scws,word_net
from text_classify import text_net

def cut_filter(text):
    pattern_list = [r'\（分享自 .*\）', r'http://\w*']
    for i in pattern_list:
        p = re.compile(i)
        text = p.sub('', text)
    return text

def test(weibo,weibo_dict,flag):
    word_dict = dict()
    reader = csv.reader(file('./svm/new_feature.csv', 'rb'))
    for w,c in reader:
        word_dict[str(w)] = c 

    sw = load_scws()
    items = []
    for i in range(0,len(weibo)):
        words = sw.participle(weibo_dict[weibo[i]])
        row = dict()
        for word in words:
            if row.has_key(str(word[0])):
                row[str(word[0])] = row[str(word[0])] + 1
            else:
                row[str(word[0])] = 1
        items.append(row)


    f_items = []
    for i in range(0,len(items)):
        row = items[i]
        f_row = ''
        f_row = f_row + str(1)
        for k,v in word_dict.iteritems():
            if row.has_key(k):
                item = str(word_dict[k])+':'+str(row[k])
                f_row = f_row + ' ' + str(item) 
        f_items.append(f_row)

    with open('./svm_test/test%s.txt' % flag, 'wb') as f:
        writer = csv.writer(f)
        for i in range(0,len(f_items)):
            row = []
            row.append(f_items[i])
            writer.writerow((row))
    f.close()
    return items
    
def choose_ad(flag):
    y, x = svm_read_problem('./svm/new_train.txt')
    m = svm_train(y, x, '-c 4')

    y, x = svm_read_problem('./svm_test/test%s.txt' % flag)
    p_label, p_acc, p_val  = svm_predict(y, x, m)

    return p_label

def write(ind,word,flag):
    with open('./result_net/keyword%s.csv' % flag, 'wb') as f:
        writer = csv.writer(f)
        for i in range(0,len(word)):
            writer.writerow((word[i][0],str(word[i][1]),ind[0][i]))

def main(flag,k_cluster):
    weibo = []
    weibo_dict = dict()
    reader = csv.reader(file('./test/weibo%s.csv' % flag, 'rb'))
    for mid,text in reader:
        n = str(text).count('@')
        if n >= 5:
            continue
        value = cut_filter(text)
        if len(value) > 0:
            if text != '转发微博':
                weibo.append(str(mid))
                weibo_dict[str(mid)] = str(text)

    test(weibo,weibo_dict,flag)#生成测试数据
    
    lable = choose_ad(flag)#广告过滤

    ind, word = word_net(weibo,weibo_dict,lable,flag,k_cluster)#提取关键词对

    write(ind,word,flag)#写关键词对
    
    text_net(weibo,weibo_dict,lable,ind,word,flag)#提取代表文本

if __name__ == '__main__':
    main('0521',5)#生成训练集
