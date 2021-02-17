# 306. Additive Number

# Additive number is a string whose digits can form additive sequence.

# A valid additive sequence should contain at least three numbers. Except for the first two numbers, each subsequent number in the sequence must be the sum of the preceding two.

# Given a string containing only digits '0'-'9', write a function to determine if it's an additive number.

# Note: Numbers in the additive sequence cannot have leading zeros, so sequence 1, 2, 03 or 1, 02, 3 is invalid.

### Take a look at question 842: split array into fibonacci array

# Example 1:

# Input: "112358"
# Output: true
# Explanation: The digits can form an additive sequence: 1, 1, 2, 3, 5, 8. 
#              1 + 1 = 2, 1 + 2 = 3, 2 + 3 = 5, 3 + 5 = 8
# Example 2:

# Input: "199100199"
# Output: true
# Explanation: The additive sequence is: 1, 99, 100, 199. 
#              1 + 99 = 100, 99 + 100 = 199

class Solution:
    def isAdditiveNumber(self, num: str) -> bool:
        lnum = len(num)
        if (lnum <3):
            return False
        for i in range(1,lnum//2+1): # try every combination of the first 2 number.
            for j in range(i+1,lnum):
                a, b = num[:i], num[i:j]
                if b != str(int(b)) or a!= str(int(a)):
                    continue
                while (j < lnum): # loop through the remaining query
                    c = str(int(a) + int(b))
                    if not num[j:].startswith(str(c)):
                        break
                    lc = len(c)
                    j += lc
                    a,b = b,c
                if j == lnum:
                    return True # pass through while loop
        # no successful case in while loop
        return False


a = Solution()
print(a.isAdditiveNumber("199100199"))
print(a.isAdditiveNumber("112358"))
print(a.isAdditiveNumber("111"))
print(a.isAdditiveNumber("123"))