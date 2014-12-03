#-*- coding:utf-8 -*-
from __future__ import division
import numpy as np

def scope(lens, cursor, dur):
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
    lis_dict = {}
    for i in range(len(lis)):
        value = lis[i]
        index = i
        lis_dict[i] = value
    sorted_list = sorted(lis_dict.items(), key=lambda x:x[1])
    print 'sorted_list:', sorted_list
    new = []
    rank = []
    for index, value in sorted_list:
        new.append(value)
        rank.append(index)
    print 'new:', new
    print 'rank:', rank
    return new, rank
        
def filter_continues(bottoms):
    new_bottoms = []
    remove_list = []

    for bottom in bottoms:
        if new_bottoms==[]:
            new_bottoms.append(bottom)
        else:
            if bottom-1 in new_bottoms:
                remove_list.append(bottom)
            new_bottoms.append(bottom)

    new_bottoms = [bottom for bottom in new_bottoms if bottoms not in remove_list]
    return new_bottoms
    
def save_micro(lis, cursor, dur=6):
    begin, end = scope(len(lis), cursor, dur=dur)
    seg = lis[begin:end+1]
    if lis[cursor] == min(seg):
        return 1
    else:
        return 0

def find_bottom(lis, n):
    # n control the number of the bottom
    new, rank = sort_list(lis)
    bottom_list = []
    count = 0
    for i in new:
        #print 'i:', i
        # the first if control the minmize is not the first or the last
        if rank[count]!=0 and rank[count]!=len(new)-1:
            if i<=lis[rank[count]-1] and i<=lis[rank[count]+1]:
                print 'i:', i
                bottom_list.append(rank[count])
        count += 1
        # bottoms = [index1, index2....]
        print 'bottoms:', bottom_list
        bottoms = filter_continues(bottom_list)
        print 'filter_continues:', bottoms
    return bottoms[:n]

def max_variation(lis, dur, form):
    vs = []
    for i in range(len(lis)):
        begin,end = scope(len(lis), i, dur)
        seg = lis[begin:end+1]
        max_num = max(seg)
        if form==0:
            vs.append((lis[i] - max_num))
        else:
            vs.append((lis[i] - max_num) / max_num)
    return vs

def filter_min_gap(lis, bottom, dur, form=0):
    vs = max_variation(lis, dur, form)
    print 'vs:', vs
    if vs[bottom] <= np.mean(vs):
        return 1
    else:
        return 0


def filter_macro_micro(lis, bottoms, micro_dur=3, macro_dur=6, form=0):
    vs = max_variation(lis, dur=micro_dur, form=form)
    bottom_peak, bottom_rank = sort_list([vs[bottom] for bottom in bottoms])

    delts = []
    for bottom in bottom_rank:
        if bottom in delts:
            continue
        begin, end = scope(len(lis), bottom, dur=macro_dur)
        for i in range(bottom_rank.index(bottom)+1, len(bottom_rank)):
            if bottom_rank[i] >= begin and bottom_rank[i] <= end:
                if lis[bottom_rank[i]] > lis[bottom]:
                    delts.append(bottom_rank[i])

        return [bottom for bottom in bottoms if bottom not in delts]
                

def detect_bottom(lis, bottom_n=10, form=0, micro_dur=5, macro_dur=10):
    if lis == []:
        return []
    elif len(lis)==1:
        return [0]
    else:
        bottoms = find_bottom(lis, bottom_n)
        print 'bottoms1:', bottoms
        # consider the first and the last
        if lis[0] < lis[1]:
            bottoms.append(0)
        if lis[-1] < lis[-2]:
            bottoms.append(len(lis)-1)
    remove_nodes = []
    scan_nodes = []
    print 'bottoms2:', bottoms
    for bottom in bottoms:
        remove_stay = [0,0]
        remove_stay[0] = filter_min_gap(lis, bottom, dur=micro_dur, form=0)
        remove_stay[1] = save_micro(lis, bottom, dur=macro_dur)
        scan_nodes.append([bottom, remove_stay])
        if remove_stay ==[0, 0]:
            remove_nodes.append(bottom)

    new_zeros = set([bottom for bottom in bottoms if bottom not in remove_nodes])
    new_zeros = list(new_zeros)
    new_zeros = filter_macro_micro(lis, new_zeros, micro_dur=3, macro_dur=6, form=0)
    new_zeros = sorted(new_zeros)
    print 'end new_zeros:', new_zeros
    return new_zeros

if __name__=='__main__':
    lis = [3,4,1,2,5,7,8,12,6,7,8,7,12,3,4,8,2,7,6]
    print 'lis:', lis
    detect_bottom(lis)
    


        
        
            
