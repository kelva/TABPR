# -*- coding: utf-8 -*-\

import numpy as np
import theano
import theano.tensor as T
from sets import Set
from evaluate import evaluate_model
import time


class tabpr(object):
    '''
    BPR learning for MF model
    '''

    def __init__(self, train, test, num_user, num_item,
                 factors, learning_rate, reg, init_mean, init_stdev, writePath, writePath1, topK):
        '''
        Constructor
        '''
        self.train = train
        self.test = test
        self.num_user = num_user
        self.num_item = num_item
        self.factors = factors
        self.learning_rate = learning_rate
        self.reg = reg
        self.writePath = writePath
        self.topK = topK
        w1 = open(writePath1, 'w')
        self.w1 = w1
        # user & item latent vectors
        U_init = np.random.normal(loc=init_mean, scale=init_stdev, size=(num_user, factors))
        V_init = np.random.normal(loc=init_mean, scale=init_stdev, size=(num_item, factors))
        self.U = theano.shared(value=U_init.astype(theano.config.floatX),
                               name='U', borrow=True)
        self.V = theano.shared(value=V_init.astype(theano.config.floatX),
                               name='V', borrow=True)

        # Each element is the set of items for a user, used for negative sampling
        self.items_of_user = []  #
        self.num_rating = 0  # number of ratings
        for u in xrange(len(train)):
            self.items_of_user.append(Set([]))
            for i in xrange(len(train[u])):
                item = train[u][i][0]
                self.items_of_user[u].add(item)
                self.num_rating += 1

        # batch variables for computing gradients

        u = T.lvector('u')
        i = T.lvector('i')
        j = T.lvector('j')
        lr = T.scalar('lr')  # 数值类型

        # loss of the sample
        y_ui = T.dot(self.U[u], self.V[i].T).diagonal()
        y_uj = T.dot(self.U[u], self.V[j].T).diagonal()
        regularizer = self.reg * ((self.U[u] ** 2).sum() +
                                  (self.V[i] ** 2).sum() +
                                  (self.V[j] ** 2).sum())
        loss = regularizer - T.sum(T.log(T.nnet.sigmoid(y_ui - y_uj)))
        # SGD step
        self.sgd_step = theano.function([u, i, j, lr], [],
                                        updates=[(self.U, self.U - lr * T.grad(loss, self.U)),
                                                 (self.V, self.V - lr * T.grad(loss, self.V))])

    def build_model(self, maxIter=100, num_thread=4, batch_size=32):
        # Training process
        print("Training MF-BPR with: learning_rate=%.2f, regularization=%.4f, factors=%d, #epoch=%d, batch_size=%d."
              % (self.learning_rate, self.reg, self.factors, maxIter, batch_size))
        w = open(self.writePath, 'w')
        for iteration in xrange(maxIter):
            # Each training epoch
            t1 = time.time()
            for s in xrange(self.num_rating / batch_size):
                # sample a batch of users, positive samples and negative samples 
                (users, items_pos, items_neg) = self.get_batch(batch_size)
                # perform a batched SGD step
                self.sgd_step(users, items_pos, items_neg, self.learning_rate)

            # check performance
            t2 = time.time()
            self.U_np = self.U.eval()
            self.V_np = self.V.eval()
            topK = self.topK
            (hits, mrrs) = evaluate_model(self, self.test, topK)
            self.w1.write("#####" + '\n')
            print("Iter=%d [%.1f s] HitRatio@%d = %.3f, MRR@%d = %.3f [%.1f s]"
                  % (iteration, t2 - t1, topK, np.array(hits).mean(), topK, np.array(mrrs).mean(), time.time() - t2))
            w.write(str(iteration) + "\t" + str(np.array(hits).mean()) + "\t" + str(np.array(mrrs).mean()) + '\n')
        w.close()

    def predict(self, u, i):
        return np.inner(self.U_np[u], self.V_np[i])  #
        # return T.dot(self.U[u], self.V[i])

    def get_batch(self, batch_size):
        users, pos_items, neg_items = [], [], []
        for i in xrange(batch_size):
            # sample a user
            u = np.random.randint(0, self.num_user)
            pos = []
            neg = []
            for l in range(0, len(self.train[u])):
                if self.train[u][l][1] == 0:
                    neg.append(self.train[u][l][0])
                else:
                    pos.append(self.train[u][l][0])
            if len(pos) != 0:
                i = pos[np.random.randint(0, len(pos))]
            else:
                i = np.random.randint(0, self.num_item)  # find pos_items from pos
                while i in neg:
                    i = np.random.randint(0, self.num_item)
            j = np.random.randint(0, self.num_item)  # find neg_items from neg
            while j in pos:
                j = np.random.randint(0, self.num_item)

            users.append(u)
            pos_items.append(i)
            neg_items.append(j)
        return (users, pos_items, neg_items)
