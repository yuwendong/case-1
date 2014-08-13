# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np

def scope(lens,cursor,dur):
    """define the begin and end point of the scope which has #dur spots before and after the cursor
    """
    begin = 0
    end = lens-1
    if dur < lens:
        begin = cursor-dur
        if begin < 0:
            begin = 0
        end = begin + dur
        if end > lens-1:
                    end = lens-1
                    begin = end-dur
    return begin,end

def sort_list(lis):
    new = [lis[0]]
    rank = [0]
    num_cursor = 1
    for num in lis[1:]:
        num_cursor += 1
        find = 0
        cursor = 0
        if num > new[0]:
            new[0:0] = [num]
            rank[0:0] = [num_cursor-1]
        else:
            for i in new:
                if num > i:
                    new[cursor:cursor] = [num]
                    rank[cursor:cursor] = [num_cursor-1]
                    find = 1
                    break
                cursor += 1
            if find == 0:
                new.append(num)
                rank.append(num_cursor-1)
    return new,rank

def filter_continuous(peaks):
    ## filter continues nodes(e.g lis[0] lis[1]), lis[1] will be filtered
    new_peaks = []
    delt = []

    for pk in peaks:
        if new_peaks == []:
            new_peaks.append(pk)
        else:
            if pk-1 in new_peaks:
                delt.append(pk)
            new_peaks.append(pk)

    new_peaks = [pk for pk in new_peaks if pk not in delt]
    return new_peaks

def min_variation(lis,dur=3,form=0):
    vs = []
    for cursor in range(len(lis)):
        begin,end = scope(len(lis),cursor,dur=dur)
        seg = lis[begin:end+1]
        min_num = min(seg)
        if form == 0:
            vs.append((lis[cursor]-min_num))
        else:
            vs.append((lis[cursor]-min_num)/min_num)
    return vs

def filter_min_gap(lis,cursor,dur=3,form=0):
    vs = min_variation(lis,dur=dur,form=form)
    if vs[cursor] >= np.mean(vs):
        return 1
    else:
        return 0

def sentiment_variation(lis,cursor,dur=3):
    stds = []
    for i in range(len(lis)):
        if i+dur > len(lis):
            break
        seg = lis[i:i+dur]
        stds.append(np.std(seg))
    global_std = np.mean(stds)

    begin,end = scope(len(lis),cursor,dur=dur)
    seg = lis[begin:end]
    ave = (seg[0]+seg[-1])/2
    local_std = np.std(seg)
    if lis[cursor]> 1.2*ave or local_std > 0.5*global_std:
        return 1
    else:
        return 0

def filter_flat(lis,peaks):
    filters = []
    for pk in peaks:
        if pk < 0 or pk > len(lis)-1:
            filters.append(pk)
            continue
        vr = sentiment_variation(lis,pk)
        if vr == 0:
            filters.append(pk)
    peaks = [pk for pk in peaks if pk not in filters]
    return peaks,filters

def save_macro(lis,cursor,dur=6):
    begin,end = scope(len(lis),cursor,dur=dur)
    seg = lis[begin:end+1]
    if lis[cursor] == max(seg):
        return 1
    else:
        return 0


def find_topN(lis,topN):
    new,rank = sort_list(lis)
    peak_x = []
    cursor = 0
    for y in new:
        if rank[cursor]!=0 and rank[cursor]!=len(new)-1:
            if y >= lis[rank[cursor]+1] and y >= lis[rank[cursor]-1]:
                peak_x.append(rank[cursor])
        cursor += 1
    peaks = filter_continuous(peak_x)
    return peaks[:topN]

def filter_micro_macro(lis,peaks,micro_dur=3,macro_dur=6,form=0):
    vs = min_variation(lis,dur=micro_dur,form=form)
    peak_gap,peak_rank = sort_list([vs[pk] for pk in peaks])

    delts = []
    for pk in peak_rank:
        if pk in delts:
            continue
        begin,end = scope(len(lis),pk,dur=macro_dur)
        for i in range(peak_rank.index(pk)+1,len(peak_rank)):
            if peak_rank[i] >= begin and peak_rank[i] <= end:
                if lis[peak_rank[i]] < lis[pk]:
                    delts.append(peak_rank[i])

    return [pk for pk in peaks if pk not in delts]


def detect_peaks(lis,topN=10,form=0,micro_dur=5,macro_dur=10):
    if len(lis) ==[]:
        return []
    elif len(lis) == 1:
        return [0]
    else:
        peaks = find_topN(lis,topN)

        if lis[0] > lis[1]:
            peaks.append(0)
        if lis[-1] > lis[-2]:
            peaks.append(len(lis)-1)

    remove_nodes = []
    scan_nodes = []
    for pk in peaks:
        remove_stay = [0,0]
        remove_stay[0] = filter_min_gap(lis,pk,dur=micro_dur,form=0)
        remove_stay[1] = save_macro(lis,pk,dur=macro_dur)
        scan_nodes.append([pk,remove_stay])
        if remove_stay == [0,0]:
            remove_nodes.append(pk)

    new_zeros = set([pk for pk in peaks if pk not in remove_nodes])
    new_zeros = list(new_zeros)
    new_zeros = filter_micro_macro(lis,new_zeros,micro_dur=3,macro_dur=6,form=0)
    new_zeros = sorted(new_zeros)

    return new_zeros

