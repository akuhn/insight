import re


HOURS = 60*60 # Missing Ruby's 6.hours :)


def pairwise(many):
    return zip(many[:-1], many[1:])


def tweetify(str):
    return re.match(re.compile('(.{,140})\s'),str).group(1)
    

class __Each(object):
    def __getitem__(self,key):
        return lambda each: each[key]
each = __Each()

    
if __name__ == "__main__":

    print map(each[0],'the quick brown fox jumps overt the lazy dog'.split())

    # => ['t', 'q', 'b', 'f', 'j', 'o', 't', 'l', 'd']
