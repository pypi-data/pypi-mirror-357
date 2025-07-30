from typing import Any, Optional, Iterator, List


class Node:
    """Node class for linked list implementation."""
    
    def __init__(self, data: Any) -> None:
        self.data = data
        self.next: Optional['Node'] = None
    
    def __repr__(self) -> str:
        return f"Node({self.data})"


class LinkedList:
    """Singly Linked List implementation."""
    
    def __init__(self) -> None:
        self.head: Optional[Node] = None
        self._size: int = 0
    
    def __len__(self) -> int:
        return self._size
    
    def __iter__(self) -> Iterator[Any]:
        current = self.head
        while current:
            yield current.data
            current = current.next
    
    def __repr__(self) -> str:
        return " -> ".join(str(item) for item in self) + " -> None"
    
    def is_empty(self) -> bool:
        """Check if the linked list is empty."""
        return self.head is None
    
    def append(self, data: Any) -> None:
        """Add a node with data at the end of the linked list."""
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1
    
    def prepend(self, data: Any) -> None:
        """Add a node with data at the beginning of the linked list."""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1
    
    def delete(self, data: Any) -> bool:
        """Delete the first occurrence of a node with the given data.
        
        Returns:
            bool: True if the node was found and deleted, False otherwise.
        """
        if self.head is None:
            return False
            
        if self.head.data == data:
            self.head = self.head.next
            self._size -= 1
            return True
            
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self._size -= 1
                return True
            current = current.next
            
        return False
    
    def search(self, data: Any) -> bool:
        """Search for a node with the given data.
        
        Returns:
            bool: True if the data is found, False otherwise.
        """
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False
    
    def size(self) -> int:
        """Return the number of nodes in the linked list."""
        return self._size
    
    def to_list(self) -> List[Any]:
        """Convert the linked list to a Python list."""
        return list(iter(self))
    
    def reverse(self) -> None:
        """Reverse the linked list in-place."""
        prev = None
        current = self.head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev
