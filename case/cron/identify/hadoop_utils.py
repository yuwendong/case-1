# -*- coding: utf-8 -*-

try:
    from hat.fs import HadoopFS
except ImportError:
    print 'Hadoop module is not installed or configured.'

import sys
import time
import tempfile
sys.path.append('../')
from time_utils import unix2hadoop_date

def generate_job_id(ts, window_size, topic_id, network_type):
    date = unix2hadoop_date(ts)
    job_id = '%s_%s_%s_%s' % (date, window_size, topic_id, network_type)
    return job_id

def monitor(job_id):
    fs = HadoopFS()
    finished = False
    has_tmps = False
    outputs = fs.ls('%s' % job_id)
    if not outputs:
        return 'data_not_prepared'
    count = 0
    for line in outputs:
        if 'tmp' in line:
            count += 1
            has_tmps = True
        if 'results' in line:
             if not has_tmps:
                 finished = True
    if not finished:
        return 'stage%s' % count
    else:
        return 'finished'

def hadoop_results(job_id, top_n):
    data = []
    fs = HadoopFS()
    outputs = fs.cat('%s/hat_results/*' % job_id)
    if not outputs:
        return [], {}
    all_outputs = outputs
    if len(outputs) > top_n:
        outputs = outputs[-top_n:]
    outputs.reverse()
    sorted_uids = []
    all_uid_r = {}
    for line in all_outputs:
        uid, r = line.strip().split('\t')
        all_uid_r[uid] = r
    for line in outputs:
        uid, r = line.strip().split('\t')
        sorted_uids.append(uid)
    return sorted_uids, all_uid_r

def prepare_data(topic_id):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file = emulate(tmp_file)
    tmp_file.flush()
    return tmp_file

def emulate(tmp_file):
    import networkx as nx
    g = nx.DiGraph(nx.powerlaw_cluster_graph(1000, 3, 0.001))
    N = len(g.nodes())
    for node in g.nodes():
        outlinks = g.out_edges(nbunch=[node])
        outlinks = map(str, [n2 for n1, n2 in outlinks])
        if not outlinks:
            value = 'pr_results,%s,%s' % (1.0/N, N)
            tmp_file.write('%s\t%s\n' % (node, value))
        else:
            outlinks_str = ','.join(outlinks)
            value = 'pr_results,%s,%s,' % (1.0/N, N)
            value += outlinks_str
            tmp_file.write('%s\t%s\n' % (node, value))
    return tmp_file

def main():
    job_id = '2013_04_11_-1_1'
    print monitor(job_id)
    data = read_results(job_id, 50, 10)
    print data

if __name__ == '__main__': main()
