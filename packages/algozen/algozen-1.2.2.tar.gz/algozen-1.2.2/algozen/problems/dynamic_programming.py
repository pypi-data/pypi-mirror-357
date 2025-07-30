"""
Dynamic Programming Problems and Solutions.

This module contains implementations of common dynamic programming problems.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Set, Any, TypeVar, Callable, Generic
from functools import wraps, lru_cache
import math

T = TypeVar('T')

def validate_input(func: Callable) -> Callable:
    """Decorator to validate input for DP problems."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)
    return wrapper

@validate_input
def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number using dynamic programming.
    
    Args:
        n: The index of the Fibonacci number to calculate
        
    Returns:
        The nth Fibonacci number
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

@validate_input
def longest_increasing_subsequence(nums: List[int]) -> int:
    """
    Find the length of the longest strictly increasing subsequence.
    
    Args:
        nums: List of integers
        
    Returns:
        Length of the longest increasing subsequence
        
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not nums:
        return 0
    
    # Patience sorting approach
    tails = []
    for num in nums:
        # Find the first index in tails where value >= num
        left, right = 0, len(tails)
        while left < right:
            mid = (left + right) // 2
            if tails[mid] < num:
                left = mid + 1
            else:
                right = mid
        
        if left == len(tails):
            tails.append(num)
        else:
            tails[left] = num
    
    return len(tails)

@validate_input
def coin_change(coins: List[int], amount: int) -> int:
    """
    Find the fewest number of coins needed to make up the given amount.
    
    Args:
        coins: List of coin denominations
        amount: Target amount
        
    Returns:
        Minimum number of coins needed, or -1 if it's not possible
        
    Time Complexity: O(amount * len(coins))
    Space Complexity: O(amount)
    """
    # Initialize DP array with amount + 1 (invalid value)
    dp = [amount + 1] * (amount + 1)
    dp[0] = 0  # Base case: 0 coins needed for amount 0
    
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != amount + 1 else -1

@validate_input
def longest_common_subsequence(text1: str, text2: str) -> int:
    """
    Find the length of the longest common subsequence between two strings.
    
    Args:
        text1: First string
        text2: Second string
        
    Returns:
        Length of the longest common subsequence
        
    Time Complexity: O(m*n)
    Space Complexity: O(m*n)
    """
    m, n = len(text1), len(text2)
    # Initialize DP table with (m+1) x (n+1) zeros
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

@validate_input
def word_break(s: str, word_dict: List[str]) -> bool:
    """
    Determine if a string can be segmented into a space-separated sequence of dictionary words.
    
    Args:
        s: Input string
        word_dict: List of dictionary words
        
    Returns:
        True if the string can be segmented, False otherwise
        
    Time Complexity: O(n²)
    Space Complexity: O(n)
    """
    word_set = set(word_dict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True  # Empty string can be segmented
    
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    
    return dp[n]

@validate_input
def knapsack(weights: List[int], values: List[int], capacity: int) -> int:
    """
    Solve the 0/1 knapsack problem.
    
    Args:
        weights: List of item weights
        values: List of item values
        capacity: Maximum weight capacity
        
    Returns:
        Maximum value that can be obtained
        
    Time Complexity: O(n * capacity)
    Space Complexity: O(capacity)
    """
    n = len(weights)
    dp = [0] * (capacity + 1)
    
    for i in range(n):
        # Iterate backwards to prevent using the same item multiple times
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[capacity]

@validate_input
def edit_distance(word1: str, word2: str) -> int:
    """
    Calculate the minimum number of operations (insert, delete, replace) to convert word1 to word2.
    
    Args:
        word1: First string
        word2: Second string
        
    Returns:
        Minimum edit distance between the two strings
        
    Time Complexity: O(m*n)
    Space Complexity: O(m*n)
    """
    m, n = len(word1), len(word2)
    
    # If one of the strings is empty
    if m * n == 0:
        return m + n
    
    # Initialize DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # Deletion
                    dp[i][j-1],    # Insertion
                    dp[i-1][j-1]   # Replacement
                )
    
    return dp[m][n]

@validate_input
def max_subarray_sum_circular(nums: List[int]) -> int:
    """
    Find the maximum possible sum of a non-empty subarray of a circular array.
    
    Args:
        nums: Circular array of integers
        
    Returns:
        Maximum subarray sum in circular array
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not nums:
        return 0
    
    total = max_sum = min_sum = current_max = current_min = nums[0]
    
    for num in nums[1:]:
        # Kadane's algorithm for max subarray
        current_max = max(num, current_max + num)
        max_sum = max(max_sum, current_max)
        
        # Modified Kadane's for min subarray
        current_min = min(num, current_min + num)
        min_sum = min(min_sum, current_min)
        
        total += num
    
    # If all numbers are negative, return the maximum element
    if max_sum < 0:
        return max_sum
    
    # The maximum could be either the max subarray or the total minus min subarray
    return max(max_sum, total - min_sum)

@validate_input
def max_product_subarray(nums: List[int]) -> int:
    """
    Find the contiguous subarray within an array that has the largest product.
    
    Args:
        nums: List of integers
        
    Returns:
        Maximum product of any contiguous subarray
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not nums:
        return 0
    
    max_so_far = min_so_far = result = nums[0]
    
    for num in nums[1:]:
        # Keep track of both max and min because multiplying two negatives gives a positive
        candidates = (num, max_so_far * num, min_so_far * num)
        max_so_far = max(candidates)
        min_so_far = min(candidates)
        
        # Update the global maximum
        result = max(result, max_so_far)
    
    return result

@validate_input
def num_ways_to_climb_stairs(n: int) -> int:
    """
    Count the number of distinct ways to climb to the top of a staircase with n steps,
    where you can take 1 or 2 steps at a time.
    
    Args:
        n: Number of steps
        
    Returns:
        Number of distinct ways to climb the stairs
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if n <= 2:
        return n
    
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    
    return b

@validate_input
def can_partition(nums: List[int]) -> bool:
    """
    Determine if the input array can be partitioned into two subsets with equal sum.
    
    Args:
        nums: List of positive integers
        
    Returns:
        True if the array can be partitioned into two equal sum subsets, False otherwise
        
    Time Complexity: O(n * sum)
    Space Complexity: O(sum)
    """
    total = sum(nums)
    
    # If total is odd, cannot partition into equal sum subsets
    if total % 2 != 0:
        return False
    
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True  # Base case: sum of 0 is always possible with empty subset
    
    for num in nums:
        # Iterate backwards to prevent reusing the same element multiple times
        for i in range(target, num - 1, -1):
            if dp[i - num]:
                dp[i] = True
    
    return dp[target]
