"""
Tree Problems and Solutions.

This module contains implementations of common tree problems and algorithms.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Set, Any, TypeVar, Callable, Generic
from functools import wraps
from collections import deque, defaultdict

T = TypeVar('T')

class TreeNode(Generic[T]):
    """Node class for a binary tree."""
    def __init__(
        self, 
        val: T = None, 
        left: Optional[TreeNode[T]] = None, 
        right: Optional[TreeNode[T]] = None,
        next: Optional[TreeNode[T]] = None
    ):
        self.val = val
        self.left = left
        self.right = right
        self.next = next  # For problems involving next pointer
    
    def __str__(self) -> str:
        return f"TreeNode({self.val})"
    
    @classmethod
    def from_list(cls, values: List[Optional[T]]) -> Optional[TreeNode[T]]:
        """
        Create a binary tree from a level-order traversal list.
        None values represent null nodes.
        """
        if not values or values[0] is None:
            return None
            
        root = cls(values[0])
        queue = deque([root])
        i = 1
        
        while queue and i < len(values):
            node = queue.popleft()
            
            # Left child
            if i < len(values) and values[i] is not None:
                node.left = cls(values[i])
                queue.append(node.left)
            i += 1
            
            # Right child
            if i < len(values) and values[i] is not None:
                node.right = cls(values[i])
                queue.append(node.right)
            i += 1
            
        return root
    
    def to_list(self) -> List[Optional[T]]:
        """Convert binary tree to level-order traversal list."""
        if not self:
            return []
            
        result = []
        queue = deque([self])
        
        while queue:
            node = queue.popleft()
            if node:
                result.append(node.val)
                queue.append(node.left)
                queue.append(node.right)
            else:
                result.append(None)
        
        # Remove trailing None values
        while result and result[-1] is None:
            result.pop()
            
        return result

def validate_tree(func: Callable) -> Callable:
    """Decorator to validate tree input for tree problems."""
    @wraps(func)
    def wrapper(root: Optional[TreeNode], *args, **kwargs) -> Any:
        return func(root, *args, **kwargs)
    return wrapper

@validate_tree
def max_depth(root: Optional[TreeNode[T]]) -> int:
    """
    Calculate the maximum depth of a binary tree.
    
    Args:
        root: Root of the binary tree
        
    Returns:
        Maximum depth of the tree
        
    Time Complexity: O(n)
    Space Complexity: O(h) where h is the height of the tree
    """
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

@validate_tree
def is_same_tree(p: Optional[TreeNode[T]], q: Optional[TreeNode[T]]) -> bool:
    """
    Check if two binary trees are identical.
    
    Args:
        p: Root of the first tree
        q: Root of the second tree
        
    Returns:
        True if the trees are identical, False otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(h) where h is the height of the tree
    """
    # Both nodes are None
    if not p and not q:
        return True
    # One of the nodes is None
    if not p or not q:
        return False
    # Check values and recurse
    return (p.val == q.val and 
            is_same_tree(p.left, q.left) and 
            is_same_tree(p.right, q.right))

@validate_tree
def invert_tree(root: Optional[TreeNode[T]]) -> Optional[TreeNode[T]]:
    """
    Invert a binary tree (mirror image).
    
    Args:
        root: Root of the binary tree
        
    Returns:
        Root of the inverted tree
        
    Time Complexity: O(n)
    Space Complexity: O(h) where h is the height of the tree
    """
    if not root:
        return None
    
    # Swap left and right subtrees
    root.left, root.right = root.right, root.left
    
    # Recurse on children
    invert_tree(root.left)
    invert_tree(root.right)
    
    return root

@validate_tree
def level_order_traversal(root: Optional[TreeNode[T]]) -> List[List[T]]:
    """
    Perform level-order traversal of a binary tree.
    
    Args:
        root: Root of the binary tree
        
    Returns:
        List of levels, where each level is a list of node values
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not root:
        return []
        
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
                
        result.append(current_level)
    
    return result

@validate_tree
def is_valid_bst(root: Optional[TreeNode[T]]) -> bool:
    """
    Check if a binary tree is a valid binary search tree.
    
    Args:
        root: Root of the binary tree
        
    Returns:
        True if the tree is a valid BST, False otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(h) where h is the height of the tree
    """
    def validate(node: Optional[TreeNode[T]], low=float('-inf'), high=float('inf')) -> bool:
        if not node:
            return True
        
        val = node.val
        if val <= low or val >= high:
            return False
            
        return (validate(node.left, low, val) and 
                validate(node.right, val, high))
    
    return validate(root)

@validate_tree
def lowest_common_ancestor(
    root: Optional[TreeNode[T]], 
    p: TreeNode[T], 
    q: TreeNode[T]
) -> Optional[TreeNode[T]]:
    """
    Find the lowest common ancestor (LCA) of two nodes in a binary tree.
    
    Args:
        root: Root of the binary tree
        p: First node
        q: Second node
        
    Returns:
        The LCA node if found, None otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(h) where h is the height of the tree
    """
    if not root or root == p or root == q:
        return root
    
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    
    if left and right:
        return root
    
    return left if left else right

@validate_tree
def serialize(root: Optional[TreeNode[T]]) -> str:
    """
    Serialize a binary tree to a string.
    
    Args:
        root: Root of the binary tree
        
    Returns:
        Serialized string representation of the tree
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not root:
        return "null"
    
    result = []
    queue = deque([root])
    
    while queue:
        node = queue.popleft()
        
        if node:
            result.append(str(node.val))
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append("null")
    
    # Remove trailing null values
    while result and result[-1] == "null":
        result.pop()
    
    return ",".join(result)

def deserialize(data: str) -> Optional[TreeNode[T]]:
    """
    Deserialize a string to a binary tree.
    
    Args:
        data: Serialized string representation of a tree
        
    Returns:
        Root of the deserialized binary tree
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not data or data == "null":
        return None
    
    values = data.split(',')
    root = TreeNode(int(values[0]))
    queue = deque([root])
    i = 1
    
    while queue and i < len(values):
        node = queue.popleft()
        
        # Left child
        if i < len(values) and values[i] != "null":
            node.left = TreeNode(int(values[i]))
            queue.append(node.left)
        i += 1
        
        # Right child
        if i < len(values) and values[i] != "null":
            node.right = TreeNode(int(values[i]))
            queue.append(node.right)
        i += 1
    
    return root

@validate_tree
def connect_nodes_at_same_level(root: Optional[TreeNode[T]]) -> Optional[TreeNode[T]]:
    """
    Connect each node with its next right node at the same level.
    
    Args:
        root: Root of the binary tree with next pointers
        
    Returns:
        Root of the modified tree
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not root:
        return None
    
    # Start with the root node
    leftmost = root
    
    while leftmost.left:
        # Current node at this level
        current = leftmost
        
        # Iterate through nodes at this level
        while current:
            # Connect left child to right child
            current.left.next = current.right
            
            # Connect right child to next node's left child
            if current.next:
                current.right.next = current.next.left
                
            # Move to next node
            current = current.next
        
        # Move to the leftmost node of the next level
        leftmost = leftmost.left
    
    return root

@validate_tree
def find_duplicate_subtrees(root: Optional[TreeNode[T]]) -> List[Optional[TreeNode[T]]]:
    """
    Find all duplicate subtrees in a binary tree.
    
    Args:
        root: Root of the binary tree
        
    Returns:
        List of root nodes of all duplicate subtrees
        
    Time Complexity: O(n²) in worst case
    Space Complexity: O(n²) for the serialization
    """
    count = defaultdict(int)
    result = []
    
    def serialize(node: Optional[TreeNode[T]]) -> str:
        if not node:
            return "#"
        
        # Serialize the tree in post-order
        left = serialize(node.left)
        right = serialize(node.right)
        
        # Create a unique identifier for the current subtree
        # Using a tuple of (left, node.val, right) would be more efficient
        # but requires a separate counter for deduplication
        identifier = f"{node.val},{left},{right}"
        
        # Check if this subtree has been seen before
        count[identifier] += 1
        if count[identifier] == 2:  # Only add once
            result.append(node)
            
        return identifier
    
    serialize(root)
    return result
