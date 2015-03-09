# -*- coding: utf-8 -*-
import os
from xapian_case.utils import load_scws, cut
from parameter import title_term_weight, content_term_weight

s = load_scws()
cx_dict = set(['Ag', 'a', 'an', 'Ng', 'n', 'nr', 'ns', 'nt', 'nz', 'Vg', 'v', 'vd', 'vn', '@', 'j']) # 关键词词性字典

EXTRA_BLACK_LIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'black.txt')

def load_black_words():
    one_words = set([line.strip('\r\n') for line in file(EXTRA_BLACK_LIST_PATH)])
    return one_words

black_words = load_black_words()

def cut_words(text):
    if not isinstance(text, str):
        print 'type_content:', type(text)
        raise ValueError('cut words input text must be string')

    cx_terms = cut(s, text, cx=True)
    
    return [term for term, cx in cx_terms if cx in cx_dict and term not in black_words]

def cut_news(input_news_list):
    news_cut_list = []
    for news in input_news_list:
        keywords_weight = {}
        title = news['title']
        content = news['content168']

        title_terms = cut_words(title.encode('utf-8'))
        content_terms = cut_words(content.encode('utf-8'))

        for term in title_terms:
            try:
                keywords_weight[term] += title_term_weight
            except KeyError:
                keywords_weight[term] = title_term_weight

        for term in content_terms:
            try:
                keywords_weight[term] += content_term_weight
            except KeyError:
                keywords_weight[term] = content_term_weight
        
        keywords_count = dict()
        total_weight = sum(keywords_weight.values())
        for keyword, weight in keywords_weight.iteritems():
            ratio = float(weight) / float(total_weight)
            if ratio >= 0.8 or weight <= 3:
                continue
            keywords_count[keyword] = weight
        sort_keywords = sorted(keywords_count.items(), key = lambda x:x[1], reverse=True)
        keywords_top = sort_keywords[:50]
        new_keywords_count = dict()
        for keyword, count in keywords_top:
            new_keywords_count[keyword] = count
        news['keywords'] = new_keywords_count
        news_cut_list.append(news)
        # news['keywords'] = {'term1':count1, 'term2':count2...}
    #print 'len(news_cut_list):', len(news_cut_list)
    return news_cut_list

def get_news_keywords(news_cut_list):
    keywords_list = []
    all_news_keywords = dict()
    for news in news_cut_list:
        keywords_count = news['keywords']
        for keyword in keywords_count:
            count = keywords_count[keyword]
            try:
                all_news_keywords[keyword] += count
            except KeyError:
                all_news_keywords[keyword] = count
                
    sort_all_news_keywords = sorted(all_news_keywords.items(), key = lambda x:x[1], reverse=True)
    top_keyword = sort_all_news_keywords[:50]
    # top_keyword = [(keyword1, count1), (keyword2, count2)...]
    keywords_list = [keyword for keyword, count in top_keyword]
    # keywords_list = [keyword1, keyword2...]
    return keywords_list

def get_news_weight(news_cut_list, keywords_list):
    weight_list = []
    for news in news_cut_list:
        weight = 0
        keywords_count = news['keywords']
        for keyword in keywords_count:
            if keyword in keywords_list:
                weight += 1
        news['weight'] = float(weight) / 50
        weight_list.append(news)
    print 'len(weight_list):', len(weight_list)
    return weight_list

def get_top_weight_news(weight_list):
    sort_list = []
    for news in weight_list:
        weight = news['weight']
        timestamp = news['timestamp']
        sort_list.append((news, weight, timestamp))
    sort_news = sorted(sort_list, key = lambda a:a[2], reverse=True)
    sort_timestamp_news = sort_news[:50]
    print 'len(sort_timestamp_news):', len(sort_timestamp_news)
    sort_news = sorted(sort_timestamp_news, key = lambda a:a[1], reverse=True)
    maker_list = [news for news, weight, timestamp in sort_news]
    #sort_weight_news = sort_news[:20]
    #maker_list = [news for news, weight, timestamp in sort_weight_news]
        
    return maker_list

