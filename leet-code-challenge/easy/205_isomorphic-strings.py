# Given two strings s and t, determine if they are isomorphic.

# Two strings s and t are isomorphic if the characters in s can be replaced to get t.

# All occurrences of a character must be replaced with another character while preserving the order of characters. No two characters may map to the same character, but a character may map to itself.

 

# Example 1:

# Input: s = "egg", t = "add"
# Output: true
# Example 2:

# Input: s = "foo", t = "bar"
# Output: false
# Example 3:

# Input: s = "paper", t = "title"
# Output: true


class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        dicts = {}

        if (len(s) != len(t)):
            return False
        elif (len(s) ==1):
            return True
        else:
            for idx,x in enumerate(s):
                if s[idx] not in dicts.keys(): # s letter not in dictionary yet
                    if t[idx] not in dicts.values():
                        dicts[s[idx]] = t[idx]
                    else:
                        return False
                else: # s letter already in dictionary
                    if (dicts[s[idx]] != t[idx]):
                        return False
            return True

a = Solution()
ans = a.isIsomorphic("paper", "title") #prints 'Foo'
print(ans)