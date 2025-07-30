"""
Advanced Graph Algorithms for AlgoZen.

This module contains implementations of advanced graph algorithms.
"""
from typing import List, Tuple, Dict, Set, Optional, Callable
import heapq
from collections import defaultdict


def a_star_search(graph: Dict[str, List[Tuple[str, int]]], 
                  start: str, goal: str, 
                  heuristic: Callable[[str], int]) -> Tuple[List[str], int]:
    """Find shortest path using A* algorithm.
    
    Args:
        graph: Adjacency list representation {node: [(neighbor, cost), ...]}
        start: Starting node
        goal: Goal node
        heuristic: Heuristic function h(node) -> estimated cost to goal
        
    Returns:
        Tuple of (path, total_cost) or ([], float('inf')) if no path
        
    Time Complexity: O(b^d) where b is branching factor, d is depth
    Space Complexity: O(b^d)
    """
    if start not in graph or goal not in graph:
        return [], float('inf')
    
    # Priority queue: (f_score, g_score, node, path)
    open_set = [(heuristic(start), 0, start, [start])]
    closed_set = set()
    g_score = {start: 0}
    
    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
            
        if current == goal:
            return path, g
            
        closed_set.add(current)
        
        for neighbor, cost in graph.get(current, []):
            if neighbor in closed_set:
                continue
                
            tentative_g = g + cost
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(open_set, (f_score, tentative_g, neighbor, path + [neighbor]))
    
    return [], float('inf')


def floyd_warshall(graph: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
    """Find all-pairs shortest paths using Floyd-Warshall algorithm.
    
    Args:
        graph: Adjacency matrix as nested dict {u: {v: weight}}
        
    Returns:
        Distance matrix with shortest paths between all pairs
        
    Time Complexity: O(V³)
    Space Complexity: O(V²)
    """
    nodes = list(graph.keys())
    dist = {}
    
    # Initialize distance matrix
    for u in nodes:
        dist[u] = {}
        for v in nodes:
            if u == v:
                dist[u][v] = 0
            elif v in graph[u]:
                dist[u][v] = graph[u][v]
            else:
                dist[u][v] = float('inf')
    
    # Floyd-Warshall main loop
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    return dist


def ford_fulkerson_max_flow(graph: Dict[str, Dict[str, int]], 
                           source: str, sink: str) -> int:
    """Find maximum flow using Ford-Fulkerson algorithm with DFS.
    
    Args:
        graph: Capacity matrix {u: {v: capacity}}
        source: Source node
        sink: Sink node
        
    Returns:
        Maximum flow value
        
    Time Complexity: O(E * max_flow)
    Space Complexity: O(V²)
    """
    # Create residual graph
    residual = defaultdict(lambda: defaultdict(int))
    for u in graph:
        for v, capacity in graph[u].items():
            residual[u][v] = capacity
    
    def dfs_find_path(current: str, sink: str, visited: Set[str], 
                      path: List[str], min_capacity: int) -> Tuple[List[str], int]:
        if current == sink:
            return path, min_capacity
            
        visited.add(current)
        
        for neighbor in residual[current]:
            if neighbor not in visited and residual[current][neighbor] > 0:
                new_min = min(min_capacity, residual[current][neighbor])
                result_path, result_flow = dfs_find_path(
                    neighbor, sink, visited, path + [neighbor], new_min
                )
                if result_path:
                    return result_path, result_flow
        
        return [], 0
    
    max_flow = 0
    
    while True:
        # Find augmenting path
        path, flow = dfs_find_path(source, sink, set(), [source], float('inf'))
        
        if not path or flow == 0:
            break
            
        # Update residual capacities
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual[u][v] -= flow
            residual[v][u] += flow
        
        max_flow += flow
    
    return max_flow


def tarjan_scc(graph: Dict[str, List[str]]) -> List[List[str]]:
    """Find strongly connected components using Tarjan's algorithm.
    
    Args:
        graph: Directed graph as adjacency list
        
    Returns:
        List of strongly connected components
        
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    sccs = []
    
    def strongconnect(node: str) -> None:
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack[node] = True
        
        for neighbor in graph.get(node, []):
            if neighbor not in index:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif on_stack[neighbor]:
                lowlinks[node] = min(lowlinks[node], index[neighbor])
        
        # If node is a root node, pop the stack and create SCC
        if lowlinks[node] == index[node]:
            component = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                component.append(w)
                if w == node:
                    break
            sccs.append(component)
    
    for node in graph:
        if node not in index:
            strongconnect(node)
    
    return sccs


def johnson_all_pairs_shortest_path(graph: Dict[str, List[Tuple[str, int]]]) -> Dict[str, Dict[str, int]]:
    """Find all-pairs shortest paths using Johnson's algorithm.
    
    Args:
        graph: Adjacency list {u: [(v, weight), ...]}
        
    Returns:
        Distance matrix with shortest paths between all pairs
        
    Time Complexity: O(V² log V + VE)
    Space Complexity: O(V²)
    """
    nodes = list(graph.keys())
    
    # Step 1: Add new vertex connected to all vertices with weight 0
    extended_graph = dict(graph)
    new_vertex = '__temp__'
    extended_graph[new_vertex] = [(node, 0) for node in nodes]
    
    # Step 2: Run Bellman-Ford from new vertex
    def bellman_ford(source: str) -> Dict[str, int]:
        dist = {node: float('inf') for node in extended_graph}
        dist[source] = 0
        
        # Relax edges V-1 times
        for _ in range(len(extended_graph) - 1):
            for u in extended_graph:
                for v, weight in extended_graph[u]:
                    if dist[u] + weight < dist[v]:
                        dist[v] = dist[u] + weight
        
        # Check for negative cycles
        for u in extended_graph:
            for v, weight in extended_graph[u]:
                if dist[u] + weight < dist[v]:
                    raise ValueError("Graph contains negative cycle")
        
        return dist
    
    h = bellman_ford(new_vertex)
    
    # Step 3: Reweight edges
    reweighted_graph = {}
    for u in nodes:
        reweighted_graph[u] = []
        for v, weight in graph.get(u, []):
            new_weight = weight + h[u] - h[v]
            reweighted_graph[u].append((v, new_weight))
    
    # Step 4: Run Dijkstra from each vertex
    def dijkstra(source: str) -> Dict[str, int]:
        dist = {node: float('inf') for node in nodes}
        dist[source] = 0
        pq = [(0, source)]
        visited = set()
        
        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)
            
            for v, weight in reweighted_graph.get(u, []):
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    heapq.heappush(pq, (dist[v], v))
        
        return dist
    
    # Step 5: Compute final distances
    result = {}
    for u in nodes:
        result[u] = {}
        dist_from_u = dijkstra(u)
        for v in nodes:
            if dist_from_u[v] == float('inf'):
                result[u][v] = float('inf')
            else:
                result[u][v] = dist_from_u[v] - h[u] + h[v]
    
    return result