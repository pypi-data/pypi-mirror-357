"""
Two Pointers Pattern implementations.

This module provides functions that demonstrate the two pointers technique,
which is useful for solving problems with arrays or linked lists where you need
to find a set of elements that fulfill certain constraints.
"""
from typing import List, Optional, Tuple, TypeVar, Any, Callable
from functools import wraps

T = TypeVar('T', int, float, str)

def validate_input(func_or_allow_empty=None, allow_empty=False, input_type=list):
    """Decorator to validate input for functions.
    
    Args:
        func_or_allow_empty: Either the function to decorate or a flag for empty lists.
        allow_empty: Whether to allow empty lists as input.
        input_type: Expected input type (list, str, or a tuple of types).
    
    Can be used as:
        @validate_input
        def func(...)
    or
        @validate_input(allow_empty=True)
        def func(...)
    or
        @validate_input(input_type=str)
        def func(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get the first argument (self for methods, first arg for functions)
            if args and hasattr(args[0], func.__name__):  # Method call
                arg = args[1] if len(args) > 1 else None
            else:  # Function call
                arg = args[0] if args else None
                
            # Skip validation if no positional args or decorator used on non-first arg
            if arg is not None:
                if not isinstance(arg, input_type):
                    raise TypeError(f"Input must be of type {input_type.__name__}")
                if not arg and not allow_empty:
                    if input_type is str:
                        raise ValueError("Input string cannot be empty")
                    else:
                        raise ValueError("Input list cannot be empty")
            return func(*args, **kwargs)
        return wrapper
    
    # Handle both @validate_input and @validate_input(...) cases
    if callable(func_or_allow_empty):
        return decorator(func_or_allow_empty)
    return decorator

@validate_input
def pair_with_target_sum(arr: List[int], target: int) -> List[int]:
    """
    Find a pair of numbers in a sorted array that sum up to the target sum.
    
    Args:
        arr: A sorted list of integers.
        target: The target sum to find.
        
    Returns:
        A list of indices of the two numbers that add up to the target sum.
        If no such pair exists, returns [-1, -1].
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    left, right = 0, len(arr) - 1
    
    while left < right:
        current_sum = arr[left] + arr[right]
        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    return [-1, -1]

@validate_input(allow_empty=True)
def remove_duplicates(arr: List[T]) -> int:
    """
    Remove duplicates from a sorted array in-place and return the new length.
    
    Args:
        arr: A sorted list of elements (must support equality comparison).
        
    Returns:
        The new length of the array after removing duplicates.
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if len(arr) <= 1:
        return len(arr)
        
    next_non_duplicate = 1
    
    for i in range(1, len(arr)):
        if arr[next_non_duplicate - 1] != arr[i]:
            arr[next_non_duplicate] = arr[i]
            next_non_duplicate += 1
            
    return next_non_duplicate

@validate_input
def make_squares(arr: List[int]) -> List[int]:
    """
    Given a sorted array of integers, return a new array containing squares of all 
    the numbers in the input array in sorted order.
    
    Args:
        arr: A sorted list of integers.
        
    Returns:
        A new list containing squares of all numbers in the input array, sorted.
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    n = len(arr)
    squares = [0] * n
    highest_square_idx = n - 1
    left, right = 0, n - 1
    
    while left <= right:
        left_square = arr[left] * arr[left]
        right_square = arr[right] * arr[right]
        
        if left_square > right_square:
            squares[highest_square_idx] = left_square
            left += 1
        else:
            squares[highest_square_idx] = right_square
            right -= 1
        highest_square_idx -= 1
        
    return squares

@validate_input
def search_triplets(arr: List[int], target: int) -> List[List[int]]:
    """
    Find all unique triplets in the array which gives the sum of zero.
    
    Args:
        arr: A list of integers.
        target: The target sum for the triplets.
        
    Returns:
        A list of all unique triplets that sum up to the target.
        
    Time Complexity: O(n²)
    Space Complexity: O(n) for sorting
    """
    arr.sort()
    triplets = []
    
    for i in range(len(arr) - 2):
        if i > 0 and arr[i] == arr[i - 1]:  # Skip same element to avoid duplicate triplets
            continue
        search_pair(arr, target - arr[i], i + 1, triplets)
    
    return triplets

def search_pair(arr: List[int], target_sum: int, left: int, triplets: List[List[int]]):
    """Helper function for search_triplets."""
    right = len(arr) - 1
    
    while left < right:
        current_sum = arr[left] + arr[right]
        
        if current_sum == target_sum:  # Found the triplet
            triplets.append([-target_sum, arr[left], arr[right]])
            left += 1
            right -= 1
            
            # Skip same elements to avoid duplicate triplets
            while left < right and arr[left] == arr[left - 1]:
                left += 1
            while left < right and arr[right] == arr[right + 1]:
                right -= 1
                
        elif current_sum < target_sum:
            left += 1  # Need a pair with a bigger sum
        else:
            right -= 1  # Need a pair with a smaller sum

@validate_input
def dutch_flag_sort(arr: List[int]) -> None:
    """
    Sort an array of 0s, 1s, and 2s in-place (Dutch National Flag problem).
    
    Args:
        arr: A list containing only 0s, 1s, and 2s.
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    low, high = 0, len(arr) - 1
    i = 0
    
    while i <= high:
        if arr[i] == 0:
            arr[i], arr[low] = arr[low], arr[i]
            low += 1
            i += 1
        elif arr[i] == 1:
            i += 1
        else:  # arr[i] == 2
            arr[i], arr[high] = arr[high], arr[i]
            high -= 1

def compare_strings_backspace(str1: str, str2: str) -> bool:
    """
    Compare if two strings are equal when both are typed into empty text editors.
    '#' means a backspace character.
    
    Args:
        str1: First input string.
        str2: Second input string.
        
    Returns:
        True if the two strings are equal when typed into editors, False otherwise.
        
    Time Complexity: O(n + m) where n and m are lengths of the input strings
    Space Complexity: O(1)
    """
    def get_next_valid_char_index(s: str, index: int) -> int:
        backspace_count = 0
        while index >= 0:
            if s[index] == '#':
                backspace_count += 1
            elif backspace_count > 0:
                backspace_count -= 1
            else:
                break
            index -= 1
        return index
    
    index1, index2 = len(str1) - 1, len(str2) - 1
    
    while index1 >= 0 or index2 >= 0:
        # Get the next valid character from the end of str1
        i1 = get_next_valid_char_index(str1, index1)
        # Get the next valid character from the end of str2
        i2 = get_next_valid_char_index(str2, index2)
        
        # If both strings are empty
        if i1 < 0 and i2 < 0:
            return True
        # If one of the strings is empty
        if i1 < 0 or i2 < 0:
            return False
        # If characters are not equal
        if str1[i1] != str2[i2]:
            return False
            
        index1 = i1 - 1
        index2 = i2 - 1
    
    return True
