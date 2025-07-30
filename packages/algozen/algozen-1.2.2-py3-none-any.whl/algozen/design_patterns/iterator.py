"""
Iterator Pattern Implementation.

This module provides an implementation of the Iterator pattern, which provides a way
to access the elements of an aggregate object sequentially without exposing its
underlying representation.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Dict, TypeVar, Generic, Iterable, Iterator, Optional
from collections.abc import MutableSequence
import collections.abc

T = TypeVar('T')

class Iterator(Generic[T], ABC):
    """
    The Iterator interface declares the operations required for traversing a collection.
    """
    @abstractmethod
    def __next__(self) -> T:
        """
        Return the next item in the sequence.
        
        Raises:
            StopIteration: When there are no more items to return.
        """
        pass
    
    def __iter__(self) -> Iterator[T]:
        """
        Return the iterator object itself.
        
        Returns:
            The iterator object itself.
        """
        return self

class IterableCollection(ABC, Generic[T]):
    """
    The Collection interface declares one or multiple methods for getting iterators
    compatible with the collection.
    """
    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """
        Return an iterator over the collection.
        
        Returns:
            An iterator object.
        """
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """
        Return the number of items in the collection.
        
        Returns:
            The number of items in the collection.
        """
        pass

# ============================================
# Basic Iterator Implementations
# ============================================

class ListIterator(Iterator[T]):
    """
    Concrete iterator for traversing a list.
    """
    def __init__(self, collection: List[T]) -> None:
        """
        Initialize the iterator with a list.
        
        Args:
            collection: The list to iterate over.
        """
        self._collection = collection
        self._index = 0
    
    def __next__(self) -> T:
        """
        Return the next item in the list.
        
        Returns:
            The next item in the list.
            
        Raises:
            StopIteration: When there are no more items to return.
        """
        try:
            item = self._collection[self._index]
            self._index += 1
            return item
        except IndexError:
            raise StopIteration()

class DictKeyIterator(Iterator[T]):
    """
    Concrete iterator for traversing dictionary keys.
    """
    def __init__(self, dictionary: Dict[T, Any]) -> None:
        """
        Initialize the iterator with a dictionary.
        
        Args:
            dictionary: The dictionary whose keys to iterate over.
        """
        self._keys = list(dictionary.keys())
        self._index = 0
    
    def __next__(self) -> T:
        """
        Return the next key in the dictionary.
        
        Returns:
            The next key in the dictionary.
            
        Raises:
            StopIteration: When there are no more keys to return.
        """
        try:
            key = self._keys[self._index]
            self._index += 1
            return key
        except IndexError:
            raise StopIteration()

class DictValueIterator(Iterator[T]):
    """
    Concrete iterator for traversing dictionary values.
    """
    def __init__(self, dictionary: Dict[Any, T]) -> None:
        """
        Initialize the iterator with a dictionary.
        
        Args:
            dictionary: The dictionary whose values to iterate over.
        """
        self._values = list(dictionary.values())
        self._index = 0
    
    def __next__(self) -> T:
        """
        Return the next value in the dictionary.
        
        Returns:
            The next value in the dictionary.
            
        Raises:
            StopIteration: When there are no more values to return.
        """
        try:
            value = self._values[self._index]
            self._index += 1
            return value
        except IndexError:
            raise StopIteration()

# ============================================
# Collection Implementations
# ============================================

class CustomList(IterableCollection[T], MutableSequence[T]):
    """
    A custom list implementation that supports the Iterator pattern.
    """
    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        """
        Initialize the custom list.
        
        Args:
            items: Optional initial items for the list.
        """
        self._items: List[T] = list(items) if items is not None else []
    
    def __iter__(self) -> Iterator[T]:
        """
        Return an iterator over the list.
        
        Returns:
            A list iterator.
        """
        return ListIterator(self._items)
    
    def __len__(self) -> int:
        """
        Return the number of items in the list.
        
        Returns:
            The number of items in the list.
        """
        return len(self._items)
    
    def __getitem__(self, index: int) -> T:
        """
        Get the item at the specified index.
        
        Args:
            index: The index of the item to get.
            
        Returns:
            The item at the specified index.
            
        Raises:
            IndexError: If the index is out of range.
        """
        return self._items[index]
    
    def __setitem__(self, index: int, value: T) -> None:
        """
        Set the item at the specified index.
        
        Args:
            index: The index at which to set the item.
            value: The value to set.
            
        Raises:
            IndexError: If the index is out of range.
        """
        self._items[index] = value
    
    def __delitem__(self, index: int) -> None:
        """
        Delete the item at the specified index.
        
        Args:
            index: The index of the item to delete.
            
        Raises:
            IndexError: If the index is out of range.
        """
        del self._items[index]
    
    def insert(self, index: int, value: T) -> None:
        """
        Insert an item at the specified index.
        
        Args:
            index: The index at which to insert the item.
            value: The value to insert.
        """
        self._items.insert(index, value)
    
    def append(self, value: T) -> None:
        """
        Append an item to the end of the list.
        
        Args:
            value: The value to append.
        """
        self._items.append(value)
    
    def reverse(self) -> None:
        """Reverse the list in place."""
        self._items.reverse()
    
    def sort(self, *, key=None, reverse=False) -> None:
        """
        Sort the list in place.
        
        Args:
            key: A function to extract a comparison key from each list element.
            reverse: If True, sort in descending order.
        """
        self._items.sort(key=key, reverse=reverse)

class CustomDict(IterableCollection[T]):
    """
    A custom dictionary implementation that supports the Iterator pattern.
    """
    def __init__(self, items: Optional[Dict[str, T]] = None) -> None:
        """
        Initialize the custom dictionary.
        
        Args:
            items: Optional initial items for the dictionary.
        """
        self._items: Dict[str, T] = dict(items) if items is not None else {}
    
    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator over the dictionary keys.
        
        Returns:
            A dictionary key iterator.
        """
        return DictKeyIterator(self._items)
    
    def __len__(self) -> int:
        """
        Return the number of items in the dictionary.
        
        Returns:
            The number of items in the dictionary.
        """
        return len(self._items)
    
    def __getitem__(self, key: str) -> T:
        """
        Get the value for the specified key.
        
        Args:
            key: The key to look up.
            
        Returns:
            The value for the specified key.
            
        Raises:
            KeyError: If the key is not found.
        """
        return self._items[key]
    
    def __setitem__(self, key: str, value: T) -> None:
        """
        Set the value for the specified key.
        
        Args:
            key: The key to set.
            value: The value to set.
        """
        self._items[key] = value
    
    def __delitem__(self, key: str) -> None:
        """
        Delete the item with the specified key.
        
        Args:
            key: The key to delete.
            
        Raises:
            KeyError: If the key is not found.
        """
        del self._items[key]
    
    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the dictionary keys.
        
        Returns:
            A dictionary key iterator.
        """
        return DictKeyIterator(self._items)
    
    def values(self) -> Iterator[T]:
        """
        Return an iterator over the dictionary values.
        
        Returns:
            A dictionary value iterator.
        """
        return DictValueIterator(self._items)
    
    def items(self) -> Iterator[tuple[str, T]]:
        """
        Return an iterator over (key, value) pairs.
        
        Returns:
            An iterator over (key, value) pairs.
        """
        return iter(self._items.items())

# ============================================
# Tree Iterator
# ============================================

class TreeNode(Generic[T]):
    """
    A node in a tree data structure.
    """
    def __init__(self, value: T) -> None:
        """
        Initialize a tree node with a value.
        
        Args:
            value: The value stored in the node.
        """
        self.value = value
        self.children: List[TreeNode[T]] = []
        self.parent: Optional[TreeNode[T]] = None
    
    def add_child(self, child: 'TreeNode[T]') -> None:
        """
        Add a child to this node.
        
        Args:
            child: The child node to add.
        """
        child.parent = self
        self.children.append(child)
    
    def is_leaf(self) -> bool:
        """
        Check if this node is a leaf (has no children).
        
        Returns:
            True if the node is a leaf, False otherwise.
        """
        return len(self.children) == 0
    
    def is_root(self) -> bool:
        """
        Check if this node is the root of the tree.
        
        Returns:
            True if the node is the root, False otherwise.
        """
        return self.parent is None

class TreeIterator(Iterator[T]):
    """
    An iterator for tree traversal (depth-first pre-order).
    """
    def __init__(self, root: TreeNode[T]) -> None:
        """
        Initialize the tree iterator with a root node.
        
        Args:
            root: The root node of the tree.
        """
        self._stack: List[TreeNode[T]] = [root]
    
    def __next__(self) -> T:
        """
        Return the next node in the tree.
        
        Returns:
            The value of the next node.
            
        Raises:
            StopIteration: When there are no more nodes to visit.
        """
        if not self._stack:
            raise StopIteration()
        
        node = self._stack.pop()
        # Push children in reverse order to process them from left to right
        for child in reversed(node.children):
            self._stack.append(child)
        
        return node.value

class Tree(IterableCollection[T]):
    """
    A tree data structure that supports the Iterator pattern.
    """
    def __init__(self, root: Optional[TreeNode[T]] = None) -> None:
        """
        Initialize the tree with an optional root node.
        
        Args:
            root: The root node of the tree.
        """
        self._root = root
    
    def __iter__(self) -> Iterator[T]:
        """
        Return an iterator for depth-first pre-order traversal of the tree.
        
        Returns:
            A tree iterator.
        """
        if self._root is None:
            return iter([])
        return TreeIterator(self._root)
    
    def __len__(self) -> int:
        """
        Return the number of nodes in the tree.
        
        Returns:
            The number of nodes in the tree.
        """
        if self._root is None:
            return 0
        
        count = 0
        for _ in self:
            count += 1
        return count
    
    def set_root(self, root: TreeNode[T]) -> None:
        """
        Set the root of the tree.
        
        Args:
            root: The new root node.
        """
        self._root = root
    
    def is_empty(self) -> bool:
        """
        Check if the tree is empty.
        
        Returns:
            True if the tree is empty, False otherwise.
        """
        return self._root is None
