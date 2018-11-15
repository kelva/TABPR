# -*- coding: utf-8 -*-\
"""
@version: python2.7
@author: ‘licaihua‘
"""

from dataloader import LoadRatingFile_HoldKOut
from tabpr import tabpr
import multiprocessing as mp

if __name__ == '__main__':
    # Load data
    dataset = "ratings.txt"
    splitter = "\t"
    hold_k_out = 1
    train, test, num_user, num_item, num_ratings = LoadRatingFile_HoldKOut(dataset, splitter, hold_k_out)
    print("Load data (%s) done." % (dataset))
    print("#users: %d, #items: %d, #ratings: %d" % (num_user, num_item, num_ratings))
    factors = 128
    writePath = "result.txt"
    writePath1 = "recommendationlist.txt"
    # MFbpr parameters
    learning_rate = 0.05
    reg = 0.0001
    init_mean = 0
    init_stdev = 0.05
    maxIter = 40
    topK = 10
    num_thread = mp.cpu_count()
    bpr = tabpr(train, test, num_user, num_item,
                factors, learning_rate, reg, init_mean, init_stdev, writePath, writePath1, topK)
    bpr.build_model(maxIter, num_thread, batch_size=64)
