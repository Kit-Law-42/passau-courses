class Solution:
    def findMaxLength(self, nums: List[int]) -> int:
        d = {0: -1}
        output = 0
        sea_level = 0
        for idx, n in enumerate(nums):
            if n ==0:
                sea_level -=1
            else:
                sea_level +=1
            
            if sea_level not in d:
                d[sea_level] = idx
            else:
                if idx - d[sea_level] > output:
                    output = idx - d[sea_level]
        return output