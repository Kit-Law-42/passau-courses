class Solution:
    def findFinalValue(self, nums: List[int], original: int) -> int:
        d = {}
        for n in nums:
            if n not in d:
                d[n] = n
        
        while original in d:
            original *=2
            
        return original
        