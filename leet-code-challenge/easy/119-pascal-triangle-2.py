# Given an integer rowIndex, return the rowIndexth row of the Pascal's triangle.

# Notice that the row index starts from 0.


# In Pascal's triangle, each number is the sum of the two numbers directly above it.

# Follow up:

# Could you optimize your algorithm to use only O(k) extra space?

 

# Example 1:

# Input: rowIndex = 3
# Output: [1,3,3,1]


import math
from typing import List

class Solution:
    def getRow(self, rowIndex: int) -> List[int]:
        r = [None for _ in range(rowIndex+1)]
        for idx, i in enumerate(r):
            r[idx] = int(math.factorial(rowIndex) / (math.factorial(idx) *  math.factorial(rowIndex-idx)))
        
        return r
    
        '''
        
        row = [1]
                for i in range(rowIndex):
                    row = [1] + [row[j]+row[j+1] for j in range(len(row)-1)] + [1] 
                return row
        '''