import networkx as nx
import numpy as np
import pymongo 
import math

pairwise = lambda l: zip(l[:-1], l[1:])   

# begin script

db = pymongo.MongoClient()['4h']
data = db.graph.find_one()

sights = db.sights.find({'name':{'$in':['Vanier Park','Vancouver Aquarium']}})

print sights.count()

XXX

G = nx.Graph()

for a,values in data['sights'].items():
    G.add_node(a,time=np.percentile(values,75))

for a,more in data['transitions'].items():
    for b,values in more.items():
        G.add_edge(a,b,time=np.median(values))
        
path = nx.all_simple_paths(G,'Vanier Park','Vancouver Aquarium').next()

data = []
t = lambda t: int(math.ceil(t/60/5)) * 5
for a,b in pairwise(path):
    data.append({'name':a,'time':t(G.node[a]['time'])})
    data.append({'time':t(G[a][b]['time'])})
    
print data

