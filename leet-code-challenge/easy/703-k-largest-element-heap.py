import heapq
from typing import List
class KthLargest:
    
    def __init__(self, k: int, nums: List[int]):
        self.k = k
        self.heap = nums
        heapq.heapify(self.heap)
        
        while len(self.heap) >k :
            heapq.heappop(self.heap)
            
        print(self.heap)

    def add(self, val: int) -> int:
        heapq.heappush(self.heap, val)
        
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
            
        return self.heap[0]

# Your KthLargest object will be instantiated and called as such:
kthLargest =  KthLargest(3, [4, 5, 8, 2])
kthLargest.add(3);   # return 4
kthLargest.add(5);   # return 5
kthLargest.add(10);  # return 5
kthLargest.add(9);   # return 8
kthLargest.add(4);   # return 8