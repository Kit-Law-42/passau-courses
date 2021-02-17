class Solution:
    def smallestRangeI(self, A, K):
        return max(0,max(A)-min(A)-2*K)

a = Solution()
ans = a.smallestRangeI([1,2,99,100], 2) #prints 'Foo'
print(ans)