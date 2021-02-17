# Given a pattern and a string s, find if s follows the same pattern.

# Here follow means a full match, such that there is a bijection between a letter in pattern and a non-empty word in s.

 

# Example 1:

# Input: pattern = "abba", s = "dog cat cat dog"
# Output: true
# Example 2:

# Input: pattern = "abba", s = "dog cat cat fish"
# Output: false
# Example 3:

# Input: pattern = "aaaa", s = "dog cat cat dog"
# Output: false
# Example 4:

# Input: pattern = "abba", s = "dog dog dog dog"
# Output: false

class Solution:
    def wordPattern(self, pattern: str, s: str) -> bool:
        wd = {}
        sL = s.split(" ")
        if len(sL) != len(pattern):
            return False
        elif (len(pattern) ==1):
            return True
        else:
            for idx, i in enumerate(pattern):
                if i not in wd.keys(): # if pattern letter not in key list
                    if sL[idx] not in wd.values(): # check if string[i] already in values list
                        wd[i] = sL[idx]
                    else:
                        return False
                else: # if pattern letter already in key list
                    if wd[i] != sL[idx]:
                        return False
            
            return True


a = Solution()
ans = a.wordPattern("aaaa", "dog cat cat dog") #prints 'Foo'
print(ans)