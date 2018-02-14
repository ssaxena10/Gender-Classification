"""
classify.py
"""
import requests
import pickle
import sys
import numpy as np
from TwitterAPI import TwitterAPI
from scipy.sparse import lil_matrix
from collections import defaultdict
import time
from sklearn.cross_validation import KFold
from sklearn.linear_model import LogisticRegression
import re

consumer_key = '89heuTBNxlDJo7t3QUhJmNZ7l'
consumer_secret = '1FLVX51MnsLFIAT85NQIDQ2V42xlB8ezTbRboLbTJg4a3XkxKp'
access_token = '318398468-YXECUxzFjhGfbXMKr7Pcjf1Qbbrw6kfvetrZiVFG'
access_token_secret = 'jNmxxQaxurwYh1eVaGE0XddedfOLE8nHmlpTvUNaNpalm'



def get_twitter():

    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)


def robust_request(twitter, resource, params, max_tries=5):
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        elif request.status_code == 88:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)
        else:
            continue


def gender(tweet, mname, fname):
    n = get_name(tweet)
    if n in fname:
        return 1
    elif n in mname:
        return 0
    else:
        return -1


def get_census_names():

    male = requests.get('http://www2.census.gov/topics/genealogy/1990surnames/dist.male.first').text.split('\n')
    fmale = requests.get('http://www2.census.gov/topics/genealogy/1990surnames/dist.female.first').text.split('\n')
    mdict = dict([(m.split()[0].lower(), float(m.split()[1]))
                      for m in male if m])
    fdict = dict([(f.split()[0].lower(), float(f.split()[1]))
                        for f in fmale if f])
    mname = set([x for x in mdict if x not in fdict or
                      mdict[x] > fdict[x]])
    fname = set([y for y in fdict if y not in mdict or
                        fdict[y] > mdict[y]])


    return mname, fname


def get_name(tweet):

    if 'user' in tweet and 'name' in tweet['user']:
        Split = tweet['user']['name'].split()
        if len(Split) > 0:
            return Split[0].lower()

def tokenize(text, lowercase, punctuation, prefix,urls, mentions):

    if not text:
        return []
    if lowercase:
        text = text.lower()
    tokens = []
    if urls:
        text = re.sub('http\S+', '', text)
    if mentions:
        text = re.sub('@\S+', '', text)
    if punctuation:
        tokens = text.split()
    else:
        tokens = re.sub('\W+', ' ', text).split()
    if prefix:
        tokens = ['%s%s' % (prefix, t) for t in tokens]
    return tokens


def get_tokens(tweet, descr=True, lowercase=True,punctuation=True, prefix='d=',urls=True, mentions=True):

    tok = tokenize(tweet['text'], lowercase, punctuation, None,urls, mentions)
    if descr:
        tok.extend(tokenize(tweet['user']['description'], lowercase,punctuation, prefix,urls, mentions))

    return tok


def LR_model(X, y, nfolds):

    kf = KFold(len(y), nfolds)

    for train, test in kf:
        cl = LogisticRegression()
        cl.fit(X[train], y[train])

    return cl


def feature_matrix(tweets, tlist, vocab):

    mat = lil_matrix((len(tweets), len(vocab)))
    for i, tokens in enumerate(tlist):
        for t in tokens:
            j = vocab[t]
            mat[i, j] += 1
    return mat.tocsr()


def make_vocab(tlist):

    vocab = defaultdict(lambda: len(vocab))
    for tok in tlist:
        for t in tok:
            vocab[t]

    return vocab


def main():

    mname, fname = get_census_names()
    tlist = []

    with open('output.pkl', 'rb') as f:
        output = pickle.load(f)

    with open('tweets.pkl', 'rb') as tw:
        tweets = pickle.load(tw)

    gArray = np.array([gender(t, mname, fname) for t in tweets])

    output['tottweets'] = len(tweets)
    for t in tweets:
        tlist = [get_tokens(t, descr=True, lowercase=True,punctuation=True, prefix='d=',urls=True, mentions=True)]

    vocab = make_vocab(tlist)
    fMat = feature_matrix(tweets, tlist, vocab)

    clf = LR_model(fMat, gArray, 2)
    m = 1
    f = 1
    itrr = np.nditer(gArray, flags=['f_index'])

    while not itrr.finished:
        prd = clf.predict(fMat[itrr.index])
        if (m == 0 and f == 0):
            break
        if itrr[0] == 0 and prd == itrr[0] and m:
            test = tweets[itrr.index]
            output['male'] = test
            m = 0
        if itrr[0] == 1 and prd == itrr[0] and f:
            test = tweets[itrr.index]
            output['female'] = test
            f = 0
        itrr.iternext()

    pickle.dump(output, open('output.pkl', 'wb'))
    #print(clf.score(fMat,gArray))


if __name__ == '__main__':
    main()
