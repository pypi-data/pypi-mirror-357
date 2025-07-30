"""
Backtracking Problems and Solutions.

This module contains implementations of common backtracking problems.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Set, Any, TypeVar, Callable, Generic
from functools import wraps
import copy

T = TypeVar('T')

def validate_input(func: Callable) -> Callable:
    """Decorator to validate input for backtracking problems."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)
    return wrapper

@validate_input
def subsets(nums: List[int]) -> List[List[int]]:
    """
    Generate all possible subsets (the power set) of a set of distinct integers.
    
    Args:
        nums: List of distinct integers
        
    Returns:
        List of all possible subsets
        
    Time Complexity: O(n * 2^n)
    Space Complexity: O(n * 2^n)
    """
    result = []
    
    def backtrack(start: int, path: List[int]) -> None:
        result.append(path.copy())
        
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    
    backtrack(0, [])
    return result

@validate_input
def permutations(nums: List[int]) -> List[List[int]]:
    """
    Generate all possible permutations of a list of distinct integers.
    
    Args:
        nums: List of distinct integers
        
    Returns:
        List of all possible permutations
        
    Time Complexity: O(n! * n)
    Space Complexity: O(n! * n)
    """
    result = []
    used = [False] * len(nums)
    
    def backtrack(path: List[int]) -> None:
        if len(path) == len(nums):
            result.append(path.copy())
            return
            
        for i in range(len(nums)):
            if not used[i]:
                used[i] = True
                path.append(nums[i])
                backtrack(path)
                path.pop()
                used[i] = False
    
    backtrack([])
    return result

@validate_input
def combination_sum(candidates: List[int], target: int) -> List[List[int]]:
    """
    Find all unique combinations of candidates that sum to target.
    The same number may be chosen from candidates an unlimited number of times.
    
    Args:
        candidates: List of distinct integers
        target: Target sum
        
    Returns:
        List of all unique combinations that sum to target
        
    Time Complexity: O(2^t) where t is the target value
    Space Complexity: O(n) for recursion stack
    """
    result = []
    
    def backtrack(start: int, path: List[int], remaining: int) -> None:
        if remaining == 0:
            result.append(path.copy())
            return
        
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                continue
            path.append(candidates[i])
            backtrack(i, path, remaining - candidates[i])
            path.pop()
    
    backtrack(0, [], target)
    return result

@validate_input
def palindrome_partitioning(s: str) -> List[List[str]]:
    """
    Partition a string such that every substring is a palindrome.
    
    Args:
        s: Input string
        
    Returns:
        List of all possible palindrome partitioning
        
    Time Complexity: O(n * 2^n)
    Space Complexity: O(n^2)
    """
    result = []
    n = len(s)
    
    # Pre-process to check if s[i..j] is palindrome
    dp = [[False] * n for _ in range(n)]
    
    for i in range(n-1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i <= 2 or dp[i+1][j-1]):
                dp[i][j] = True
    
    def backtrack(start: int, path: List[str]) -> None:
        if start == n:
            result.append(path.copy())
            return
            
        for end in range(start, n):
            if dp[start][end]:
                path.append(s[start:end+1])
                backtrack(end + 1, path)
                path.pop()
    
    backtrack(0, [])
    return result

@validate_input
def solve_n_queens(n: int) -> List[List[str]]:
    """
    Solve the N-Queens puzzle.
    
    Args:
        n: Size of the chessboard (n x n)
        
    Returns:
        List of all distinct solutions to the n-queens puzzle
        
    Time Complexity: O(n!)
    Space Complexity: O(n^2)
    """
    result = []
    board = [['.'] * n for _ in range(n)]
    
    def is_valid(row: int, col: int) -> bool:
        # Check column
        for i in range(row):
            if board[i][col] == 'Q':
                return False
        
        # Check upper left diagonal
        i, j = row - 1, col - 1
        while i >= 0 and j >= 0:
            if board[i][j] == 'Q':
                return False
            i -= 1
            j -= 1
        
        # Check upper right diagonal
        i, j = row - 1, col + 1
        while i >= 0 and j < n:
            if board[i][j] == 'Q':
                return False
            i -= 1
            j += 1
            
        return True
    
    def backtrack(row: int) -> None:
        if row == n:
            result.append([''.join(row) for row in board])
            return
            
        for col in range(n):
            if is_valid(row, col):
                board[row][col] = 'Q'
                backtrack(row + 1)
                board[row][col] = '.'
    
    backtrack(0)
    return result

@validate_input
def generate_parentheses(n: int) -> List[str]:
    """
    Generate all combinations of well-formed parentheses.
    
    Args:
        n: Number of pairs of parentheses
        
    Returns:
        List of all valid combinations
        
    Time Complexity: O(4^n / sqrt(n))
    Space Complexity: O(n) for recursion stack
    """
    result = []
    
    def backtrack(open_count: int, close_count: int, path: str) -> None:
        if len(path) == 2 * n:
            result.append(path)
            return
            
        if open_count < n:
            backtrack(open_count + 1, close_count, path + '(')
            
        if close_count < open_count:
            backtrack(open_count, close_count + 1, path + ')')
    
    backtrack(0, 0, '')
    return result

@validate_input
def letter_combinations(digits: str) -> List[str]:
    """
    Generate all possible letter combinations from phone number digits.
    
    Args:
        digits: String containing digits from 2-9
        
    Returns:
        List of all possible letter combinations
        
    Time Complexity: O(4^n * n) where n is the number of digits
    Space Complexity: O(n) for recursion stack
    """
    if not digits:
        return []
    
    digit_to_letters = {
        '2': 'abc',
        '3': 'def',
        '4': 'ghi',
        '5': 'jkl',
        '6': 'mno',
        '7': 'pqrs',
        '8': 'tuv',
        '9': 'wxyz'
    }
    
    result = []
    
    def backtrack(index: int, path: str) -> None:
        if index == len(digits):
            result.append(path)
            return
            
        current_digit = digits[index]
        for letter in digit_to_letters[current_digit]:
            backtrack(index + 1, path + letter)
    
    backtrack(0, '')
    return result

@validate_input
def combination_sum_iii(k: int, n: int) -> List[List[int]]:
    """
    Find all possible combinations of k numbers that add up to n.
    Only numbers 1 through 9 can be used and each combination should be unique.
    
    Args:
        k: Number of digits in the combination
        n: Target sum
        
    Returns:
        List of all valid combinations
        
    Time Complexity: O(9! * k / (9 - k)!)
    Space Complexity: O(k) for recursion stack
    """
    result = []
    
    def backtrack(start: int, path: List[int], remaining: int) -> None:
        if len(path) == k and remaining == 0:
            result.append(path.copy())
            return
            
        for num in range(start, 10):
            if num > remaining:
                break
            path.append(num)
            backtrack(num + 1, path, remaining - num)
            path.pop()
    
    backtrack(1, [], n)
    return result

@validate_input
def word_search(board: List[List[str]], word: str) -> bool:
    """
    Determine if the word exists in the grid.
    
    Args:
        board: 2D grid of characters
        word: Word to search for
        
    Returns:
        True if word exists in the grid, False otherwise
        
    Time Complexity: O(m * n * 4^l) where l is the length of the word
    Space Complexity: O(l) for recursion stack
    """
    if not board or not board[0]:
        return False
    
    m, n = len(board), len(board[0])
    
    def dfs(i: int, j: int, index: int) -> bool:
        if index == len(word):
            return True
            
        if i < 0 or i >= m or j < 0 or j >= n or board[i][j] != word[index]:
            return False
            
        # Mark the cell as visited by changing its content
        temp = board[i][j]
        board[i][j] = '#'
        
        # Explore all 4 directions
        found = (dfs(i+1, j, index+1) or
                dfs(i-1, j, index+1) or
                dfs(i, j+1, index+1) or
                dfs(i, j-1, index+1))
        
        # Backtrack: restore the cell's content
        board[i][j] = temp
        return found
    
    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):
                return True
    
    return False

@validate_input
def restore_ip_addresses(s: str) -> List[str]:
    """
    Restore all possible valid IP address combinations from a string.
    
    Args:
        s: String containing only digits
        
    Returns:
        List of all possible valid IP address combinations
        
    Time Complexity: O(3^4) = O(1) since the maximum depth is 4
    Space Complexity: O(1) since the number of results is limited
    """
    result = []
    
    def backtrack(start: int, parts: List[str]) -> None:
        if len(parts) == 4 and start == len(s):
            result.append('.'.join(parts))
            return
            
        if len(parts) == 4 or start == len(s):
            return
            
        # Try 1, 2, or 3 digit numbers
        for length in range(1, 4):
            if start + length > len(s):
                continue
                
            segment = s[start:start+length]
            
            # Check for leading zeros and valid range
            if (len(segment) > 1 and segment[0] == '0') or int(segment) > 255:
                continue
                
            parts.append(segment)
            backtrack(start + length, parts)
            parts.pop()
    
    backtrack(0, [])
    return result
