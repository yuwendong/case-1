# -*- coding: utf-8 -*-

import os
import scws
import csv
from news_cut import *

def main(flag,cluster):

    news, cluster_ids, big_news, big_lable = cut_word(flag,cluster)#进行新闻的分类与聚类

    count1,rate1,n1 = keyword(flag,news,cluster_ids[0])#对聚类的新闻提关键词对、代表性文本

    count2,rate2,n2 = keyword(flag,big_news,big_lable)#对分类的新闻提关键词对、代表性文本

    write_rate(count1,count2,flag)#计算每一类的混杂度

    write_z_count(n1,n2,flag)#计算每一类的比例

if __name__ == '__main__':
    main('lianghui',20)
