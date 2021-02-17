# You are given a string s and two integers x and y. You can perform two types of operations any number of times.

# Remove substring "ab" and gain x points.
# For example, when removing "ab" from "cabxbae" it becomes "cxbae".
# Remove substring "ba" and gain y points.
# For example, when removing "ba" from "cabxbae" it becomes "cabxe".
# Return the maximum points you can gain after applying the above operations on s.

 

# Example 1:

# Input: s = "cdbcbbaaabab", x = 4, y = 5
# Output: 19
# Explanation:
# - Remove the "ba" underlined in "cdbcbbaaabab". Now, s = "cdbcbbaaab" and 5 points are added to the score.
# - Remove the "ab" underlined in "cdbcbbaaab". Now, s = "cdbcbbaa" and 4 points are added to the score.
# - Remove the "ba" underlined in "cdbcbbaa". Now, s = "cdbcba" and 5 points are added to the score.
# - Remove the "ba" underlined in "cdbcba". Now, s = "cdbc" and 5 points are added to the score.
# Total score = 5 + 4 + 5 + 5 = 19.
# Example 2:

# Input: s = "aabbaaxybbaabb", x = 5, y = 4
# Output: 20

from collections import Counter
class Solution:
    def maximumGain(self, s: str, x: int, y: int) -> int:
        # assume that 'ab'' has highe score than 'ba'
        # if not, switch them.
        a = 'a'
        b = 'b'
        if x < y:
            x, y = y, x
            a, b = b, a
        
        seen = Counter()
        ans = 0
        for c in s + 'x':
            if c in 'ab':
                if c == b and 0 < seen[a]: # if c is b and we found an a before.
                    ans += x
                    seen[a] -= 1
                else:
                    seen[c] += 1  # count(a) +1
            else:
                ans += y * min(seen[a], seen[b]) # this string is not reducible anymore, count number of ba left in counter()
                seen = Counter()

        return ans