# -*- coding: utf-8 -*-

import os
import csv
from svmutil import *

def main(flag):
    y, x = svm_read_problem('./svm_data/new_train.txt')
    m = svm_train(y, x, '-c 4')#-v 5

    y, x = svm_read_problem('./svm_data/test%s.txt' % flag)
    p_label, p_acc, p_val  = svm_predict(y, x, m)

    with open('./svm_data/lable%s.txt' % flag, 'wb') as f:
        writer = csv.writer(f)
        for i in range(0,len(p_label)):
            row = []
            row.append(int(p_label[i]))
            writer.writerow((row))
    f.close()
    

if __name__ == '__main__':
    main('maoming')
