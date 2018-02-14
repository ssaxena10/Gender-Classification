"""
sumarize.py
"""
import pickle
import string


def main():
    total = 0
    with open('users.pkl', 'rb') as f:
        users = pickle.load(f)

    file = open('summary.txt', 'w')

    for u in users:
        total = total + len(u['followers'])

    file.write("Total Users: %d & Total Followers: %d" % (len(users), total))

    with open('output.pkl', 'rb') as f:
        output = pickle.load(f)

    file.write("\nTotal tweets collected: %d" % output['Tweets'])
    file.write("\nCommunities Discovered: %d" % output['community'])
    file.write("\nPer community average no. of users: %d" % output['avg'])
    file.write("\nMales & Females users found: Male users : %d & Female users : %d" % (output['mcount'], output['fcount']))
    file.write("\nExample of male & female user's tweet: ")
    Mtweet = output['male']
    Msn = Mtweet['user']['screen_name']
    Mname = Mtweet['user']['name']
    Mmsg = Mtweet['text']

    file.write('\n Male Example: \n\tscreen_name=%s & name=%s\n\ttext=%s' %(Msn,Mname,Mmsg))
    Ftweet = output['female']
    Fsn = Ftweet['user']['screen_name']
    Fname = Ftweet['user']['name']
    Fmsg = Ftweet['text']

    file.write('\n Female Example: \n\tscreen_name=%s & name=%s\n\ttext=%s' %(Fsn,Fname,Fmsg))


if __name__ == '__main__':
    main()
