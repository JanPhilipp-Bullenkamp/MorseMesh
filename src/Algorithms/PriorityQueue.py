##
# @file PriorityQueue.py
#
# @brief Contains a PriorityQueue class.

'''
!!!!!!!
\todo should implement heapq as well
!!!!!!!!!!
'''
class PriorityQueue(object):
    """! @brief Priority Queue class used for a queue sorted after function values.
    
    @details The elements in this queue should consist of a key - value pair (key stored under index 0 
    and value under index 1). The priority will be sorted after the values stored under index 1.
      
    """
    ## @var queue 
    # The priority queue stored as an array.
    
    def __init__(self): 
        """! @brief The Constructor of a Priority Queue"""
        self.queue = []
  
    # for checking if the queue is empty 
    def notEmpty(self): 
        """! @brief Checks whether the priority queue is empty
        @return Returns a boolean: True if the queue is not empty, Flase otherwise.
        """
        return len(self.queue) != 0
  
    # for inserting an element in the queue 
    def insert(self, data): 
        """! @brief Inserts one element at the right place in the queue.
        @param data The element to be added to the queue. The priority after which it should be ranked has to be stored under index 1.
        """
        if data not in self.queue:
            self.queue.append(data) 
            self.queue = merge_sort(self.queue)
  
    # for popping an element based on Priority 
    def pop_front(self): 
        """! @brief Removes and returns the highest priority element from the queue.
        @return The highest priority element.
        """
        return self.queue.pop(0)
    
    def keys(self):
        """! @brief Returns a list of the keys of the queue elements, e.g. the 0 indices.
        @return A list of the keys of the elemets in the queue.
        """
        return [tup[0] for tup in self.queue]
    
    def pop_key(self,key):
        """! @brief Removes an element from the queue.
        @param key The key of the element to be removed from the queue.
        
        @return The function value of the key that is popped.
        """
        for i, tup in enumerate(self.queue):
            if tup[0] == key:
                ind, hei = self.queue.pop(i)
                return hei
            
def compare_heights(small, big):
    """! @brief Compares two tuples of sorted values.
    
    @details Compares two sorted tuples of possibly different length and returns True if the second
    one is considered larger and False if the first one is considered larger. Tuples are higher
    if their highest (first) value is larger than the highest value of the other tuple and shorter
    tuples are higher than longer if all values are equal up to the length of the shorter tuple.
    For example the following tuples are sorted from high to low:
    
    (4), (4,3), (3,2,2), (3,2,1), (2), (2,9), (2,7), (2,9,15)
    
    @param small First tuple to be compared.
    @param big Second tuple to be compared.
    
    @return True if small is smaller than big according to the metric. False otherwise.
    """
    # return True if small is smaller than big, False otherwise
    if len(small) == len(big):
        for i in range(len(small)):
            if small[i] < big[i]:
                return True
            elif small[i] > big[i]:
                return False
        return False
    if len(small) < len(big):
        for i in range(len(small)):
            if small[i] < big[i]:
                return True
            elif small[i] > big[i]:
                return False
        return False
    if len(small) > len(big):
        for i in range(len(big)):
            if small[i] < big[i]:
                return True
            elif small[i] > big[i]:
                return False
        return True


def merge_sort(arr):
    """! @brief Sorts a given array recursively using merge sort.
    
    @param arr The array to be sorted
    
    @return The sorted array.
    """
    # The last array split
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    # Perform merge_sort recursively on both halves
    left, right = merge_sort(arr[:mid]), merge_sort(arr[mid:])

    # Merge each side together
    return merge(left, right, arr.copy())


def merge(left, right, merged):
    """! @brief Merges two arrays together sorted after their priority.
    
    @param left The left array to be merged.
    @param right The right array to be merged.
    @merged The original array that needs to be sorted.
    
    @return The merge sorted array.
    """
    left_cursor, right_cursor = 0, 0
    while left_cursor < len(left) and right_cursor < len(right):
      
        # Sort each one and place into the result
        if compare_heights(left[left_cursor][1], right[right_cursor][1]):
            merged[left_cursor+right_cursor]=left[left_cursor]
            left_cursor += 1
        else:
            merged[left_cursor + right_cursor] = right[right_cursor]
            right_cursor += 1
            
    for left_cursor in range(left_cursor, len(left)):
        merged[left_cursor + right_cursor] = left[left_cursor]
        
    for right_cursor in range(right_cursor, len(right)):
        merged[left_cursor + right_cursor] = right[right_cursor]

    return merged