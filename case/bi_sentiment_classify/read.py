# -*- coding: utf-8 -*-

import sys
import json

sys.path.append('./libsvm-3.17/python')
from sta_ad import start

f = open('items.jl')
items_dict = {}
items_mid_text = []
for line in f:
    item = json.loads(line.strip())
    items_dict[item['_id']] = item
    items_mid_text.append((item['_id'], item['text'].encode('utf-8')))
f.close()

print len(items_mid_text)
mid_str_list = start(items_mid_text, '0915')
print mid_str_list[:10]
print len(mid_str_list)

fw = open('items_filter.jl', 'wb')
for mid in mid_str_list:
    fw.write(json.dumps(items_dict[int(mid)]) + '\n')
fw.close()

