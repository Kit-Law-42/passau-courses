# You are given an n x n 2D matrix representing an image, rotate the image by 90 degrees (clockwise).

# You have to rotate the image in-place, which means you have to modify the input 2D matrix directly. DO NOT allocate another 2D matrix and do the rotation.

# Input: matrix = [[1,2,3],[4,5,6],[7,8,9]]
# Output: [[7,4,1],[8,5,2],[9,6,3]]

class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        
        n = len(matrix)
        
        for i in range(n):
            for j in range(i+1, n):
                a = matrix[i][j]
                matrix[i][j] =  matrix[j][i]
                matrix[j][i] = a
        for i in range(n):
            for j in range(n//2):
                a = matrix[i][n-j-1]
                matrix[i][n-j-1] =  matrix[i][j]
                matrix[i][j] = a
                
        return(matrix)
