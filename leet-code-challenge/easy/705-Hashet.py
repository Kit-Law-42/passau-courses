class MyHashSet(object):
    
    def __init__(self):
        """
        Initialize your data structure here.
        """
        self.capacity = 8
        self.size = 0
        self.s = [None]*8
        self.lf = float(2)/3
        
    def myhash(self, key): # can be modified to hash other hashable objects like built in python hash function
        return key%self.capacity # divisible hash.
        

    def add(self, key):
        """
        :type key: int
        :rtype: void
        """
        if float(self.size)/self.capacity >= self.lf:
            self.capacity <<= 1
            ns = [None]*self.capacity
            for i in range(self.capacity >> 1):
                if self.s[i] and self.s[i] != "==TOMBSTONE==":
                    n = self.myhash(self.s[i])
                    while ns[n] is not None: #find an empty space to put it.
                        n = (5*n+1)%self.capacity
                    ns[n] = self.s[i]
            self.s = ns
        h = self.myhash(key)
        while self.s[h] is not None:
            if self.s[h] == key: #existing key.
                return
            h = (5*h + 1) % self.capacity
            if self.s[h] == "==TOMBSTONE==": # if an index appear later than tomestone, it will be a bug.
                break
        self.s[h] = key
        self.size += 1
        
        

    def remove(self, key):
        """
        :type key: int
        :rtype: void
        """
        h = self.myhash(key)
        while self.s[h]:
            if self.s[h] == key:
                self.s[h] = "==TOMBSTONE=="
                self.size -= 1
                return
            h = (5*h+1)%self.capacity
        

    def contains(self, key):
        """
        Returns true if this set contains the specified element
        :type key: int
        :rtype: bool
        """
        h = self.myhash(key)
        while self.s[h] is not None:
            if self.s[h] == key:
                return True
            h = (5*h + 1)%self.capacity
        return False