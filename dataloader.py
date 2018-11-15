# -*- coding: utf-8 -*-\
"""
@version: python2.7
@author: ‘licaihua‘
"""
def LoadRatingFile_HoldKOut(filename, splitter, K):
    """
    Each line of .rating file is: userId(starts from 0), itemId, ratingScore, time
    Each element of train is the [[item1, time1], [item2, time2] of the user, sorted by time
    Each element of test is the [user, item, time] interaction, sorted by time
    """
    train = []
    test = []

    # load ratings into train.
    num_ratings = 0
    num_item = 0
    with open(filename, "r") as f:
        line = f.readline()
        while line != None and line != "":
            arr = line.strip("\n").split(splitter)
            if (len(arr) < 3):
                continue
            user, item, score = int(arr[0]), int(arr[1]), (int(arr[2]))
            if (len(train) <= user):
                train.append([])
            try:
                train[user].append([item, score])
            except:
                train.append([])
                train[user].append([item, score])

            num_ratings += 1
            num_item = max(item, num_item)
            line = f.readline()
    num_user = len(train)
    num_item = num_item + 1

    # split into train/test
    for u in range(len(train)):
        for k in range(K):
            if (len(train[u]) == 0):
                break
            i = -1
            flag = 1
            # find the last rating who equals 1 as the test data
            while flag == 1:
                try:
                    if train[u][i][1] == 1:
                        test.append([u, train[u][i][0], train[u][i][1]])
                        del train[u][i]
                        flag = 0
                except:
                    print u, i
                i -= 1

    return train, test, num_user, num_item, num_ratings
