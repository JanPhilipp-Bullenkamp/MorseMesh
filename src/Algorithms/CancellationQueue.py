##
# @file CancellationQueue.py
#
# @brief Contains a Cancellation queue class.
#
# @section libraries_cancellationQueue Libraries/Modules
# - heapq standard library

import heapq

class CancellationQueue(object):
    """! @brief Implements a Priority Queue used for Cancellations in Reduce Morse Complex."""
    ## @var queue
    # The priority queue storing the elements to be cancelled.
    def __init__(self): 
        """! The Constructor of the Cancellation Queue."""
        self.queue = []
        heapq.heapify(self.queue)
  
    # for checking if the queue is empty 
    def notEmpty(self): 
        """! @brief Checks if the queue is empty.
        @return Returns True if the queue contains at least one element, False, if it is empty."""
        return len(self.queue) != 0
  
    # for inserting an element in the queue 
    def insert(self, data): 
        """! @brief Inserts a new element to the cancellation queue (based on the priority).
        @deatils Need a tuple of 3, with the actual priority first and the id of the CritEdges to be cancelled, 
        because we need a tiebreaker if two elements have the same priority (than the id will always give decision, 
        as they should be unique and for two elements with equal priority, we do not care which one comes first.
        
        @param data The element to be inserted. Should be a tuple of priority, id of the edge (for tiebreakers) and 
        edge to be cancelled."""
        heapq.heappush(self.queue, data)
  
    # for popping an element based on Priority 
    def pop_front(self): 
        """! @brief Pops the first element with the highest priority from the queue.
        @return The highest priority element.
        """
        return heapq.heappop(self.queue)
    
    # for checking the 'second' item (actually is first, cause we popped first one)
    def check_distance(self):
        """! @brief Check the next priority in the queue.
        @details Needed cause we have to recompute the priority once we popped an element and than we need to make
        sure that the next element in the queue would still have a lower priority than the one we popped.
        
        @return The priority of the first element in the queue. If it is empty, the priority is set to inf.
        """
        if self.queue:
            return self.queue[0][0]
        else:
            return float('inf')
    
    # get length of queue
    def length(self):
        """! @brief Give the length of the queue.
        @return Returns the length of the queue.
        """
        return len(self.queue)
    