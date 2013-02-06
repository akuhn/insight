import networkx as nx
import numpy as np
import pymongo 
import math
import re

# Monkey patching (fold)

def pairwise(l):
    return zip(l[:-1], l[1:])

def k(key):
    lambda each: each[key]

def tweetify(str):
    return re.match(re.compile('(.{,140})\s'),str).group(1)

# (end)

def itinerary():
    db = pymongo.MongoClient()['4h']
    g = db.graph.find_one()

    G = nx.Graph()
    for a,values in g['sights'].items():
        G.add_node(a,time=np.percentile(values,75))
    for a,more in g['transitions'].items():
        for b,values in more.items():
            G.add_edge(a,b)
            e,k = G[a][b],'time'
            if not e.has_key(k): e[k] = []  
            e[k] += values
        
    path = nx.shortest_path(G,'Vanier Park','Capilano Suspension Bridge')
    path.append(None)
    sights = {}
    for each in db.sights.find({'name':{'$in':path}}):
        sights[each['name']] = each

    data = []
    t75 = lambda values: int(math.ceil(np.percentile(values,75)/60/5)) * 5
    t50 = lambda values: int(math.ceil(np.median(values)/60/5)) * 5

    for a,b in pairwise(path):
        s = sights[a]
        data.append({
            'name':a,
            'time':t75(G.node[a]['time']),
            'latitude':s['latitude'],
            'longitude':s['longitude'],
            'description':tweetify(s['description']),
            'url':s['url']
        })
        if b: data.append({'time':t50(G[a][b]['time'])})

    return data
