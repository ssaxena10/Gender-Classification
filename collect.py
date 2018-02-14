"""
collect.py
"""

import networkx as nx
import matplotlib.pyplot as plt
from TwitterAPI import TwitterAPI
from collections import Counter
import pickle
import time
import sys
import requests

consumer_key = 'yLpYwmrVpKffycVKLk6aeGqwC'
consumer_secret = 'p1aruuoo1oFnGe0z9Dxc7veISdeHlZO94dJ3taTU2LWzy03FvH'
access_token = '318398468-IiEkpZoAvZh8ROHsRTY71tCI8Rkv3wKiNSuvxhDj'
access_token_secret = 'yevGQC1KnhSll0bt0tIoQykhPfY6GC4VmtHlHf9TVRnzo'


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


def read_screen_names(filename):

    with open(filename) as f:
        data = f.readlines()

    data = [x.strip() for x in data]
    return data

    pass


def get_users(twitter, screen_names):

    request = robust_request(twitter, "users/lookup", {"screen_name": screen_names})

    return request


def count_friends(users):

    c = Counter()
    for u in users:
        for f in u['followers']:
            c[f] += 1
    return c

    pass


def get_friends(twitter, screen_name):

    follower = robust_request(twitter, "followers/ids", {"screen_name": screen_name, "Count": 5000})
    fjson = follower.json()
    flist = fjson['ids']
    return sorted(flist, key=int)

    pass


def get_name(tweet):

    if 'user' in tweet and 'name' in tweet['user']:
        Split = tweet['user']['name'].split()
        if len(Split) > 0:
            return Split[0].lower()


def fetch_tweets(twitter, mname, fname, userid, tweets):

    x = -1
    request = robust_request(twitter, 'statuses/user_timeline', {'user_id': userid, "count": 10})
    if request != None:
        for r in request:
            if 'user' in r:
                n = get_name(r)
                if n in mname:
                    tweets.append(r)
                    print("Collecting Tweets : %d " % len(tweets))
                    x = 0
                if n in fname:
                    tweets.append(r)
                    print("Collecting Tweets : %d " % len(tweets))
                    x = 1

    return tweets, x


def add_all_friends(twitter, users):

    uDict = {}
    for u in users:
        uDict['screen_name'] = u['screen_name']
        uFriend = get_friends(twitter, uDict['screen_name'])
        u['followers'] = uFriend

    pass


def print_num_friends(users):

    flist = []
    for user in users:
        ptup = user['screen_name'], len(user['followers'])
        flist.append(ptup)
    sorted(flist, key=lambda x: x[0])
    for t in flist:
        print("User: ",t[0],"Followers: ", t[1])

    pass


def create_graph(users, friend_counts):

    graph = nx.Graph()
    for u in users:
        graph.add_node(u['screen_name'])
        for f in u['followers'][:300]:
            graph.add_node(f)
            graph.add_edge(u['screen_name'], f)
    nx.write_gpickle(graph, "graph.gpickle")
    return graph

    pass

def draw_network(graph, users, filename):

    plt.figure(figsize=(12, 12))
    get_lablel = {n: '' if isinstance(n, int) else n for n in graph.nodes()}
    nx.draw_networkx(graph, labels=get_lablel, alpha=.4, width=.1,
                     node_size=75)
    plt.axis("off")
    plt.savefig(filename)

    pass

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


def main():

    mname, fname = get_census_names()
    tweet_limit = 1500
    tweets = []
    flist = []
    twitter = get_twitter()
    output ={}
    screen_names = read_screen_names('celebrity.txt')
    print('Established Twitter connection.')
    users = sorted(get_users(twitter, screen_names), key=lambda x: x['screen_name'])
    print('found %d users with screen_names %s' %
          (len(users), str([u['screen_name'] for u in users])))
    print('Followers fetched are limited to 5000 each')
    add_all_friends(twitter, users)
    print_num_friends(users)
    friend_counts = count_friends(users)
    pickle.dump(users, open('users.pkl', 'wb'))
    graph = create_graph(users, friend_counts)
    draw_network(graph, users, 'network.png')
    print("Graph Created & saved in network.png ")
    for u in users:
        for f in u['followers'][:250]:
            if f not in flist:
                flist.append(f)
    output['mcount'] = 0
    output['fcount'] = 0
    for f in flist:
        tweets, x = fetch_tweets(twitter, mname, fname, f, tweets)
        if x == 0:
            output['mcount'] += 1
        if x == 1:
            output['fcount'] += 1
        if (len(tweets) > tweet_limit):
            break
    print("fetched %d tweets " % len(tweets))
    output['Tweets'] = len(tweets)
    pickle.dump(tweets, open('tweets.pkl', 'wb'))
    pickle.dump(output, open('output.pkl', 'wb'))
    print("Collected Data")

if __name__ == '__main__':
    main()