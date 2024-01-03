"""
    MorseMesh
    Copyright (C) 2023  Jan Philipp Bullenkamp

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

##
# @file PriorityQueue.py
#
# @brief Contains a PriorityQueue class
#
# @section libraries_PriorityQueue Libraries/Modules
# - heapq standard library

# imports
import heapq

class PriorityQueue(object):
    """! @brief Priority Queue class used for a queue sorted after function values.
    
    @details The elements in this queue should consist of a key - value pair 
    (value stored under index 0 and key under index 1), since the priority 
    will be sorted after position 0.
    """
    ## @var queue 
    # The priority queue stored as an array.
    
    def __init__(self): 
        """! @brief The Constructor of a Priority Queue"""
        self.queue = []
        heapq.heapify(self.queue)
  
    # for checking if the queue is empty 
    def notEmpty(self): 
        """! @brief Checks whether the priority queue is empty
        @return Returns a boolean: True if the queue is not empty, Flase otherwise.
        """
        return len(self.queue) != 0
  
    # for inserting an element in the queue 
    def insert(self, data): 
        """! @brief Inserts one element at the right place in the queue.
        @param data The element to be added to the queue. The priority after which 
               it should be ranked has to be stored at the first position (index 0).
        """
        heapq.heappush(self.queue, data)
  
    # for popping an element based on Priority 
    def pop_front(self): 
        """! @brief Removes and returns the highest priority element from the queue.
        @return The highest priority element.
        """
        return heapq.heappop(self.queue)
    
    def items(self):
        """! @brief Returns a list of the index, simplex pairs of the queue elements.
        @return A list of the index, simplex tuples of the elemets in the queue.
        """
        return self.queue
    
    def pop(self, data):
        """! @brief Removes an element from the heapq that is not at the highest 
        priority and heapifies it again.
        
        @param data The data to be removed.
        """
        i = self.queue.index(data)
        self.queue[i] = self.queue[-1]
        self.queue.pop()
        heapq.heapify(self.queue)
            