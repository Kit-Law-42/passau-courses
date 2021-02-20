# Given an array of strings words, return the words that can be typed using letters of the alphabet on only one row of American keyboard like the image below.

# In the American keyboard:

# the first row consists of the characters "qwertyuiop",
# the second row consists of the characters "asdfghjkl", and
# the third row consists of the characters "zxcvbnm".

 

# Example 1:

# Input: words = ["Hello","Alaska","Dad","Peace"]
# Output: ["Alaska","Dad"]

from typing import List


class Solution:
    def findWords(self, words: List[str]) -> List[str]:
        kb = {0: set("qwertyuiop"), 1: set("asdfghjkl"), 2: set("zxcvbnm")}
        r = []
        for w in words:
            if set(w.lower()) <= kb[0] or set(w.lower()) <= kb[1] or set(w.lower()) <= kb[2]:
                r.append(w)
        return r