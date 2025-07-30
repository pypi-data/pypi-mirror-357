"""
Array Problems and Solutions.

This module contains implementations of common array-based problems.
"""
from typing import List, Tuple, Optional, Dict, Set, Any, TypeVar, Callable
from functools import wraps
import math

T = TypeVar('T')

def validate_array_input(func: Callable) -> Callable:
    """Decorator to validate array input for array problems."""
    @wraps(func)
    def wrapper(arr: List[T], *args, **kwargs) -> Any:
        if not isinstance(arr, list):
            raise TypeError("Input must be a list")
        return func(arr, *args, **kwargs)
    return wrapper

@validate_array_input
def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Find two numbers in the array that add up to the target sum.
    
    Args:
        nums: List of integers
        target: Target sum
        
    Returns:
        List of indices of the two numbers that add up to target
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    num_map = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    
    return []  # No solution found

@validate_array_input
def find_max_min(arr: List[int]) -> Tuple[int, int]:
    """
    Find the minimum and maximum values in an array in a single pass.
    
    Args:
        arr: List of integers
        
    Returns:
        A tuple (min, max) containing the minimum and maximum values
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not arr:
        raise ValueError("Input list cannot be empty")
        
    min_val = max_val = arr[0]
    
    for num in arr[1:]:
        if num < min_val:
            min_val = num
        elif num > max_val:
            max_val = num
            
    return (min_val, max_val)

@validate_array_input
def remove_duplicates(arr: List[int]) -> int:
    """
    Remove duplicates from a sorted array in-place and return the new length.
    
    Args:
        arr: A sorted list of integers with duplicates
        
    Returns:
        The new length of the array after removing duplicates
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not arr:
        return 0
        
    # Use two pointers: one for the current element and one for the next non-duplicate
    write_index = 1
    
    for i in range(1, len(arr)):
        if arr[i] != arr[i-1]:
            arr[write_index] = arr[i]
            write_index += 1
            
    # Return the new length
    return write_index

@validate_array_input
def max_subarray_sum(arr: List[int]) -> int:
    """
    Find the maximum sum of any contiguous subarray (Kadane's Algorithm).
    
    Args:
        arr: List of integers
        
    Returns:
        Maximum sum of any contiguous subarray
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not arr:
        return 0
        
    max_so_far = max_ending_here = arr[0]
    
    for num in arr[1:]:
        max_ending_here = max(num, max_ending_here + num)
        max_so_far = max(max_so_far, max_ending_here)
    
    return max_so_far

@validate_array_input
def max_profit(prices: List[int]) -> int:
    """
    Find the maximum profit that can be achieved by buying and selling a stock once.
    
    Args:
        prices: List of stock prices where prices[i] is the price on day i
        
    Returns:
        Maximum profit that can be achieved
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not prices or len(prices) < 2:
        return 0
    
    min_price = float('inf')
    max_profit = 0
    
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    
    return max_profit

@validate_array_input
def product_except_self(nums: List[int]) -> List[int]:
    """
    Given an array of integers, return a new array such that each element at index i 
    is equal to the product of all the elements of the original array except the one at i.
    
    Args:
        nums: List of integers
        
    Returns:
        New list where each element is the product of all elements except itself
        
    Time Complexity: O(n)
    Space Complexity: O(1) excluding the result
    """
    if not nums:
        return []
    
    n = len(nums)
    result = [1] * n
    
    # Calculate left products
    left_product = 1
    for i in range(1, n):
        left_product *= nums[i-1]
        result[i] = left_product
    
    # Calculate right products and multiply with left products
    right_product = 1
    for i in range(n-2, -1, -1):
        right_product *= nums[i+1]
        result[i] *= right_product
    
    return result

@validate_array_input
def rotate_array(nums: List[int], k: int) -> None:
    """
    Rotate the array to the right by k steps in-place.
    
    Args:
        nums: List of integers to rotate
        k: Number of steps to rotate
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not nums:
        return
    
    n = len(nums)
    k %= n  # Handle cases where k > n
    
    # Reverse the entire array
    def reverse(start: int, end: int) -> None:
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start += 1
            end -= 1
    
    # Reverse the first part
    reverse(0, n - 1)
    # Reverse the first k elements
    reverse(0, k - 1)
    # Reverse the remaining elements
    reverse(k, n - 1)


@validate_array_input
def find_duplicate_and_missing(nums: List[int]) -> Tuple[int, int]:
    """
    Find the duplicate and missing numbers in an array of integers from 1 to n.
    
    Args:
        nums: List of integers containing numbers from 1 to n with one duplicate and one missing
        
    Returns:
        A tuple (duplicate, missing)
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not nums:
        raise ValueError("Input list cannot be empty")
    
    n = len(nums)
    
    # Calculate the expected and actual sums
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(nums)
    
    # Calculate the expected and actual sum of squares
    expected_sum_sq = n * (n + 1) * (2 * n + 1) // 6
    actual_sum_sq = sum(x * x for x in nums)
    
    # Let x be the duplicate, y be the missing
    # x - y = actual_sum - expected_sum
    # x² - y² = actual_sum_sq - expected_sum_sq
    # => x + y = (actual_sum_sq - expected_sum_sq) / (x - y)
    
    sum_diff = actual_sum - expected_sum  # x - y
    sum_sq_diff = actual_sum_sq - expected_sum_sq  # x² - y²
    
    sum_xy = sum_sq_diff // sum_diff  # x + y
    
    x = (sum_diff + sum_xy) // 2  # duplicate
    y = (sum_xy - sum_diff) // 2   # missing
    
    return (x, y)

@validate_array_input
def max_area(height: List[int]) -> int:
    """
    Find the maximum area of water that can be contained between two lines.
    
    Args:
        height: List of non-negative integers representing the height of each line
        
    Returns:
        Maximum area of water that can be contained
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not height or len(height) < 2:
        return 0
    
    left, right = 0, len(height) - 1
    max_area = 0
    
    while left < right:
        # Calculate the area between the two lines
        h = min(height[left], height[right])
        w = right - left
        max_area = max(max_area, h * w)
        
        # Move the pointer pointing to the shorter line
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_area

@validate_array_input
def trap_rain_water(height: List[int]) -> int:
    """
    Given n non-negative integers representing an elevation map where the width of
    each bar is 1, compute how much water it can trap after raining.
    
    Args:
        height: List of non-negative integers representing the height of each bar
        
    Returns:
        Total amount of trapped water
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not height:
        return 0
    
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    
    return water
