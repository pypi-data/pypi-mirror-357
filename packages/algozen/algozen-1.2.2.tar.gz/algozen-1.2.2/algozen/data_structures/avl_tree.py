"""
AVL Tree implementation for AlgoZen.

An AVL tree is a self-balancing binary search tree where the heights of the
two child subtrees of any node differ by at most one.
"""
from typing import Optional, List, TypeVar

T = TypeVar('T')


class AVLNode:
    """Node class for AVL Tree."""
    
    def __init__(self, val: T) -> None:
        self.val = val
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height = 1


class AVLTree:
    """AVL Tree implementation with automatic balancing."""
    
    def __init__(self) -> None:
        """Initialize empty AVL tree."""
        self.root: Optional[AVLNode] = None
    
    def insert(self, val: T) -> None:
        """Insert value into AVL tree.
        
        Args:
            val: Value to insert
            
        Time Complexity: O(log n)
        Space Complexity: O(log n)
        """
        self.root = self._insert(self.root, val)
    
    def _insert(self, node: Optional[AVLNode], val: T) -> AVLNode:
        """Insert helper with balancing."""
        # Standard BST insertion
        if not node:
            return AVLNode(val)
        
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        else:
            return node  # Duplicate values not allowed
        
        # Update height
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        
        # Get balance factor
        balance = self._get_balance(node)
        
        # Left Left Case
        if balance > 1 and val < node.left.val:
            return self._right_rotate(node)
        
        # Right Right Case
        if balance < -1 and val > node.right.val:
            return self._left_rotate(node)
        
        # Left Right Case
        if balance > 1 and val > node.left.val:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        
        # Right Left Case
        if balance < -1 and val < node.right.val:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        
        return node
    
    def delete(self, val: T) -> None:
        """Delete value from AVL tree.
        
        Args:
            val: Value to delete
            
        Time Complexity: O(log n)
        Space Complexity: O(log n)
        """
        self.root = self._delete(self.root, val)
    
    def _delete(self, node: Optional[AVLNode], val: T) -> Optional[AVLNode]:
        """Delete helper with balancing."""
        if not node:
            return node
        
        if val < node.val:
            node.left = self._delete(node.left, val)
        elif val > node.val:
            node.right = self._delete(node.right, val)
        else:
            # Node to be deleted found
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            
            # Node with two children
            temp = self._get_min_value_node(node.right)
            node.val = temp.val
            node.right = self._delete(node.right, temp.val)
        
        # Update height
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        
        # Get balance factor
        balance = self._get_balance(node)
        
        # Left Left Case
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)
        
        # Left Right Case
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        
        # Right Right Case
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)
        
        # Right Left Case
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        
        return node
    
    def search(self, val: T) -> bool:
        """Search for value in AVL tree.
        
        Args:
            val: Value to search for
            
        Returns:
            True if found, False otherwise
            
        Time Complexity: O(log n)
        Space Complexity: O(log n)
        """
        return self._search(self.root, val)
    
    def _search(self, node: Optional[AVLNode], val: T) -> bool:
        """Search helper."""
        if not node:
            return False
        if val == node.val:
            return True
        elif val < node.val:
            return self._search(node.left, val)
        else:
            return self._search(node.right, val)
    
    def inorder(self) -> List[T]:
        """Get inorder traversal of tree.
        
        Returns:
            List of values in sorted order
            
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        result = []
        self._inorder(self.root, result)
        return result
    
    def _inorder(self, node: Optional[AVLNode], result: List[T]) -> None:
        """Inorder traversal helper."""
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)
    
    def _get_height(self, node: Optional[AVLNode]) -> int:
        """Get height of node."""
        if not node:
            return 0
        return node.height
    
    def _get_balance(self, node: Optional[AVLNode]) -> int:
        """Get balance factor of node."""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
    
    def _left_rotate(self, z: AVLNode) -> AVLNode:
        """Perform left rotation."""
        y = z.right
        T2 = y.left
        
        # Perform rotation
        y.left = z
        z.right = T2
        
        # Update heights
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        return y
    
    def _right_rotate(self, z: AVLNode) -> AVLNode:
        """Perform right rotation."""
        y = z.left
        T3 = y.right
        
        # Perform rotation
        y.right = z
        z.left = T3
        
        # Update heights
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        return y
    
    def _get_min_value_node(self, node: AVLNode) -> AVLNode:
        """Get node with minimum value."""
        while node.left:
            node = node.left
        return node