from gensim import corpora, models, similarities, utils
from nltk.corpus import stopwords
import sys
import collections
import itertools
import pymongo
import json
import re as regex
#
from my_config import db,config
from my_util import *
import my_facebook as fb


"""
Given a facebook token, find the top 10 sights.

"""

# Setup stopwords

stoplist = stopwords.words('english')
stoplist.append('point')
stoplist.append('university')
stoplist.append('place')


def append_word(words,w,count):
    if len(w) < 5: return
    if w in stoplist: return
    for n in range(count):
        words.append(w)


class Identity(object):
    def __getitem__(self,key):
        return key


def create_sight_corpus():

    # Load sight descriptions

    documents = list(db['sights'].find({
        'category':'sights',
        'subcategory':{'$not':{'$in':['stadium','hostel']}}},
        fields={'description':1,'subcategory':1,'name':1,'_id':0}))

    # Split documents into words
    
    re = regex.compile(r'[a-z]\w+')
    texts = []
    for doc in documents:
        words = []
        for w in regex.findall(re,doc['description'].lower()): 
            append_word(words,w,1)
        for w in regex.findall(re,doc['subcategory'].lower()): # boost categories 2x
            append_word(words,w,2)
        for w in regex.findall(re,doc['name'].lower()): # boost names 10x
            append_word(words,w,10)
        texts.append(words)

    # Map words to (arbitrary) numbers

    dictionary = corpora.Dictionary(texts)

    # Create LSI index

    corpus = [dictionary.doc2bow(doc) for doc in texts]
    
    return corpus,dictionary,documents


def create_index():
    corpus,dictionary,documents = create_sight_corpus()    
    tfidf = models.TfidfModel(corpus)
    # tfidf = Identity()
    lsi = models.LsiModel(tfidf[corpus], num_topics=25)
    index = similarities.SparseMatrixSimilarity(lsi[tfidf[corpus]],num_features=len(dictionary))
    return index,lsi,tfidf,dictionary,documents  


def bag2bow(dictionary,bag):
    # apparently dictionary.doc2bow does not work with Counter() !?
    v = []
    for word,count in bag.iteritems():
        n = dictionary.token2id.get(word)
        if n: v.append((n,count))
    v.sort()
    return v


def top_ten_sights_for(token):
    if token == 'me': return top_ten_sights_for_me()
    index,lsi,tfidf,dictionary,documents = create_index() 
    name = fb.me(token)['name']
    bag = fb.count_words_in_url_likes(token)
    # print bag
    v = bag2bow(dictionary,bag)
    sims = index[lsi[tfidf[v]]]
    ranking = sorted(enumerate(sims), key=each[1], reverse=True)
    # print ranking
    top10 = map(each[0], itertools.islice(ranking,10))
    return [documents[rank]['name'] for rank in top10]

def top_ten_sights_for_me():
    return ['David Lam Park',
     'HR MacMillan Space Centre',
     'Science World',
     'Beaty Biodiversity Museum',
     'Science World & Alcan Omnimax Theatre',
     'Lynn Canyon Park',
     'Ecology Centre',
     'Vanier Park',
     'University Town',
     'Vancouver Museum']


if __name__ == "__main__":
    tokens = json.load(open('token-facebook-users.json'))
    token = tokens['thereza']
    top_ten = top_ten_sights_for(token)
    print top_ten
    import my_routing
    G = my_routing.read_graph()
    w = my_routing.find_route(G,top_ten,6*HOURS)
    print w.path
    print w.prev
    print w.time/HOURS
    
