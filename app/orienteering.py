import networkx as nx
import numpy as np
import pymongo 
import math
import itertools
import re
import random

# Monkey patching (fold)

def pairwise(l):
    return zip(l[:-1], l[1:])

def k(key):
    lambda each: each[key]

def tweetify(str):
    return re.match(re.compile('(.{,140})\s'),str).group(1)

# (end)

class Walk(object):
    def __init__(self,graph):
        self.path = []
        self.data = []
        self.G = graph
    def __lshift__(self,node):
        if len(self.path) > 0: 
            self.data[-1]['transition'] += self.G[self.path[-1]][node]['time']
        if not node in self.path:
            self.data.append({
                'name':node,
                'time':self.G.node[node]['time'],
                'transition':0
            })
        self.path.append(node)
    def time(self):
        if len(self.path) == 0: return 0.0
        time = 0
        time += sum([each['time'] for each in self.data])
        time += sum([each['transition'] for each in self.data])
        time -= self.data[-1]['transition'] # but last
        return time
    def example():
        w = Walk(read_graph())
        w << 'Waterfront Station'
        w << 'Steam Clock'
        w << 'Vancouver Art Gallery'
        w << 'Steam Clock'
        w << 'Waterfront Station'
        print w.path
        print w.data
        print w.time()

def read_graph():
    db = pymongo.MongoClient()['4h']
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
    
def random_walk(G,a,time):
    walk = [a]
    while True:
        neighbors = G.neighbors(a)
        if a in neighbors: neighbors.remove(a)
        if len(neighbors) == 0: break 
        b = random.sample(neighbors,1)[0]
        time_0 = time
        time -= G.node[a]['time']
        time -= G.edge[a][b]['time']
        if abs(time) > abs(time_0): break
        walk.append(b)
        a = b
    return walk

def prize(G,path):
    d = {}
    for each in path: 
        d[each] = G.node[each]['time']
    return sum(d.values())

def budget(G,path):
    x = 0
    for each in set(path):
        x += G.node[each]['time']
    for a,b in pairwise(path):
        x += G.edge[a][b]['time']
    return x
    
def best_random_walk(G,time):
    best,hiscore = None,None
    for n in range(0,20):
        a = random.sample(G.nodes(),1)[0]
        walk = random_walk(read_graph(),a,time)
        duration = budget(G,walk)
        score = prize(G,walk) - abs(time - duration)**2
        if not best or score > hiscore:
            best,hiscore = walk,score
    return best
    
print best_random_walk(read_graph(),4*60*60)
    
def itinerary():
    G = read_graph()
    path = best_random_walk(G,4*60*60)
    path.append(None)
    sights = {}
    db = pymongo.MongoClient()['4h']
    for each in db.sights.find({'name':{'$in':path}}):
        sights[each['name']] = each

    data = []
    t = lambda t: int(math.ceil(t/60/5)) * 5

    for a,b in pairwise(path):
        s = sights[a]
        data.append({
            'name':a,
            'time':t(G.node[a]['time']),
            'latitude':s['latitude'],
            'longitude':s['longitude'],
            'description':tweetify(s['description']),
            'url':s['url']
        })
        if b: data.append({'time':t(G[a][b]['time'])})

    return data
