# Given a linked list, swap every two adjacent nodes and return its head.

 

# Example 1:


# Input: head = [1,2,3,4]
# Output: [2,1,4,3]
# Example 2:

# Input: head = []
# Output: []

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def swapPairs(self, head: ListNode) -> ListNode:
        root = ListNode(-1)
        root.next = head
        
        r = root
        while r.next and r.next.next:
            n = r.next
            nn= r.next.next
            n.next = nn.next
            nn.next = n
            r.next = nn
            r = r.next.next
            print(r.val)
            
        return root.next