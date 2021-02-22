# Definition for a binary tree node.
from typing import List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def sortedArrayToBST(self, nums: List[int]) -> TreeNode:
        if len(nums)==0:
            return None
        if len(nums)==1:
            return TreeNode(nums[0])
        l = len(nums)//2
        leftTree = self.sortedArrayToBST(nums[:l])
        rightTree = self.sortedArrayToBST(nums[l+1:])
        
        return TreeNode(nums[l], leftTree, rightTree)