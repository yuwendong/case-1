#-*- coding: utf-8 -*-

import os

try:
    from hat.job import Hat
    from hat.fs import HadoopFS
except ImportError:
    print 'Hadoop module is not installed or configured.'

from hadoop_utils import monitor, hadoop_results


class TsRankIter(Hat):
    def mapper(self, key, value):
        #in case of somw bad inputs
        if not key.strip():
            return
        tokens = value.split(',') # value = 'ts_results,1/n,n,B+0.23,C+0.31' 此处0.23表示的是i(B,A)
        symbol = tokens[0]
        if symbol != 'tr_results':
            return
        current_tr = float(tokens[1])
        total_nodes = int(tokens[2])
        if len(tokens) > 3:
            outlink_pairs = tokens[3:] # outlink_pairs = ['B+i(B,A)', 'C+i(C,A)'...]
            L= len(outlink_pairs)
            for outlink_pair in outlink_pairs:
                # make sure outlink is not empty
                if outlink_pair.strip():
                    outlink, i = outlink_pair.split('+')
                    i = float(i)
                    yield (outlink, '%s,%s,%s,%s' % ('tr', key, current_tr*i, total_nodes))
            # prepare for next iter
            yield (key, '%s,%s,%s' % ('outlinks', total_nodes, ','.join(outlink_pairs)))
        else:
            # do not have outlinks
            yield (key, '%s,%s,%s,%s' % ('tr', key, current_tr, total_nodes))
            yield (key, '%s,%s' % ('outlinks', total_nodes))

    def reducer(self, key, value):
        d = 0.2
        tr_sum = 0.0
        outlink_pairs = None
        total_nodes = None
        for value in values: # HAT中已经进行集群group，即将发射向点B的所有信息集合在key为B的values中
            tokens = value.split(',') # value为'tr,A,tr(A)*i(B,A),N'或者'outlinks,N,outlink_pairs'
            symbol = tokens[0]
            if symbol == 'tr':
                tr_i = tokens[2] # tr_i = tr(A)*i(B,A)
                total_nodes = int(tokens[3])
                tr_sum += float(tr_i)
            elif symbol == 'outlinks':
                total_nodes = int(tokens[1])
                try:
                    outlink_pairs = tokens[2:]
                except IndexError:
                    outlinks = None
        rank = d * (1.0 / total_nodes) + (1 - d) * tr_sum
        if outlink_pairs:
            yield(key, '%s,%s,%s,%s' % ('tr_results', rank, total_nodes, ','.join(outlink_pairs)))
        else:
            yield(key, '%s,%s,%s' % ('tr_results', rank, total_nodes))
            

        
class TsRankSorter(Hat):
    def mapper(self, key, value):
        tokens = value.split(',')
        symbol = tokens[0]
        if symbol != 'tr_results':
            return
        current_tr = '%.8f' % float(tokens[1])
        yield (current_tr, key)

    def reducer(self, key, values):
        for value in values:
            yield (value, key)


def ts_rank(job_id, iter_count, input_path, top_n):
    if not(job_id and iter_count and input_path and os.path.exists(input_path)):
        print 'error'
        return []
    print 'job_id:', monitor(job_id)
    if monitor(job_id) == 'finished':
        print 'hadoop_results start'
        return hadoop_results(job_id, top_n)
    fs = HadoopFS()
    fs.rmr('%s' % job_id)
    fs.mkdir('%s' % job_id)
    fs.put(input_path, '%s/hat_init' % job_id) # input文件的路径
    #init
    ts_rank_iter = TsRankIter(input_path='%s/hat_init' % job_id, output_path='%s/hat_tmp1' % job_id)
    ts_rank_iter.run()
    #iter
    for i in range(iter_count-1):
        ts_rank_iter = TsRankIter(input_path='%s/hat_tmp%s' % (job_id, (i+1)), output_path='%s/hat_tmp%s' % (job_id, (i+2)))
        ts_rank_iter.run()
    #sort
    ts_rank_sorter = TsRankSorter(input_path='%s/hat_tmp%s' % (job_id, iter_count), output_path='%s/hat_results' % job_id) # 这里的input_path是不是错了?
    ts_rank_sorter.run()
    # clean init and temp files
    fs.rmr('%s/hat_tmp*' % job_id)
    fs.rmr('%s/hat_init' % job_id)
    sorted_uids, all_uid_tr = hadoop_results(job_id, top_n)

    return sorted_uids, all_uid_tr

if __name__ == '__main__':
    from optparse import OptionParser

    optparser = OptionParser()
    optparser.add_option('-j', '--job_id', dest='job_id', help='Hadoop Job ID', default=None, type='string')
    optparser.add_option('-c', '--iter_count', dest='iter_count', help='PageRank Iter Count', default=2, type='int')
    optparser.add_option('-i', '--input', dest='input_path', help='Input File Path', default=None, type='string')
    (options, args) = optparser.parse_args()

    job_id = options.job_id
    iter_count = options.iter_count
    input_path = options.input_path

    if not (job_id and iter_count and input_path and os.path.exists(input_path)):
        print 'Usage: python pagerank.py --help'
        sys.exit()

    top_n = 500
    for uid in pagerank(job_id, iter_count, input_path, top_n):
        print uid

