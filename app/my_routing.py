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
    
    
class Walk(object):
    def __init__(self,G):
        self.g = G
        self.path = []
        self.prev = None
        self.time = 0
        self.accrued_time = 0
        self.json = []
    def __lshift__(self,node):
        if self.prev: 
            self.accrued_time = 0.5 * self.accrued_time + self.g.edge[self.prev][node]['time']
        if not node in self.path: # deduplicate on the fly!
            time = self.g.node[node]['time']
            if self.prev:
                self.json.append({
                    'time':self.accrued_time
                })
            self.json.append({
                'name':node,
                'time':time})
            self.path.append(node)
            self.time += time + self.accrued_time
            self.accrued_time = 0
        self.prev = node
    def time_at_sights(self):
        values = [each['time'] for each in self.json if 'name' in each]
        return sum(values)
    def time_between_sights(self):
        values = [each['time'] for each in self.json if not 'name' in each]
        return sum([x**1.2 for x in values if x > 25])
        


def append_random_step(G,w,top_ten):
    more = G.neighbors(w.prev)
    if w.prev in more: more.remove(w.prev)
    if len(more) == 0: return 
    n = random.sample(more,1)[0]
    w << n
    if each in top_ten: top_ten.remove(each) 


def find_route(G,top_ten,duration):
    w = Walk(G)
    w << 'Waterfront Station'
    for _ in range(10):
        path = find_path_to_nearest_sight(G,w.prev,top_ten)
        if not path: return w
        path.pop(0) # remove first element
        for each in path:
            w << each
            if each in top_ten: top_ten.remove(each) 
            if w.time > duration: return w
        # Then append some random steps
        for _ in range(2):
            append_random_step(G,w,top_ten)
            if w.time > duration: return w
    for _ in range(10):
        append_random_step(G,w,top_ten)
        if w.time > duration: return w
    return w


def fitness(walk,duration):
    return 0.25 * walk.time_at_sights() - walk.time_between_sights()  


def find_best_route_of_many(G,top_ten,duration):
    many = [find_route(G,list(top_ten),duration) for _ in range(20)]
    best = max(many,key=lambda each: fitness(each,duration))
    return best


def serve_walk_to_website(walk,seed):
    sights = {}
    db = mongo_db()
    for each in db.sights.find({'name':{'$in':walk.path}}):
        sights[each['name']] = each
    t = lambda t: int(math.ceil(t/60/5)) * 5
    n = 0
    for each in walk.json:
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
    walk.json[0]['marker'] = 'http://maps.google.com/mapfiles/marker_yellowA.png'
    walk.json[-1]['marker'] = 'http://maps.google.com/mapfiles/marker_yellowZ.png'
    return {
        'seed':seed,
        'path':walk.path,
        'walk':walk.json,
        'time':walk.time/HOURS
    }    


def itinerary(token,seed):
    from my_ranking import top_ten_sights_for
    top_ten = top_ten_sights_for(token)
    G = read_graph()
    w = find_best_route_of_many(G,top_ten,6*HOURS)
    return serve_walk_to_website(w,seed)
      
  
if __name__ == "__main__":
    w = itinerary('me',0)
    print w['path']
    print w['time']
    

