"""
Generates random walks => old algorithm, not used anymore!!!

"""
import networkx as nx
import numpy as np
from time import time as unix_epoch
import pymongo 
import math
import itertools
import re
import random
#
from my_util import *

def mongo_db():
    return pymongo.MongoClient()['insight']

def read_graph():
    db = mongo_db()
    g = db.graph.find_one()
    G = nx.Graph()
    for each,values in g['nodes'].items():
        if len(values) == 0:
            G.add_node(each,time=1)
        else:    
            G.add_node(each,time=np.percentile(values,75))
    for a,more in g['edges'].items():
        for b,values in more.items():
            G.add_edge(a,b)
            e,k = G[a][b],'time'
            if not e.has_key(k): e[k] = []  
            e[k] += values    
    for a,b in G.edges():
        values = G[a][b]['time']
        if len(values) > 1:
            G[a][b]['time'] = np.percentile(G[a][b]['time'],50) 
        else:
            G.remove_edge(a,b)          
    return G


class Walk(object):
    def __init__(self):
        self.path = []
        self.dedup = None
        self.data = None
    def __lshift__(self,node):
        self.path.append(node)
    def deduplicate(self):
        last = self.path[-1]
        self.dedup = []
        for each in self.path:
            if each == last or each in self.dedup:
                self.dedup.append(None)
            else:    
                self.dedup.append(each)
        self.dedup[0] = self.path[0]
        self.dedup[-1] = self.path[-1]
    def fetch_time_data(self,G):
        self.data = []
        prev = None
        for each,uniq in zip(self.path,self.dedup):
            if prev:
                self.data[-1]['time'] += G.edge[prev][each]['time']
            if uniq: 
                self.data.append({
                    'name':each,
                    'time':G.node[each]['time']
                })
                self.data.append({
                    'time':0
                })
            prev = each
        self.data.pop()
    def time(self):
        return sum([each['time'] for each in self.data])
    def time_at_sights(self):
        return sum([each['time'] for each in self.data if 'name' in each])
    def time_between_sights(self):
        return sum([each['time'] for each in self.data if not 'name' in each])
    def mine(self):
        w = self
        w << 'Waterfront Station'
        w << 'Steam Clock'
        w << 'Maple Tree Square'
        w << 'Dr Sun Yat-Sen Classical Chinese Garden & Park'
        w << 'Maple Tree Square'
        w << 'Steam Clock'
        w << 'Vancouver Art Gallery'
        w << 'HR MacMillan Space Centre'
        w << 'Granville Island Public Market'
        w.deduplicate()
        G = read_graph()
        w.fetch_time_data(read_graph())
        return w
    def example(self):
        w = self
        w << 'Waterfront Station'
        w << 'Steam Clock'
        w << 'Vancouver Art Gallery'
        w << 'Steam Clock'
        w << 'Waterfront Station'
        print w.path
        w.deduplicate()
        print w.path
        w.fetch_time_data(read_graph())
        print w.data
        print w.time()
        print w.time_at_sights()
        print w.time_between_sights()
  
def random_walk(G,a,time):
    walk = Walk()
    walk << a
    while True:
        neighbors = G.neighbors(a)
        if a in neighbors: neighbors.remove(a)
        if len(neighbors) == 0: break 
        b = random.sample(neighbors,1)[0]
        time_0 = time
        time -= G.node[a]['time']
        time -= G.edge[a][b]['time']
        if abs(time) > abs(time_0): break
        walk << b
        a = b
    return walk

def best_random_walk(G,time):
    best,hiscore = None,None
    for n in range(0,50):
        # a = random.sample(G.nodes(),1)[0]
        a = 'Waterfront Station'
        walk = random_walk(read_graph(),a,time)
        walk.deduplicate()
        walk.fetch_time_data(G)
        duration = walk.time()
        score = walk.time_at_sights() - walk.time_between_sights() - abs(time - duration)**2
        if not best or score > hiscore:
            best,hiscore = walk,score
    return best
    
def serve_walk_to_website(walk,seed):
    sights = {}
    db = mongo_db()
    for each in db.sights.find({'name':{'$in':walk.path}}):
        sights[each['name']] = each
    t = lambda t: int(math.ceil(t/60/5)) * 5
    n = 0
    for each in walk.data:
        each['time'] = t(each['time'])
        if 'name' in each:
            s = sights[each['name']]
            photos = db['flickr'].find({'geotag':{'$near':[s['longitude'],s['latitude']]}})
            each.update({
                'latitude':s['latitude'],
                'longitude':s['longitude'],
                'description':tweetify(s['description']),
                'url':s['url'],
                'photo_url': '', # random.sample(list(photos),1)[0]['url_s'],
                'cssid':'sight'+str(n),
                'marker':'http://maps.google.com/mapfiles/marker{}.png'.format(chr(ord('A')+n))
            })
            n += 1
    walk.data[0]['marker'] = 'http://maps.google.com/mapfiles/marker_yellowA.png'
    walk.data[-1]['marker'] = 'http://maps.google.com/mapfiles/marker_yellowZ.png'
    return {
        'seed':seed,
        'walk':walk.data,
        'time':walk.time() / 3600.0
    }    
    
def itinerary(time,me=False):
    if me: return serve_walk_to_website(Walk().mine(),-1)
    seed = int(unix_epoch())
    random.seed(seed)
    G = read_graph()
    walk = best_random_walk(G,time)
    return serve_walk_to_website(walk,seed)

if __name__ == "__main__":
    print Walk().mine().data