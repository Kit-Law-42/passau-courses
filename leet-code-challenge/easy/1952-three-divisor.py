import math

class Solution:
    def isThree(self, n: int) -> bool:
        res =0
        for i in range(2,int(math.sqrt(n)+1)):
            if n%i ==0:
                res+=1 if i*i==n else 2
        return res==1

a = Solution()
print(a.isThree(n=4))
print(a.isThree(n=6))
print(a.isThree(n=12))
print(a.isThree(n=14))
print(a.isThree(n=9))
print(a.isThree(n=81))