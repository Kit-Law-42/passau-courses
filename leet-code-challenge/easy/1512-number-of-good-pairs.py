from typing import List
import math

class Solution:
    def numIdenticalPairs(self, nums: List[int]) -> int:
        a = {}
        total = 0
        for i in nums:
            if i in a:
                a[i] +=1
            else:
                a[i] = 1
        
        for k, i in a.items():
            if i>1:
                total += math.factorial(i)// math.factorial(i-2) //2
        return total