"""
Strategy Pattern Implementation.

This module provides an implementation of the Strategy pattern, which defines
a family of algorithms, encapsulates each one, and makes them interchangeable.
Strategy lets the algorithm vary independently from clients that use it.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Dict, TypeVar, Generic, Optional
import json

T = TypeVar('T')

class SortStrategy(ABC):
    """
    The Strategy interface declares operations common to all supported versions
    of some algorithm. The Context uses this interface to call the algorithm
    defined by Concrete Strategies.
    """
    @abstractmethod
    def sort(self, data: List[Any]) -> List[Any]:
        """
        Execute the sorting algorithm on the given data.
        
        Args:
            data: The list of items to be sorted.
            
        Returns:
            A new list containing the sorted items.
        """
        pass

class BubbleSortStrategy(SortStrategy):
    """
    Concrete strategy that implements bubble sort algorithm.
    """
    def sort(self, data: List[Any]) -> List[Any]:
        """
        Sort the data using bubble sort algorithm.
        
        Time Complexity: O(n²) in worst and average case, O(n) in best case.
        Space Complexity: O(1) as it's an in-place sorting algorithm.
        """
        items = data.copy()
        n = len(items)
        for i in range(n):
            swapped = False
            for j in range(0, n-i-1):
                if items[j] > items[j+1]:
                    items[j], items[j+1] = items[j+1], items[j]
                    swapped = True
            if not swapped:
                break
        return items

class QuickSortStrategy(SortStrategy):
    """
    Concrete strategy that implements quicksort algorithm.
    """
    def sort(self, data: List[Any]) -> List[Any]:
        """
        Sort the data using quicksort algorithm.
        
        Time Complexity: O(n log n) in average case, O(n²) in worst case.
        Space Complexity: O(log n) due to recursion stack.
        """
        if len(data) <= 1:
            return data.copy()
        
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        
        return self.sort(left) + middle + self.sort(right)

class Context:
    """
    The Context defines the interface of interest to clients.
    """
    def __init__(self, strategy: Optional[SortStrategy] = None) -> None:
        """
        Initialize the context with a strategy.
        
        Args:
            strategy: The sorting strategy to use. If None, defaults to QuickSortStrategy.
        """
        self._strategy = strategy or QuickSortStrategy()
    
    @property
    def strategy(self) -> SortStrategy:
        """
        Get the current strategy.
        
        Returns:
            The current sorting strategy.
        """
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: SortStrategy) -> None:
        """
        Set a new strategy at runtime.
        
        Args:
            strategy: The new sorting strategy to use.
        """
        self._strategy = strategy
    
    def sort_data(self, data: List[Any]) -> List[Any]:
        """
        Sort the data using the current strategy.
        
        Args:
            data: The list of items to be sorted.
            
        Returns:
            A new list containing the sorted items.
        """
        return self._strategy.sort(data)

class DataExporter(ABC):
    """
    The Strategy interface for data export strategies.
    """
    @abstractmethod
    def export(self, data: Any) -> str:
        """
        Export the data in a specific format.
        
        Args:
            data: The data to be exported.
            
        Returns:
            A string representation of the exported data.
        """
        pass

class JSONExporter(DataExporter):
    """
    Concrete strategy that exports data in JSON format.
    """
    def export(self, data: Any) -> str:
        """
        Export data in JSON format.
        
        Args:
            data: The data to be exported (must be JSON serializable).
            
        Returns:
            A JSON string representation of the data.
            
        Raises:
            TypeError: If the data is not JSON serializable.
        """
        return json.dumps(data, indent=2)

class CSVExporter(DataExporter):
    """
    Concrete strategy that exports data in CSV format.
    """
    def export(self, data: List[Dict[str, Any]]) -> str:
        """
        Export data in CSV format.
        
        Args:
            data: A list of dictionaries where each dictionary represents a row.
            
        Returns:
            A CSV string representation of the data.
            
        Raises:
            ValueError: If the data is not a list of dictionaries with the same keys.
        """
        if not data:
            return ""
            
        if not all(isinstance(row, dict) for row in data):
            raise ValueError("All items in data must be dictionaries")
            
        # Get all unique keys from all dictionaries
        keys = set()
        for row in data:
            keys.update(row.keys())
        keys = sorted(keys)
        
        # Create CSV header
        result = [",".join(keys)]
        
        # Add rows
        for row in data:
            row_values = []
            for key in keys:
                value = str(row.get(key, "")).replace('"', '""')  # Escape double quotes
                # If value contains comma, newline, or double quote, wrap in quotes
                if any(c in value for c in ',\n\r"'):
                    value = f'"{value}"'
                row_values.append(value)
            result.append(",".join(row_values))
            
        return "\n".join(result)

# Aliases for backward compatibility
ConcreteStrategyA = BubbleSortStrategy
ConcreteStrategyB = QuickSortStrategy
