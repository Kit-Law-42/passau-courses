# You are given two arrays rowSum and colSum of non-negative integers where rowSum[i] is the sum of the elements in the ith row and colSum[j] is the sum of the elements of the jth column of a 2D matrix. In other words, you do not know the elements of the matrix, but you do know the sums of each row and column.

# Find any matrix of non-negative integers of size rowSum.length x colSum.length that satisfies the rowSum and colSum requirements.

# Return a 2D array representing any matrix that fulfills the requirements. It's guaranteed that at least one matrix that fulfills the requirements exists.

 

# Example 1:

# Input: rowSum = [3,8], colSum = [4,7]
# Output: [[3,0],
#          [1,7]]
# Explanation:
# 0th row: 3 + 0 = 3 == rowSum[0]
# 1st row: 1 + 7 = 8 == rowSum[1]
# 0th column: 3 + 1 = 4 == colSum[0]
# 1st column: 0 + 7 = 7 == colSum[1]
# The row and column sums match, and all matrix elements are non-negative.
# Another possible matrix is: [[1,2],
#                              [3,5]]
from typing import List


class Solution:
    def restoreMatrix(self, rowSum: List[int], colSum: List[int]) -> List[List[int]]:
        # m, n = len(rowSum), len(colSum)
        # A = [[0] * n for i in range(m)]
        # for i in range(m):
        #     for j in range(n):
        #         A[i][j] = min(rowSum[i], colSum[j])
        #         rowSum[i] -= A[i][j]
        #         colSum[j] -= A[i][j]
        # return A

        m, n = len(rowSum), len(colSum)
        g = [[0] * n for i in range(m)]
        ii = n - (colSum[n-1] == 0)
        jj = m - (rowSum[m-1] == 0)
        i, j = 0, 0
        while (i+j) < (ii+jj):
            print(i, j, rowSum, colSum, ii, jj)
            x = min(rowSum[j], colSum[i])
            g[j][i], rowSum[j], colSum[i] = x, rowSum[j] - x, colSum[i] - x
            if colSum[i] == 0: # column is done
                i = min(i+1, ii)
            if rowSum[j] == 0: # row is done
                j = min(j+1, jj)
        return g

a = Solution()
print(a.restoreMatrix([3,8], [4,7]))
print(a.restoreMatrix([14,9], [6,9,8]))