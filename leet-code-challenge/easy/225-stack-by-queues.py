from queue import Queue 

class MyStack:

    def __init__(self):
        """
        Initialize your data structure here.
        """
        # Two inbuilt queues  
        self.q1 = Queue() 
        self.q2 = Queue()  
              
        # To maintain current number  
        # of elements 
        self.curr_size = 0

    def push(self, x: int) -> None:
        """
        Push element x onto stack.
        """
        self.curr_size += 1
  
        # Push x first in empty q2  
        self.q2.put(x)  
  
        # Push all the remaining  
        # elements in q1 to q2.  
        while (not self.q1.empty()): 
            self.q2.put(self.q1.queue[0])  
            self.q1.get() 
  
        # swap the names of two queues  
        self.q = self.q1  
        self.q1 = self.q2  
        self.q2 = self.q 

    def pop(self) -> int:
        """
        Removes the element on top of the stack and returns that element.
        """
        if (self.q1.empty()):  
            return
        self.curr_size -= 1
        return self.q1.get()  

    def top(self) -> int:
        """
        Get the top element.
        """
        if (self.q1.empty()): 
            return -1
        return self.q1.queue[0] 

    def empty(self) -> bool:
        """
        Returns whether the stack is empty.
        """
        return self.curr_size ==0


# Your MyStack object will be instantiated and called as such:
# obj = MyStack()
# obj.push(x)
# param_2 = obj.pop()
# param_3 = obj.top()
# param_4 = obj.empty()