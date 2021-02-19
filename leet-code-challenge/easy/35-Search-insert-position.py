# Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order.

 

# Example 1:

# Input: nums = [1,3,5,6], target = 5
# Output: 2
# Example 2:

# Input: nums = [1,3,5,6], target = 2
# Output: 1

from typing import List


class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        idx =0
        for idx, i in enumerate(nums):
            if nums[idx]>= target:
                return idx
        
        return idx+1