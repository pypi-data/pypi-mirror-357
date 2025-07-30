"""
String Manipulation Problems and Solutions.

This module contains implementations of common string manipulation problems.
"""
from typing import List, Tuple, Optional, Dict, Set, Any, TypeVar, Callable, Iterator
from functools import wraps
import re
from collections import defaultdict, Counter

T = TypeVar('T')

def validate_string_input(func: Callable) -> Callable:
    """Decorator to validate string input for string problems."""
    @wraps(func)
    def wrapper(s: str, *args, **kwargs) -> Any:
        if not isinstance(s, str):
            raise TypeError("Input must be a string")
        return func(s, *args, **kwargs)
    return wrapper

@validate_string_input
def is_palindrome(s: str) -> bool:
    """
    Check if a string is a palindrome, considering only alphanumeric characters
    and ignoring cases.
    
    Args:
        s: Input string
        
    Returns:
        True if the string is a valid palindrome, False otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    left, right = 0, len(s) - 1
    
    while left < right:
        # Skip non-alphanumeric characters from left
        while left < right and not s[left].isalnum():
            left += 1
        # Skip non-alphanumeric characters from right
        while left < right and not s[right].isalnum():
            right -= 1
            
        if s[left].lower() != s[right].lower():
            return False
            
        left += 1
        right -= 1
        
    return True

@validate_string_input
def longest_substring_without_repeating_chars(s: str) -> int:
    """
    Find the length of the longest substring without repeating characters.
    
    Args:
        s: Input string
        
    Returns:
        Length of the longest substring without repeating characters
        
    Time Complexity: O(n)
    Space Complexity: O(min(m, n)) where m is the character set size
    """
    if not s:
        return 0
        
    char_index = {}
    max_length = 0
    left = 0
    
    for right, char in enumerate(s):
        # If the character is already in the current window
        if char in char_index and char_index[char] >= left:
            # Move the left pointer to the right of the previous occurrence
            left = char_index[char] + 1
        
        # Update the last seen index of the character
        char_index[char] = right
        # Update the maximum length
        max_length = max(max_length, right - left + 1)
    
    return max_length

@validate_string_input
def longest_palindromic_substring(s: str) -> str:
    """
    Find the longest palindromic substring in a given string.
    
    Args:
        s: Input string
        
    Returns:
        The longest palindromic substring
        
    Time Complexity: O(n²)
    Space Complexity: O(1)
    """
    if not s:
        return ""
    
    start = 0
    max_length = 1
    n = len(s)
    
    # Helper function to expand around center
    def expand_around_center(left: int, right: int) -> int:
        while left >= 0 and right < n and s[left] == s[right]:
            left -= 1
            right += 1
        return right - left - 1  # (right - 1) - (left + 1) + 1
    
    for i in range(n):
        # Odd length palindrome
        len1 = expand_around_center(i, i)
        # Even length palindrome
        len2 = expand_around_center(i, i + 1)
        
        # Get the maximum length palindrome centered at i
        current_max = max(len1, len2)
        
        # Update the longest palindrome found so far
        if current_max > max_length:
            max_length = current_max
            start = i - (current_max - 1) // 2
    
    return s[start:start + max_length]

def group_anagrams(strs: List[str]) -> List[List[str]]:
    """
    Group anagrams together from a list of strings.
    
    Args:
        strs: List of strings to group
        
    Returns:
        List of grouped anagrams
        
    Time Complexity: O(n * k) where n is the number of strings and k is the maximum length of a string
    Space Complexity: O(n * k)
    """
    if not strs:
        return []
    
    anagrams = defaultdict(list)
    
    for s in strs:
        # Create a count array for each string
        count = [0] * 26
        for char in s:
            count[ord(char) - ord('a')] += 1
        # Use the count array as a tuple key in the dictionary
        anagrams[tuple(count)].append(s)
    
    return list(anagrams.values())

@validate_string_input
def is_valid_parentheses(s: str) -> bool:
    """
    Check if the input string has valid parentheses.
    
    Args:
        s: String containing only '(', ')', '{', '}', '[' and ']'
        
    Returns:
        True if the string has valid parentheses, False otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            # Pop the top element if it's a closing bracket
            top_element = stack.pop() if stack else '#'
            
            # If the mapping doesn't match, return False
            if mapping[char] != top_element:
                return False
        else:
            # Push opening bracket to stack
            stack.append(char)
    
    # If stack is empty, all brackets were matched
    return not stack

@validate_string_input
def min_window_substring(s: str, t: str) -> str:
    """
    Find the minimum window in s which will contain all the characters in t.
    
    Args:
        s: The string to search in
        t: The string containing characters to find
        
    Returns:
        The minimum window substring or an empty string if not found
        
    Time Complexity: O(|S| + |T|) where |S| and |T| are lengths of s and t
    Space Complexity: O(1) - fixed size arrays for character counting
    """
    if not s or not t or len(s) < len(t):
        return ""
    
    # Initialize character count for t
    t_count = [0] * 128
    for char in t:
        t_count[ord(char)] += 1
    
    required = len(t)  # Number of characters to match
    left = 0
    min_length = float('inf')
    min_left = 0
    
    # Sliding window approach
    for right in range(len(s)):
        # If current character is in t, decrement required
        if t_count[ord(s[right])] > 0:
            required -= 1
        t_count[ord(s[right])] -= 1
        
        # When we've found a valid window, try to minimize it from the left
        while required == 0:
            # Update the minimum window
            if right - left + 1 < min_length:
                min_length = right - left + 1
                min_left = left
            
            # Move left pointer to try to find a smaller window
            t_count[ord(s[left])] += 1
            if t_count[ord(s[left])] > 0:
                required += 1
            left += 1
    
    return "" if min_length == float('inf') else s[min_left:min_left + min_length]

@validate_string_input
def reverse_string(s: str) -> str:
    """
    Reverse a string.
    
    Args:
        s: Input string
        
    Returns:
        Reversed string
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    return s[::-1]

@validate_string_input
def first_unique_char(s: str) -> int:
    """
    Find the first non-repeating character in a string and return its index.
    
    Args:
        s: Input string
        
    Returns:
        Index of the first unique character, or -1 if not found
        
    Time Complexity: O(n)
    Space Complexity: O(1) - at most 26 characters
    """
    char_count = {}
    
    # Count frequency of each character
    for char in s:
        char_count[char] = char_count.get(char, 0) + 1
    
    # Find the first character with count 1
    for i, char in enumerate(s):
        if char_count[char] == 1:
            return i
    
    return -1

def valid_anagram(s: str, t: str) -> bool:
    """
    Check if two strings are anagrams of each other.
    
    Args:
        s: First string
        t: Second string
        
    Returns:
        True if the strings are anagrams, False otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(1) - at most 26 characters
    """
    if len(s) != len(t):
        return False
    
    return sorted(s) == sorted(t)
