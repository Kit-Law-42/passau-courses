# Solution 1
class Solution:
    def sequentialDigits(self, low: int, high: int) -> List[int]:
        llow = len(str(low)) #4
        lhigh = len(str(high)) #5
        res = []
        for no_of_dig in range(llow, lhigh+1):
            # Generate all numbers with fixed-length no_of_dig
            for i in range(1,10-no_of_dig+1):
                digit = i
                pw = no_of_dig -1 
                seq_no = 0
                for j in range(pw+1):
                    seq_no += digit * 10**pw
                    pw -=1
                    digit+=1
                # print(seq_no)
                res.append(seq_no)
        
        filtered = filter(lambda x: x>=low and x<=high, res)
        return filtered
        
# Solution 2
class Solution:
    def sequentialDigits(self, low: int, high: int) -> List[int]:
        queue = collections.deque(list(range(1, 10)))
        
        res = []
        while queue:
            u = queue.popleft()
            if low <= u <= high:
                res.append(u)
            last_num = u % 10
            if last_num != 9:
                queue.append(u * 10 + last_num + 1)
        return res