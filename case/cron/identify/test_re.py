# -*- coding: utf-8 -*-

import re

if __name__=='__main__':
    weibo_text = '天气很冷//@风风风风：降温降温//@alalal:eryo:er'
    weibo_text1 = 'asdasf//@asdfads:asfsdgsdfg//@erqewer:dfgdf'
    if isinstance(weibo_text, str):
        weibo_text = weibo_text.decode('utf-8', 'ignore')
    direct_superior_weibo = re.findall(r'//@[a-zA-Z]+:(\S+)/{2}', weibo_text)
    #RE = re.compile(u'//@([a-zA-Z-_⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]+):(\s+)/{2}', re.UNICODE)
    #result = RE.findall(weibo_text1)
    weibo_list = weibo_text.split('//@')
    weibo1 = weibo_list[1]
    index = weibo1.find(':')
    result = weibo1[index+1:]
    RE = re.compile(u'//@[a-zA-Z]+:(\S+)/{2}', re.UNICODE)
    result1 = RE.findall(weibo_text)
    print result1
