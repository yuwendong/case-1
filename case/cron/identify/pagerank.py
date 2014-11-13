#-*- coding: utf-8 -*-

import os

try:
    from hat.job import Hat
    from hat.fs import HadoopFS
except ImportError:
    print 'Hadoop module is not installed or configured.'

from hadoop_utils import monitor, hadoop_results 

class PageRankIter(Hat):
    def mapper(self, key, value):
        #in case of some bad inputs
        if not key.strip():
            return
        tokens = value.split(',')
        symbol = tokens[0]
        if symbol != 'pr_results':
            return
        current_pr = float(tokens[1])
        total_nodes = int(tokens[2])
        if len(tokens) > 3:
            outlinks = tokens[3:]
            L = len(outlinks)
            for outlink in outlinks:
                #make sure outlink is not empty
                if outlink.strip():
                    yield (outlink, '%s,%s,%s,%s' % ('pr', key, current_pr / L, total_nodes))
            #prepare for next iter
            yield (key, '%s,%s,%s' % ('outlinks', total_nodes, ','.join(outlinks)))
        else:
            #do not have outlinks
            yield (key, '%s,%s,%s,%s' % ('pr', key, current_pr, total_nodes))
            yield (key, '%s,%s' % ('outlinks', total_nodes))

    def reducer(self, key, values):
        alpha = 0.85
        pr_sum = 0.0
        outlinks = None
        total_nodes = None
        for value in values:
            tokens = value.split(',')
            symbol = tokens[0]
            if symbol == 'pr':
                pr_i = tokens[2]
                total_nodes = int(tokens[3])
                pr_sum += float(pr_i)
            if symbol == 'outlinks':
                total_nodes = int(tokens[1])
                try:
                    outlinks = tokens[2:]
                except IndexError:
                    outlinks = None
        rank = (1 - alpha) / total_nodes + alpha * pr_sum
        if outlinks:
            yield (key, '%s,%s,%s,%s' % ('pr_results', rank, total_nodes, ','.join(outlinks)))
        else:
            yield (key, '%s,%s,%s' % ('pr_results', rank, total_nodes))


class PageRankSorter(Hat):
    def mapper(self, key, value):
        tokens = value.split(',')
        symbol = tokens[0]
        if symbol != 'pr_results':
            return
        current_pr = '%.8f' % float(tokens[1])
        yield (current_pr, key)

    def reducer(self, key, values):
        for value in values:
            yield (value, key)

def pagerank(job_id, iter_count, input_path, top_n):
    #print 'step1'
    if not (job_id and iter_count and input_path and os.path.exists(input_path)):
        print 'error'
        return []
    #print 'step1 end'
    print 'job_id:', job_id
    print 'monitor(job_id):', monitor(job_id)
    if monitor(job_id) == 'finished':
        print 'hadoop_results start'
        return hadoop_results(job_id, top_n)
    #print 'step2'
    #set work dir and put input temp file into file system
    fs = HadoopFS()
    fs.rmr('%s' % job_id)
    fs.mkdir('%s' % job_id)
    fs.put(input_path, '%s/hat_init' % job_id)
    #print 'step3'
    #init
    pr_iter = PageRankIter(input_path='%s/hat_init' % job_id, output_path='%s/hat_tmp1' % job_id)
    pr_iter.run()
    #print 'step4'
    #iter
    for i in range(iter_count-1):
        pr_iter = PageRankIter(input_path='%s/hat_tmp%s' % (job_id, (i+1)), output_path='%s/hat_tmp%s' % (job_id, (i+2)))
        pr_iter.run()
    #print 'step5'
    #sort
    pr_sorter = PageRankSorter(input_path='%s/hat_tmp%s' % (job_id, iter_count), output_path='%s/hat_results' % job_id)
    pr_sorter.run()
    #print 'step6'
    #clean init and temp files
    fs.rmr('%s/hat_tmp*' % job_id)
    fs.rmr('%s/hat_init' % job_id)
    #print 'step7'
    sorted_uids, all_uid_pr = hadoop_results(job_id, top_n)

    return sorted_uids, all_uid_pr # 返回uid排序组成的序列，所有uid的pr
    
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
