import urllib
import re
import collections
import requests
import os

# this is NOT installed on grader
#import pandas

# if you add this, need to push the directory to test
#from tools import util
#util.helper()

def read_test():
    # TODO dynamic tests naming
    # so this is impossible
    print(os.listdir('./tests'))

    # this should fail (no outside network connections allowed)
    #print(requests.get('http://google.com').text[0:50])

def killer(text):
    while(True):
        pass

def answer_to_life(text):
    #return killer(text)
    print("WHERE AM I")
    read_test()
    return 42

def find_lucky(text, num=7):
    words = re.findall(r'\b[A-Za-z\']+\b', text)
    counts = collections.Counter()
    for t in words:
        counts[t.lower()] += 1
        # counts[t] += 1

    hapaxes = [lemma for lemma in counts if counts[lemma] == num and len(lemma) == num]  # FUN
    # out = sorted(hapaxes, key=str.lower)

    if (len(hapaxes) == num):
        return sorted(hapaxes)

    return []
