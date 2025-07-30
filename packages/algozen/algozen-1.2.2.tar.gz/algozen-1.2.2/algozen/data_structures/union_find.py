"""
Union-Find (Disjoint Set Union) implementation for AlgoZen.

Union-Find is a data structure that keeps track of elements partitioned into
disjoint sets. It supports union and find operations efficiently.
"""
from typing import Dict, List, Optional, TypeVar

T = TypeVar('T')


class UnionFind:
    """Union-Find data structure with path compression and union by rank."""
    
    def __init__(self, n: int) -> None:
        """Initialize Union-Find with n elements (0 to n-1).
        
        Args:
            n: Number of elements
            
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        self.parent = list(range(n))
        self.rank = [0] * n
        self.size = [1] * n
        self.components = n
    
    def find(self, x: int) -> int:
        """Find the root of element x with path compression.
        
        Args:
            x: Element to find root for
            
        Returns:
            Root of the set containing x
            
        Time Complexity: O(α(n)) amortized, where α is inverse Ackermann
        Space Complexity: O(1)
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """Union two sets containing x and y.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            True if union was performed, False if already in same set
            
        Time Complexity: O(α(n)) amortized
        Space Complexity: O(1)
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False
        
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x
        
        self.parent[root_y] = root_x
        self.size[root_x] += self.size[root_y]
        
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1
        
        self.components -= 1
        return True
    
    def connected(self, x: int, y: int) -> bool:
        """Check if two elements are in the same set.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            True if x and y are connected, False otherwise
            
        Time Complexity: O(α(n)) amortized
        Space Complexity: O(1)
        """
        return self.find(x) == self.find(y)
    
    def get_size(self, x: int) -> int:
        """Get the size of the set containing x.
        
        Args:
            x: Element to get set size for
            
        Returns:
            Size of the set containing x
            
        Time Complexity: O(α(n)) amortized
        Space Complexity: O(1)
        """
        return self.size[self.find(x)]
    
    def count_components(self) -> int:
        """Get the number of disjoint components.
        
        Returns:
            Number of connected components
            
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        return self.components
    
    def get_components(self) -> Dict[int, List[int]]:
        """Get all components as a dictionary.
        
        Returns:
            Dictionary mapping root to list of elements in that component
            
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        components = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            if root not in components:
                components[root] = []
            components[root].append(i)
        return components


class WeightedUnionFind:
    """Weighted Union-Find for maintaining relative weights/distances."""
    
    def __init__(self, n: int) -> None:
        """Initialize Weighted Union-Find with n elements.
        
        Args:
            n: Number of elements
        """
        self.parent = list(range(n))
        self.weight = [0] * n  # weight[i] = weight from i to parent[i]
        self.rank = [0] * n
    
    def find(self, x: int) -> int:
        """Find root with path compression and weight update.
        
        Args:
            x: Element to find root for
            
        Returns:
            Root of the set containing x
        """
        if self.parent[x] != x:
            root = self.find(self.parent[x])
            self.weight[x] += self.weight[self.parent[x]]
            self.parent[x] = root
        return self.parent[x]
    
    def union(self, x: int, y: int, w: int) -> bool:
        """Union with constraint: weight[y] - weight[x] = w.
        
        Args:
            x: First element
            y: Second element  
            w: Weight difference (weight[y] - weight[x])
            
        Returns:
            True if union was successful, False if constraint conflicts
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return self.weight[y] - self.weight[x] == w
        
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
            self.weight[root_x] = self.weight[y] - self.weight[x] - w
        else:
            self.parent[root_y] = root_x
            self.weight[root_y] = self.weight[x] - self.weight[y] + w
            if self.rank[root_x] == self.rank[root_y]:
                self.rank[root_x] += 1
        
        return True
    
    def diff(self, x: int, y: int) -> Optional[int]:
        """Get weight difference between x and y.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            weight[y] - weight[x] if connected, None otherwise
        """
        if self.find(x) != self.find(y):
            return None
        return self.weight[y] - self.weight[x]