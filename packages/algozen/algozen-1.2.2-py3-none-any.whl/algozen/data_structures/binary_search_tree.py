"""
Binary Search Tree (BST) implementation for AlgoZen.

A binary search tree is a node-based binary tree where each node has a comparable key (and an associated value)
and satisfies the restriction that the key in any node is larger than the keys in all nodes in that node's
left subtree and smaller than the keys in all nodes in that node's right subtree.
"""
from typing import TypeVar, Generic, Optional, List, Iterator, Any, Tuple, Callable
from algozen.data_structures.binary_tree import BinaryTree, TreeNode

T = TypeVar('T', int, float, str)

class BSTNode(TreeNode[T]):
    """Node class for Binary Search Tree implementation.
    
    Attributes:
        key: The key used for ordering the BST
        val: The value associated with the key
        left: Reference to the left child node
        right: Reference to the right child node
        size: Number of nodes in the subtree rooted at this node
    """
    
    def __init__(self, key: T, val: Any = None, 
                 left: Optional['BSTNode[T]'] = None, 
                 right: Optional['BSTNode[T]'] = None) -> None:
        """Initialize a BST node with a key, optional value, and optional children."""
        super().__init__(val, left, right)
        self.key = key
        self.val = val if val is not None else key
        self.left = left
        self.right = right
        self.size = 1  # Number of nodes in the subtree rooted at this node
    
    def __repr__(self) -> str:
        return f"BSTNode(key={self.key}, val={self.val})"


class BinarySearchTree(Generic[T], BinaryTree[T]):
    """Binary Search Tree implementation.
    
    A binary search tree is a binary tree where each node has a key and satisfies the BST property:
    - The left subtree of a node contains only nodes with keys less than the node's key.
    - The right subtree of a node contains only nodes with keys greater than the node's key.
    - Both the left and right subtrees must also be binary search trees.
    """
    
    def __init__(self) -> None:
        """Initialize an empty BST."""
        super().__init__()
    
    def size(self) -> int:
        """Return the number of nodes in the BST.
        
        Returns:
            int: The number of nodes in the BST
        """
        return self._size(self.root)
    
    def _size(self, node: Optional[BSTNode[T]]) -> int:
        """Return the number of nodes in the subtree rooted at the given node."""
        if node is None:
            return 0
        return node.size
    
    def is_empty(self) -> bool:
        """Check if the BST is empty.
        
        Returns:
            bool: True if the BST is empty, False otherwise
        """
        return self.root is None
    
    def put(self, key: T, val: Any = None) -> None:
        """Insert a key-value pair into the BST.
        
        If the key already exists, update its value.
        
        Args:
            key: The key to insert
            val: The value associated with the key (defaults to the key if not provided)
        """
        self.root = self._put(self.root, key, val)
    
    def _put(self, node: Optional[BSTNode[T]], key: T, val: Any) -> BSTNode[T]:
        """Helper method to recursively insert a key-value pair into the BST."""
        if node is None:
            return BSTNode(key, val)
        
        if key < node.key:
            node.left = self._put(node.left, key, val)
        elif key > node.key:
            node.right = self._put(node.right, key, val)
        else:
            node.val = val  # Update value if key already exists
        
        # Update size
        node.size = 1 + self._size(node.left) + self._size(node.right)
        return node
    
    def get(self, key: T) -> Optional[Any]:
        """Get the value associated with the given key.
        
        Args:
            key: The key to search for
            
        Returns:
            The value associated with the key, or None if the key is not found
        """
        return self._get(self.root, key)
    
    def _get(self, node: Optional[BSTNode[T]], key: T) -> Optional[Any]:
        """Helper method to recursively get the value associated with a key."""
        if node is None:
            return None
        
        if key < node.key:
            return self._get(node.left, key)
        elif key > node.key:
            return self._get(node.right, key)
        else:
            return node.val
    
    def contains(self, key: T) -> bool:
        """Check if the BST contains the given key.
        
        Args:
            key: The key to search for
            
        Returns:
            bool: True if the key is in the BST, False otherwise
        """
        return self.get(key) is not None
    
    def insert(self, key: T, val: Any = None) -> None:
        """Insert a key-value pair into the BST (alias for put).
        
        Args:
            key: The key to insert
            val: The value associated with the key
        """
        self.put(key, val)
    
    def search(self, key: T) -> bool:
        """Search for a key in the BST (alias for contains).
        
        Args:
            key: The key to search for
            
        Returns:
            bool: True if the key is found, False otherwise
        """
        return self.contains(key)
    
    def delete(self, key: T) -> None:
        """Delete the node with the given key from the BST.
        
        Args:
            key: The key of the node to delete
            
        Raises:
            KeyError: If the key is not found in the BST
        """
        if not self.contains(key):
            raise KeyError(f"Key {key} not found in the BST")
        self.root = self._delete(self.root, key)
    
    def _delete(self, node: Optional[BSTNode[T]], key: T) -> Optional[BSTNode[T]]:
        """Helper method to recursively delete a node with the given key."""
        if node is None:
            return None
        
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            # Node with only one child or no child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            
            # Node with two children: get the inorder successor (smallest in the right subtree)
            temp = self._min(node.right)
            
            # Copy the inorder successor's content to this node
            node.key = temp.key
            node.val = temp.val
            
            # Delete the inorder successor
            node.right = self._delete_min(node.right)
        
        # Update size
        node.size = 1 + self._size(node.left) + self._size(node.right)
        return node
    
    def delete_min(self) -> None:
        """Delete the node with the smallest key in the BST."""
        if self.is_empty():
            raise Exception("BST is empty")
        self.root = self._delete_min(self.root)
    
    def _delete_min(self, node: BSTNode[T]) -> Optional[BSTNode[T]]:
        """Helper method to delete the node with the smallest key in the subtree."""
        if node.left is None:
            return node.right
        node.left = self._delete_min(node.left)
        
        # Update size
        node.size = 1 + self._size(node.left) + self._size(node.right)
        return node
    
    def delete_max(self) -> None:
        """Delete the node with the largest key in the BST."""
        if self.is_empty():
            raise Exception("BST is empty")
        self.root = self._delete_max(self.root)
    
    def _delete_max(self, node: BSTNode[T]) -> Optional[BSTNode[T]]:
        """Helper method to delete the node with the largest key in the subtree."""
        if node.right is None:
            return node.left
        node.right = self._delete_max(node.right)
        
        # Update size
        node.size = 1 + self._size(node.left) + self._size(node.right)
        return node
    
    def min(self) -> T:
        """Find the smallest key in the BST.
        
        Returns:
            The smallest key in the BST
            
        Raises:
            Exception: If the BST is empty
        """
        if self.is_empty():
            raise Exception("BST is empty")
        return self._min(self.root).key
    
    def _min(self, node: BSTNode[T]) -> BSTNode[T]:
        """Helper method to find the node with the smallest key in the subtree."""
        if node.left is None:
            return node
        return self._min(node.left)
    
    def max(self) -> T:
        """Find the largest key in the BST.
        
        Returns:
            The largest key in the BST
            
        Raises:
            Exception: If the BST is empty
        """
        if self.is_empty():
            raise Exception("BST is empty")
        return self._max(self.root).key
    
    def _max(self, node: BSTNode[T]) -> BSTNode[T]:
        """Helper method to find the node with the largest key in the subtree."""
        if node.right is None:
            return node
        return self._max(node.right)
    
    def floor(self, key: T) -> Optional[T]:
        """Find the largest key in the BST less than or equal to the given key.
        
        Args:
            key: The key to find the floor for
            
        Returns:
            The largest key in the BST less than or equal to the given key,
            or None if there is no such key
        """
        node = self._floor(self.root, key)
        if node is None:
            return None
        return node.key
    
    def _floor(self, node: Optional[BSTNode[T]], key: T) -> Optional[BSTNode[T]]:
        """Helper method to find the floor of a key in the BST."""
        if node is None:
            return None
            
        if key == node.key:
            return node
        elif key < node.key:
            return self._floor(node.left, key)
        
        temp = self._floor(node.right, key)
        if temp is not None:
            return temp
        return node
    
    def ceiling(self, key: T) -> Optional[T]:
        """Find the smallest key in the BST greater than or equal to the given key.
        
        Args:
            key: The key to find the ceiling for
            
        Returns:
            The smallest key in the BST greater than or equal to the given key,
            or None if there is no such key
        """
        node = self._ceiling(self.root, key)
        if node is None:
            return None
        return node.key
    
    def _ceiling(self, node: Optional[BSTNode[T]], key: T) -> Optional[BSTNode[T]]:
        """Helper method to find the ceiling of a key in the BST."""
        if node is None:
            return None
            
        if key == node.key:
            return node
        elif key > node.key:
            return self._ceiling(node.right, key)
            
        temp = self._ceiling(node.left, key)
        if temp is not None:
            return temp
        return node
    
    def rank(self, key: T) -> int:
        """Return the number of keys in the BST less than the given key.
        
        Args:
            key: The key to find the rank for
            
        Returns:
            int: The number of keys in the BST less than the given key
        """
        return self._rank(self.root, key)
    
    def _rank(self, node: Optional[BSTNode[T]], key: T) -> int:
        """Helper method to find the rank of a key in the BST."""
        if node is None:
            return 0
            
        if key < node.key:
            return self._rank(node.left, key)
        elif key > node.key:
            return 1 + self._size(node.left) + self._rank(node.right, key)
        else:
            return self._size(node.left)
    
    def select(self, rank: int) -> Optional[T]:
        """Return the key with the given rank.
        
        Args:
            rank: The rank of the key to find (0-based)
            
        Returns:
            The key with the given rank, or None if no such key exists
        """
        if rank < 0 or rank >= self.size():
            return None
        node = self._select(self.root, rank)
        if node is None:
            return None
        return node.key
    
    def _select(self, node: Optional[BSTNode[T]], rank: int) -> Optional[BSTNode[T]]:
        """Helper method to find the node with the given rank."""
        if node is None:
            return None
            
        left_size = self._size(node.left)
        
        if left_size > rank:
            return self._select(node.left, rank)
        elif left_size < rank:
            return self._select(node.right, rank - left_size - 1)
        else:
            return node
    
    def keys(self) -> Iterator[T]:
        """Return all keys in the BST in ascending order."""
        return self.keys_range(self.min(), self.max())
    
    def keys_range(self, lo: T, hi: T) -> Iterator[T]:
        """Return all keys in the BST in the range [lo, hi] in ascending order.
        
        Args:
            lo: The lower bound (inclusive)
            hi: The upper bound (inclusive)
            
        Returns:
            An iterator of keys in the specified range
        """
        queue = []
        self._keys_range(self.root, queue, lo, hi)
        return iter(queue)
    
    def _keys_range(self, node: Optional[BSTNode[T]], queue: List[T], lo: T, hi: T) -> None:
        """Helper method to collect keys in the range [lo, hi] in the subtree."""
        if node is None:
            return
            
        if lo < node.key:
            self._keys_range(node.left, queue, lo, hi)
            
        if lo <= node.key <= hi:
            queue.append(node.key)
            
        if hi > node.key:
            self._keys_range(node.right, queue, lo, hi)
    
    def height(self) -> int:
        """Return the height of the BST (the number of edges on the longest path).
        
        Returns:
            int: The height of the BST, or -1 if the BST is empty
        """
        return self._height(self.root)
    
    def _height(self, node: Optional[BSTNode[T]]) -> int:
        """Helper method to calculate the height of the subtree."""
        if node is None:
            return -1
        return 1 + max(self._height(node.left), self._height(node.right))
    
    def is_bst(self) -> bool:
        """Check if the tree is a valid BST.
        
        Returns:
            bool: True if the tree is a valid BST, False otherwise
        """
        return self._is_bst(self.root, None, None)
    
    def _is_bst(self, node: Optional[BSTNode[T]], min_val: Optional[T], max_val: Optional[T]) -> bool:
        """Helper method to check if the subtree is a valid BST."""
        if node is None:
            return True
            
        if (min_val is not None and node.key <= min_val) or \
           (max_val is not None and node.key >= max_val):
            return False
            
        return (self._is_bst(node.left, min_val, node.key) and 
                self._is_bst(node.right, node.key, max_val))
    
    def level_order_traversal(self) -> Iterator[T]:
        """Perform a level-order (breadth-first) traversal of the BST.
        
        Yields:
            The keys of the nodes in level-order
        """
        if self.is_empty():
            return
            
        queue = [self.root]
        
        while queue:
            node = queue.pop(0)
            yield node.key
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
