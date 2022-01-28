# 1st solution: Recursion

class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        
        
        def tile(x, y):
            if (x==m-1 and y==n-1):
                return 0
            if (x==m-1):
                return tile(x, y+1)
            if (y==n-1):
                return tile(x+1, y)
            return 1+tile(x+1, y)+tile(x, y+1)
        
        return 1+tile(0,0)
        
        
        #2nd solution
        class Solution:
    
    def uniquePaths(self, m: int, n: int) -> int:
        arr = [[0]*n for _ in range(m)]
        arr[0]=[1]*n
        for i in range(1,m):
            arr[i][0]=1
            for j in range(1,n):
                arr[i][j]=(arr[i-1][j]+arr[i][j-1])
        return int(arr[m-1][n-1])
