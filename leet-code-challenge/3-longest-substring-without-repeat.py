# Given a string s, find the length of the longest substring without repeating characters.

 

# Example 1:

# Input: s = "abcabcbb"
# Output: 3
# Explanation: The answer is "abc", with the length of 3.
# Example 2:

# Input: s = "bbbbb"
# Output: 1
# Explanation: The answer is "b", with the length of 1.
# Example 3:

# Input: s = "pwwkew"
# Output: 3
# Explanation: The answer is "wke", with the length of 3.
# Notice that the answer must be a substring, "pwke" is a subsequence and not a substring.

class Solution:
    
    def lengthOfLongestSubstring(self, string):
        """
        Method: Sliding window
        Time:  O(n)
        Space: O(k)
        [k = length of the longest substring w/o repeating characters]
        """
        longest = 0
        left, right = 0, 0
        chars = set()
        while left < len(string) and right < len(string):
            print("left: "+ str(left))
            print("right: "+ str(right))
            if string[right] not in chars:
                chars.add(string[right])
                right += 1
                longest = max(longest, right - left)
            else:
                chars.remove(string[left])
                left += 1
        return longest

        '''
        used = {}
        max_length = start = 0
        for i, c in enumerate(s):
            if c in used and start <= used[c]: # if c is used and in current substr.
                start = used[c] + 1 #  left flag +=1
            else:
                max_length = max(max_length, i - start + 1) # e.g. abcabcbb => abc = 2-0+1 = length(3)
                
            used[c] = i 
            # i = right flag, right flag +=1
        
        return max_length
        '''

a = Solution()
print(a.lengthOfLongestSubstring("abcabcbb"))