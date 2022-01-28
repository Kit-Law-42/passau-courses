# Given an array arr of positive integers sorted in a strictly increasing order, and an integer k.

# Find the kth positive integer that is missing from this array.

 

# Example 1:

# Input: arr = [2,3,4,7,11], k = 5
# Output: 9
# Explanation: The missing positive integers are [1,5,6,8,9,10,12,13,...]. The 5th missing positive integer is 9.
# Example 2:

# Input: arr = [1,2,3,4], k = 2
# Output: 6
# Explanation: The missing positive integers are [5,6,7,...]. The 2nd missing positive integer is 6.

from typing import List
# Solution 1:
class Solution:
    def findKthPositive(self, arr: List[int], k: int) -> int:
        i =1
        while True:
            if i not in arr:
                k-=1
            if (k==0):
                return i
            i+=1

# Solution 2
class Solution:
    def findKthPositive(self, arr: List[int], k: int) -> int:
        i =1
        idx_arr =0
        while idx_arr < len(arr):
            if i==arr[idx_arr]:
                idx_arr+=1
            else:
                k-=1
            if k==0:
                return i
            i+=1
        return arr[idx_arr-1] +k

solution = Solution()
print(solution.findKthPositive([1,2,3,4], 2))
print(solution.findKthPositive([2,3,4,7,11], 5))