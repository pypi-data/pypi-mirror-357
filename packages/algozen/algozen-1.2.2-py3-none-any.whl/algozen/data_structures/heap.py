"""
Heap data structure implementation.

This module provides MinHeap and MaxHeap implementations.
"""
from typing import List, TypeVar, Generic, Optional, Any, Callable

T = TypeVar('T')

class Heap(Generic[T]):
    """Base class for heap implementations."""
    def __init__(self, compare: Callable[[T, T], bool]):
        """Initialize the heap with a comparison function.
        
        Args:
            compare: A function that takes two elements and returns True if the first
                   should be higher in the heap than the second.
        """
        self._heap: List[T] = []
        self._compare = compare
    
    def __len__(self) -> int:
        """Return the number of elements in the heap."""
        return len(self._heap)
    
    def is_empty(self) -> bool:
        """Check if the heap is empty."""
        return len(self._heap) == 0
    
    def peek(self) -> Optional[T]:
        """Return the top element of the heap without removing it."""
        return self._heap[0] if self._heap else None
    
    def push(self, item: T) -> None:
        """Add an item to the heap."""
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)
    
    def pop(self) -> T:
        """Remove and return the top element from the heap."""
        if not self._heap:
            raise IndexError("pop from empty heap")
        
        self._swap(0, len(self._heap) - 1)
        item = self._heap.pop()
        
        if self._heap:
            self._sift_down(0)
        
        return item
    
    def _sift_up(self, idx: int) -> None:
        """Move the element at the given index up to its correct position."""
        while idx > 0:
            parent = (idx - 1) // 2
            if self._compare(self._heap[idx], self._heap[parent]):
                self._swap(idx, parent)
                idx = parent
            else:
                break
    
    def _sift_down(self, idx: int) -> None:
        """Move the element at the given index down to its correct position."""
        n = len(self._heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            candidate = idx
            
            if left < n and self._compare(self._heap[left], self._heap[candidate]):
                candidate = left
            if right < n and self._compare(self._heap[right], self._heap[candidate]):
                candidate = right
                
            if candidate == idx:
                break
                
            self._swap(idx, candidate)
            idx = candidate
    
    def _swap(self, i: int, j: int) -> None:
        """Swap elements at the given indices."""
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

class MinHeap(Heap[T]):
    """Min-heap implementation."""
    def __init__(self):
        """Initialize a new MinHeap."""
        super().__init__(lambda a, b: a < b)
    
    def insert(self, item: T) -> None:
        """Alias for push to maintain backward compatibility."""
        self.push(item)
    
    def extract_min(self) -> T:
        """Alias for pop to maintain backward compatibility."""
        return self.pop()
    
    def get_min(self) -> Optional[T]:
        """Alias for peek to maintain backward compatibility."""
        return self.peek()
    
    def size(self) -> int:
        """Return the number of elements in the heap."""
        return len(self._heap)

class MaxHeap(Heap[T]):
    """Max-heap implementation."""
    def __init__(self):
        """Initialize a new MaxHeap."""
        super().__init__(lambda a, b: a > b)
    
    def insert(self, item: T) -> None:
        """Alias for push to maintain backward compatibility."""
        self.push(item)
    
    def extract_max(self) -> T:
        """Alias for pop to maintain backward compatibility."""
        return self.pop()
    
    def get_max(self) -> Optional[T]:
        """Alias for peek to maintain backward compatibility."""
        return self.peek()
