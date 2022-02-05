class Solution:
    def checkString(self, s: str) -> bool:
        for i in range(len(s)-1):
            if s[i:i+2]=="ba":
                return False
        return True