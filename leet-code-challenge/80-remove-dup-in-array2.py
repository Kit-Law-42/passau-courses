class Solution:
    def removeDuplicates(self, nums):
        if len(nums) < 2:
            return len(nums)
        slow, fast = 2, 2

        while fast < len(nums):
            if nums[slow - 2] != nums[fast]:
                nums[slow] = nums[fast]
                slow += 1
            fast += 1
        return slow

# solution 2, simpler.
class Solution:
    def removeDuplicates(self, nums):
        i = 0
        for n in nums:
            if (i < 2 or n > nums[i - 2]):
                nums[i] = n
                i+=1
        return i