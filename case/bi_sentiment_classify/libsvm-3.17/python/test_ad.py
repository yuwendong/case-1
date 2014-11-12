# -*- coding: utf-8 -*-

import os
import csv
from sta_ad import start

def main(flag):

    weibo = []
    reader = csv.reader(file('./test/weibo%s.csv' % flag, 'rb'))
    for mid,text in reader:
        weibo.append([mid,text])

    data = start(weibo,flag)

    for i in range(0,len(data)):
        print data[i]

if __name__ == '__main__':
    main('0521')#生成训练集
