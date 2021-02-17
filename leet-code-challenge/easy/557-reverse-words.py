class Solution:
    def reverseWords(self, s: str) -> str:
        ss = s.split(" ")
        for idx, sToken in enumerate(ss):
            ss[idx] = sToken[::-1]
        
        return " ".join(ss)

a = Solution()
ans = a.reverseWords("Let's take LeetCode contest") #prints 'Foo'
print(ans)