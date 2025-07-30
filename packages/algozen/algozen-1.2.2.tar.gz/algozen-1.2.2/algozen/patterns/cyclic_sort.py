"""
Cyclic Sort Pattern implementations.

This module provides functions that demonstrate the cyclic sort technique,
which is useful for solving problems involving arrays containing numbers in a given range.
"""
from typing import List, Optional, Tuple, TypeVar, Callable, Set, Any
from functools import wraps

T = TypeVar('T', int, float)

def validate_array(func: Callable) -> Callable:
    """Decorator to validate array input for cyclic sort functions."""
    @wraps(func)
    def wrapper(nums: List[int], *args, **kwargs) -> Any:
        if not isinstance(nums, list):
            raise TypeError("Input must be a list")
        return func(nums, *args, **kwargs)
    return wrapper

@validate_array
def cyclic_sort(nums: List[int]) -> List[int]:
    """
    Sort an array in O(n) time and O(1) space where elements are in the range [1..n].
    
    Args:
        nums: List of integers in the range [1..n]
        
    Returns:
        The sorted list
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    i = 0
    n = len(nums)
    
    while i < n:
        # The correct position of nums[i] is nums[i] - 1 (for 1-based to 0-based index)
        correct_pos = nums[i] - 1
        
        # If the current number is not in its correct position, swap it
        if nums[i] != nums[correct_pos]:
            nums[i], nums[correct_pos] = nums[correct_pos], nums[i]
        else:
            i += 1
    
    return nums

@validate_array
def find_missing_number(nums: List[int]) -> int:
    """
    Find the missing number in an array containing n distinct numbers in the range [0..n].
    
    Args:
        nums: List of integers in the range [0..n] with one number missing
        
    Returns:
        The missing number
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    i, n = 0, len(nums)
    
    # Cyclic sort
    while i < n:
        # The correct position of nums[i] is nums[i] (since range is 0 to n)
        correct_pos = nums[i]
        
        # Place nums[i] at its correct position if possible
        if nums[i] < n and nums[i] != nums[correct_pos]:
            nums[i], nums[correct_pos] = nums[correct_pos], nums[i]
        else:
            i += 1
    
    # Find the first index that doesn't match its value
    for i in range(n):
        if nums[i] != i:
            return i
    
    # If all numbers are in place, n is the missing number
    return n

@validate_array
def find_all_missing_numbers(nums: List[int]) -> List[int]:
    """
    Find all missing numbers in an array containing n integers in the range [1..n].
    
    Args:
        nums: List of integers in the range [1..n]
        
    Returns:
        List of all missing numbers
        
    Time Complexity: O(n)
    Space Complexity: O(1) excluding the result
    """
    i, n = 0, len(nums)
    
    # Cyclic sort
    while i < n:
        correct_pos = nums[i] - 1  # Convert to 0-based index
        
        # Place nums[i] at its correct position if possible
        if nums[i] != nums[correct_pos]:
            nums[i], nums[correct_pos] = nums[correct_pos], nums[i]
        else:
            i += 1
    
    # Find all indices that don't match their value + 1
    missing = []
    for i in range(n):
        if nums[i] != i + 1:
            missing.append(i + 1)
    
    return missing

@validate_array
def find_duplicate_number(nums: List[int]) -> int:
    """
    Find the duplicate number in an array containing n+1 integers in the range [1..n].
    
    Args:
        nums: List of integers in the range [1..n] with one duplicate
        
    Returns:
        The duplicate number
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    i, n = 0, len(nums)
    
    # Cyclic sort
    while i < n:
        # If the current number is not at its correct position
        if nums[i] != i + 1:
            correct_pos = nums[i] - 1
            
            # If the correct position already has the same number, it's a duplicate
            if nums[i] == nums[correct_pos]:
                return nums[i]
            
            # Otherwise, swap
            nums[i], nums[correct_pos] = nums[correct_pos], nums[i]
        else:
            i += 1
    
    # If no duplicate found (shouldn't happen as per problem constraints)
    return -1

@validate_array
def find_all_duplicate_numbers(nums: List[int]) -> List[int]:
    """
    Find all duplicate numbers in an array containing n integers in the range [1..n].
    
    Args:
        nums: List of integers in the range [1..n]
        
    Returns:
        List of all duplicate numbers
        
    Time Complexity: O(n)
    Space Complexity: O(1) excluding the result
    """
    i, n = 0, len(nums)
    duplicates = set()
    
    # Cyclic sort
    while i < n:
        correct_pos = nums[i] - 1  # Convert to 0-based index
        
        # If the number is not in its correct position
        if nums[i] != nums[correct_pos]:
            nums[i], nums[correct_pos] = nums[correct_pos], nums[i]
        # If it is in the correct position but not at the current index
        elif i != correct_pos:
            duplicates.add(nums[i])
            i += 1
        else:
            i += 1
    
    return list(duplicates)

@validate_array
def find_corrupt_pair(nums: List[int]) -> Tuple[int, int]:
    """
    Find the corrupt pair (duplicate, missing) in an unsorted array containing n numbers
    from 1 to n with one number being duplicated and another missing.
    
    Args:
        nums: List of integers in the range [1..n] with one duplicate and one missing
        
    Returns:
        A tuple (duplicate, missing)
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    i, n = 0, len(nums)
    
    # Cyclic sort
    while i < n:
        correct_pos = nums[i] - 1  # Convert to 0-based index
        
        # Place nums[i] at its correct position if possible
        if nums[i] != nums[correct_pos]:
            nums[i], nums[correct_pos] = nums[correct_pos], nums[i]
        else:
            i += 1
    
    # Find the first number that is not in its correct position
    for i in range(n):
        if nums[i] != i + 1:
            return (nums[i], i + 1)  # (duplicate, missing)
    
    # If no corrupt pair found (shouldn't happen as per problem constraints)
    return (-1, -1)

@validate_array
def find_first_smallest_missing_positive(nums: List[int]) -> int:
    """
    Find the first missing positive integer in an unsorted array.
    
    Args:
        nums: List of integers
        
    Returns:
        The smallest missing positive integer
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    n = len(nums)
    i = 0
    
    # Cyclic sort: place each number at its correct position if possible
    while i < n:
        correct_pos = nums[i] - 1
        
        # Place nums[i] at its correct position if it's a positive number <= n
        if 0 < nums[i] <= n and nums[i] != nums[correct_pos]:
            nums[i], nums[correct_pos] = nums[correct_pos], nums[i]
        else:
            i += 1
    
    # Find the first index that doesn't match its value
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    
    # If all numbers from 1 to n are present, return n + 1
    return n + 1

@validate_array
def find_first_k_missing_positive(nums: List[int], k: int) -> List[int]:
    """
    Find the first k missing positive integers in an unsorted array.
    
    Args:
        nums: List of integers
        k: Number of missing positive integers to find
        
    Returns:
        List of first k missing positive integers
        
    Time Complexity: O(n + k)
    Space Complexity: O(k) for the result and additional set
    """
    n = len(nums)
    i = 0
    missing_numbers = []
    extra_numbers = set()
    
    # Cyclic sort: place each number at its correct position if possible
    while i < n:
        correct_pos = nums[i] - 1
        
        # Place nums[i] at its correct position if it's a positive number <= n
        if 0 < nums[i] <= n and nums[i] != nums[correct_pos]:
            nums[i], nums[correct_pos] = nums[correct_pos], nums[i]
        else:
            i += 1
    
    # Find all missing numbers within the array
    for i in range(n):
        if nums[i] != i + 1:
            missing_numbers.append(i + 1)
            if len(missing_numbers) == k:
                return missing_numbers
            
            # Keep track of numbers that are out of the array range
            if nums[i] > 0:
                extra_numbers.add(nums[i])
    
    # If we still need more missing numbers, continue beyond the array length
    i = 1
    while len(missing_numbers) < k:
        candidate = n + i
        if candidate not in extra_numbers:
            missing_numbers.append(candidate)
        i += 1
    
    return missing_numbers[:k]
