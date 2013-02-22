"""
Magic happens here.

Given the graph of all tourist paths, start at a major public transit hub, eg
Waterfront Stations, look for the nearest top 10 sights, walk there, take one
random step, and repeat. 

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

BEST_OF_TWENTY = 20

def mongo_db():
    return pymongo.MongoClient()['insight']

def read_graph():
    
    # Read graph from database and fill in networkx graph
    
    db = mongo_db()
    g = db.graph.find_one()
    G = nx.Graph()
    
    # Each node is a sight, time at sight is 75% percentile of time between
    # first and last photo taken by others at that sight.
    
    for each,values in g['nodes'].items():
        if len(values) == 0:
            G.add_node(each,time=1)
        else:    
            G.add_node(each,time=np.percentile(values,75))
    
    # Turn directed into undirected graph, merging time data. 
    
    for a,more in g['edges'].items():
        for b,values in more.items():
            G.add_edge(a,b)
            e,k = G[a][b],'time'
            if not e.has_key(k): e[k] = []  
            e[k] += values
            
    # Time between sights is median of last photo taken by others at previous 
    # sight and first at next sight.        
                
    for a,b in G.edges():
        values = G[a][b]['time']
        if len(values) > 1:
            G[a][b]['time'] = np.percentile(G[a][b]['time'],50) 
        else:
            G.remove_edge(a,b)          
    return G


def duration(G,path):
    
    # walking time between sights in a path
    
    time = 0
    prev = None
    for each in path:
        time += G.node[each]['time']
        if prev: G.edge[prev][each]['time']
        prev = each
    return time
    

def find_path_to_nearest_sight(G,n,top_ten):
    
    # Given node n find path to nearest top 10 sight, or none
    
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
    """
    An itinerary. Keeps track of path, total time and json payload.
    """
    def __init__(self,G):
        self.g = G
        self.path = []
        self.prev = None
        self.time = 0
        self.accrued_time = 0
        self.json = []
    def __lshift__(self,node):
        
        # Accrue walking time between sights
        
        if self.prev: 
            self.accrued_time = 0.8 * self.accrued_time + self.g.edge[self.prev][node]['time']
            
        # Append sight, skipping duplicates
            
        if not node in self.path: 
            time = self.g.node[node]['time']
            
            # Construct json payload
            
            if self.prev:
                self.json.append({
                    'time':self.accrued_time
                })
            self.json.append({
                'name':node,
                'time':time})
                
            # Actually append node
            
            self.path.append(node)
            
            # Add time at sights as well as accrued time between sights
            
            self.time += time + self.accrued_time
            self.accrued_time = 0
            
        self.prev = node
    def time_at_sights(self):
        
        # Cost function for time at sight
        
        values = [each['time'] for each in self.json if 'name' in each]
        return sum(values)
    def time_between_sights(self):
        
        # Cost function for time between sights (square beyond 25 minutes)
        
        values = [each['time'] for each in self.json if not 'name' in each]
        return sum([x**1.2 for x in values if x > 25])
        


def append_random_step(G,w,top_ten):

    # Sample a random neighbor but the current node

    more = G.neighbors(w.prev)
    if w.prev in more: more.remove(w.prev)
    if len(more) == 0: return 
    n = random.sample(more,1)[0]
    
    # Append to itinerary
    
    w << n
    
    # Remove from top 10 sights
    
    if each in top_ten: top_ten.remove(each) 


def find_route(G,top_ten,duration):

    # Start at a major public transit hub
    
    w = Walk(G)
    w << 'Waterfront Station'
    
    # 10.times { ... }
    
    for _ in range(10):
        
        # Walk to nearest top 10 sight
        
        path = find_path_to_nearest_sight(G,w.prev,top_ten)
        if not path: return w
        path.pop(0) # remove first element
        for each in path:
            w << each
            if each in top_ten: top_ten.remove(each) 
            if w.time > duration: return w
            
        # Append two random steps to itinerary
        
        for _ in range(2):
            append_random_step(G,w,top_ten)
            if w.time > duration: return w
            
    # Once we're out of nearest sights, keep walking randomly ...
            
    for _ in range(10):
        append_random_step(G,w,top_ten)
        if w.time > duration: return w
        
    return w


def fitness(walk,duration):
    
    # Fitness function for generated itineraries
    
    return 0.25 * walk.time_at_sights() - walk.time_between_sights()  


def find_best_route_of_many(G,top_ten,duration):
    
    # Find best of BEST_OF_TWENTY paths
    
    many = [find_route(G,list(top_ten),duration) for _ in range(BEST_OF_TWENTY)]
    best = max(many,key=lambda each: fitness(each,duration))
    return best


def serve_walk_to_website(walk,seed):
    
    # Wrap the itinerary in a rich set of jsonified data
    
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
    

