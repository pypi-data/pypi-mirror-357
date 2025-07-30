"""
Optimization patterns and complexity analysis for AlgoZen.

This module provides various optimization techniques and algorithmic patterns.
"""
from typing import List, Tuple, Dict, Callable, Any
from functools import lru_cache
import heapq
from collections import defaultdict


def ternary_search(f: Callable[[float], float], left: float, right: float, eps: float = 1e-9) -> float:
    """Find minimum of unimodal function using ternary search.
    
    Time Complexity: O(log((right-left)/eps))
    Space Complexity: O(1)
    """
    while right - left > eps:
        m1 = left + (right - left) / 3
        m2 = right - (right - left) / 3
        
        if f(m1) > f(m2):
            left = m1
        else:
            right = m2
    
    return (left + right) / 2


def parallel_binary_search(queries: List[Tuple[int, int]], check_function: Callable) -> List[int]:
    """Solve multiple binary search queries in parallel.
    
    Time Complexity: O(q * log(max_answer) * log(q))
    Space Complexity: O(q)
    """
    q = len(queries)
    left = [0] * q
    right = [10**9] * q  # Adjust based on problem
    answers = [-1] * q
    
    for _ in range(60):  # log2(10^9) iterations
        mid_queries = defaultdict(list)
        
        for i in range(q):
            if left[i] <= right[i]:
                mid = (left[i] + right[i]) // 2
                mid_queries[mid].append(i)
        
        if not mid_queries:
            break
        
        # Process all queries with same mid value together
        for mid, query_indices in mid_queries.items():
            results = check_function(mid, [queries[i] for i in query_indices])
            
            for idx, result in zip(query_indices, results):
                if result:
                    answers[idx] = mid
                    right[idx] = mid - 1
                else:
                    left[idx] = mid + 1
    
    return answers


def meet_in_the_middle(arr: List[int], target: int) -> bool:
    """Check if subset sum equals target using meet-in-the-middle.
    
    Time Complexity: O(2^(n/2) * n/2)
    Space Complexity: O(2^(n/2))
    """
    n = len(arr)
    mid = n // 2
    
    def generate_sums(start: int, end: int) -> List[int]:
        sums = []
        for mask in range(1 << (end - start)):
            current_sum = 0
            for i in range(end - start):
                if mask & (1 << i):
                    current_sum += arr[start + i]
            sums.append(current_sum)
        return sorted(sums)
    
    left_sums = generate_sums(0, mid)
    right_sums = generate_sums(mid, n)
    
    # Two pointers to find complementary sums
    i, j = 0, len(right_sums) - 1
    
    while i < len(left_sums) and j >= 0:
        current_sum = left_sums[i] + right_sums[j]
        if current_sum == target:
            return True
        elif current_sum < target:
            i += 1
        else:
            j -= 1
    
    return False


def branch_and_bound_tsp(dist_matrix: List[List[int]]) -> Tuple[int, List[int]]:
    """Solve TSP using branch and bound.
    
    Time Complexity: O(n! * n) worst case, much better in practice
    Space Complexity: O(n)
    """
    n = len(dist_matrix)
    
    def calculate_bound(path: List[int], visited: List[bool]) -> int:
        bound = 0
        
        # Add cost of current path
        for i in range(len(path) - 1):
            bound += dist_matrix[path[i]][path[i + 1]]
        
        # Add minimum outgoing edge for each unvisited vertex
        for i in range(n):
            if not visited[i]:
                min_edge = min(dist_matrix[i][j] for j in range(n) if i != j)
                bound += min_edge
        
        return bound
    
    best_cost = float('inf')
    best_path = []
    
    def branch_and_bound(path: List[int], visited: List[bool], current_cost: int):
        nonlocal best_cost, best_path
        
        if len(path) == n:
            # Complete tour
            total_cost = current_cost + dist_matrix[path[-1]][path[0]]
            if total_cost < best_cost:
                best_cost = total_cost
                best_path = path[:]
            return
        
        # Pruning: if bound exceeds best known solution
        bound = calculate_bound(path, visited)
        if bound >= best_cost:
            return
        
        # Branch on unvisited cities
        for next_city in range(n):
            if not visited[next_city]:
                visited[next_city] = True
                path.append(next_city)
                
                new_cost = current_cost + dist_matrix[path[-2]][next_city]
                branch_and_bound(path, visited, new_cost)
                
                path.pop()
                visited[next_city] = False
    
    # Start from city 0
    visited = [False] * n
    visited[0] = True
    branch_and_bound([0], visited, 0)
    
    return best_cost, best_path


def simulated_annealing(initial_solution: Any, cost_function: Callable, 
                       neighbor_function: Callable, max_iterations: int = 10000) -> Any:
    """Generic simulated annealing optimization.
    
    Time Complexity: O(max_iterations * neighbor_cost)
    Space Complexity: O(solution_size)
    """
    import random
    import math
    
    current_solution = initial_solution
    current_cost = cost_function(current_solution)
    best_solution = current_solution
    best_cost = current_cost
    
    temperature = 1000.0
    cooling_rate = 0.995
    
    for iteration in range(max_iterations):
        # Generate neighbor solution
        neighbor = neighbor_function(current_solution)
        neighbor_cost = cost_function(neighbor)
        
        # Accept or reject neighbor
        if neighbor_cost < current_cost:
            current_solution = neighbor
            current_cost = neighbor_cost
            
            if current_cost < best_cost:
                best_solution = current_solution
                best_cost = current_cost
        else:
            # Accept worse solution with probability
            delta = neighbor_cost - current_cost
            probability = math.exp(-delta / temperature)
            
            if random.random() < probability:
                current_solution = neighbor
                current_cost = neighbor_cost
        
        # Cool down
        temperature *= cooling_rate
    
    return best_solution


def genetic_algorithm(population_size: int, chromosome_length: int,
                     fitness_function: Callable, max_generations: int = 1000) -> Any:
    """Generic genetic algorithm optimization.
    
    Time Complexity: O(max_generations * population_size * fitness_cost)
    Space Complexity: O(population_size * chromosome_length)
    """
    import random
    
    def create_individual():
        return [random.randint(0, 1) for _ in range(chromosome_length)]
    
    def crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        crossover_point = random.randint(1, chromosome_length - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2
    
    def mutate(individual: List[int], mutation_rate: float = 0.01):
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual[i] = 1 - individual[i]
        return individual
    
    # Initialize population
    population = [create_individual() for _ in range(population_size)]
    
    for generation in range(max_generations):
        # Evaluate fitness
        fitness_scores = [(fitness_function(individual), individual) 
                         for individual in population]
        fitness_scores.sort(reverse=True)
        
        # Selection (top 50%)
        survivors = [individual for _, individual in fitness_scores[:population_size // 2]]
        
        # Create new generation
        new_population = survivors[:]
        
        while len(new_population) < population_size:
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            child1, child2 = crossover(parent1, parent2)
            
            new_population.append(mutate(child1))
            if len(new_population) < population_size:
                new_population.append(mutate(child2))
        
        population = new_population
    
    # Return best individual
    final_fitness = [(fitness_function(individual), individual) for individual in population]
    return max(final_fitness)[1]


def memoization_decorator(func: Callable) -> Callable:
    """Generic memoization decorator for dynamic programming.
    
    Time Complexity: Depends on subproblems
    Space Complexity: O(number of unique subproblems)
    """
    cache = {}
    
    def wrapper(*args, **kwargs):
        # Create hashable key
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    wrapper.cache = cache
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper


def iterative_deepening_search(start_state: Any, goal_test: Callable,
                              successor_function: Callable, max_depth: int = 100) -> List[Any]:
    """Iterative deepening depth-first search.
    
    Time Complexity: O(b^d) where b is branching factor, d is depth
    Space Complexity: O(d)
    """
    def depth_limited_search(state: Any, depth: int, path: List[Any]) -> List[Any]:
        if goal_test(state):
            return path + [state]
        
        if depth == 0:
            return None
        
        for successor in successor_function(state):
            if successor not in path:  # Avoid cycles
                result = depth_limited_search(successor, depth - 1, path + [state])
                if result is not None:
                    return result
        
        return None
    
    for depth in range(max_depth + 1):
        result = depth_limited_search(start_state, depth, [])
        if result is not None:
            return result
    
    return None


def approximation_algorithm_vertex_cover(edges: List[Tuple[int, int]], n: int) -> List[int]:
    """2-approximation algorithm for minimum vertex cover.
    
    Time Complexity: O(E)
    Space Complexity: O(V)
    """
    vertex_cover = set()
    remaining_edges = set(edges)
    
    while remaining_edges:
        # Pick any edge
        u, v = remaining_edges.pop()
        
        # Add both vertices to cover
        vertex_cover.add(u)
        vertex_cover.add(v)
        
        # Remove all edges incident to u or v
        to_remove = []
        for edge in remaining_edges:
            if edge[0] == u or edge[0] == v or edge[1] == u or edge[1] == v:
                to_remove.append(edge)
        
        for edge in to_remove:
            remaining_edges.discard(edge)
    
    return list(vertex_cover)


def randomized_quicksort(arr: List[int]) -> List[int]:
    """Randomized quicksort with expected O(n log n) time.
    
    Time Complexity: O(n log n) expected, O(n²) worst case
    Space Complexity: O(log n) expected
    """
    import random
    
    def partition(arr: List[int], low: int, high: int) -> int:
        # Random pivot
        pivot_idx = random.randint(low, high)
        arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
        
        pivot = arr[high]
        i = low - 1
        
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def quicksort_helper(arr: List[int], low: int, high: int):
        if low < high:
            pi = partition(arr, low, high)
            quicksort_helper(arr, low, pi - 1)
            quicksort_helper(arr, pi + 1, high)
    
    result = arr[:]
    quicksort_helper(result, 0, len(result) - 1)
    return result