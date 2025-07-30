"""
Graph Problems and Solutions.

This module contains implementations of common graph problems and algorithms.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Set, Any, TypeVar, Callable, Generic, Deque
from functools import wraps
from collections import deque, defaultdict
import heapq

T = TypeVar('T')

class GraphNode(Generic[T]):
    """Node class for a graph with neighbors and weights."""
    def __init__(self, val: T):
        self.val = val
        self.neighbors: List[GraphNode[T]] = []
        self.weights: Dict[GraphNode[T], int] = {}
    
    def add_neighbor(self, node: GraphNode[T], weight: int = 1) -> None:
        """Add a neighbor to this node with an optional weight."""
        self.neighbors.append(node)
        self.weights[node] = weight
    
    def __str__(self) -> str:
        return f"GraphNode({self.val})"

class Graph:
    """Graph implementation using adjacency list."""
    def __init__(self, directed: bool = False):
        self.nodes: Dict[T, GraphNode[T]] = {}
        self.directed = directed
    
    def add_node(self, val: T) -> GraphNode[T]:
        """Add a node to the graph if it doesn't exist."""
        if val not in self.nodes:
            self.nodes[val] = GraphNode(val)
        return self.nodes[val]
    
    def add_edge(self, src: T, dest: T, weight: int = 1) -> None:
        """Add an edge between two nodes with an optional weight."""
        src_node = self.add_node(src)
        dest_node = self.add_node(dest)
        
        src_node.add_neighbor(dest_node, weight)
        if not self.directed:
            dest_node.add_neighbor(src_node, weight)
    
    def get_node(self, val: T) -> Optional[GraphNode[T]]:
        """Get a node by its value."""
        return self.nodes.get(val)

def has_path_dfs(graph: Graph[T], start: T, end: T) -> bool:
    """
    Check if there's a path between two nodes using DFS.
    
    Args:
        graph: The graph to search
        start: Starting node value
        end: Target node value
        
    Returns:
        True if a path exists, False otherwise
        
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    if start not in graph.nodes or end not in graph.nodes:
        return False
    
    visited = set()
    stack = [graph.get_node(start)]
    
    while stack:
        node = stack.pop()
        if node.val == end:
            return True
        
        if node.val not in visited:
            visited.add(node.val)
            # Push neighbors in reverse order to process them left-to-right
            for neighbor in reversed(node.neighbors):
                if neighbor.val not in visited:
                    stack.append(neighbor)
    
    return False

def has_path_bfs(graph: Graph[T], start: T, end: T) -> bool:
    """
    Check if there's a path between two nodes using BFS.
    
    Args:
        graph: The graph to search
        start: Starting node value
        end: Target node value
        
    Returns:
        True if a path exists, False otherwise
        
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    if start not in graph.nodes or end not in graph.nodes:
        return False
    
    visited = set()
    queue = deque([graph.get_node(start)])
    
    while queue:
        node = queue.popleft()
        if node.val == end:
            return True
        
        if node.val not in visited:
            visited.add(node.val)
            for neighbor in node.neighbors:
                if neighbor.val not in visited:
                    queue.append(neighbor)
    
    return False

def topological_sort(graph: Graph[T]) -> List[T]:
    """
    Perform topological sort on a directed acyclic graph (DAG).
    
    Args:
        graph: The directed acyclic graph
        
    Returns:
        A topological ordering of the nodes, or empty list if graph is not a DAG
        
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    if not graph.directed:
        return []
    
    in_degree = {node: 0 for node in graph.nodes}
    
    # Calculate in-degree for each node
    for node in graph.nodes.values():
        for neighbor in node.neighbors:
            in_degree[neighbor.val] += 1
    
    # Initialize queue with nodes having 0 in-degree
    queue = deque([node for node, degree in in_degree.items() if degree == 0])
    topo_order = []
    
    while queue:
        if len(queue) > 1:
            # If there are multiple nodes with 0 in-degree, the graph has multiple valid orderings
            pass
            
        node_val = queue.popleft()
        topo_order.append(node_val)
        
        # Reduce in-degree of all neighbors
        node = graph.get_node(node_val)
        for neighbor in node.neighbors:
            in_degree[neighbor.val] -= 1
            if in_degree[neighbor.val] == 0:
                queue.append(neighbor.val)
    
    # Check if topological sort is possible (no cycles)
    if len(topo_order) != len(graph.nodes):
        return []
    
    return topo_order

def dijkstra_shortest_path(graph: Graph[T], start: T, end: T) -> Tuple[float, List[T]]:
    """
    Find the shortest path between two nodes using Dijkstra's algorithm.
    
    Args:
        graph: The weighted graph (must have non-negative edge weights)
        start: Starting node value
        end: Target node value
        
    Returns:
        A tuple of (shortest_distance, path) or (float('inf'), []) if no path exists
        
    Time Complexity: O((V + E) log V) with min-heap
    Space Complexity: O(V)
    """
    if start not in graph.nodes or end not in graph.nodes:
        return float('inf'), []
    
    # Priority queue: (distance, node_value, path)
    heap = [(0, start, [start])]
    visited = set()
    
    while heap:
        dist, current_val, path = heapq.heappop(heap)
        
        if current_val in visited:
            continue
            
        if current_val == end:
            return dist, path
            
        visited.add(current_val)
        current_node = graph.get_node(current_val)
        
        for neighbor in current_node.neighbors:
            if neighbor.val not in visited:
                new_dist = dist + current_node.weights[neighbor]
                new_path = path + [neighbor.val]
                heapq.heappush(heap, (new_dist, neighbor.val, new_path))
    
    return float('inf'), []

def bellman_ford_shortest_path(graph: Graph[T], start: T) -> Dict[T, float]:
    """
    Find the shortest paths from a start node to all other nodes using Bellman-Ford algorithm.
    Can detect negative weight cycles.
    
    Args:
        graph: The weighted graph (can have negative weights)
        start: Starting node value
        
    Returns:
        Dictionary of shortest distances to each node, or empty dict if a negative cycle exists
        
    Time Complexity: O(V * E)
    Space Complexity: O(V)
    """
    if start not in graph.nodes:
        return {}
    
    # Initialize distances
    dist = {node: float('inf') for node in graph.nodes}
    dist[start] = 0
    
    # Relax all edges V-1 times
    for _ in range(len(graph.nodes) - 1):
        updated = False
        for node in graph.nodes.values():
            for neighbor, weight in node.weights.items():
                if dist[node.val] + weight < dist[neighbor.val]:
                    dist[neighbor.val] = dist[node.val] + weight
                    updated = True
        if not updated:
            break
    
    # Check for negative weight cycles
    for node in graph.nodes.values():
        for neighbor, weight in node.weights.items():
            if dist[node.val] + weight < dist[neighbor.val]:
                return {}  # Negative cycle detected
    
    return dist

def kruskal_mst(graph: Graph[T]) -> List[Tuple[T, T, int]]:
    """
    Find the minimum spanning tree (MST) using Kruskal's algorithm.
    
    Args:
        graph: The undirected weighted graph
        
    Returns:
        List of edges in the MST as (u, v, weight) tuples
        
    Time Complexity: O(E log E) or O(E log V)
    Space Complexity: O(V + E)
    """
    if graph.directed:
        return []
    
    # Disjoint-set (Union-Find) data structure
    parent = {}
    
    def find(u: T) -> T:
        while parent[u] != u:
            parent[u] = parent[parent[u]]  # Path compression
            u = parent[u]
        return u
    
    def union(u: T, v: T) -> None:
        u_root = find(u)
        v_root = find(v)
        if u_root != v_root:
            parent[u_root] = v_root
    
    # Initialize parent pointers
    for node in graph.nodes:
        parent[node] = node
    
    # Get all edges and sort them by weight
    edges = []
    for node in graph.nodes.values():
        for neighbor, weight in node.weights.items():
            # Add each edge only once (since graph is undirected)
            if node.val < neighbor.val:
                edges.append((node.val, neighbor.val, weight))
    
    edges.sort(key=lambda x: x[2])  # Sort by weight
    
    mst = []
    for u, v, weight in edges:
        if find(u) != find(v):
            union(u, v)
            mst.append((u, v, weight))
            if len(mst) == len(graph.nodes) - 1:
                break
    
    return mst

def prim_mst(graph: Graph[T]) -> List[Tuple[T, T, int]]:
    """
    Find the minimum spanning tree (MST) using Prim's algorithm.
    
    Args:
        graph: The undirected weighted graph
        
    Returns:
        List of edges in the MST as (u, v, weight) tuples
        
    Time Complexity: O(E log V) with min-heap
    Space Complexity: O(V + E)
    """
    if graph.directed or not graph.nodes:
        return []
    
    # Start with the first node
    start_node = next(iter(graph.nodes.values()))
    visited = {start_node.val}
    mst = []
    
    # Priority queue: (weight, u, v)
    edges = []
    for neighbor, weight in start_node.weights.items():
        heapq.heappush(edges, (weight, start_node.val, neighbor.val))
    
    while edges and len(visited) < len(graph.nodes):
        weight, u, v = heapq.heappop(edges)
        
        if v not in visited:
            visited.add(v)
            mst.append((u, v, weight))
            
            # Add edges from the newly added node
            node = graph.get_node(v)
            for neighbor, w in node.weights.items():
                if neighbor.val not in visited:
                    heapq.heappush(edges, (w, v, neighbor.val))
    
    return mst if len(visited) == len(graph.nodes) else []

def find_articulation_points(graph: Graph[T]) -> Set[T]:
    """
    Find all articulation points (cut vertices) in an undirected graph.
    
    Args:
        graph: The undirected graph
        
    Returns:
        Set of articulation points
        
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    if graph.directed or not graph.nodes:
        return set()
    
    disc = {}
    low = {}
    parent = {}
    visited = set()
    articulation_points = set()
    time = 0
    
    def dfs(u: T) -> None:
        nonlocal time
        
        # Count of children in DFS tree
        children = 0
        
        # Mark the current node as visited
        visited.add(u)
        disc[u] = low[u] = time
        time += 1
        
        # Recur for all vertices adjacent to this vertex
        for v in graph.get_node(u).neighbors:
            v = v.val  # Get the node value
            
            # If v is not visited yet, then make it a child of u
            if v not in visited:
                parent[v] = u
                children += 1
                dfs(v)
                
                # Check if the subtree rooted with v has a connection to
                # one of the ancestors of u
                low[u] = min(low[u], low[v])
                
                # u is an articulation point in following cases:
                # (1) u is root of DFS tree and has two or more children
                if parent.get(u) is None and children > 1:
                    articulation_points.add(u)
                    
                # (2) If u is not root and low value of one of its child is more than discovery value of u
                if parent.get(u) is not None and low[v] >= disc[u]:
                    articulation_points.add(u)
                    
            # Update low value of u for parent function calls
            elif v != parent.get(u):
                low[u] = min(low[u], disc[v])
    
    # Initialize parent and call DFS for each unvisited vertex
    for node in graph.nodes:
        if node not in visited:
            parent[node] = None
            dfs(node)
    
    return articulation_points

def find_bridges(graph: Graph[T]) -> List[Tuple[T, T]]:
    """
    Find all bridges (cut edges) in an undirected graph.
    
    Args:
        graph: The undirected graph
        
    Returns:
        List of bridge edges as (u, v) tuples
        
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    if graph.directed or not graph.nodes:
        return []
    
    disc = {}
    low = {}
    visited = set()
    bridges = []
    time = 0
    
    def dfs(u: T, parent: Optional[T] = None) -> None:
        nonlocal time
        
        visited.add(u)
        disc[u] = low[u] = time
        time += 1
        
        for v in graph.get_node(u).neighbors:
            v = v.val  # Get the node value
            
            if v not in visited:
                dfs(v, u)
                
                # Check if the subtree rooted with v has a connection to
                # one of the ancestors of u
                low[u] = min(low[u], low[v])
                
                # If the lowest vertex reachable from subtree under v is
                # below u in DFS tree, then u-v is a bridge
                if low[v] > disc[u]:
                    bridges.append((u, v) if u < v else (v, u))
                    
            # Update low value of u for parent function calls
            elif v != parent:
                low[u] = min(low[u], disc[v])
    
    # Call DFS for each unvisited vertex
    for node in graph.nodes:
        if node not in visited:
            dfs(node)
    
    return bridges
