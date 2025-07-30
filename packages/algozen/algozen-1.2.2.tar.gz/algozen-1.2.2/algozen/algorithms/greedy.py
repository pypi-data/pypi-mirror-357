"""
Greedy algorithms implementation for AlgoZen.

This module provides various greedy algorithm implementations.
"""
from typing import List, Tuple, Optional
import heapq


def activity_selection(activities: List[Tuple[int, int]]) -> List[int]:
    """Select maximum number of non-overlapping activities.
    
    Args:
        activities: List of (start_time, end_time) tuples
        
    Returns:
        List of indices of selected activities
        
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not activities:
        return []
    
    # Sort by end time
    indexed_activities = [(end, start, i) for i, (start, end) in enumerate(activities)]
    indexed_activities.sort()
    
    selected = [indexed_activities[0][2]]  # Select first activity
    last_end_time = indexed_activities[0][0]
    
    for end_time, start_time, index in indexed_activities[1:]:
        if start_time >= last_end_time:
            selected.append(index)
            last_end_time = end_time
    
    return selected


def fractional_knapsack(items: List[Tuple[int, int]], capacity: int) -> float:
    """Solve fractional knapsack problem.
    
    Args:
        items: List of (value, weight) tuples
        capacity: Maximum weight capacity
        
    Returns:
        Maximum value achievable
        
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not items or capacity <= 0:
        return 0.0
    
    # Sort by value-to-weight ratio in descending order
    ratios = [(value / weight, value, weight, i) for i, (value, weight) in enumerate(items)]
    ratios.sort(reverse=True)
    
    total_value = 0.0
    remaining_capacity = capacity
    
    for ratio, value, weight, _ in ratios:
        if weight <= remaining_capacity:
            # Take the whole item
            total_value += value
            remaining_capacity -= weight
        else:
            # Take fraction of the item
            total_value += ratio * remaining_capacity
            break
    
    return total_value


def job_scheduling(jobs: List[Tuple[int, int]]) -> List[int]:
    """Schedule jobs to minimize maximum lateness.
    
    Args:
        jobs: List of (processing_time, deadline) tuples
        
    Returns:
        List of job indices in optimal order
        
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not jobs:
        return []
    
    # Sort by deadline (Earliest Deadline First)
    indexed_jobs = [(deadline, processing_time, i) for i, (processing_time, deadline) in enumerate(jobs)]
    indexed_jobs.sort()
    
    return [index for _, _, index in indexed_jobs]


def huffman_coding(frequencies: List[Tuple[str, int]]) -> dict:
    """Generate Huffman codes for given character frequencies.
    
    Args:
        frequencies: List of (character, frequency) tuples
        
    Returns:
        Dictionary mapping characters to their Huffman codes
        
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not frequencies:
        return {}
    
    if len(frequencies) == 1:
        return {frequencies[0][0]: '0'}
    
    # Create min heap
    heap = []
    for char, freq in frequencies:
        heapq.heappush(heap, (freq, char))
    
    # Build Huffman tree
    node_counter = 0
    while len(heap) > 1:
        freq1, node1 = heapq.heappop(heap)
        freq2, node2 = heapq.heappop(heap)
        
        merged_freq = freq1 + freq2
        merged_node = f"internal_{node_counter}"
        node_counter += 1
        
        heapq.heappush(heap, (merged_freq, merged_node))
        
        # Store tree structure (simplified for code generation)
        if not hasattr(huffman_coding, 'tree'):
            huffman_coding.tree = {}
        huffman_coding.tree[merged_node] = (node1, node2)
    
    # Generate codes
    codes = {}
    
    def generate_codes(node: str, code: str = '') -> None:
        if node in [char for char, _ in frequencies]:
            codes[node] = code or '0'
        else:
            left, right = huffman_coding.tree[node]
            generate_codes(left, code + '0')
            generate_codes(right, code + '1')
    
    root = heap[0][1]
    generate_codes(root)
    
    return codes


def coin_change_greedy(coins: List[int], amount: int) -> List[int]:
    """Make change using greedy approach (works for canonical coin systems).
    
    Args:
        coins: List of coin denominations (sorted in descending order)
        amount: Amount to make change for
        
    Returns:
        List of coins used (may not be optimal for all coin systems)
        
    Time Complexity: O(n)
        Space Complexity: O(1)
    """
    if amount == 0:
        return []
    
    coins_sorted = sorted(coins, reverse=True)
    result = []
    
    for coin in coins_sorted:
        while amount >= coin:
            result.append(coin)
            amount -= coin
    
    return result if amount == 0 else []


def interval_scheduling(intervals: List[Tuple[int, int]]) -> List[int]:
    """Select maximum number of non-overlapping intervals.
    
    Args:
        intervals: List of (start, end) tuples
        
    Returns:
        List of indices of selected intervals
        
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not intervals:
        return []
    
    # Sort by end time
    indexed_intervals = [(end, start, i) for i, (start, end) in enumerate(intervals)]
    indexed_intervals.sort()
    
    selected = []
    last_end = float('-inf')
    
    for end, start, index in indexed_intervals:
        if start >= last_end:
            selected.append(index)
            last_end = end
    
    return selected


def minimum_spanning_tree_prim(graph: dict) -> List[Tuple[str, str, int]]:
    """Find MST using Prim's algorithm (greedy approach).
    
    Args:
        graph: Adjacency list {node: [(neighbor, weight), ...]}
        
    Returns:
        List of edges in MST as (u, v, weight) tuples
        
    Time Complexity: O(E log V)
    Space Complexity: O(V)
    """
    if not graph:
        return []
    
    # Start with arbitrary vertex
    start_vertex = next(iter(graph))
    visited = {start_vertex}
    mst_edges = []
    
    # Priority queue of edges: (weight, u, v)
    edges = []
    for neighbor, weight in graph[start_vertex]:
        heapq.heappush(edges, (weight, start_vertex, neighbor))
    
    while edges and len(visited) < len(graph):
        weight, u, v = heapq.heappop(edges)
        
        if v not in visited:
            visited.add(v)
            mst_edges.append((u, v, weight))
            
            # Add new edges from v
            for neighbor, edge_weight in graph.get(v, []):
                if neighbor not in visited:
                    heapq.heappush(edges, (edge_weight, v, neighbor))
    
    return mst_edges