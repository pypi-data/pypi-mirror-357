"""
Graph implementation for AlgoZen.

A graph is a non-linear data structure consisting of nodes (vertices) and edges.
This implementation supports both directed and undirected graphs.
"""
from typing import TypeVar, Generic, Dict, List, Set, Optional, Any, Tuple, Union
from collections import defaultdict

T = TypeVar('T')

class Edge(Generic[T]):
    """Edge class for Graph implementation.
    
    Attributes:
        source: The source vertex of the edge
        destination: The destination vertex of the edge
        weight: The weight of the edge (default: 1)
    """
    
    def __init__(self, source: T, destination: T, weight: Union[int, float] = 1) -> None:
        self.source = source
        self.destination = destination
        self.weight = weight
    
    def __repr__(self) -> str:
        if self.weight == 1:
            return f"{self.source} -> {self.destination}"
        return f"{self.source} -[{self.weight}]-> {self.destination}"
    
    def __lt__(self, other: 'Edge[T]') -> bool:
        return self.weight < other.weight


class Graph(Generic[T]):
    """Graph implementation using adjacency list representation."""
    
    def __init__(self, directed: bool = False) -> None:
        """Initialize a graph.
        
        Args:
            directed: Whether the graph is directed (default: False)
        """
        self.adjacency_list: Dict[T, List[Edge[T]]] = defaultdict(list)
        self.vertices: Set[T] = set()
        self.directed = directed
        self._edge_count = 0
    
    def add_vertex(self, vertex: T) -> None:
        """Add a vertex to the graph.
        
        Args:
            vertex: The vertex to add
        """
        if vertex not in self.vertices:
            self.vertices.add(vertex)
            self.adjacency_list[vertex] = []
    
    def add_edge(self, source: T, destination: T, weight: Union[int, float] = 1) -> None:
        """Add an edge to the graph.
        
        Args:
            source: The source vertex
            destination: The destination vertex
            weight: The weight of the edge (default: 1)
        """
        self.add_vertex(source)
        self.add_vertex(destination)
        
        edge = Edge(source, destination, weight)
        self.adjacency_list[source].append(edge)
        
        if not self.directed:
            reverse_edge = Edge(destination, source, weight)
            self.adjacency_list[destination].append(reverse_edge)
        
        self._edge_count += 1
    
    def remove_edge(self, source: T, destination: T) -> None:
        """Remove an edge from the graph.
        
        Args:
            source: The source vertex of the edge to remove
            destination: The destination vertex of the edge to remove
            
        Raises:
            ValueError: If the edge does not exist
        """
        if source not in self.vertices or destination not in self.vertices:
            raise ValueError("One or both vertices not in the graph")
        
        # Remove source -> destination edge
        removed = False
        for i, edge in enumerate(self.adjacency_list[source]):
            if edge.destination == destination:
                self.adjacency_list[source].pop(i)
                removed = True
                self._edge_count -= 1
                break
        
        if not removed:
            raise ValueError(f"Edge {source} -> {destination} not found in the graph")
        
        # For undirected graphs, also remove the reverse edge
        if not self.directed:
            for i, edge in enumerate(self.adjacency_list[destination]):
                if edge.destination == source:
                    self.adjacency_list[destination].pop(i)
                    break
    
    def remove_vertex(self, vertex: T) -> None:
        """Remove a vertex and all its incident edges from the graph.
        
        Args:
            vertex: The vertex to remove
            
        Raises:
            ValueError: If the vertex is not in the graph
        """
        if vertex not in self.vertices:
            raise ValueError(f"Vertex {vertex} not in the graph")
        
        # Remove all edges to this vertex
        for v in self.vertices:
            if v != vertex:
                self.adjacency_list[v] = [
                    edge for edge in self.adjacency_list[v] 
                    if edge.destination != vertex
                ]
        
        # Remove the vertex and its adjacency list
        self._edge_count -= len(self.adjacency_list[vertex])
        del self.adjacency_list[vertex]
        self.vertices.remove(vertex)
    
    def get_vertices(self) -> List[T]:
        """Get all vertices in the graph.
        
        Returns:
            List of all vertices in the graph
        """
        return list(self.vertices)
    
    def get_edges(self) -> List[Edge[T]]:
        """Get all edges in the graph.
        
        For undirected graphs, each edge is included only once.
        
        Returns:
            List of all edges in the graph
        """
        edges = []
        for vertex in self.vertices:
            edges.extend(self.adjacency_list[vertex])
        
        if not self.directed:
            # For undirected graphs, we only need to include each edge once
            seen = set()
            unique_edges = []
            for edge in edges:
                if (edge.source, edge.destination) not in seen and \
                   (edge.destination, edge.source) not in seen:
                    unique_edges.append(edge)
                    seen.add((edge.source, edge.destination))
            return unique_edges
        
        return edges
    
    def get_neighbors(self, vertex: T) -> List[T]:
        """Get all neighbors of a vertex.
        
        Args:
            vertex: The vertex to get neighbors for
            
        Returns:
            List of neighboring vertices
            
        Raises:
            ValueError: If the vertex is not in the graph
        """
        if vertex not in self.vertices:
            raise ValueError(f"Vertex {vertex} not in the graph")
        
        return [edge.destination for edge in self.adjacency_list[vertex]]
    
    def get_edge_weight(self, source: T, destination: T) -> Union[int, float]:
        """Get the weight of the edge between two vertices.
        
        Args:
            source: The source vertex
            destination: The destination vertex
            
        Returns:
            The weight of the edge, or infinity if no edge exists
            
        Raises:
            ValueError: If either vertex is not in the graph
        """
        if source not in self.vertices or destination not in self.vertices:
            raise ValueError("One or both vertices not in the graph")
        
        for edge in self.adjacency_list[source]:
            if edge.destination == destination:
                return edge.weight
        
        return float('inf')
    
    def has_vertex(self, vertex: T) -> bool:
        """Check if a vertex exists in the graph.
        
        Args:
            vertex: The vertex to check
            
        Returns:
            bool: True if the vertex exists, False otherwise
        """
        return vertex in self.vertices
    
    def has_edge(self, source: T, destination: T) -> bool:
        """Check if an edge exists between two vertices.
        
        Args:
            source: The source vertex
            destination: The destination vertex
            
        Returns:
            bool: True if the edge exists, False otherwise
        """
        if not self.has_vertex(source) or not self.has_vertex(destination):
            return False
        
        for edge in self.adjacency_list[source]:
            if edge.destination == destination:
                return True
        
        return False
    
    def vertex_count(self) -> int:
        """Get the number of vertices in the graph.
        
        Returns:
            int: The number of vertices
        """
        return len(self.vertices)
    
    def edge_count(self) -> int:
        """Get the number of edges in the graph.
        
        For undirected graphs, each edge is counted only once.
        
        Returns:
            int: The number of edges
        """
        if self.directed:
            return self._edge_count
        return self._edge_count // 2
    
    def is_directed(self) -> bool:
        """Check if the graph is directed.
        
        Returns:
            bool: True if the graph is directed, False otherwise
        """
        return self.directed
    
    def degree(self, vertex: T) -> int:
        """Get the degree of a vertex (number of incident edges).
        
        For directed graphs, this returns the out-degree.
        
        Args:
            vertex: The vertex to get the degree of
            
        Returns:
            int: The degree of the vertex
            
        Raises:
            ValueError: If the vertex is not in the graph
        """
        if not self.has_vertex(vertex):
            raise ValueError(f"Vertex {vertex} not in the graph")
        
        return len(self.adjacency_list[vertex])
    
    def in_degree(self, vertex: T) -> int:
        """Get the in-degree of a vertex (number of incoming edges).
        
        For undirected graphs, this is the same as the degree.
        
        Args:
            vertex: The vertex to get the in-degree of
            
        Returns:
            int: The in-degree of the vertex
            
        Raises:
            ValueError: If the vertex is not in the graph
        """
        if not self.has_vertex(vertex):
            raise ValueError(f"Vertex {vertex} not in the graph")
        
        if not self.directed:
            return self.degree(vertex)
        
        count = 0
        for v in self.vertices:
            for edge in self.adjacency_list[v]:
                if edge.destination == vertex:
                    count += 1
        
        return count
    
    def out_degree(self, vertex: T) -> int:
        """Get the out-degree of a vertex (number of outgoing edges).
        
        For undirected graphs, this is the same as the degree.
        
        Args:
            vertex: The vertex to get the out-degree of
            
        Returns:
            int: The out-degree of the vertex
            
        Raises:
            ValueError: If the vertex is not in the graph
        """
        if not self.has_vertex(vertex):
            raise ValueError(f"Vertex {vertex} not in the graph")
        
        if not self.directed:
            return self.degree(vertex)
        
        return len(self.adjacency_list[vertex])
    
    def get_adjacency_matrix(self) -> Dict[T, Dict[T, Union[int, float]]]:
        """Get the adjacency matrix representation of the graph.
        
        Returns:
            A dictionary of dictionaries where matrix[u][v] is the weight of the edge
            from u to v, or infinity if no such edge exists.
        """
        vertices = sorted(self.vertices)
        matrix = {}
        
        for u in vertices:
            matrix[u] = {}
            for v in vertices:
                if u == v:
                    matrix[u][v] = 0
                else:
                    matrix[u][v] = self.get_edge_weight(u, v)
        
        return matrix
    
    def __str__(self) -> str:
        """Return a string representation of the graph.
        
        Returns:
            str: A string representation of the graph
        """
        result = []
        for vertex in sorted(self.vertices):
            edges = []
            for edge in self.adjacency_list[vertex]:
                if self.directed or edge.source <= edge.destination:
                    edges.append(str(edge))
            if edges:
                result.append(f"{vertex}: {', '.join(edges)}")
        return "\n".join(result)
    
    def __repr__(self) -> str:
        """Return a string representation of the graph for debugging.
        
        Returns:
            str: A string representation of the graph
        """
        return f"Graph(directed={self.directed}, vertices={self.vertex_count()}, edges={self.edge_count()})"
