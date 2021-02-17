# You are given an array rectangles where rectangles[i] = [li, wi] represents the ith rectangle of length li and width wi.

# You can cut the ith rectangle to form a square with a side length of k if both k <= li and k <= wi. For example, if you have a rectangle [4,6], you can cut it to get a square with a side length of at most 4.

# Let maxLen be the side length of the largest square you can obtain from any of the given rectangles.

# Return the number of rectangles that can make a square with a side length of maxLen.

 

# Example 1:

# Input: rectangles = [[5,8],[3,9],[5,12],[16,5]]
# Output: 3
# Explanation: The largest squares you can get from each rectangle are of lengths [5,3,5,5].
# The largest possible square is of length 5, and you can get it out of 3 rectangles.
# Example 2:

# Input: rectangles = [[2,3],[3,7],[4,3],[3,7]]
# Output: 3

from typing import Counter, List


class Solution:
    def countGoodRectangles(self, rectangles: List[List[int]]) -> int:
        # 1. 
        rect = list(map(lambda x: min(x[0],x[1]),rectangles))
        ob = Counter(rect)
        return ob[max(rect)] # get the 1st most common tuple and its value.
        # 2.
        d = {}
        for i,j in rectangles:
            minimum = min(i,j)
            d[minimum] = d.get(minimum,0)+1        
        return d[max(d)]

a = Solution()
print(a.countGoodRectangles([[5,8],[3,9],[5,12],[16,5]]))
print(a.countGoodRectangles([[5,8],[3,9],[3,12]]))