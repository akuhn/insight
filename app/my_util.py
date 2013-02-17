import re


class Each(object):
    def __getitem__(self,key):
        return lambda each: each[key]
each = Each()


def pairwise(many):
    return zip(many[:-1], many[1:])


def tweetify(str):
    return re.match(re.compile('(.{,140})\s'),str).group(1)
    
    
if __name__ == "__main__":
    print map(each[0],'the quick brown fox jumps overt the lazy dog'.split())
