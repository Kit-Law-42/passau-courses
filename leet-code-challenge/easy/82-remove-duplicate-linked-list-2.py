# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def deleteDuplicates(self, head: ListNode) -> ListNode:
        root = ListNode(-1)
        root.next = head
        
        pre = root
        while head and head.next:
            if head.val == head.next.val:
                while (head and head.next and head.val == head.next.val):
                    head = head.next
                head = head.next
                pre.next = head
            else:
                head = head.next
                pre = pre.next
        
        return root.next