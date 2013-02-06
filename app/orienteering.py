import networkx as nx
import numpy as np
import pymongo 
import math
import itertools
import re

# Monkey patching (fold)

def pairwise(l):
    return zip(l[:-1], l[1:])

def k(key):
    lambda each: each[key]

def tweetify(str):
    return re.match(re.compile('(.{,140})\s'),str).group(1)

def shuffle(iter):
    t = list(iter)
    np.random.shuffle(t)
    return t
    
# (end)

def read_graph():
    db = pymongo.MongoClient()['4h']
    g = db.graph.find_one()
    G = nx.Graph()
    for each,values in g['sights'].items():
        G.add_node(each,time=np.percentile(values,75))
    for a,more in g['transitions'].items():
        for b,values in more.items():
            G.add_edge(a,b)
            e,k = G[a][b],'time'
            if not e.has_key(k): e[k] = []  
            e[k] += values    
    for a,b in G.edges():
        G[a][b]['time'] = np.median(G[a][b]['time'])       
    return G
    
def random_walk(G,a,time):
    walk = [a]
    t_a = [G.node[a]['time']]
    t_ab = []
    while time > sum(t_a) + sum(t_ab):
        neighbors = G.neighbors(a)
        if a in neighbors: neighbors.remove(a)
        if len(neighbors) == 0: break 
        b = shuffle(neighbors)[0]
        t_a.append(G.node[a]['time'])
        t_ab.append(G.edge[a][b]['time'])
        walk.append(b)
        a = b
    return walk,t_a,t_ab

def best_random_walk(G,time):
    best,hiscore = None,None
    for n in range(0,20):
        a = shuffle(G.nodes())[0]
        walk,t_a,t_ab = random_walk(read_graph(),a,time)
        total = sum(t_a) + sum(t_ab)
        score = sum(t_a) - sum(t_ab) - abs(time - total)
        if not best or hiscore > score:
            best,hiscore = walk,score
    return best
    
# print best_random_walk(read_graph(),4*60*60)

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
