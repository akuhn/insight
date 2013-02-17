import urllib2
import re as regex
import facebook
import collections
import lxml.html as lxml
#
from my_util import each
from my_parallel import pmap
from my_config import *


def download(url):
    """
    Download url if html.
    """
    try:
        request = urllib2.Request(url)
        request.get_method = lambda: 'HEAD'
        mime = urllib2.urlopen(request).info().gettype() 
        if not mime == 'text/html': return None
        return urllib2.urlopen(url).read()
    except urllib2.HTTPError as error:
        print "HTML {}: {}".format(error.code,url)
        return None    

def extend_token(fb_token):
    fb = facebook.GraphAPI(fb_token)
    fb.extend_access_token(config['key'],config['secret'])
    me = fb.get_object('me')
    db.facebook.update(
        {'id':me['id']}, # query
        {'id':me['id'],'me':me,'token':fb.access_token}, #update
        upsert=True) 
    return fb.access_token


def count_words_in_url(url):
    """
    Counts words in an html document.
    """
    bag = collections.Counter()
    re = regex.compile(r'[a-z]\w+')
    for word in regex.findall(re,url.lower()): bag[str(word)] += 10
    html = download(url)  
    if not html: return bag
    doc = lxml.fromstring(html.decode('utf-8','ignore'))
    for text in doc.xpath('//text()'):
        if text.getparent().tag in ['script','style']: continue
        for word in regex.findall(re,text.lower()): bag[str(word)] += 1
    return bag

    
def count_words_in_urls(urls):
    bag = collections.Counter()
    for each in pmap(count_words_in_url,urls[0:50]):
        bag.update(each)
    return bag


def count_words_in_url_likes(fb_token):
    fb = facebook.GraphAPI(fb_token)
    urls = fb.fql('SELECT url FROM url_like WHERE user_id = me()')
    return count_words_in_urls(map(each['url'],urls))
 
 
if __name__ == "__main__":
    # print count_words_in_url('http://twitter.com/akuhn')
    print count_words_in_url_likes('AAAISAiG44iIBABMRolVWAgXHF2k3u3iilSJXvXHb3i0B9jyZBpZCZCi9fHcKAEEclNE8x3jE1Epl0HTvZB1UuC3ZBKw2OJokZD')
