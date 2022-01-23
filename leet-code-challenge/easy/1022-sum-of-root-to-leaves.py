# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

from typing import Optional
class Solution:
    def sumRootToLeaf(self, root: Optional[TreeNode]) -> int:
        def preorder (r, currNum):
            nonlocal root_to_leaf
            if r:
                # bitwise can also applied to int values.
                currNum = (currNum <<1) | r.val
                print(currNum)

                # if there is no child nodes, add the curr_number to sum.
                if not (r.left or r.right):
                    root_to_leaf += currNum

                # one of the node may be none, need to stop @ next level.
                preorder(r.left, currNum)
                preorder(r.right, currNum)
        root_to_leaf =0
        preorder(root, 0)
        
        return root_to_leaf
        