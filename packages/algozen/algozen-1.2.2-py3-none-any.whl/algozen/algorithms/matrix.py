"""
Matrix algorithms implementation for AlgoZen.

This module provides various matrix manipulation and traversal algorithms.
"""
from typing import List, Tuple


def rotate_matrix_90(matrix: List[List[int]]) -> List[List[int]]:
    """Rotate matrix 90 degrees clockwise in-place.
    
    Args:
        matrix: Square matrix to rotate
        
    Returns:
        Rotated matrix
        
    Time Complexity: O(n²)
    Space Complexity: O(1)
    """
    n = len(matrix)
    
    # Transpose matrix
    for i in range(n):
        for j in range(i, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    
    # Reverse each row
    for i in range(n):
        matrix[i].reverse()
    
    return matrix


def spiral_traversal(matrix: List[List[int]]) -> List[int]:
    """Traverse matrix in spiral order.
    
    Args:
        matrix: 2D matrix
        
    Returns:
        List of elements in spiral order
        
    Time Complexity: O(mn)
    Space Complexity: O(1)
    """
    if not matrix or not matrix[0]:
        return []
    
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        # Traverse right
        for col in range(left, right + 1):
            result.append(matrix[top][col])
        top += 1
        
        # Traverse down
        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1
        
        # Traverse left (if we still have rows)
        if top <= bottom:
            for col in range(right, left - 1, -1):
                result.append(matrix[bottom][col])
            bottom -= 1
        
        # Traverse up (if we still have columns)
        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1
    
    return result


def matrix_multiply(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    """Multiply two matrices.
    
    Args:
        A: First matrix (m x n)
        B: Second matrix (n x p)
        
    Returns:
        Product matrix (m x p)
        
    Time Complexity: O(mnp)
    Space Complexity: O(mp)
    """
    if not A or not B or not A[0] or not B[0]:
        return []
    
    m, n, p = len(A), len(A[0]), len(B[0])
    
    if len(B) != n:
        raise ValueError("Matrix dimensions don't match for multiplication")
    
    result = [[0] * p for _ in range(m)]
    
    for i in range(m):
        for j in range(p):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    
    return result


def set_matrix_zeros(matrix: List[List[int]]) -> None:
    """Set entire row and column to zero if element is zero.
    
    Args:
        matrix: Matrix to modify in-place
        
    Time Complexity: O(mn)
    Space Complexity: O(1)
    """
    if not matrix or not matrix[0]:
        return
    
    m, n = len(matrix), len(matrix[0])
    first_row_zero = any(matrix[0][j] == 0 for j in range(n))
    first_col_zero = any(matrix[i][0] == 0 for i in range(m))
    
    # Use first row and column as markers
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0
    
    # Set zeros based on markers
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
    
    # Handle first row and column
    if first_row_zero:
        for j in range(n):
            matrix[0][j] = 0
    
    if first_col_zero:
        for i in range(m):
            matrix[i][0] = 0


def search_2d_matrix(matrix: List[List[int]], target: int) -> bool:
    """Search for target in sorted 2D matrix.
    
    Args:
        matrix: Sorted matrix (rows and columns)
        target: Value to search for
        
    Returns:
        True if target found, False otherwise
        
    Time Complexity: O(m + n)
    Space Complexity: O(1)
    """
    if not matrix or not matrix[0]:
        return False
    
    m, n = len(matrix), len(matrix[0])
    row, col = 0, n - 1
    
    while row < m and col >= 0:
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] > target:
            col -= 1
        else:
            row += 1
    
    return False


def diagonal_traversal(matrix: List[List[int]]) -> List[int]:
    """Traverse matrix diagonally.
    
    Args:
        matrix: 2D matrix
        
    Returns:
        List of elements in diagonal order
        
    Time Complexity: O(mn)
    Space Complexity: O(1)
    """
    if not matrix or not matrix[0]:
        return []
    
    m, n = len(matrix), len(matrix[0])
    result = []
    
    # Traverse upper diagonals
    for d in range(n):
        i, j = 0, d
        while i < m and j >= 0:
            result.append(matrix[i][j])
            i += 1
            j -= 1
    
    # Traverse lower diagonals
    for d in range(1, m):
        i, j = d, n - 1
        while i < m and j >= 0:
            result.append(matrix[i][j])
            i += 1
            j -= 1
    
    return result


def transpose_matrix(matrix: List[List[int]]) -> List[List[int]]:
    """Transpose a matrix.
    
    Args:
        matrix: Input matrix
        
    Returns:
        Transposed matrix
        
    Time Complexity: O(mn)
    Space Complexity: O(mn)
    """
    if not matrix or not matrix[0]:
        return []
    
    m, n = len(matrix), len(matrix[0])
    transposed = [[0] * m for _ in range(n)]
    
    for i in range(m):
        for j in range(n):
            transposed[j][i] = matrix[i][j]
    
    return transposed