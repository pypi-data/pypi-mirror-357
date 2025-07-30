"""
Sliding Window pattern implementations for AlgoZen.

This module provides solutions to common problems that can be solved using
the sliding window technique, which is useful for array/string problems
involving subarrays or substrings.
"""
from typing import List, Dict, Any, Set
from collections import defaultdict

def max_sum_subarray_of_size_k(arr: List[int], k: int) -> int:
    """
    Find the maximum sum of any contiguous subarray of size 'k'.
    
    Args:
        arr: List of integers
        k: Size of the subarray
        
    Returns:
        int: Maximum sum of any subarray of size 'k'
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not arr or k <= 0 or k > len(arr):
        return 0
    
    max_sum = window_sum = sum(arr[:k])
    
    for i in range(len(arr) - k):
        window_sum = window_sum - arr[i] + arr[i + k]
        max_sum = max(max_sum, window_sum)
    
    return max_sum

def max_sum_subarray(arr: List[int], k: int) -> int:
    """
    Find the maximum sum of any contiguous subarray of size 'k'.
    
    Args:
        arr: List of integers
        k: Size of the subarray
        
    Returns:
        int: Maximum sum of any subarray of size 'k'
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not arr or k <= 0 or k > len(arr):
        return 0
    
    max_sum = window_sum = sum(arr[:k])
    
    for i in range(len(arr) - k):
        window_sum = window_sum - arr[i] + arr[i + k]
        max_sum = max(max_sum, window_sum)
    
    return max_sum

def smallest_subarray_with_given_sum(arr: List[int], s: int) -> int:
    """
    Find the length of the smallest contiguous subarray with a sum greater than or equal to 's'.
    
    Args:
        arr: List of positive integers
        s: Target sum
        
    Returns:
        int: Length of the smallest subarray with sum >= s, or 0 if no such subarray exists
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not arr or s <= 0:
        return 0
    
    min_length = float('inf')
    window_sum = 0
    window_start = 0
    
    for window_end in range(len(arr)):
        window_sum += arr[window_end]
        
        while window_sum >= s:
            min_length = min(min_length, window_end - window_start + 1)
            window_sum -= arr[window_start]
            window_start += 1
    
    return min_length if min_length != float('inf') else 0

def longest_substring_with_k_distinct(s: str, k: int) -> int:
    """
    Find the length of the longest substring with at most 'k' distinct characters.
    
    Args:
        s: Input string
        k: Maximum number of distinct characters allowed in the substring
        
    Returns:
        int: Length of the longest substring with at most 'k' distinct characters
        
    Time Complexity: O(n)
    Space Complexity: O(k)
    """
    if not s or k <= 0:
        return 0
    
    char_freq = {}
    max_length = 0
    window_start = 0
    
    for window_end in range(len(s)):
        right_char = s[window_end]
        char_freq[right_char] = char_freq.get(right_char, 0) + 1
        
        while len(char_freq) > k:
            left_char = s[window_start]
            char_freq[left_char] -= 1
            if char_freq[left_char] == 0:
                del char_freq[left_char]
            window_start += 1
        
        max_length = max(max_length, window_end - window_start + 1)
    
    return max_length

def longest_substring_without_repeating_chars(s: str) -> int:
    """
    Find the length of the longest substring without repeating characters.
    
    Args:
        s: Input string
        
    Returns:
        int: Length of the longest substring without repeating characters
        
    Time Complexity: O(n)
    Space Complexity: O(min(m, n)) where m is the character set size
    """
    if not s:
        return 0
    
    char_index = {}
    max_length = 0
    window_start = 0
    
    for window_end in range(len(s)):
        right_char = s[window_end]
        
        if right_char in char_index:
            window_start = max(window_start, char_index[right_char] + 1)
        
        char_index[right_char] = window_end
        max_length = max(max_length, window_end - window_start + 1)
    
    return max_length

def find_anagrams(s: str, p: str) -> List[int]:
    """
    Find all the start indices of p's anagrams in s.
    
    Args:
        s: Input string
        p: Pattern to find anagrams of
        
    Returns:
        List[int]: List of starting indices of all anagrams of p in s
        
    Time Complexity: O(n + m) where n is len(s) and m is len(p)
    Space Complexity: O(1) since the character set is limited to lowercase English letters
    """
    if not s or not p or len(p) > len(s):
        return []
    
    p_freq = {}
    window_freq = {}
    result = []
    
    # Initialize frequency map for the pattern
    for char in p:
        p_freq[char] = p_freq.get(char, 0) + 1
    
    # Initialize the sliding window
    window_start = 0
    matched = 0
    
    for window_end in range(len(s)):
        right_char = s[window_end]
        
        # Add the current character to the window
        if right_char in p_freq:
            window_freq[right_char] = window_freq.get(right_char, 0) + 1
            if window_freq[right_char] == p_freq[right_char]:
                matched += 1
        
        # If we've found all characters in the pattern, add the start index
        if matched == len(p_freq):
            result.append(window_start)
        
        # Shrink the window from the left if it's larger than the pattern
        if window_end >= len(p) - 1:
            left_char = s[window_start]
            window_start += 1
            
            if left_char in p_freq:
                if window_freq[left_char] == p_freq[left_char]:
                    matched -= 1
                window_freq[left_char] -= 1
    
    return result

def max_fruit_count_of_2_types(fruits: List[str]) -> int:
    """
    Given an array of characters where each character represents a fruit tree,
    find the maximum number of fruits you can collect with at most 2 types of fruits.
    
    This is equivalent to finding the longest subarray with at most 2 distinct characters.
    
    Args:
        fruits: List of characters representing fruits
        
    Returns:
        int: Maximum number of fruits that can be collected
        
    Time Complexity: O(n)
    Space Complexity: O(1) since there can be at most 2 types of fruits in the map
    """
    if not fruits:
        return 0
    
    fruit_freq = {}
    max_fruits = 0
    window_start = 0
    
    for window_end in range(len(fruits)):
        right_fruit = fruits[window_end]
        fruit_freq[right_fruit] = fruit_freq.get(right_fruit, 0) + 1
        
        # Shrink the window until we have at most 2 types of fruits
        while len(fruit_freq) > 2:
            left_fruit = fruits[window_start]
            fruit_freq[left_fruit] -= 1
            if fruit_freq[left_fruit] == 0:
                del fruit_freq[left_fruit]
            window_start += 1
        
        max_fruits = max(max_fruits, window_end - window_start + 1)
    
    return max_fruits
