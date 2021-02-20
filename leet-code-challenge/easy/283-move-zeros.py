# Given an array nums, write a function to move all 0's to the end of it while maintaining the relative order of the non-zero elements.

# Example:

# Input: [0,1,0,3,12]
# Output: [1,3,12,0,0]

class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        # Method 1
        p1 = 0
        for i in nums:
            if i != 0:
                nums[p1] = i
                p1 +=1
        nums[p1:] = [0 for _ in range(p1, len(nums))]

        # Method 2, use swapping