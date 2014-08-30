# -*- coding: utf-8 -*-

import math
import time
import datetime
from city_repost_search import repost_search

SECOND = 1
TENSECONDS = 10 * SECOND
MINUTE = 60
FIFTEENMINUTES = 15 * MINUTE
HOUR = 3600
SIXHOURS = 6 * HOUR
DAY = 24 * HOUR

INTERVAL = TENSECONDS

BEGIN_TS = time.mktime(datetime.datetime(2013, 9, 1, 16, 0, 0).timetuple())
END_TS = time.mktime(datetime.datetime(2013, 9, 1, 16, 1, 0).timetuple())

def partition_count(ts_arr, data, interval = INTERVAL):
    ts_series = []
    each_step = interval
    index = 0
    index += each_step
    data_cursor = -1
    groups = []
    while index < len(ts_arr):
        p_index = index - each_step
        s_ts = ts_arr[p_index]
        f_ts = ts_arr[index]
        ts_series.append([s_ts, f_ts])
        group = []
        for d in data[data_cursor + 1:]:
            ts = d['ts']
            if ts >= f_ts:
                break
            group.append(d)
            data_cursor += 1
        groups.append(group)
        index += each_step
    if index >= len(ts_arr):
        p_index = index - each_step
        s_ts = ts_arr[p_index]
        f_ts = ts_arr[-1]
        ts_series.append([s_ts, f_ts])
        group = []
        for d in data[data_cursor + 1:]:
            ts = d['ts']
            if ts >= f_ts:
                break
            group.append(d)
            data_cursor += 1
        groups.append(group)
    return ts_series, groups


def map_circle_data(groups, incremental = True):
    draw_circle_data = []
    for index, group in enumerate(groups):
        latlng_count_dict = {}
        for status in group:

            if status['original']:
                release_latlng = status['origin_location']
            else:
                release_latlng = status['repost_location']

            if release_latlng not in latlng_count_dict:
                repost_num = 0
                origin_num = 0
                if incremental == True:
                    j = index
                    while j > 0:
                        previous_data = draw_circle_data[index-1]
                        if release_latlng in previous_data:
                            repost_num = previous_data[release_latlng][0]
                            origin_num = previous_data[release_latlng][1]
                            break
                        else:
                            j -= 1
                latlng_count_dict[release_latlng] = [repost_num, origin_num]

            if status['original']:
                latlng_count_dict[release_latlng][1] += 1
            else:
                latlng_count_dict[release_latlng][0] += 1

        if incremental == True:
            if index > 0:
                previous_data = draw_circle_data[index-1]
                for release_latlng in previous_data:
                    try:
                        latlng_count_dict[release_latlng]
                    except KeyError:
                        latlng_count_dict[release_latlng] = previous_data[release_latlng]
                        continue
        draw_circle_data.append(latlng_count_dict)
    return draw_circle_data



def map_line_data(groups):
    draw_line_data = []
    max_repost_num = 0
    for index, group in enumerate(groups):
        province_repost_count = {}
        for status in group:
            if not status['original']:
                t_province_latlng = status['origin_location']
                f_province_latlng = status['repost_location']
                key = '%s-%s' % (t_province_latlng, f_province_latlng)
                if key not in province_repost_count:
                    province_repost_count[key] = {'count': 0, 'rank': 0}
                province_repost_count[key]['count'] += 1

        visited = set()
        new_dict = {}
        for key in province_repost_count:
            r_key = reverse_key(key)

            if r_key in visited or key in visited:
                continue
            if key == r_key:
                continue

            count = province_repost_count[key]['count']
            if r_key in province_repost_count:
                r_count = province_repost_count[r_key]['count']
                if count > r_count:
                    count += r_count
                    new_dict[key] = {'count': count,'rank': 0}
                else:
                    r_count += count
                    new_dict[r_key] = {'count': r_count,'rank': 0}
                max_repost_num = max(max_repost_num, count, r_count)
                visited.add(r_key)
            else:
                new_dict[key] = {'count': count,'rank': 0}
                max_repost_num = max(max_repost_num, count)
            visited.add(key)
        province_repost_count = new_dict
        draw_line_data.append(province_repost_count)
    for province_repost_count in draw_line_data:
        for key in province_repost_count:
            count = province_repost_count[key]['count']
            province_repost_count[key]['rank'] = repost_level(count, max_repost_num)
    return max_repost_num, draw_line_data

def statistics_data(groups, alertcoe):
    statistics_data = []
    fipost_series = []
    repost_series = []
    post_series = []
    history_data = []
    alerts = []
    alert = False
    first = True
    max_phi = 0
    max_delta_repost = 0
    max_delta_fipost = 0
    for index, group in enumerate(groups):
        latlng_count_dict = {}
        for status in group:
            release_latlng = status['release_province_latlng']
            province_name = status['release_province']
            if release_latlng not in latlng_count_dict:
                repost_num = 0
                fipost_num = 0
                latlng_count_dict[release_latlng] = [repost_num, fipost_num, province_name]
            if status['original']:
                latlng_count_dict[release_latlng][1] += 1
            else:
                latlng_count_dict[release_latlng][0] += 1
        province_count_repost_dict = {}
        province_count_fipost_dict = {}
        province_count_post_dict = {}
##        province_alert = {}
        all_fipost = 0
        all_repost = 0
        all_post = 0
        for latlng in latlng_count_dict:
            cur_repost = latlng_count_dict[latlng][0]
            cur_fipost = latlng_count_dict[latlng][1]
            all_fipost += cur_repost
            all_repost += cur_fipost
            all_post += all_fipost + all_repost
            province_name = latlng_count_dict[latlng][2]
            pre_repost = 0
            pre_fipost = 0
            j = index
            while j > 0:
                pre_data = history_data[index-1]
                if latlng in pre_data:
                    pre_repost = pre_data[latlng][0]
                    pre_fipost = pre_data[latlng][1]
                    break
                else:
                    j -= 1
            status_repost = -1
            status_fipost = -1
            status_post = -1
            if pre_repost != 0:
                delta_repost = repr(int((cur_repost - pre_repost)*10000/pre_repost)/100.0) + '%'
                if cur_repost - pre_repost > 0:
                    delta_repost = '+' + delta_repost
                    status_repost = 1
            else:
                delta_repost = repr(cur_repost - pre_repost)
                if cur_repost - pre_repost > 0:
                    delta_repost = '+' + delta_repost
                    status_repost = 1
            if pre_fipost != 0:
                delta_fipost = repr(int((cur_fipost - pre_fipost)*10000/pre_fipost)/100.0) + '%'
                if cur_fipost - pre_fipost > 0:
                    delta_fipost = '+' + delta_fipost
                    status_fipost = 1
            else:
                delta_fipost = repr(cur_fipost - pre_fipost)
                if cur_fipost - pre_fipost > 0:
                    delta_fipost = '+' + delta_fipost
                    status_fipost = 1
            if pre_repost + pre_fipost != 0:
                phi = repr(int((cur_repost - pre_repost + cur_fipost - pre_fipost)*10000/(pre_repost + pre_fipost))/100.0) + '%'
                if cur_repost - pre_repost + cur_fipost - pre_fipost > 0:
                    phi = '+' + phi
                    status_post = 1
            else:
                phi = repr(cur_repost - pre_repost + cur_fipost - pre_fipost)
                if cur_repost - pre_repost + cur_fipost - pre_fipost > 0:
                    phi = '+' + phi
                    status_post = 1
            total_post = cur_repost + cur_fipost
            
##            if j > 0:
##                if max_phi < phi:
##                    max_phi = phi
##                if max_delta_repost < delta_repost:
##                    max_delta_repost = delta_repost
##                if max_delta_fipost < delta_fipost:
##                    max_delta_fipost = delta_fipost
                
##            if phi > 200 and first:
##                alert = True
##                province_alert[latlng] = {'name': province_name, 'count': phi}
##            province_alert[latlng] = {'name': province_name, 'count': (phi, delta_repost, delta_fipost)}
                
##            data = [cur_repost, cur_fipost, total_post]
            province_count_repost_dict[province_name] = [cur_repost, delta_repost, repr(status_repost)]
            province_count_fipost_dict[province_name] = [cur_fipost, delta_fipost, repr(status_fipost)]
            province_count_post_dict[province_name] = [total_post, phi, repr(status_post)]
##        if alert:
##            first = False
##        alerts.append(province_alert)
        history_data.append(latlng_count_dict)
        province_count_repost_dict = sorted(province_count_repost_dict.iteritems(), key=lambda(k, v): v[0], reverse=True)
        province_count_fipost_dict = sorted(province_count_fipost_dict.iteritems(), key=lambda(k, v): v[0], reverse=True)
        province_count_post_dict = sorted(province_count_post_dict.iteritems(), key=lambda(k, v): v[0], reverse=True)
        
        statistics_data.append([province_count_repost_dict, province_count_fipost_dict, province_count_post_dict])
        
        repost_series.append(all_repost)
        fipost_series.append(all_fipost)
        post_series.append(all_post)
    return repost_series, fipost_series, post_series, statistics_data                 
##    alerts.append({})
##    alert_phi, alert_delta_repost, alert_delta_fipost = alert_degree(max_phi, max_delta_repost, max_delta_fipost, alertcoe)
##    
##    alerts_results = []
##    count = 0
##    for ale in alerts:
##        if count == 0:
##            alerts_results.append({})
##            count +=1
##            continue
##        count += 1
##        alert_dict = {}
##        for key in ale.keys():
##            latlng = key
##            name = ale[key]['name']
##            phi, delta_repost, delta_fipost = ale[key]['count']
##            status_dict = {}
##            if phi > alert_phi:
##                status_dict['total'] = int(phi*100/max_phi)/100.0
##            else:
##                status_dict['total'] = 0
##            if delta_repost > alert_delta_repost:
##                status_dict['repost'] = int(delta_repost*100/max_delta_repost)/100.0
##            else:
##                status_dict['repost'] = 0
##            if delta_fipost > alert_delta_fipost:
##                status_dict['fipost'] = int(delta_fipost*100/max_delta_fipost)/100.0
##            else:
##                status_dict['fipost'] = 0
##            if status_dict['total'] != 0 or status_dict['repost'] != 0 or status_dict['fipost'] != 0:
##                alert_dict[latlng] = {'name': name, 'status': status_dict}
##        alerts_results.append(alert_dict)

def repost_level(count, max_repost_num):
    step = int(max_repost_num / 3)
    if not count or count <= 0:
        rank = 1
    elif step < count <= 2 * step:
        rank = 2
    elif:
        rank = 3
    return rank

def reverse_key(key):
    t_province_latlng, f_province_latlng = key.split('-')
    return '%s-%s' % (f_province_latlng, t_province_latlng)

if __name__ == '__main__':
    topic = u'中国'
    ts_arr, results = repost_search(topic, BEGIN_TS, END_TS)
    ts_series, groups = partition_count(ts_arr, results)
    draw_circle_data = map_circle_data(groups)
    max_repost_num, draw_line_data = map_line_data(groups)
    statistic_data, alerts = statistics_data(groups)
