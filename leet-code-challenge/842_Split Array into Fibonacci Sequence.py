# Given a string S of digits, such as S = "123456579", we can split it into a Fibonacci-like sequence [123, 456, 579].

# Formally, a Fibonacci-like sequence is a list F of non-negative integers such that:

# 0 <= F[i] <= 2^31 - 1, (that is, each integer fits a 32-bit signed integer type);
# F.length >= 3;
# and F[i] + F[i+1] = F[i+2] for all 0 <= i < F.length - 2.
# Also, note that when splitting the string into pieces, each piece must not have extra leading zeroes, except if the piece is the number 0 itself.

# Return any Fibonacci-like sequence split from S, or return [] if it cannot be done.

# Example 1:

# Input: "123456579"
# Output: [123,456,579]
# Example 2:

# Input: "11235813"
# Output: [1,1,2,3,5,8,13]
# Example 3:

# Input: "112358130"
# Output: []
# Explanation: The task is impossible.


###  TAKE A LOOK AT 306 TOO.
from typing import List, Set


class Solution:
    def splitIntoFibonacci(self, S: str) -> List[int]:
        ls = len(S)
        r = []
        if ls <3:
            return list(r)
        for i in range(1,ls//2+1): # try every combination of the first 2 number.
            for j in range(i+1,ls):
                #r.clear()
                a, b = S[:i], S[i:j]
                r = [a,b]
                if b != str(int(b)) or a!= str(int(a)):
                    continue
                if c > 2**31 -1: break
                while (j < ls): # loop through the remaining query
                    c = str(int(a) + int(b))
                    if not S[j:].startswith(str(c)):
                        break
                    if int(c) > 2**31 -1: break
                    lc = len(c)
                    j += lc
                    r.append(c)
                    a,b = b,c
                    if j == ls:
                        return r # pass through while loop
        # no successful case in while loop
        return []

a = Solution()
print(a.splitIntoFibonacci("199100199"))
print(a.splitIntoFibonacci("112358"))
print(a.splitIntoFibonacci("111"))
print(a.splitIntoFibonacci("123"))
print(a.splitIntoFibonacci("112358130"))