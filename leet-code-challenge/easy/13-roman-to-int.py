class Solution:
    def romanToInt(self, s: str) -> int:
        r = 0
        d = {"I": 1, "V": 5, "X": 10 , "L" : 50, "C" : 100, "D" : 500, "M": 1000}
        for i in range(len(s)-1, -1, -1):
            #print(s[i])
            if (s[i] in d.keys()):
                r += d[s[i]]
            if (s[i] in ["V", "X"]):
                d["I"] = -d["I"]
            if (s[i] in ["L", "C"]):
                d["X"] = -d["X"]
            if (s[i] in ["D", "M"]):
                d["C"] = -d["C"]
        
        return r
            