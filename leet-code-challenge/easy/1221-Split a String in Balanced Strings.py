# Balanced strings are those that have an equal quantity of 'L' and 'R' characters.

# Given a balanced string s, split it in the maximum amount of balanced strings.

# Return the maximum amount of split balanced strings.

 

# Example 1:

# Input: s = "RLRRLLRLRL"
# Output: 4
# Explanation: s can be split into "RL", "RRLL", "RL", "RL", each substring contains same number of 'L' and 'R'.
# Example 2:

# Input: s = "RLLLLRRRLR"
# Output: 3
# Explanation: s can be split into "RL", "LLLRRR", "LR", each substring contains same number of 'L' and 'R'.

class Solution:
    def balancedStringSplit(self, s: str) -> int:
        b = 0
        r =0
        for i in s:
            if i=="R":
                b +=1
            elif i=="L":
                b -=1
            
            if b==0:
                r +=1
        
        return r