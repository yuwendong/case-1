# -*- coding: utf-8 -*-

import sys
import json

f = open('items_filter.jl')
items_dict = {}
for line in f:
    item = json.loads(line.strip())
    items_dict[item['_id']] = item
f.close()

print len(items_dict.keys())

