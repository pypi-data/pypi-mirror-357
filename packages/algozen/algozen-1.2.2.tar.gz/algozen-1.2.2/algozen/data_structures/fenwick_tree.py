"""
Fenwick Tree (Binary Indexed Tree) implementation for AlgoZen.

A Fenwick Tree is a data structure that can efficiently calculate prefix sums
and update elements in O(log n) time.
"""
from typing import List


class FenwickTree:
    """Binary Indexed Tree for prefix sum queries and updates."""
    
    def __init__(self, arr: List[int]) -> None:
        """Initialize Fenwick Tree with array.
        
        Args:
            arr: Input array
            
        Time Complexity: O(n log n)
        Space Complexity: O(n)
        """
        self.n = len(arr)
        self.tree = [0] * (self.n + 1)
        
        for i, val in enumerate(arr):
            self.update(i, val)
    
    def update(self, idx: int, delta: int) -> None:
        """Add delta to element at index idx.
        
        Args:
            idx: Index to update (0-based)
            delta: Value to add
            
        Time Complexity: O(log n)
        Space Complexity: O(1)
        """
        idx += 1  # Convert to 1-based indexing
        while idx <= self.n:
            self.tree[idx] += delta
            idx += idx & (-idx)
    
    def prefix_sum(self, idx: int) -> int:
        """Get sum of elements from index 0 to idx (inclusive).
        
        Args:
            idx: End index (0-based, inclusive)
            
        Returns:
            Sum of elements from 0 to idx
            
        Time Complexity: O(log n)
        Space Complexity: O(1)
        """
        idx += 1  # Convert to 1-based indexing
        result = 0
        while idx > 0:
            result += self.tree[idx]
            idx -= idx & (-idx)
        return result
    
    def range_sum(self, left: int, right: int) -> int:
        """Get sum of elements from left to right (inclusive).
        
        Args:
            left: Start index (0-based, inclusive)
            right: End index (0-based, inclusive)
            
        Returns:
            Sum of elements from left to right
            
        Time Complexity: O(log n)
        Space Complexity: O(1)
        """
        if left == 0:
            return self.prefix_sum(right)
        return self.prefix_sum(right) - self.prefix_sum(left - 1)


class FenwickTree2D:
    """2D Binary Indexed Tree for 2D range sum queries."""
    
    def __init__(self, matrix: List[List[int]]) -> None:
        """Initialize 2D Fenwick Tree.
        
        Args:
            matrix: 2D input matrix
            
        Time Complexity: O(mn log m log n)
        Space Complexity: O(mn)
        """
        if not matrix or not matrix[0]:
            self.m = self.n = 0
            self.tree = []
            return
            
        self.m, self.n = len(matrix), len(matrix[0])
        self.tree = [[0] * (self.n + 1) for _ in range(self.m + 1)]
        
        for i in range(self.m):
            for j in range(self.n):
                self.update(i, j, matrix[i][j])
    
    def update(self, row: int, col: int, delta: int) -> None:
        """Add delta to element at (row, col).
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            delta: Value to add
            
        Time Complexity: O(log m log n)
        Space Complexity: O(1)
        """
        r = row + 1  # Convert to 1-based
        while r <= self.m:
            c = col + 1  # Convert to 1-based
            while c <= self.n:
                self.tree[r][c] += delta
                c += c & (-c)
            r += r & (-r)
    
    def prefix_sum(self, row: int, col: int) -> int:
        """Get sum from (0,0) to (row,col) inclusive.
        
        Args:
            row: End row (0-based, inclusive)
            col: End column (0-based, inclusive)
            
        Returns:
            Sum of rectangle from (0,0) to (row,col)
            
        Time Complexity: O(log m log n)
        Space Complexity: O(1)
        """
        result = 0
        r = row + 1  # Convert to 1-based
        while r > 0:
            c = col + 1  # Convert to 1-based
            while c > 0:
                result += self.tree[r][c]
                c -= c & (-c)
            r -= r & (-r)
        return result
    
    def range_sum(self, row1: int, col1: int, row2: int, col2: int) -> int:
        """Get sum of rectangle from (row1,col1) to (row2,col2).
        
        Args:
            row1: Top-left row (0-based, inclusive)
            col1: Top-left column (0-based, inclusive)
            row2: Bottom-right row (0-based, inclusive)
            col2: Bottom-right column (0-based, inclusive)
            
        Returns:
            Sum of the specified rectangle
            
        Time Complexity: O(log m log n)
        Space Complexity: O(1)
        """
        return (self.prefix_sum(row2, col2) - 
                (self.prefix_sum(row1 - 1, col2) if row1 > 0 else 0) -
                (self.prefix_sum(row2, col1 - 1) if col1 > 0 else 0) +
                (self.prefix_sum(row1 - 1, col1 - 1) if row1 > 0 and col1 > 0 else 0))