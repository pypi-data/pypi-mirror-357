"""
Queue implementation for AlgoZen.

A queue is a linear data structure that follows the First In First Out (FIFO) principle.
It has two main operations: enqueue (adds an element to the rear) and 
dequeue (removes the element from the front).
"""
from typing import TypeVar, Generic, List, Optional, Any, Deque
from collections import deque

T = TypeVar('T')

class Queue(Generic[T]):
    """Queue implementation using collections.deque for efficient operations.
    
    Attributes:
        _items (Deque[T]): Internal deque to store queue items
    """
    
    def __init__(self) -> None:
        """Initialize an empty queue."""
        self._items: Deque[T] = deque()
    
    def enqueue(self, item: T) -> None:
        """Add an item to the rear of the queue.
        
        Args:
            item: The item to be added to the queue
        """
        self._items.append(item)
    
    def dequeue(self) -> T:
        """Remove and return the item at the front of the queue.
        
        Returns:
            The item at the front of the queue
            
        Raises:
            IndexError: If the queue is empty
        """
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()
    
    def peek(self) -> T:
        """Return the item at the front of the queue without removing it.
        
        Returns:
            The item at the front of the queue
            
        Raises:
            IndexError: If the queue is empty
        """
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._items[0]
    
    def front(self) -> T:
        """Alias for peek to maintain backward compatibility."""
        return self.peek()
    
    def is_empty(self) -> bool:
        """Check if the queue is empty.
        
        Returns:
            bool: True if the queue is empty, False otherwise
        """
        return len(self._items) == 0
    
    def size(self) -> int:
        """Return the number of items in the queue.
        
        Returns:
            int: The number of items in the queue
        """
        return len(self._items)
    
    def __len__(self) -> int:
        """Return the number of items in the queue.
        
        Returns:
            int: The number of items in the queue
        """
        return self.size()
    
    def __bool__(self) -> bool:
        """Return True if the queue is not empty.
        
        Returns:
            bool: True if the queue is not empty, False otherwise
        """
        return not self.is_empty()
    
    def __str__(self) -> str:
        """Return a string representation of the queue.
        
        Returns:
            str: String representation of the queue
        """
        return f"Queue({', '.join(map(str, self._items))})"
    
    def __contains__(self, item: T) -> bool:
        """Check if an item is in the queue.
        
        Args:
            item: The item to search for
            
        Returns:
            bool: True if the item is in the queue, False otherwise
        """
        return item in self._items
    
    def clear(self) -> None:
        """Remove all items from the queue."""
        self._items.clear()
    
    def copy(self) -> 'Queue[T]':
        """Create a shallow copy of the queue.
        
        Returns:
            Queue[T]: A new queue with the same items
        """
        new_queue = Queue[T]()
        new_queue._items = self._items.copy()
        return new_queue
    
    def to_list(self) -> List[T]:
        """Convert the queue to a list.
        
        Returns:
            List[T]: A list containing the queue items
        """
        return list(self._items)
    
    def rotate(self, n: int = 1) -> None:
        """Rotate the queue n steps to the right.
        
        If n is negative, rotate to the left.
        
        Args:
            n: Number of steps to rotate
        """
        self._items.rotate(n)
