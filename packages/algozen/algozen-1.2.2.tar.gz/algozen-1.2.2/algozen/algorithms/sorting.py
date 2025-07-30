"""
Sorting algorithms implementation for AlgoZen.

This module provides various sorting algorithms with consistent interfaces.
All sorting functions sort the input list in-place and return it for method chaining.
"""
from typing import List, TypeVar, Callable, Any, Optional
from functools import wraps
import random

T = TypeVar('T', int, float, str)

def validate_input(func: Callable) -> Callable:
    """Decorator to validate input for sorting functions."""
    @wraps(func)
    def wrapper(arr: List[T], *args, **kwargs) -> List[T]:
        if not isinstance(arr, list):
            raise TypeError("Input must be a list")
        if len(arr) <= 1:
            return arr
        return func(arr, *args, **kwargs)
    return wrapper

@validate_input
def bubble_sort(arr: List[T]) -> List[T]:
    """Sort a list using bubble sort algorithm.
    
    Time Complexity: O(n²) in worst and average case, O(n) in best case (already sorted)
    Space Complexity: O(1)
    """
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
        if not swapped:  # If no swaps in inner loop, array is sorted
            break
    return arr

@validate_input
def selection_sort(arr: List[T]) -> List[T]:
    """Sort a list using selection sort algorithm.
    
    Time Complexity: O(n²) in all cases
    Space Complexity: O(1)
    """
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

@validate_input
def insertion_sort(arr: List[T]) -> List[T]:
    """Sort a list using insertion sort algorithm.
    
    Time Complexity: O(n²) in worst and average case, O(n) in best case (already sorted)
    Space Complexity: O(1)
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key < arr[j]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

def _merge(left: List[T], right: List[T]) -> List[T]:
    """Merge two sorted lists into one sorted list."""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sort(arr: List[T]) -> List[T]:
    """Sort a list using merge sort algorithm.
    
    Time Complexity: O(n log n) in all cases
    Space Complexity: O(n)
    """
    if len(arr) <= 1:
        return arr
        
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    result = _merge(left, right)
    arr[:] = result  # Update the original array
    return arr

def _partition(arr: List[T], low: int, high: int) -> int:
    """Helper function for quick sort to partition the array."""
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return i + 1

def _quick_sort_helper(arr: List[T], low: int, high: int) -> None:
    """Recursive helper function for quick sort."""
    if low < high:
        pi = _partition(arr, low, high)
        _quick_sort_helper(arr, low, pi-1)
        _quick_sort_helper(arr, pi+1, high)

@validate_input
def quick_sort(arr: List[T]) -> List[T]:
    """Sort a list using quick sort algorithm.
    
    Time Complexity: O(n log n) average case, O(n²) worst case (rare)
    Space Complexity: O(log n) due to recursion
    """
    _quick_sort_helper(arr, 0, len(arr)-1)
    return arr

@validate_input
def heap_sort(arr: List[T]) -> List[T]:
    """Sort a list using heap sort algorithm.
    
    Time Complexity: O(n log n) in all cases
    Space Complexity: O(1)
    """
    def heapify(n: int, i: int) -> None:
        """Heapify subtree rooted at index i."""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[i] < arr[left]:
            largest = left
            
        if right < n and arr[largest] < arr[right]:
            largest = right
            
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(n, largest)
    
    n = len(arr)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)
    
    # Extract elements one by one
    for i in range(n-1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(i, 0)
    
    return arr


@validate_input
def counting_sort(arr: List[int]) -> List[int]:
    """Sort a list using counting sort algorithm.
    
    Time Complexity: O(n + k) where k is the range of input
    Space Complexity: O(k)
    """
    if not arr:
        return arr
    
    # Find range
    min_val, max_val = min(arr), max(arr)
    range_size = max_val - min_val + 1
    
    # Count occurrences
    count = [0] * range_size
    for num in arr:
        count[num - min_val] += 1
    
    # Reconstruct array
    arr.clear()
    for i, freq in enumerate(count):
        arr.extend([i + min_val] * freq)
    
    return arr


@validate_input
def radix_sort(arr: List[int]) -> List[int]:
    """Sort a list using radix sort algorithm.
    
    Time Complexity: O(d * (n + k)) where d is number of digits, k is base
    Space Complexity: O(n + k)
    """
    if not arr or all(x == 0 for x in arr):
        return arr
    
    # Handle negative numbers by separating them
    negatives = [x for x in arr if x < 0]
    positives = [x for x in arr if x >= 0]
    
    # Sort positives with radix sort
    if positives:
        max_num = max(positives)
        exp = 1
        while max_num // exp > 0:
            _counting_sort_by_digit(positives, exp)
            exp *= 10
    
    # Sort negatives (convert to positive, sort, then convert back)
    if negatives:
        negatives = [-x for x in negatives]
        max_num = max(negatives)
        exp = 1
        while max_num // exp > 0:
            _counting_sort_by_digit(negatives, exp)
            exp *= 10
        negatives = [-x for x in reversed(negatives)]
    
    # Combine results
    arr[:] = negatives + positives
    return arr


def _counting_sort_by_digit(arr: List[int], exp: int) -> None:
    """Helper function for radix sort - sort by specific digit."""
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    
    # Count occurrences of each digit
    for num in arr:
        digit = (num // exp) % 10
        count[digit] += 1
    
    # Change count[i] to actual position
    for i in range(1, 10):
        count[i] += count[i - 1]
    
    # Build output array
    for i in range(n - 1, -1, -1):
        digit = (arr[i] // exp) % 10
        output[count[digit] - 1] = arr[i]
        count[digit] -= 1
    
    # Copy output array to arr
    for i in range(n):
        arr[i] = output[i]
