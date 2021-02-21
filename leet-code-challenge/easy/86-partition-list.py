# Given the head of a linked list and a value x, partition it such that all nodes less than x come before nodes greater than or equal to x.

# You should preserve the original relative order of the nodes in each of the two partitions.

 

# Example 1:


# Input: head = [1,4,3,2,5,2], x = 3
# Output: [1,2,2,4,3,5]

# Core idea: split it into 2 linked list and concat them

# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def partition(self, head: ListNode, x: int) -> ListNode:
        def partition(self, head, x):
            h1 = l1 = ListNode(0)
            h2 = l2 = ListNode(0)
            while head:
                if head.val < x:
                    l1.next = head
                    l1 = l1.next
                else:
                    l2.next = head
                    l2 = l2.next
                head = head.next
            l2.next = None
            l1.next = h2.next
            return h1.next