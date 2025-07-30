"""
Advanced tree patterns for AlgoZen.

This module provides various advanced tree algorithmic patterns.
"""
from typing import List, Optional, Dict, Tuple
from collections import defaultdict, deque


class TreeNode:
    def __init__(self, val: int = 0, left: 'TreeNode' = None, right: 'TreeNode' = None):
        self.val = val
        self.left = left
        self.right = right


def heavy_light_decomposition(adj: List[List[int]], root: int = 0) -> Dict:
    """Decompose tree using Heavy-Light Decomposition.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    n = len(adj)
    parent = [-1] * n
    depth = [0] * n
    subtree_size = [0] * n
    heavy_child = [-1] * n
    
    def dfs1(u: int, p: int, d: int):
        parent[u] = p
        depth[u] = d
        subtree_size[u] = 1
        max_child_size = 0
        
        for v in adj[u]:
            if v != p:
                dfs1(v, u, d + 1)
                subtree_size[u] += subtree_size[v]
                if subtree_size[v] > max_child_size:
                    max_child_size = subtree_size[v]
                    heavy_child[u] = v
    
    dfs1(root, -1, 0)
    
    chain_head = [-1] * n
    chain_id = [0] * n
    pos_in_chain = [0] * n
    chain_count = 0
    
    def dfs2(u: int, head: int):
        nonlocal chain_count
        chain_head[u] = head
        chain_id[u] = chain_count if head == u else chain_id[head]
        pos_in_chain[u] = 0 if head == u else pos_in_chain[parent[u]] + 1
        
        if heavy_child[u] != -1:
            dfs2(heavy_child[u], head)
        
        for v in adj[u]:
            if v != parent[u] and v != heavy_child[u]:
                chain_count += 1
                dfs2(v, v)
    
    dfs2(root, root)
    
    return {
        'parent': parent,
        'depth': depth,
        'chain_head': chain_head,
        'chain_id': chain_id,
        'pos_in_chain': pos_in_chain
    }


def lca_binary_lifting(adj: List[List[int]], root: int = 0) -> Dict:
    """Preprocess tree for LCA queries using binary lifting.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n log n)
    """
    n = len(adj)
    LOG = 20
    up = [[-1] * LOG for _ in range(n)]
    depth = [0] * n
    
    def dfs(u: int, p: int, d: int):
        up[u][0] = p
        depth[u] = d
        
        for i in range(1, LOG):
            if up[u][i-1] != -1:
                up[u][i] = up[up[u][i-1]][i-1]
        
        for v in adj[u]:
            if v != p:
                dfs(v, u, d + 1)
    
    dfs(root, -1, 0)
    
    def lca(u: int, v: int) -> int:
        if depth[u] < depth[v]:
            u, v = v, u
        
        # Bring u to same level as v
        diff = depth[u] - depth[v]
        for i in range(LOG):
            if (diff >> i) & 1:
                u = up[u][i]
        
        if u == v:
            return u
        
        # Binary search for LCA
        for i in range(LOG - 1, -1, -1):
            if up[u][i] != up[v][i]:
                u = up[u][i]
                v = up[v][i]
        
        return up[u][0]
    
    return {'lca': lca, 'depth': depth}


def centroid_decomposition(adj: List[List[int]]) -> Dict:
    """Decompose tree using centroid decomposition.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    n = len(adj)
    removed = [False] * n
    subtree_size = [0] * n
    centroid_parent = [-1] * n
    
    def get_subtree_size(u: int, p: int) -> int:
        subtree_size[u] = 1
        for v in adj[u]:
            if v != p and not removed[v]:
                subtree_size[u] += get_subtree_size(v, u)
        return subtree_size[u]
    
    def get_centroid(u: int, p: int, tree_size: int) -> int:
        for v in adj[u]:
            if v != p and not removed[v] and subtree_size[v] > tree_size // 2:
                return get_centroid(v, u, tree_size)
        return u
    
    def decompose(u: int, p: int) -> int:
        tree_size = get_subtree_size(u, -1)
        centroid = get_centroid(u, -1, tree_size)
        
        removed[centroid] = True
        centroid_parent[centroid] = p
        
        for v in adj[centroid]:
            if not removed[v]:
                decompose(v, centroid)
        
        return centroid
    
    root = decompose(0, -1)
    return {'root': root, 'parent': centroid_parent}


def tree_isomorphism(tree1: List[List[int]], tree2: List[List[int]]) -> bool:
    """Check if two trees are isomorphic.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if len(tree1) != len(tree2):
        return False
    
    def get_canonical_form(adj: List[List[int]], root: int) -> str:
        def dfs(u: int, p: int) -> str:
            children = []
            for v in adj[u]:
                if v != p:
                    children.append(dfs(v, u))
            children.sort()
            return '(' + ''.join(children) + ')'
        
        return dfs(root, -1)
    
    # Try all possible roots for tree1
    for root1 in range(len(tree1)):
        canonical1 = get_canonical_form(tree1, root1)
        
        # Try all possible roots for tree2
        for root2 in range(len(tree2)):
            canonical2 = get_canonical_form(tree2, root2)
            if canonical1 == canonical2:
                return True
    
    return False


def tree_diameter_and_center(adj: List[List[int]]) -> Tuple[int, List[int]]:
    """Find tree diameter and center nodes.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    n = len(adj)
    
    def bfs_farthest(start: int) -> Tuple[int, int]:
        visited = [False] * n
        queue = deque([(start, 0)])
        visited[start] = True
        farthest_node = start
        max_dist = 0
        
        while queue:
            node, dist = queue.popleft()
            if dist > max_dist:
                max_dist = dist
                farthest_node = node
            
            for neighbor in adj[node]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append((neighbor, dist + 1))
        
        return farthest_node, max_dist
    
    # Find one end of diameter
    end1, _ = bfs_farthest(0)
    
    # Find other end and diameter
    end2, diameter = bfs_farthest(end1)
    
    # Find center(s) - middle node(s) of diameter path
    def find_path(start: int, end: int) -> List[int]:
        parent = [-1] * n
        visited = [False] * n
        queue = deque([start])
        visited[start] = True
        
        while queue:
            node = queue.popleft()
            if node == end:
                break
            
            for neighbor in adj[node]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    parent[neighbor] = node
                    queue.append(neighbor)
        
        path = []
        current = end
        while current != -1:
            path.append(current)
            current = parent[current]
        
        return path[::-1]
    
    diameter_path = find_path(end1, end2)
    center_idx = len(diameter_path) // 2
    
    if len(diameter_path) % 2 == 1:
        centers = [diameter_path[center_idx]]
    else:
        centers = [diameter_path[center_idx - 1], diameter_path[center_idx]]
    
    return diameter, centers


def tree_hash(adj: List[List[int]], root: int = 0) -> int:
    """Compute hash of rooted tree.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    MOD = 10**9 + 7
    BASE = 31
    
    def dfs(u: int, p: int) -> int:
        hash_val = 1
        child_hashes = []
        
        for v in adj[u]:
            if v != p:
                child_hashes.append(dfs(v, u))
        
        child_hashes.sort()
        
        for child_hash in child_hashes:
            hash_val = (hash_val * BASE + child_hash) % MOD
        
        return hash_val
    
    return dfs(root, -1)


def tree_dp_rerooting(adj: List[List[int]], values: List[int]) -> List[int]:
    """Tree DP with rerooting technique.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    n = len(adj)
    dp_down = [0] * n  # DP values going down from root
    dp_up = [0] * n    # DP values going up from children
    
    def dfs1(u: int, p: int):
        dp_down[u] = values[u]
        for v in adj[u]:
            if v != p:
                dfs1(v, u)
                dp_down[u] += dp_down[v]
    
    def dfs2(u: int, p: int):
        # Calculate prefix and suffix sums for rerooting
        children = [v for v in adj[u] if v != p]
        
        prefix = [0] * (len(children) + 1)
        suffix = [0] * (len(children) + 1)
        
        for i, v in enumerate(children):
            prefix[i + 1] = prefix[i] + dp_down[v]
        
        for i in range(len(children) - 1, -1, -1):
            suffix[i] = suffix[i + 1] + dp_down[children[i]]
        
        for i, v in enumerate(children):
            dp_up[v] = values[u] + dp_up[u] + prefix[i] + suffix[i + 1]
            dfs2(v, u)
    
    dfs1(0, -1)
    dfs2(0, -1)
    
    # Combine results
    result = [0] * n
    for i in range(n):
        result[i] = dp_down[i] + dp_up[i] - values[i]  # Subtract to avoid double counting
    
    return result


def euler_tour_tree(adj: List[List[int]], root: int = 0) -> Dict:
    """Create Euler tour of tree for range queries.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    n = len(adj)
    euler_tour = []
    first_occurrence = [-1] * n
    last_occurrence = [-1] * n
    depth = [0] * n
    
    def dfs(u: int, p: int, d: int):
        depth[u] = d
        first_occurrence[u] = len(euler_tour)
        euler_tour.append(u)
        
        for v in adj[u]:
            if v != p:
                dfs(v, u, d + 1)
                euler_tour.append(u)
        
        last_occurrence[u] = len(euler_tour) - 1
    
    dfs(root, -1, 0)
    
    return {
        'tour': euler_tour,
        'first': first_occurrence,
        'last': last_occurrence,
        'depth': depth
    }