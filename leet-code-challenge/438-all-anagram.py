from collections import defaultdict
from typing import List
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        p_dict, s_dict, res, len_p, len_s = defaultdict(int), defaultdict(int), [], len(p), len(s)
        
        for i in p : p_dict[i] += 1
        for i in s[:len(p)-1] : s_dict[i] += 1
        
        for i in range(len(p)-1, len(s)) : 
            s_dict[s[i]] += 1
            if s_dict == p_dict : 
                res.append(i-len(p)+1)
            s_dict[s[i-len(p)+1]] -= 1
            if s_dict[s[i-len(p)+1]] == 0 : 
                del s_dict[s[i-len(p)+1]]
            
        return res