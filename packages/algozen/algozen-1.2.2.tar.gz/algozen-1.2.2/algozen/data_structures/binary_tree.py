"""
Binary Tree implementation for AlgoZen.

A binary tree is a tree data structure in which each node has at most two children,
referred to as the left child and the right child.
"""
from typing import TypeVar, Generic, Optional, List, Any, Callable, Iterator
from collections import deque

T = TypeVar('T')

class TreeNode(Generic[T]):
    """Node class for binary tree implementation.
    
    Attributes:
        val: The value stored in the node
        left: Reference to the left child node
        right: Reference to the right child node
    """
    
    def __init__(self, val: T, left: Optional['TreeNode[T]'] = None, 
                 right: Optional['TreeNode[T]'] = None) -> None:
        self.val = val
        self.left = left
        self.right = right
    
    def __repr__(self) -> str:
        return f"TreeNode({self.val})"
    
    def is_leaf(self) -> bool:
        """Check if the node is a leaf (has no children).
        
        Returns:
            bool: True if the node is a leaf, False otherwise
        """
        return self.left is None and self.right is None
    
    def height(self) -> int:
        """Calculate the height of the node.
        
        The height of a node is the number of edges on the longest path 
        from the node to a leaf.
        
        Returns:
            int: The height of the node
        """
        if self.is_leaf():
            return 0
        
        left_height = self.left.height() if self.left else 0
        right_height = self.right.height() if self.right else 0
        
        return 1 + max(left_height, right_height)


class BinaryTree(Generic[T]):
    """Binary Tree implementation.
    
    A binary tree is a tree data structure in which each node has at most two children,
    referred to as the left child and the right child.
    """
    
    def __init__(self, root: Optional[TreeNode[T]] = None) -> None:
        """Initialize the binary tree with an optional root node.
        
        Args:
            root: The root node of the tree
        """
        self.root = root
    
    def is_empty(self) -> bool:
        """Check if the tree is empty.
        
        Returns:
            bool: True if the tree is empty, False otherwise
        """
        return self.root is None
    
    def height(self) -> int:
        """Calculate the height of the tree.
        
        The height of a tree is the number of edges on the longest path 
        from the root node to a leaf node.
        
        Returns:
            int: The height of the tree, or -1 if the tree is empty
        """
        if self.is_empty():
            return -1
        return self.root.height()
    
    def size(self) -> int:
        """Calculate the number of nodes in the tree.
        
        Returns:
            int: The number of nodes in the tree
        """
        return sum(1 for _ in self.level_order_traversal())
    
    def __len__(self) -> int:
        """Return the number of nodes in the tree.
        
        Returns:
            int: The number of nodes in the tree
        """
        return self.size()
    
    def level_order_traversal(self) -> Iterator[T]:
        """Perform a level-order (breadth-first) traversal of the tree.
        
        Yields:
            The values of the nodes in level-order
        """
        if self.is_empty():
            return
            
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            yield node.val
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    
    def preorder_traversal(self) -> Iterator[T]:
        """Perform a pre-order traversal of the tree (root -> left -> right).
        
        Yields:
            The values of the nodes in pre-order
        """
        def _preorder(node: Optional[TreeNode[T]]) -> Iterator[T]:
            if node:
                yield node.val
                yield from _preorder(node.left)
                yield from _preorder(node.right)
        
        return _preorder(self.root)
    
    def inorder_traversal(self) -> Iterator[T]:
        """Perform an in-order traversal of the tree (left -> root -> right).
        
        Yields:
            The values of the nodes in in-order
        """
        def _inorder(node: Optional[TreeNode[T]]) -> Iterator[T]:
            if node:
                yield from _inorder(node.left)
                yield node.val
                yield from _inorder(node.right)
        
        return _inorder(self.root)
    
    def postorder_traversal(self) -> Iterator[T]:
        """Perform a post-order traversal of the tree (left -> right -> root).
        
        Yields:
            The values of the nodes in post-order
        """
        def _postorder(node: Optional[TreeNode[T]]) -> Iterator[T]:
            if node:
                yield from _postorder(node.left)
                yield from _postorder(node.right)
                yield node.val
        
        return _postorder(self.root)
    
    def is_complete(self) -> bool:
        """Check if the binary tree is complete.
        
        A binary tree is complete if all levels are completely filled except 
        possibly the last level, which is filled from left to right.
        
        Returns:
            bool: True if the tree is complete, False otherwise
        """
        if self.is_empty():
            return True
            
        queue = deque([self.root])
        has_null_child = False
        
        while queue:
            node = queue.popleft()
            
            if node is None:
                has_null_child = True
            else:
                if has_null_child:
                    return False
                queue.append(node.left)
                queue.append(node.right)
        
        return True
    
    def is_full(self) -> bool:
        """Check if the binary tree is full.
        
        A binary tree is full if every node has either 0 or 2 children.
        
        Returns:
            bool: True if the tree is full, False otherwise
        """
        def _is_full(node: Optional[TreeNode[T]]) -> bool:
            if node is None:
                return True
                
            if node.is_leaf():
                return True
                
            if node.left is not None and node.right is not None:
                return _is_full(node.left) and _is_full(node.right)
                
            return False
        
        return _is_full(self.root)
    
    def is_perfect(self) -> bool:
        """Check if the binary tree is perfect.
        
        A binary tree is perfect if all internal nodes have exactly two children 
        and all leaves are at the same level.
        
        Returns:
            bool: True if the tree is perfect, False otherwise
        """
        def _is_perfect(node: Optional[TreeNode[T]], level: int, leaf_level: List[int]) -> bool:
            if node is None:
                return True
                
            if node.is_leaf():
                if leaf_level[0] == -1:
                    leaf_level[0] = level
                return leaf_level[0] == level
                
            if node.left is None or node.right is None:
                return False
                
            return (_is_perfect(node.left, level + 1, leaf_level) and 
                    _is_perfect(node.right, level + 1, leaf_level))
        
        leaf_level = [-1]
        return _is_perfect(self.root, 0, leaf_level)
    
    def is_balanced(self) -> bool:
        """Check if the binary tree is balanced.
        
        A binary tree is balanced if the heights of the two child subtrees of 
        every node differ by at most 1.
        
        Returns:
            bool: True if the tree is balanced, False otherwise
        """
        def _check_balanced(node: Optional[TreeNode[T]]) -> int:
            if node is None:
                return 0
                
            left_height = _check_balanced(node.left)
            if left_height == -1:
                return -1
                
            right_height = _check_balanced(node.right)
            if right_height == -1:
                return -1
                
            if abs(left_height - right_height) > 1:
                return -1
                
            return 1 + max(left_height, right_height)
        
        return _check_balanced(self.root) != -1
    
    def to_list_level_order(self) -> List[Optional[T]]:
        """Convert the binary tree to a list in level-order (breadth-first) with None for missing nodes.
        
        Returns:
            List[Optional[T]]: A list representation of the tree in level-order
        """
        if self.is_empty():
            return []
            
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            
            if node:
                result.append(node.val)
                queue.append(node.left)
                queue.append(node.right)
            else:
                result.append(None)
        
        # Remove trailing Nones
        while result and result[-1] is None:
            result.pop()
            
        return result
    
    @classmethod
    def from_list(cls, values: List[Optional[T]]) -> 'BinaryTree[T]':
        """Create a binary tree from a list in level-order.
        
        Args:
            values: List of values in level-order, with None for missing nodes
            
        Returns:
            BinaryTree[T]: A new binary tree constructed from the input list
        """
        if not values:
            return cls()
            
        root = TreeNode(values[0])
        queue = deque([root])
        i = 1
        
        while queue and i < len(values):
            node = queue.popleft()
            
            if i < len(values) and values[i] is not None:
                node.left = TreeNode(values[i])
                queue.append(node.left)
            i += 1
            
            if i < len(values) and values[i] is not None:
                node.right = TreeNode(values[i])
                queue.append(node.right)
            i += 1
        
        return cls(root)
    
    def __str__(self) -> str:
        """Return a string representation of the binary tree.
        
        Returns:
            str: A string representation of the tree in level-order
        """
        return str(self.to_list_level_order())
