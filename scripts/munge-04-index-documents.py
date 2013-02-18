from gensim import corpora, models, similarities, utils
from nltk.corpus import stopwords
import collections
import itertools
import pymongo
import json
import re as regex
#
from app.my_config import db,config
from app.my_util import each


documents = list(db['sights'].find({
    'category':'sights',
    'subcategory':{'$not':{'$in':['stadium','hostel']}}},
    fields={'description':1,'subcategory':1,'name':1,'_id':0}))

# Split into words

stoplist = stopwords.words('english')
stoplist.append('point')
stoplist.append('university')
stoplist.append('place')

def append_word(words,w,count):
    if len(w) < 5: return
    if w in stoplist: return
    for n in range(count):
        words.append(w)

re = regex.compile(r'[a-z]\w+')
texts = []
for doc in documents:
    words = []
    for w in regex.findall(re,doc['description'].lower()): 
        append_word(words,w,1)
    for w in regex.findall(re,doc['subcategory'].lower()): 
        append_word(words,w,2)
    for w in regex.findall(re,doc['name'].lower()): 
        append_word(words,w,10)
    texts.append(words)

# Remove unique words

def _():
    words = bag()
    for t in texts: 
        for w in t: 
            words[w] += 1
    uniqs = [w for w,count in words.items() if count > 1]
    texts = [[w for w in each if not w in uniqs] for each in texts]

# Map words to (arbitrary) numbers

dictionary = corpora.Dictionary(texts)

# Create index

corpus = [dictionary.doc2bow(doc) for doc in texts]

class Identity(object):
    def __getitem__(self,key):
        return key

tfidf = models.TfidfModel(corpus)
# tfidf = Identity()
lsi = models.LsiModel(tfidf[corpus], num_topics=25)
index = similarities.SparseMatrixSimilarity(lsi[tfidf[corpus]],num_features=len(dictionary))

# query = "I love books, art and space travel. I wish to retire on mars!".split()
# v = dictionary.doc2bow(query)
# sims = index[tfidf[v]]
# 
# ranking = sorted(enumerate(sims), key=each[1], reverse=True)
# top10 = map(each[0], itertools.islice(ranking,10))
# for rank in top10: print documents[rank]['name']

import app.my_facebook as fb

tokens = json.load(open('token-facebook-users.json'))

token = tokens['diane']

print fb.me(token)['name']

import time
t = time.time()
bag = fb.count_words_in_url_likes(token)
print time.time() - t

# apparently dictionary.doc2vbow does not work with Counter()
print bag
v = []
for word,count in bag.iteritems():
    n = dictionary.token2id.get(word)
    if n: v.append((n,count))
v.sort()
sims = index[lsi[tfidf[v]]]

ranking = sorted(enumerate(sims), key=each[1], reverse=True)
top10 = map(each[0], itertools.islice(ranking,10))
for rank in top10: print documents[rank]['name']

