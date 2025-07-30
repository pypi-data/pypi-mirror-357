"""
Advanced graph patterns for AlgoZen.

This module provides various advanced graph algorithmic patterns.
"""
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, deque
import heapq


def bipartite_matching(graph: Dict[int, List[int]]) -> int:
    """Find maximum bipartite matching using DFS.
    
    Time Complexity: O(VE)
    Space Complexity: O(V)
    """
    match = {}
    
    def dfs(u: int, visited: Set[int]) -> bool:
        for v in graph.get(u, []):
            if v in visited:
                continue
            visited.add(v)
            
            if v not in match or dfs(match[v], visited):
                match[v] = u
                return True
        return False
    
    matching = 0
    for u in graph:
        if dfs(u, set()):
            matching += 1
    
    return matching


def network_delay_time(times: List[List[int]], n: int, k: int) -> int:
    """Find minimum time for signal to reach all nodes.
    
    Time Complexity: O(E log V)
    Space Complexity: O(V + E)
    """
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    
    dist = {i: float('inf') for i in range(1, n + 1)}
    dist[k] = 0
    
    pq = [(0, k)]
    
    while pq:
        d, u = heapq.heappop(pq)
        
        if d > dist[u]:
            continue
            
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    
    max_dist = max(dist.values())
    return max_dist if max_dist != float('inf') else -1


def course_schedule_order(num_courses: int, prerequisites: List[List[int]]) -> List[int]:
    """Find valid course order using topological sort.
    
    Time Complexity: O(V + E)
    Space Complexity: O(V + E)
    """
    graph = defaultdict(list)
    in_degree = [0] * num_courses
    
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1
    
    queue = deque([i for i in range(num_courses) if in_degree[i] == 0])
    order = []
    
    while queue:
        course = queue.popleft()
        order.append(course)
        
        for next_course in graph[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)
    
    return order if len(order) == num_courses else []


def alien_dictionary(words: List[str]) -> str:
    """Find alien dictionary order using topological sort.
    
    Time Complexity: O(C) where C is total characters
    Space Complexity: O(1) for English alphabet
    """
    graph = defaultdict(set)
    in_degree = defaultdict(int)
    
    # Initialize in_degree for all characters
    for word in words:
        for char in word:
            in_degree[char] = 0
    
    # Build graph
    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i + 1]
        min_len = min(len(word1), len(word2))
        
        for j in range(min_len):
            if word1[j] != word2[j]:
                if word2[j] not in graph[word1[j]]:
                    graph[word1[j]].add(word2[j])
                    in_degree[word2[j]] += 1
                break
        else:
            # word1 is prefix of word2, but word1 is longer
            if len(word1) > len(word2):
                return ""
    
    # Topological sort
    queue = deque([char for char in in_degree if in_degree[char] == 0])
    result = []
    
    while queue:
        char = queue.popleft()
        result.append(char)
        
        for neighbor in graph[char]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return ''.join(result) if len(result) == len(in_degree) else ""


def critical_connections(n: int, connections: List[List[int]]) -> List[List[int]]:
    """Find critical connections (bridges) in network.
    
    Time Complexity: O(V + E)
    Space Complexity: O(V + E)
    """
    graph = defaultdict(list)
    for u, v in connections:
        graph[u].append(v)
        graph[v].append(u)
    
    visited = [False] * n
    disc = [0] * n
    low = [0] * n
    parent = [-1] * n
    bridges = []
    time = [0]
    
    def bridge_dfs(u):
        visited[u] = True
        disc[u] = low[u] = time[0]
        time[0] += 1
        
        for v in graph[u]:
            if not visited[v]:
                parent[v] = u
                bridge_dfs(v)
                
                low[u] = min(low[u], low[v])
                
                if low[v] > disc[u]:
                    bridges.append([u, v])
            elif v != parent[u]:
                low[u] = min(low[u], disc[v])
    
    for i in range(n):
        if not visited[i]:
            bridge_dfs(i)
    
    return bridges


def shortest_path_all_keys(grid: List[str]) -> int:
    """Find shortest path to collect all keys.
    
    Time Complexity: O(mn * 2^k) where k is number of keys
    Space Complexity: O(mn * 2^k)
    """
    m, n = len(grid), len(grid[0])
    start = None
    key_count = 0
    
    for i in range(m):
        for j in range(n):
            if grid[i][j] == '@':
                start = (i, j)
            elif grid[i][j].islower():
                key_count += 1
    
    target_keys = (1 << key_count) - 1
    queue = deque([(start[0], start[1], 0, 0)])  # row, col, keys, steps
    visited = set()
    visited.add((start[0], start[1], 0))
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    while queue:
        row, col, keys, steps = queue.popleft()
        
        if keys == target_keys:
            return steps
        
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            
            if 0 <= nr < m and 0 <= nc < n:
                cell = grid[nr][nc]
                
                if cell == '#':
                    continue
                
                new_keys = keys
                
                if cell.islower():
                    new_keys |= 1 << (ord(cell) - ord('a'))
                elif cell.isupper():
                    if not (keys & (1 << (ord(cell) - ord('A')))):
                        continue
                
                if (nr, nc, new_keys) not in visited:
                    visited.add((nr, nc, new_keys))
                    queue.append((nr, nc, new_keys, steps + 1))
    
    return -1


def minimum_cost_connect_points(points: List[List[int]]) -> int:
    """Find minimum cost to connect all points (MST).
    
    Time Complexity: O(n² log n)
    Space Complexity: O(n²)
    """
    n = len(points)
    
    def manhattan_distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    
    # Prim's algorithm
    visited = [False] * n
    min_heap = [(0, 0)]  # (cost, point_index)
    total_cost = 0
    
    while min_heap:
        cost, u = heapq.heappop(min_heap)
        
        if visited[u]:
            continue
        
        visited[u] = True
        total_cost += cost
        
        for v in range(n):
            if not visited[v]:
                dist = manhattan_distance(points[u], points[v])
                heapq.heappush(min_heap, (dist, v))
    
    return total_cost


def accounts_merge(accounts: List[List[str]]) -> List[List[str]]:
    """Merge accounts with common emails using Union-Find.
    
    Time Complexity: O(n * α(n))
    Space Complexity: O(n)
    """
    parent = {}
    
    def find(x):
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    email_to_name = {}
    
    for account in accounts:
        name = account[0]
        emails = account[1:]
        
        for email in emails:
            email_to_name[email] = name
            if len(emails) > 1:
                union(emails[0], email)
    
    groups = defaultdict(list)
    for email in email_to_name:
        groups[find(email)].append(email)
    
    result = []
    for emails in groups.values():
        name = email_to_name[emails[0]]
        result.append([name] + sorted(emails))
    
    return result


def word_ladder_length(begin_word: str, end_word: str, word_list: List[str]) -> int:
    """Find shortest transformation sequence length.
    
    Time Complexity: O(M² * N) where M is word length, N is word count
    Space Complexity: O(M² * N)
    """
    if end_word not in word_list:
        return 0
    
    word_set = set(word_list)
    queue = deque([(begin_word, 1)])
    visited = {begin_word}
    
    while queue:
        word, length = queue.popleft()
        
        if word == end_word:
            return length
        
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                new_word = word[:i] + c + word[i+1:]
                
                if new_word in word_set and new_word not in visited:
                    visited.add(new_word)
                    queue.append((new_word, length + 1))
    
    return 0