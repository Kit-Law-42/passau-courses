# 88. Merge Sorted Array
# Share

# Given two sorted integer arrays nums1 and nums2, merge nums2 into nums1 as one sorted array.

# The number of elements initialized in nums1 and nums2 are m and n respectively. You may assume that nums1 has a size equal to m + n such that it has enough space to hold additional elements from nums2.

 

# Example 1:

# Input: nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3
# Output: [1,2,2,3,5,6]
# Example 2:

# Input: nums1 = [1], m = 1, nums2 = [], n = 0
# Output: [1]

from typing import List


class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """
        while m > 0 and n >0:
            if nums2[n-1] > nums1[m-1]:
                nums1[n+m-1] = nums2[n-1]
                n-=1
            else:
                nums1[n+m-1] = nums1[m-1]
                m-=1
        
        if n>0:
            nums1[:n] = nums2[:n]

a = Solution()
a.merge([1,2,3,0,0,0], 3, [2,5,6], 3)
a.merge([4,0,0,0,0,0],1,[1,2,3,5,6],5)