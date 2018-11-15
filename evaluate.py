# -*- coding: utf-8 -*-\
"""
@version: python2.7
@author: ‘licaihua‘
"""
import heapq

# Global variables that are shared across processes
_model = None
_testRatings = None
_K = None


def evaluate_model(model, testRatings, K):
    """
    Evaluate the performance (HR, MRR) of top-K recommendation
    Return: score of each test rating.
    """
    global _model
    global _testRatings
    global _K
    _model = model
    _testRatings = testRatings
    _K = K
    num_rating = len(testRatings)

    res = map(eval_one_rating, range(num_rating))
    hits = [r[0] for r in res]
    mrrs = [r[1] for r in res]
    return (hits, mrrs)


def eval_one_rating(idx):
    rating = _testRatings[idx]
    hr = mrr = 0
    u = rating[0]
    gtItem = rating[1]  # item
    map_item_score = {}
    # Get the score of the test item first
    maxScore = _model.predict(u, gtItem)
    # Early stopping if there are K items larger than maxScore.
    countLarger = 0

    _model.w1.write(str(gtItem) + "\t")
    for i in xrange(_model.num_item):

        early_stop = False
        score = _model.predict(u, i)
        map_item_score[i] = score
        if score > maxScore:
            countLarger += 1
        if countLarger > _K:  # topk
            hr = mrr = 0
            early_stop = True
            break
    # Generate topK rank list
    _model.w1.write(str(early_stop) + '\t')
    if early_stop == False:
        ranklist = heapq.nlargest(_K, map_item_score, key=map_item_score.get)
        for item in ranklist:
            _model.w1.write(str(item) + '\t')
        _model.w1.write("\n")
        hr = getHitRatio(ranklist, gtItem)
        mrr = getMRR(ranklist, gtItem)
    else:
        _model.w1.write("\n")
    return (hr, mrr)


def getHitRatio(ranklist, gtItem):
    for item in ranklist:
        if item == gtItem:
            return 1
    return 0


def getMRR(ranklist, gtItem):
    for i in xrange(len(ranklist)):
        item = ranklist[i]
        if item == gtItem:
            return 1 / (i + 1)
    return 0
