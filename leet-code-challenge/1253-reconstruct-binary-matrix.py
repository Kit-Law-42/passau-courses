# Given the following details of a matrix with n columns and 2 rows :

# The matrix is a binary matrix, which means each element in the matrix can be 0 or 1.
# The sum of elements of the 0-th(upper) row is given as upper.
# The sum of elements of the 1-st(lower) row is given as lower.
# The sum of elements in the i-th column(0-indexed) is colsum[i], where colsum is given as an integer array with length n.
# Your task is to reconstruct the matrix with upper, lower and colsum.

# Return it as a 2-D integer array.

# If there are more than one valid solution, any of them will be accepted.

# If no valid solution exists, return an empty 2-D array.

 

# Example 1:

# Input: upper = 2, lower = 1, colsum = [1,1,1]
# Output: [[1,1,0],[0,0,1]]
# Explanation: [[1,0,1],[0,1,0]], and [[0,1,1],[1,0,0]] are also correct answers.
# Example 2:

# Input: upper = 2, lower = 3, colsum = [2,2,1,1]
# Output: []
# Example 3:

# Input: upper = 5, lower = 5, colsum = [2,1,2,0,1,0,1,2,0,1]
# Output: [[1,1,1,0,1,0,0,1,0,0],[1,0,1,0,0,0,1,1,0,1]]
from typing import List


class Solution:
    def reconstructMatrix(self, upper: int, lower: int, colsum: List[int]) -> List[List[int]]:
        if upper + lower != sum(colsum) or min([upper, lower]) < len([i for i in colsum if i==2]):
            return []
        else:
            up = []
            low = []
            for col in colsum:
                if col ==2:
                    up.append(1)
                    low.append(1)
                    upper -=1
                    lower -=1
                else:
                    up.append(0)
                    low.append(0)
            for idx, col in enumerate(colsum):
                if col ==1:
                    if upper >0:
                        up[idx] = 1
                        upper -=1
                    else:
                        low[idx] = 1
                        lower -=1
            return [up, low]

a = Solution()
print(a.reconstructMatrix(2,1,[1,1,1]))
print(a.reconstructMatrix(2,3,[2,2,1,1]))
print(a.reconstructMatrix(5,5, [2,1,2,0,1,0,1,2,0,1]))
print(a.reconstructMatrix(9,2,[0,1,2,0,0,0,0,0,2,1,2,1,2]))