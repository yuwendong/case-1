# -*- coding: utf-8 -*-

import math
import time
import datetime
import types
from case.extensions import db
from case.model import CityRepost

SECOND = 1
TENSECONDS = 10 * SECOND
MINUTE = 60
FIFTEENMINUTES = 15 * MINUTE
HOUR = 3600
SIXHOURS = 6 * HOUR
DAY = 24 * HOUR

INTERVAL = HOUR

# BEGIN_TS = time.mktime(datetime.datetime(2013, 9, 1, 16, 0, 0).timetuple())
# END_TS = time.mktime(datetime.datetime(2013, 9, 1, 16, 1, 0).timetuple())

def partition_time(ts_arr, data, interval = INTERVAL):
    ts_series = []
    ts_start = ts_arr[0]
    ts_end = ts_arr[-1]
    each_step = interval
    ts_current = ts_start
    data_cursor = -1
    groups = []
    while ts_current  < ts_end:

        s_ts = ts_current
        f_ts = ts_current + each_step
        ts_series.append([s_ts, f_ts])
        group = []
        for d in data[data_cursor + 1:]:
            ts = d['ts']
            if ts >= f_ts:
                break
            data_cursor += 1
            group.append(d)
        groups.append(group)
        ts_current += each_step

    while data_cursor < len(data) - 1: # 有剩余
        groups[-1].append(data[data_cursor + 1])
        data_cursor += 1

    print 'groups', len(groups)
    return ts_series, groups

def select_groups(ts_series, groups, start_ts, end_ts):
    selected_ts_series = []
    selected_groups = []
    for index, ts_sery in enumerate(ts_series):
        if ((ts_sery[0] >= start_ts) and (ts_sery[1] <= end_ts)):
            selected_ts_series.append(ts_series[index])
            selected_groups.append(groups[index])

    return selected_ts_series, selected_groups

def partition_count(ts_arr, data, interval = INTERVAL):
    ts_series = []
    each_step = interval
    index = 0
    data_cursor = -1
    groups = []
    while index < len(ts_arr):
        f_index = min(index + each_step, len(ts_arr) - 1)
        s_ts = ts_arr[index]
        f_ts = ts_arr[f_index]
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

    while data_cursor < len(data) - 1: # 有剩余
        groups[-1].append(data[data_cursor + 1])
        data_cursor += 1

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
                        previous_data = draw_circle_data[j-1]
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



def map_line_data(groups, incremental = True):
    raw_line_data = []
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
                    if incremental == True:
                        j = index
                        while j > 0:
                            previous_data = raw_line_data[j-1]
                            if key in previous_data:
                                province_repost_count[key] = previous_data[key]
                                break
                            else:
                                j -=1
                province_repost_count[key]['count'] += 1

        if incremental == True:
            if index > 0:
                previous_data = raw_line_data[index-1]
                for key in previous_data:
                    try:
                        province_repost_count[key]
                    except KeyError:
                        province_repost_count[key] = previous_data[key]
                        continue

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
        raw_line_data.append(province_repost_count)
        draw_line_data.append(new_dict)
    for province_repost_count in draw_line_data:
        for key in province_repost_count:
            count = province_repost_count[key]['count']
            province_repost_count[key]['rank'] = repost_level(count, max_repost_num)
    return max_repost_num, draw_line_data

def work_in_out(draw_line_data):
    # in_out_results=[[(city,{'in':[(city,value),(city,value),],'out':[(city,value),(city,value),], 'total':value}),(city,{})],[]]

    in_out_results = []

    for index, group in enumerate(draw_line_data):
        latlng_count_dict = {}
        for key in group:
            out_city = key.split('-')[0]
            in_city = key.split('-')[1]
            if out_city not in latlng_count_dict:
                latlng_count_dict[out_city] = {'in': {}, 'out': {}, 'in_total': 0, 'out_total': 0, 'total': 0}
            if in_city not in latlng_count_dict:
                latlng_count_dict[in_city] = {'in': {}, 'out': {}, 'in_total':0, 'out_total': 0,  'total': 0}
            latlng_count_dict[out_city]['out'][in_city] = group[key]['count']
            latlng_count_dict[out_city]['out_total'] += group[key]['count']
            latlng_count_dict[out_city]['total'] += group[key]['count']
            latlng_count_dict[in_city]['in'][out_city] = group[key]['count']
            latlng_count_dict[in_city]['in_total'] += group[key]['count']
            latlng_count_dict[in_city]['total'] += group[key]['count']

        for city in latlng_count_dict:
            latlng_count_dict[city]['in'] = sorted(latlng_count_dict[city]['in'].iteritems(), key=lambda(k,v):v, reverse=True)
            latlng_count_dict[city]['out'] = sorted(latlng_count_dict[city]['out'].iteritems(), key=lambda(k,v):v, reverse=True)

        latlng_count_dict = sorted(latlng_count_dict.iteritems(), key=lambda(k,v):v['total'], reverse=True)
        in_out_results.append(latlng_count_dict)

    return in_out_results

def work_total_data(draw_line_data):
    draw_total_data = []
    history_data = []

    for index, group in enumerate(draw_line_data):
        latlng_count_dict = {}
        for key in group:
            city = key.split('-')[0]
            if city not in latlng_count_dict:
                latlng_count_dict[city] = 0
            latlng_count_dict[city] += group[key]['count']

        total_data_dict = {}
        for latlng in latlng_count_dict:
            cur = latlng_count_dict[latlng]
            pre = 0
            j = index
            while j > 0:
                pre_data = history_data[index-1]
                if latlng in pre_data:
                    pre = pre_data[latlng]
                    break
                else:
                    j -= 1

            status = -1
            if pre != 0:
                delta = repr(int((cur - pre)*10000/pre)/100.0) + '%'
                if ((cur - pre) > 0):
                    delta= '+' + delta
                    status = 1
            else:
                delta = repr(cur - pre)
                if ((cur - pre) > 0):
                    delta= '+' + delta
                    status = 1
            total_data_dict[latlng] = [cur, delta, repr(status)]

        history_data.append(latlng_count_dict)
        total_data_dict = sorted(total_data_dict.iteritems(),key=lambda(k, v): v[0], reverse=True)
        draw_total_data.append(total_data_dict)
    return draw_total_data



def statistics_data(groups, draw_line_data, incremental = True):
    statistics_data = []
    origin_series = []
    repost_series = []
    post_series = []
    history_data = []
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
                        previous_data = history_data[index-1]
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
                previous_data = history_data[index-1]
                for release_latlng in previous_data:
                    try:
                        latlng_count_dict[release_latlng]
                    except KeyError:
                        latlng_count_dict[release_latlng] = previous_data[release_latlng]
                        continue
        history_data.append(latlng_count_dict)

        province_count_repost_dict = {}
        province_count_origin_dict = {}
        province_count_post_dict = {}

        all_origin = 0
        all_repost = 0
        all_post = 0
        for latlng in latlng_count_dict:
            cur_repost = latlng_count_dict[latlng][0]
            cur_origin = latlng_count_dict[latlng][1]
            total_post = cur_repost + cur_origin
            all_repost += cur_repost
            all_origin += cur_origin
            all_post += total_post

            pre_repost = 0
            pre_origin = 0

            j = index
            while j > 0:
                pre_data = history_data[index-1]
                if latlng in pre_data:
                    pre_repost = pre_data[latlng][0]
                    pre_origin = pre_data[latlng][1]
                    break
                else:
                    j -= 1

            status_repost = -1
            status_origin = -1
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
            if pre_origin != 0:
                delta_origin = repr(int((cur_origin - pre_origin)*10000/pre_origin)/100.0) + '%'
                if cur_origin - pre_origin > 0:
                    delta_origin = '+' + delta_origin
                    status_origin = 1
            else:
                delta_origin = repr(cur_origin - pre_origin)
                if cur_origin - pre_origin > 0:
                    delta_origin = '+' + delta_origin
                    status_origin = 1
            if pre_repost + pre_origin != 0:
                phi = repr(int((cur_repost - pre_repost + cur_origin - pre_origin)*10000/(pre_repost + pre_origin))/100.0) + '%'
                if cur_repost - pre_repost + cur_origin - pre_origin > 0:
                    phi = '+' + phi
                    status_post = 1
            else:
                phi = repr(cur_repost - pre_repost + cur_origin - pre_origin)
                if cur_repost - pre_repost + cur_origin - pre_origin > 0:
                    phi = '+' + phi
                    status_post = 1

            province_count_repost_dict[latlng] = [cur_repost, delta_repost, repr(status_repost)]
            province_count_origin_dict[latlng] = [cur_origin, delta_origin, repr(status_origin)]
            province_count_post_dict[latlng] = [total_post, phi, repr(status_post)]

        province_count_repost_dict = sorted(province_count_repost_dict.iteritems(), key=lambda(k, v): v[0], reverse=True)
        province_count_origin_dict = sorted(province_count_origin_dict.iteritems(), key=lambda(k, v): v[0], reverse=True)
        province_count_post_dict = sorted(province_count_post_dict.iteritems(), key=lambda(k, v): v[0], reverse=True)

        statistics_data.append([province_count_repost_dict, province_count_origin_dict, province_count_post_dict])

        repost_series.append(all_repost)
        origin_series.append(all_origin)
        post_series.append(all_post)

    draw_total_data = work_total_data(draw_line_data)
    i = 0
    for sta in statistics_data:
        sta.append(draw_total_data[i])
        i += 1

    return repost_series, origin_series, post_series, statistics_data

def repost_level(count, max_repost_num):
    step = int(max_repost_num / 3)
    if not count or count <= step:
        rank = 1
    elif step < count <= 2 * step:
        rank = 2
    else:
        rank = 3
    return rank

def reverse_key(key):
    t_province_latlng, f_province_latlng = key.split('-')
    return '%s-%s' % (f_province_latlng, t_province_latlng)

