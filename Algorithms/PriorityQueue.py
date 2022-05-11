'''
!!!!!!!
\todo should implement heapq as well
!!!!!!!!!!
'''
class PriorityQueue(object): 
    def __init__(self): 
        self.queue = []
  
    # for checking if the queue is empty 
    def notEmpty(self): 
        return len(self.queue) != 0
  
    # for inserting an element in the queue 
    def insert(self, data): 
        if data not in self.queue:
            self.queue.append(data) 
            self.queue = merge_sort(self.queue)
  
    # for popping an element based on Priority 
    def pop_front(self): 
        return self.queue.pop(0)
    
    def keys(self):
        return [tup[0] for tup in self.queue]
    
    def pop_key(self,key):
        for i, tup in enumerate(self.queue):
            if tup[0] == key:
                ind, hei = self.queue.pop(i)
                return hei
            
def compare_heights(small, big):
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
    # The last array split
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    # Perform merge_sort recursively on both halves
    left, right = merge_sort(arr[:mid]), merge_sort(arr[mid:])

    # Merge each side together
    return merge(left, right, arr.copy())


def merge(left, right, merged):

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