from typing import List


class Solution:
    def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
        d = {} # set up a dictionary
        for idx, i in enumerate(nums):
            if i in d and i - d[i] <= k:
                return True
            d[i] = idx
        
        return False