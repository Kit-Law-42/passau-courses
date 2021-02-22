# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def hasPathSum(self, root: TreeNode, targetSum: int) -> bool:
        if not root:
            return False
        return self.dfs(root, targetSum, 0)
    
    def dfs(self, root, targetSum, s):
        if root.left is None and root.right is None:
            return targetSum ==s+ root.val
        
        left = right = False
        if (root.left is not None):
            left = self.dfs(root.left, targetSum, s+root.val)
        if root.right is not None:
            right = self.dfs(root.right, targetSum, s+root.val)
        
        return (left or right)

    # alternative solution, use deduction instead of addition.
        