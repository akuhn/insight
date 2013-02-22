"""
Given a user's facebook token finds the top 10 sights.

Uses latent semantic indexing to index all sights. And then queries the index
with the words found in recent Facebook likes to identify sights the user
might be most interested in.

Assumes that we find a good travel signal in a user's recent likes. Which is 
not always given, but I've found that people are amazing in rationalizing
random results, so we're good :)

"""
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

TOP = 10
TOPICS = 7


# Setup stopwords

stoplist = stopwords.words('english')
stoplist.append('point')
stoplist.append('university')
stoplist.append('place')


def append_word(words,w,count):

    # Appends word to list, but short words and stopwords

    if len(w) < 5: return
    if w in stoplist: return
    for n in range(count):
        words.append(w)


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
    lsi = models.LsiModel(tfidf[corpus], num_topics=TOPICS)
    index = similarities.SparseMatrixSimilarity(lsi[tfidf[corpus]],num_features=len(dictionary))
    return index,lsi,tfidf,dictionary,documents  


def bag2bow(dictionary,bag):
    
    # Apparently dictionary.doc2bow does not work with counter !?
    
    v = []
    for word,count in bag.iteritems():
        n = dictionary.token2id.get(word)
        if n: v.append((n,count))
    v.sort()
    return v


def top_ten_sights_for(token):
    
    # Hard-wired itinerary for demo.
    
    if token == 'me': return top_ten_sights_for_me()
    
    # Create index of sights
    
    index,lsi,tfidf,dictionary,documents = create_index() 
    
    # Connect words in facebook likes
    
    bag = fb.count_words_in_url_likes(token)
    
    # Get ranking of sights
    
    v = bag2bow(dictionary,bag)
    sims = index[lsi[tfidf[v]]]
    ranking = sorted(enumerate(sims), key=each[1], reverse=True)
    
    # Return name of top 10 sights
    
    top10 = map(each[0], itertools.islice(ranking,TOP))
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
    
