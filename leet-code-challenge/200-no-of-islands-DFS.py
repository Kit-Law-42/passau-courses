from typing import List


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        
#         FFFFF
#         FFFFF
#         FFFFF
#         FFFFF
        
        
#         11110   => TTTTF
#         11010      TTFTF
#         11000      TTFFF 
#         00100   => FFFFF
#         cnt +=1
#         11110   => TTTTF
#         11010      TTFTF
#         11000      TTFTF 
#         00100   => FFTFF
#         cnt+=1
        
#         => 2
        
        
        m = len(grid)
        n = len(grid[0])
        g1 = [[False for i in range(n)] for j in range(m)] 
        
        cnt =0
        for i in range(m):
            for j in range(n):
                if (grid[i][j] == "1" and g1[i][j] == False):
                    # start opening adjacent cell
                    self.openAdjacent(grid, i, j)
                    cnt +=1
        return cnt
    
    def openAdjacent(self, grid, i, j):
        if i<0 or j<0 or i>=len(grid) or j>=len(grid[0]) or grid[i][j] != '1':
            return 
        grid[i][j] = True
        #left
        self.openAdjacent(grid, i-1, j)
        #top
        self.openAdjacent(grid, i+1, j)
        #right
        self.openAdjacent(grid, i, j+1)
        self.openAdjacent(grid, i, j-1)
        
        return 
        