#-*-coding=utf-8-*-

import re

f = open('mongodb_batch_write_user_1.log')
fw = open('mongodb_batch_write_user_stat.txt', 'w')
for line in f:
    line_text = line.strip()

    total_deliver_count = re.search(r'total deliver (.*?),', line_text)
    if total_deliver_count:
        total_deliver_count = total_deliver_count.group(1)

    ten_thousand_cost = re.search(r'cost: (.*?) sec', line_text)
    if ten_thousand_cost:
        ten_thousand_cost = ten_thousand_cost.group(1)

    avg_speed = re.search(r'avg: (.*?)per', line_text)
    if avg_speed:
        avg_speed = avg_speed.group(1)

    if avg_speed:
        print total_deliver_count, ten_thousand_cost, avg_speed
        fw.write('%s\t%s\t%s\n' % (total_deliver_count, ten_thousand_cost, avg_speed))

f.close()
fw.close()
