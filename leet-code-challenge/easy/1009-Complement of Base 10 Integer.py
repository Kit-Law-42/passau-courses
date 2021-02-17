class Solution:
    def bitwiseComplement(self, N: int) -> int:
        B = bin(N)[2:]
        return int(''.join(map(lambda x: str(abs(int(x)-1)), B)), 2)

a = Solution()
b = a.bitwiseComplement(7)
print(b)