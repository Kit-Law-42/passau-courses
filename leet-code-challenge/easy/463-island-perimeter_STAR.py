# You are given row x col grid representing a map where grid[i][j] = 1 represents land and grid[i][j] = 0 represents water.

# Grid cells are connected horizontally/vertically (not diagonally). The grid is completely surrounded by water, and there is exactly one island (i.e., one or more connected land cells).

# The island doesn't have "lakes", meaning the water inside isn't connected to the water around the island. One cell is a square with side length 1. The grid is rectangular, width and height don't exceed 100. Determine the perimeter of the island.

 

# Example 1:


# Input: grid = [[0,1,0,0],[1,1,1,0],[0,1,0,0],[1,1,0,0]]
# Output: 16
# Explanation: The perimeter is the 16 yellow stripes in the image above.

from typing import List

import operator

class Solution:
    def islandPerimeter(self, grid: List[List[int]]) -> int:
        r = sum(sum(map(operator.ne, [0] + row, row + [0]))
               for row in grid + map(list, zip(*grid))) #horizontal row and vertial row
        return r

        m, n, Perimeter = len(grid), len(grid[0]), 0

        for i in range(m):
            for j in range(n):
                Perimeter += 4*grid[i][j]
                if i > 0:   Perimeter -= grid[i][j]*grid[i-1][j]
                if i < m-1: Perimeter -= grid[i][j]*grid[i+1][j]
                if j > 0:   Perimeter -= grid[i][j]*grid[i][j-1]
                if j < n-1: Perimeter -= grid[i][j]*grid[i][j+1]
                    
        return Perimeter

# ,
# >>> A = [[ 1, 2, 3],[ 4, 5, 6]]
# >>> zip(*A)
# [(1, 4), (2, 5), (3, 6)]
# >>> lis  = [[1,2,3], 
# ... [4,5,6],
# ... [7,8,9]]
# >>> zip(*lis)
# [(1, 4, 7), (2, 5, 8), (3, 6, 9)]