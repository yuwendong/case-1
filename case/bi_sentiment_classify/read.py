# -*- coding: utf-8 -*-

import json
import sys

sys.path.append('./libsvm-3.17/python/')
from sta_ad import start

f = open('items.jl')
items_mid_text = []
for line in f:
    item = json.loads(line.strip())
    items_mid_text.append((item['_id'], item['text']))
f.close()

mid_str_list = start(weibo, '0915')
print mid_str_list[:10]

