# Given an array nums containing n distinct numbers in the range [0, n], return the only number in the range that is missing from the array.

# Follow up: Could you implement a solution using only O(1) extra space complexity and O(n) runtime complexity?

 

# Example 1:

# Input: nums = [3,0,1]
# Output: 2
# Explanation: n = 3 since there are 3 numbers, so all numbers are in the range [0,3]. 2 is the missing number in the range since it does not appear in nums.

# Constraints:

# n == nums.length
# 1 <= n <= 10^4
# 0 <= nums[i] <= n
# All the numbers of nums are unique.

from typing import List


class Solution:
    def missingNumber(self, nums: List[int]) -> int:
        s = (len(nums)+1)*len(nums)/2
        return int(s - sum(nums))