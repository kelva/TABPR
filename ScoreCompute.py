# -*- coding: utf-8 -*-\

"""
@version: python2.7
@author: ‘licaihua‘
"""
import time
from collections import Counter

'''
slotmergedata

'''


def readProgramInfo():
    """
       read the program flie and make a dict of item and item time length

       """
    f = open(programFliePath, 'r')
    i = 0
    for line in f:
        line = line.strip("\n").split("\t")
        itemLengthDic[int(line[0])] = float(line[4])
        i += 1
    f.close()


def ScoreCompute(day, item, duration):
    """
      compute the score

      """
    decay1 = 1 / 3 * 2 ** (-decay * (len(date) - 1 - day))
    length = itemLengthDic[item]
    score1 = duration / length
    if score1 > 1:
        score1 = 1.0
    score = decay1 * (score1) ** (interest / itemLengthDic[item])
    return score


def NoSlidingWindow():
    """
    compute the score without sliding window

    """
    scoreList = []
    with open(behaviorFliePath, "r") as f:
        for line in f:
            line = line.strip("\n").split("\t")
            user = int(line[0])  # user
            # if user == U:
            #     break
            item = int(line[1])
            duration = float(line[2])
            day = dateDict[line[3]]
            slot = int(line[4])
            timestamp = time.mktime(time.strptime(line[3] + ' ' + line[5], "%Y-%m-%d %H:%M:%S"))
            score = ScoreCompute(day, item, duration)
            scoreList.append([user, day, slot, item, score, duration, timestamp])

    f.close()
    SlidingWindow(scoreList)


def SlidingWindow(scoreList):
    """
    add scores of previous and posterior time slot

    """
    userTime = {}  # store the timestamp of last log in each slot
    adjacentSlotScore = []  # store the score of adjacent time slot
    IdDict = {}  # give every log a id
    n = 0
    for line in scoreList:
        userTime[(line[0], line[2])] = float(line[6])
        IdDict[(line[0], line[1], line[2], line[3])] = n
        n += 1
    for line in scoreList:
        user = line[0]
        day = line[1]
        slot = line[2]
        item = line[3]
        duration = line[5]
        timestamp = line[6]

        # add this log to its adjacent time slot
        for j in range(S):
            if j != slot and min(abs(slot - j), S - abs(slot - j)) == 1:
                # if the time slot j has no log
                if userTime.has_key((user, j)) == False:
                    continue
                # if the timestamp of the log is larger than the last log in slot j
                elif userTime.has_key((user, j)) == True:
                    if float(timestamp) > userTime[(user, j)]:
                        continue
                score = ScoreCompute(day, item, duration)

                if IdDict.has_key((user, day, j, item)):
                    key = IdDict[(user, day, j, item)]
                    scoreList[key][4] += score
                else:
                    adjacentSlotScore.append([user, day, j, item, score, duration, timestamp])
    scoreList += adjacentSlotScore
    scoreList = sorted(scoreList, key=lambda item: (int(item[0]), int(item[2]), float(item[6])))
    mergeScore(scoreList)


def mergeScore(scoreList):
    """
    add up scores of all days as the unified score for each program in each time slot.
    """

    userSlotId = {}  # give every slot of every user a id
    mergescore = {}  # the dict of scores and each item in each user's time slot
    j = -1
    for i in range(len(scoreList)):
        user = scoreList[i][0]
        slot = scoreList[i][2]
        item = scoreList[i][3]
        score = scoreList[i][4]

        if userSlotId.has_key((user, slot)) == False:
            j += 1
            userSlotId[(scoreList[i][0], scoreList[i][2])] = j
        if mergescore.has_key((userSlotId[(user, slot)], item)):
            mergescore[(userSlotId[(user, slot)], item)] += score
        else:
            mergescore[(userSlotId[(user, slot)], item)] = score

    # if the items of a time slot are all negative, i.e., score = 0
    # We treat the item with largest score and item with most viewing times as the positive item i.e., score=1

    UserSlotItem = {}  # store all items of each time slot for all users
    UserSlotScore = {}  # store all score of each time slot for all users to judge weather all scores of item are negative
    maxScoreItem = {}  # store the item with the largest score of each time slot for all users

    for i in range(len(scoreList)):
        user = scoreList[i][0]
        slot = scoreList[i][2]
        item = scoreList[i][3]
        score = mergescore[(userSlotId[(user, slot)], item)]
        if maxScoreItem.has_key((user, slot)) == False:
            maxScoreItem[(user, slot)] = [0, 0]
        if score > maxScoreItem[(user, slot)][1]:
            maxScoreItem[(user, slot)] = [item, score]

        if score >= threshold:
            mergescore[(userSlotId[(user, slot)], item)] = 1
        else:
            mergescore[(userSlotId[(user, slot)], item)] = 0

        if UserSlotScore.has_key((user, slot)) == False:
            UserSlotScore[(user, slot)] = []
        UserSlotScore[(user, slot)].append(mergescore[(userSlotId[(user, slot)], item)])

        if UserSlotItem.has_key((user, slot)) == False:
            UserSlotItem[(user, slot)] = []
        UserSlotItem[(user, slot)].append(item)

    for key in UserSlotItem:
        if sum(UserSlotScore[key]) != 0:
            continue
        else:
            mergescore[userSlotId[key], maxScoreItem[key][0]] = 1  # the item with the largest score

            item_count = Counter(UserSlotItem[key])
            item = item_count.most_common(1)  # the item with the most viewing time
            for it in item:
                mergescore[userSlotId[key], it[0]] = 1
    writeFile(scoreList, userSlotId, mergescore)


def writeFile(scoreList, userSlotId, mergescore):
    """
    write the data to ratings
    """
    with open(writePath, "w") as w:
        for i in range(len(scoreList)):
            user = scoreList[i][0]
            slot = scoreList[i][2]
            item = scoreList[i][3]
            score = mergescore[(userSlotId[(user, slot)], item)]
            w.write(str(userSlotId[(user, slot)]) + '\t' + str(scoreList[i][3]) + '\t' + str(score) + '\n')


if __name__ == '__main__':

    date = ["2017-08-28", "2017-08-29", "2017-08-30", "2017-08-31", "2017-09-01", "2017-09-02", "2017-09-03",
            "2017-09-04", "2017-09-05", "2017-09-06", "2017-09-07", "2017-09-08", "2017-09-09", "2017-09-10",
            "2017-09-11", "2017-09-12", "2017-09-13", "2017-09-14", "2017-09-15", "2017-09-16", "2017-09-17",
            "2017-09-18", "2017-09-19", "2017-09-20", "2017-09-21", "2017-09-22", "2017-09-23", "2017-09-24",
            "2017-09-25", "2017-09-26", "2017-09-27", "2017-09-28", "2017-09-29", "2017-09-30", "2017-10-01",
            "2017-10-02", "2017-10-03", "2017-10-04", "2017-10-05", "2017-10-06", "2017-10-07", "2017-10-08",
            "2017-10-09", "2017-10-10", "2017-10-11", "2017-10-12", "2017-10-13", "2017-10-14", "2017-10-15",
            "2017-10-16", "2017-10-17", "2017-10-18", "2017-10-19", "2017-10-20", "2017-10-21", "2017-10-22",
            "2017-10-23", "2017-10-24", "2017-10-25", "2017-10-26", "2017-10-27", "2017-10-28", "2017-10-29",
            "2017-10-30", "2017-10-31", "2017-11-01", "2017-11-02", "2017-11-03", "2017-11-04", "2017-11-05",
            "2017-11-06", "2017-11-07", "2017-11-08", "2017-11-09", "2017-11-10", "2017-11-11", "2017-11-12",
            "2017-11-13", "2017-11-14", "2017-11-15", "2017-11-16", "2017-11-17", "2017-11-18", "2017-11-19",
            "2017-11-20", "2017-11-21", "2017-11-22", "2017-11-23", "2017-11-24", "2017-11-25", "2017-11-26",
            ]
    programFliePath = 'programdata.txt'
    behaviorFliePath = "behaviordata.txt"
    writePath = "ratings.txt"
    dateDict = {}
    Score = []
    for i in range(0, len(date)):
        dateDict[date[i]] = i
    itemLengthDic = {}  # dict of item and item time length
    U = 10000  # numbers of user
    S = 6  # numbers of time slot
    interest = 7200  # adjust the influence of different time lengths of programs
    decay = 0.5  # adjust the influence of time decay term
    threshold = 0.6  # the threshold to distinguish positive or negative instances
    readProgramInfo()
    NoSlidingWindow()
