"""
GHL's original threading source:
https://gist.github.com/ghl3/4556336
"""
import threading
from Queue import Queue


class Worker(threading.Thread):
    """
    """
    def __init__(self, queue, callback):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.results = []
        self.callback = callback
        self.queue = queue
        
    def run(self):
        while True:
            if self.queue.empty(): 
                return
            url = self.queue.get()
            value = self.callback(url)
            self.results.append(value)


def pmap(callback, urls, nThreads=8):
    """
    """
    q = Queue()
    for url in urls:
        q.put(url)
        
    # start threads to consume the queue
    threads = [] 
    for i in xrange(nThreads):
        thread = Worker(q,callback)
        thread.start()
        threads.append(thread)
        
    # collect results from threads
    for thread in threads:
        thread.join()
        
    # gather and return all results
    results = []
    for thread in threads:
        results += thread.results
    return results
    
if __name__ == "__main__":
    print pmap(lambda x: x*x,range(10))
