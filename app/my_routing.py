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


def duration(G,path):
    time = 0
    prev = None
    for each in path:
        time += G.node[each]['time']
        if prev: G.edge[prev][each]['time']
        prev = each
    return time
    

def find_path_to_nearest_sight(G,n,top_ten):
    paths = []
    for each in top_ten:
        try:
            if not each in G: continue
            paths.append(nx.shortest_path(G,n,each))
        except nx.NetworkXNoPath:
            pass  
    if len(paths) == 0: return None
    return min(paths,key=lambda path: duration(G,path))
    
    
class Walk2(object):
    def __init__(self,G):
        self.g = G
        self.path = []
        self.prev = None
        self.time = 0
        self.accrued_time = 0
    def __lshift__(self,node):
        if self.prev: 
            self.accrued_time += self.g.edge[self.prev][node]['time']
        if not node in self.path: # deduplicate on the fly!
            self.time += self.g.node[node]['time']
            self.time += self.accrued_time
            self.accrued_time = 0
            self.path.append(node)
        self.prev = node


def append_random_step(G,w):
    more = G.neighbors(w.prev)
    if w.prev in more: more.remove(w.prev)
    if len(more) == 0: return 
    n = random.sample(more,1)[0]
    w << n


def find_route(G,top_ten,duration):
    w = Walk2(G)
    w << 'Waterfront Station'
    for _ in range(10):
        path = find_path_to_nearest_sight(G,w.prev,top_ten)
        if not path: return w
        path.pop(0) # remove first element
        for each in path:
            w << each
            if each in top_ten: top_ten.remove(each) 
            if w.time > duration: return w
        # Then append a random step
        append_random_step(G,w)
        if w.time > duration: return w
    for _ in range(10):
        append_random_step(G,w)
        if w.time > duration: return w
    return w
  
  
if __name__ == "__main__":
    G = read_graph()
    top_ten = ['David Lam Park',
     'HR MacMillan Space Centre',
     'Science World',
     'Beaty Biodiversity Museum',
     'Science World & Alcan Omnimax Theatre',
     'Lynn Canyon Park',
     'Ecology Centre',
     'Vanier Park',
     'University Town',
     'Vancouver Museum']
    w = find_route(G,top_ten,6*HOURS)
    print w.path
    print w.prev
    print w.time/HOURS
    

