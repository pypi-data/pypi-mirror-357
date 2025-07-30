"""
Stack implementation for AlgoZen.

A stack is a linear data structure that follows the Last In First Out (LIFO) principle.
It has two main operations: push (adds an element) and pop (removes the most recently added element).
"""
from typing import TypeVar, Generic, List, Optional, Any

T = TypeVar('T')

class Stack(Generic[T]):
    """Stack implementation using a Python list.
    
    Attributes:
        _items (List[T]): Internal list to store stack items
    """
    
    def __init__(self) -> None:
        """Initialize an empty stack."""
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        """Add an item to the top of the stack.
        
        Args:
            item: The item to be added to the stack
        """
        self._items.append(item)
    
    def pop(self) -> T:
        """Remove and return the item at the top of the stack.
        
        Returns:
            The item at the top of the stack
            
        Raises:
            IndexError: If the stack is empty
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()
    
    def peek(self) -> T:
        """Return the item at the top of the stack without removing it.
        
        Returns:
            The item at the top of the stack
            
        Raises:
            IndexError: If the stack is empty
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]
    
    def is_empty(self) -> bool:
        """Check if the stack is empty.
        
        Returns:
            bool: True if the stack is empty, False otherwise
        """
        return len(self._items) == 0
    
    def size(self) -> int:
        """Return the number of items in the stack.
        
        Returns:
            int: The number of items in the stack
        """
        return len(self._items)
    
    def __len__(self) -> int:
        """Return the number of items in the stack.
        
        Returns:
            int: The number of items in the stack
        """
        return self.size()
    
    def __bool__(self) -> bool:
        """Return True if the stack is not empty.
        
        Returns:
            bool: True if the stack is not empty, False otherwise
        """
        return not self.is_empty()
    
    def __str__(self) -> str:
        """Return a string representation of the stack.
        
        Returns:
            str: String representation of the stack
        """
        return f"Stack({', '.join(map(str, self._items))})"
    
    def __contains__(self, item: T) -> bool:
        """Check if an item is in the stack.
        
        Args:
            item: The item to search for
            
        Returns:
            bool: True if the item is in the stack, False otherwise
        """
        return item in self._items
    
    def clear(self) -> None:
        """Remove all items from the stack."""
        self._items.clear()
    
    def copy(self) -> 'Stack[T]':
        """Create a shallow copy of the stack.
        
        Returns:
            Stack[T]: A new stack with the same items
        """
        new_stack = Stack[T]()
        new_stack._items = self._items.copy()
        return new_stack
    
    def to_list(self) -> List[T]:
        """Convert the stack to a list.
        
        Returns:
            List[T]: A list containing the stack items
        """
        return self._items.copy()
