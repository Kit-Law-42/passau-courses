# Example:

# Input: 5
# Output:
# [
#      [1],
#     [1,1],
#    [1,2,1],
#   [1,3,3,1],
#  [1,4,6,4,1]
# ]

from typing import List


class Solution:
    def generate(self, numRows: int) -> List[List[int]]:
        r = []
        for i in range(numRows):
            arr= [None for _ in range(i+1)]
            arr[0] = arr[-1] = 1
            for j in range(1, len(arr)-1):
                arr[j] = r[i-1][j-1] + r[i-1][j]
            r.append(arr)
        return r          
        