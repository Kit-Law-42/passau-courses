from typing import List

class Solution:
    def findGCD(self, nums: List[int]) -> int:
        mn = nums[0]
        mx = nums[0]
        
        for i in range(1, len(nums)):
            if nums[i] < mn:
                mn = nums[i]
            elif nums[i] > mx:
                mx = nums[i]
        
        res = 1
        for j in range(2,mn+1):
            if mx%j ==0 and mn%j ==0:
                res = j
        
        return res
        