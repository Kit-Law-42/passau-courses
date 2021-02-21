# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def removeElements(self, head: ListNode, val: int) -> ListNode:
        o1 = l = ListNode(0, head)
        
        
        while l.next:
            if l.next.val == val:
                l.next = l.next.next
            else:
                l = l.next
        return o1.next