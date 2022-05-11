import heapq

class CancellationQueue(object):
    def __init__(self): 
        self.queue = []
        heapq.heapify(self.queue)
  
    # for checking if the queue is empty 
    def notEmpty(self): 
        return len(self.queue) != 0
  
    # for inserting an element in the queue 
    def insert(self, data): 
        heapq.heappush(self.queue, data)
  
    # for popping an element based on Priority 
    def pop_front(self): 
        return heapq.heappop(self.queue)
    
    # for checking the 'second' item (actually is first, cause we popped first one)
    def check_distance(self):
        if self.queue:
            return self.queue[0][0]
        else:
            return float('inf')
    
    # get length of queue
    def length(self):
        return len(self.queue)
    