import pymongo
import json
#
from util import each

db = pymongo.MongoClient().insight
config = json.load(open('token-facebook.json'))

if __name__ == "__main__":
    print "Database:"
    print "\t{} = {}".format(db.name,", ".join(sorted(db.collection_names())))
    print "Config:"
    for key,value in sorted(config.items(),key=each[0]):
        print "\t{} = {}".format(key,value)