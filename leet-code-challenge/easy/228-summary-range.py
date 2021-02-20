# You are given a sorted unique integer array nums.

# Return the smallest sorted list of ranges that cover all the numbers in the array exactly. That is, each element of nums is covered by exactly one of the ranges, and there is no integer x such that x is in one of the ranges but not in nums.

# Each range [a,b] in the list should be output as:

# "a->b" if a != b
# "a" if a == b
 

# Example 1:

# Input: nums = [0,1,2,4,5,7]
# Output: ["0->2","4->5","7"]
# Explanation: The ranges are:
# [0,2] --> "0->2"
# [4,5] --> "4->5"
# [7,7] --> "7"

class Solution:
    def summaryRanges(self, nums: List[int]) -> List[str]:
        if len(nums) <=1:
            return map(str,nums)
        r = []
        s, e = nums[0], nums[0]
        for i in range(1, len(nums)):
            if (nums[i] - nums[i-1] > 1):
                r.append(self.printRange(s,e))
                s = e = nums[i]
            else:
                e = nums[i]
        r.append(self.printRange(s,e))
        return r
    
    def printRange(self, s, e):
        if (s != e):
            return str(s) + "->" + str(e)
        else:
            return str(s)