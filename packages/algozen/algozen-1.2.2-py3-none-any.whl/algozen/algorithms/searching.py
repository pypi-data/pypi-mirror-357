"""
Searching algorithms implementation for AlgoZen.

This module provides various searching algorithms with consistent interfaces.
"""
from typing import List, TypeVar, Optional, Callable, Any
from functools import wraps
from .string_algorithms import kmp_search, rabin_karp_search

T = TypeVar('T', int, float, str)

def validate_input(func: Callable) -> Callable:
    """Decorator to validate input for searching functions."""
    @wraps(func)
    def wrapper(arr: List[T], *args, **kwargs) -> Any:
        if not isinstance(arr, list):
            raise TypeError("Input must be a list")
        if not arr:
            return -1
        return func(arr, *args, **kwargs)
    return wrapper

@validate_input
def linear_search(arr: List[T], target: T) -> int:
    """Search for target in a list using linear search.
    
    Args:
        arr: List of elements to search in
        target: Element to search for
        
    Returns:
        int: Index of the target if found, -1 otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    for i, item in enumerate(arr):
        if item == target:
            return i
    return -1

@validate_input
def binary_search(arr: List[T], target: T) -> int:
    """Search for target in a sorted list using binary search.
    
    Args:
        arr: Sorted list of elements to search in
        target: Element to search for
        
    Returns:
        int: Index of the target if found, -1 otherwise
        
    Time Complexity: O(log n)
    Space Complexity: O(1) for iterative, O(log n) for recursive
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        # Check if target is present at mid
        if arr[mid] == target:
            return mid
            
        # If target is greater, ignore left half
        elif arr[mid] < target:
            left = mid + 1
            
        # If target is smaller, ignore right half
        else:
            right = mid - 1
    
    # Target not found
    return -1

def interpolation_search(arr: List[int], target: int) -> int:
    """Search for target in a uniformly distributed sorted list using interpolation search.
    
    Args:
        arr: Sorted list of integers to search in
        target: Integer to search for
        
    Returns:
        int: Index of the target if found, -1 otherwise
        
    Time Complexity: O(log log n) for uniformly distributed data, O(n) in worst case
    Space Complexity: O(1)
    """
    if not arr:
        return -1
        
    left, right = 0, len(arr) - 1
    
    while left <= right and arr[left] <= target <= arr[right]:
        if left == right:
            return left if arr[left] == target else -1
            
        # Calculate position using interpolation formula
        pos = left + ((target - arr[left]) * (right - left)) // (arr[right] - arr[left])
        
        # Check if pos is within bounds
        if pos < left or pos > right:
            break
            
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            left = pos + 1
        else:
            right = pos - 1
    
    return -1

def exponential_search(arr: List[T], target: T) -> int:
    """Search for target in a sorted list using exponential search.
    
    Args:
        arr: Sorted list of elements to search in
        target: Element to search for
        
    Returns:
        int: Index of the target if found, -1 otherwise
        
    Time Complexity: O(log n)
    Space Complexity: O(1)
    """
    if not arr:
        return -1
        
    n = len(arr)
    
    # If target is present at first position
    if arr[0] == target:
        return 0
    
    # Find range for binary search by repeated doubling
    i = 1
    while i < n and arr[i] <= target:
        if arr[i] == target:
            return i
        i *= 2
    
    # Perform binary search on the found range
    left, right = i // 2, min(i, n - 1)
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

def jump_search(arr: List[T], target: T) -> int:
    """Search for target in a sorted list using jump search.
    
    Args:
        arr: Sorted list of elements to search in
        target: Element to search for
        
    Returns:
        int: Index of the target if found, -1 otherwise
        
    Time Complexity: O(√n)
    Space Complexity: O(1)
    """
    if not arr:
        return -1
        
    n = len(arr)
    step = int(n ** 0.5)
    prev = 0
    
    # Finding the block where element is present (if it is present)
    while arr[min(step, n) - 1] < target:
        prev = step
        step += int(n ** 0.5)
        if prev >= n:
            return -1
    
    # Doing a linear search for target in block beginning with prev
    while arr[prev] < target:
        prev += 1
        
        # If we reach next block or end of array, element is not present
        if prev == min(step, n):
            return -1
    
    # If element is found
    if arr[prev] == target:
        return prev
        
    return -1


def string_search(text: str, pattern: str, algorithm: str = 'kmp') -> List[int]:
    """Search for pattern in text using specified string algorithm.
    
    Args:
        text: Text to search in
        pattern: Pattern to search for
        algorithm: Algorithm to use ('kmp' or 'rabin_karp')
        
    Returns:
        List of starting indices where pattern occurs
        
    Time Complexity: O(n + m) for KMP, O(n + m) average for Rabin-Karp
    Space Complexity: O(m)
    """
    if algorithm == 'kmp':
        return kmp_search(text, pattern)
    elif algorithm == 'rabin_karp':
        return rabin_karp_search(text, pattern)
    else:
        raise ValueError("Algorithm must be 'kmp' or 'rabin_karp'")
    
    return []
