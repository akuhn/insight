import pymongo
import json
#
from my_util import each

config = json.load(open('token-facebook.json'))
db = pymongo.MongoClient()[config['database']]

if __name__ == "__main__":
    print "Database:"
    print "\t{} = {}".format(db.name,", ".join(sorted(db.collection_names())))
    print "Config:"
    for key,value in sorted(config.items(),key=each[0]):
        print "\t{} = {}".format(key,value)