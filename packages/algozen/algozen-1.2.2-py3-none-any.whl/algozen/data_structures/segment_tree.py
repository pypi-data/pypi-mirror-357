"""
Segment Tree implementation for AlgoZen.

A segment tree is a binary tree used for storing information about intervals or segments.
It allows querying which of the stored segments contain a given point efficiently.
"""
from typing import List, Callable, TypeVar, Optional

T = TypeVar('T')


class SegmentTree:
    """Segment Tree for range queries and updates."""
    
    def __init__(self, arr: List[int], operation: str = 'sum') -> None:
        """Initialize segment tree with array and operation.
        
        Args:
            arr: Input array
            operation: 'sum', 'min', or 'max'
            
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.arr = arr[:]
        
        if operation == 'sum':
            self.op = lambda x, y: x + y
            self.identity = 0
        elif operation == 'min':
            self.op = lambda x, y: min(x, y)
            self.identity = float('inf')
        elif operation == 'max':
            self.op = lambda x, y: max(x, y)
            self.identity = float('-inf')
        else:
            raise ValueError("Operation must be 'sum', 'min', or 'max'")
        
        self._build(0, 0, self.n - 1)
    
    def _build(self, node: int, start: int, end: int) -> None:
        """Build the segment tree recursively."""
        if start == end:
            self.tree[node] = self.arr[start]
        else:
            mid = (start + end) // 2
            self._build(2 * node + 1, start, mid)
            self._build(2 * node + 2, mid + 1, end)
            self.tree[node] = self.op(self.tree[2 * node + 1], self.tree[2 * node + 2])
    
    def update(self, idx: int, val: int) -> None:
        """Update value at index idx to val.
        
        Args:
            idx: Index to update
            val: New value
            
        Time Complexity: O(log n)
        Space Complexity: O(log n)
        """
        self.arr[idx] = val
        self._update(0, 0, self.n - 1, idx, val)
    
    def _update(self, node: int, start: int, end: int, idx: int, val: int) -> None:
        """Update helper function."""
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self._update(2 * node + 1, start, mid, idx, val)
            else:
                self._update(2 * node + 2, mid + 1, end, idx, val)
            self.tree[node] = self.op(self.tree[2 * node + 1], self.tree[2 * node + 2])
    
    def query(self, l: int, r: int) -> int:
        """Query the result for range [l, r].
        
        Args:
            l: Left boundary (inclusive)
            r: Right boundary (inclusive)
            
        Returns:
            Result of operation over the range
            
        Time Complexity: O(log n)
        Space Complexity: O(log n)
        """
        return self._query(0, 0, self.n - 1, l, r)
    
    def _query(self, node: int, start: int, end: int, l: int, r: int) -> int:
        """Query helper function."""
        if r < start or end < l:
            return self.identity
        if l <= start and end <= r:
            return self.tree[node]
        
        mid = (start + end) // 2
        left_result = self._query(2 * node + 1, start, mid, l, r)
        right_result = self._query(2 * node + 2, mid + 1, end, l, r)
        return self.op(left_result, right_result)


class LazySegmentTree:
    """Segment Tree with lazy propagation for range updates."""
    
    def __init__(self, arr: List[int]) -> None:
        """Initialize lazy segment tree for range sum queries.
        
        Args:
            arr: Input array
            
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self.arr = arr[:]
        self._build(0, 0, self.n - 1)
    
    def _build(self, node: int, start: int, end: int) -> None:
        """Build the segment tree."""
        if start == end:
            self.tree[node] = self.arr[start]
        else:
            mid = (start + end) // 2
            self._build(2 * node + 1, start, mid)
            self._build(2 * node + 2, mid + 1, end)
            self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]
    
    def _push(self, node: int, start: int, end: int) -> None:
        """Push lazy values down."""
        if self.lazy[node] != 0:
            self.tree[node] += self.lazy[node] * (end - start + 1)
            if start != end:
                self.lazy[2 * node + 1] += self.lazy[node]
                self.lazy[2 * node + 2] += self.lazy[node]
            self.lazy[node] = 0
    
    def range_update(self, l: int, r: int, val: int) -> None:
        """Add val to all elements in range [l, r].
        
        Args:
            l: Left boundary (inclusive)
            r: Right boundary (inclusive)
            val: Value to add
            
        Time Complexity: O(log n)
        Space Complexity: O(log n)
        """
        self._range_update(0, 0, self.n - 1, l, r, val)
    
    def _range_update(self, node: int, start: int, end: int, l: int, r: int, val: int) -> None:
        """Range update helper."""
        self._push(node, start, end)
        if start > r or end < l:
            return
        if start >= l and end <= r:
            self.lazy[node] += val
            self._push(node, start, end)
            return
        
        mid = (start + end) // 2
        self._range_update(2 * node + 1, start, mid, l, r, val)
        self._range_update(2 * node + 2, mid + 1, end, l, r, val)
        
        self._push(2 * node + 1, start, mid)
        self._push(2 * node + 2, mid + 1, end)
        self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]
    
    def query(self, l: int, r: int) -> int:
        """Query sum for range [l, r].
        
        Args:
            l: Left boundary (inclusive)
            r: Right boundary (inclusive)
            
        Returns:
            Sum of elements in range
            
        Time Complexity: O(log n)
        Space Complexity: O(log n)
        """
        return self._query(0, 0, self.n - 1, l, r)
    
    def _query(self, node: int, start: int, end: int, l: int, r: int) -> int:
        """Query helper."""
        if start > r or end < l:
            return 0
        self._push(node, start, end)
        if start >= l and end <= r:
            return self.tree[node]
        
        mid = (start + end) // 2
        return (self._query(2 * node + 1, start, mid, l, r) + 
                self._query(2 * node + 2, mid + 1, end, l, r))