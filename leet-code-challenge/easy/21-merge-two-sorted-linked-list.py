# Merge two sorted linked lists and return it as a sorted list. The list should be made by splicing together the nodes of the first two lists.

 

# Example 1:


# Input: l1 = [1,2,4], l2 = [1,3,4]
# Output: [1,1,2,3,4,4]
# Example 2:

# Input: l1 = [], l2 = []
# Output: []
# Example 3:

# Input: l1 = [], l2 = [0]
# Output: [0]

# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def mergeTwoLists(self, l1: ListNode, l2: ListNode) -> ListNode:
        r =n =  ListNode(0)
        while (l1 and l2):
            if l1.val < l2.val:
                n.next = l1
                l1 = l1.next
                n = n.next
            else:
                n.next = l2
                l2 = l2.next
                n = n.next
                
        n.next = l1 or l2
        
        return r.next
                
            
        