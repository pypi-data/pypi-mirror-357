"""
Tree algorithms implementation for AlgoZen.

This module provides various tree traversal and manipulation algorithms.
"""
from typing import List, Optional, Dict, Tuple
from collections import deque


class TreeNode:
    """Binary tree node."""
    def __init__(self, val: int = 0, left: 'TreeNode' = None, right: 'TreeNode' = None):
        self.val = val
        self.left = left
        self.right = right


def morris_inorder(root: Optional[TreeNode]) -> List[int]:
    """Morris inorder traversal without recursion or stack.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    result = []
    current = root
    
    while current:
        if not current.left:
            result.append(current.val)
            current = current.right
        else:
            # Find inorder predecessor
            predecessor = current.left
            while predecessor.right and predecessor.right != current:
                predecessor = predecessor.right
            
            if not predecessor.right:
                # Make current as right child of predecessor
                predecessor.right = current
                current = current.left
            else:
                # Revert changes
                predecessor.right = None
                result.append(current.val)
                current = current.right
    
    return result


def lowest_common_ancestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    """Find LCA of two nodes in binary tree.
    
    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if not root or root == p or root == q:
        return root
    
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    
    if left and right:
        return root
    return left or right


def serialize_tree(root: Optional[TreeNode]) -> str:
    """Serialize binary tree to string.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    def preorder(node):
        if not node:
            vals.append("null")
        else:
            vals.append(str(node.val))
            preorder(node.left)
            preorder(node.right)
    
    vals = []
    preorder(root)
    return ','.join(vals)


def deserialize_tree(data: str) -> Optional[TreeNode]:
    """Deserialize string to binary tree.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    def build():
        val = next(vals)
        if val == "null":
            return None
        node = TreeNode(int(val))
        node.left = build()
        node.right = build()
        return node
    
    vals = iter(data.split(','))
    return build()


def tree_diameter(root: Optional[TreeNode]) -> int:
    """Find diameter of binary tree.
    
    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    diameter = 0
    
    def depth(node):
        nonlocal diameter
        if not node:
            return 0
        
        left_depth = depth(node.left)
        right_depth = depth(node.right)
        
        diameter = max(diameter, left_depth + right_depth)
        return 1 + max(left_depth, right_depth)
    
    depth(root)
    return diameter


def vertical_order_traversal(root: Optional[TreeNode]) -> List[List[int]]:
    """Vertical order traversal of binary tree.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not root:
        return []
    
    column_table = {}
    queue = deque([(root, 0)])
    
    while queue:
        node, column = queue.popleft()
        
        if column not in column_table:
            column_table[column] = []
        column_table[column].append(node.val)
        
        if node.left:
            queue.append((node.left, column - 1))
        if node.right:
            queue.append((node.right, column + 1))
    
    return [column_table[x] for x in sorted(column_table.keys())]


def flatten_tree_to_linked_list(root: Optional[TreeNode]) -> None:
    """Flatten binary tree to linked list in-place.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    current = root
    
    while current:
        if current.left:
            # Find rightmost node in left subtree
            rightmost = current.left
            while rightmost.right:
                rightmost = rightmost.right
            
            # Rewire connections
            rightmost.right = current.right
            current.right = current.left
            current.left = None
        
        current = current.right


def path_sum_all_paths(root: Optional[TreeNode], target: int) -> List[List[int]]:
    """Find all root-to-leaf paths with given sum.
    
    Time Complexity: O(n²)
    Space Complexity: O(n²)
    """
    result = []
    
    def dfs(node, remaining, path):
        if not node:
            return
        
        path.append(node.val)
        
        if not node.left and not node.right and remaining == node.val:
            result.append(path[:])
        else:
            dfs(node.left, remaining - node.val, path)
            dfs(node.right, remaining - node.val, path)
        
        path.pop()
    
    dfs(root, target, [])
    return result


def construct_tree_from_preorder_inorder(preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
    """Construct binary tree from preorder and inorder traversals.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not preorder or not inorder:
        return None
    
    inorder_map = {val: i for i, val in enumerate(inorder)}
    preorder_idx = [0]
    
    def build(left, right):
        if left > right:
            return None
        
        root_val = preorder[preorder_idx[0]]
        preorder_idx[0] += 1
        root = TreeNode(root_val)
        
        mid = inorder_map[root_val]
        root.left = build(left, mid - 1)
        root.right = build(mid + 1, right)
        
        return root
    
    return build(0, len(inorder) - 1)


def tree_to_doubly_linked_list(root: Optional[TreeNode]) -> Optional[TreeNode]:
    """Convert BST to sorted doubly linked list.
    
    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if not root:
        return None
    
    first = last = None
    
    def inorder(node):
        nonlocal first, last
        if not node:
            return
        
        inorder(node.left)
        
        if last:
            last.right = node
            node.left = last
        else:
            first = node
        
        last = node
        inorder(node.right)
    
    inorder(root)
    
    # Make it circular
    first.left = last
    last.right = first
    
    return first