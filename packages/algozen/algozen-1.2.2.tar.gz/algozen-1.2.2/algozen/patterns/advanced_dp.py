"""
Advanced Dynamic Programming patterns for AlgoZen.

This module provides various advanced DP patterns and optimizations.
"""
from typing import List, Dict, Tuple
from functools import lru_cache


def matrix_chain_multiplication(dimensions: List[int]) -> int:
    """Find minimum scalar multiplications for matrix chain.
    
    Time Complexity: O(n³)
    Space Complexity: O(n²)
    """
    n = len(dimensions) - 1
    dp = [[0] * n for _ in range(n)]
    
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            
            for k in range(i, j):
                cost = (dp[i][k] + dp[k+1][j] + 
                       dimensions[i] * dimensions[k+1] * dimensions[j+1])
                dp[i][j] = min(dp[i][j], cost)
    
    return dp[0][n-1]


def longest_palindromic_subsequence(s: str) -> int:
    """Find length of longest palindromic subsequence.
    
    Time Complexity: O(n²)
    Space Complexity: O(n²)
    """
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    
    # Single characters are palindromes
    for i in range(n):
        dp[i][i] = 1
    
    # Check for palindromes of length 2 and more
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            
            if s[i] == s[j]:
                if length == 2:
                    dp[i][j] = 2
                else:
                    dp[i][j] = dp[i+1][j-1] + 2
            else:
                dp[i][j] = max(dp[i+1][j], dp[i][j-1])
    
    return dp[0][n-1]


def palindrome_partitioning_min_cuts(s: str) -> int:
    """Find minimum cuts needed for palindrome partitioning.
    
    Time Complexity: O(n²)
    Space Complexity: O(n²)
    """
    n = len(s)
    
    # Precompute palindrome table
    is_palindrome = [[False] * n for _ in range(n)]
    
    for i in range(n):
        is_palindrome[i][i] = True
    
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                if length == 2:
                    is_palindrome[i][j] = True
                else:
                    is_palindrome[i][j] = is_palindrome[i+1][j-1]
    
    # DP for minimum cuts
    cuts = [0] * n
    
    for i in range(1, n):
        if is_palindrome[0][i]:
            cuts[i] = 0
        else:
            cuts[i] = float('inf')
            for j in range(i):
                if is_palindrome[j+1][i]:
                    cuts[i] = min(cuts[i], cuts[j] + 1)
    
    return cuts[n-1]


def distinct_subsequences(s: str, t: str) -> int:
    """Count distinct subsequences of s that equal t.
    
    Time Complexity: O(mn)
    Space Complexity: O(mn)
    """
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Empty string has one subsequence in any string
    for i in range(m + 1):
        dp[i][0] = 1
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i-1][j]
            if s[i-1] == t[j-1]:
                dp[i][j] += dp[i-1][j-1]
    
    return dp[m][n]


def interleaving_string(s1: str, s2: str, s3: str) -> bool:
    """Check if s3 is interleaving of s1 and s2.
    
    Time Complexity: O(mn)
    Space Complexity: O(mn)
    """
    m, n, l = len(s1), len(s2), len(s3)
    
    if m + n != l:
        return False
    
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    
    # Fill first row
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j-1] and s2[j-1] == s3[j-1]
    
    # Fill first column
    for i in range(1, m + 1):
        dp[i][0] = dp[i-1][0] and s1[i-1] == s3[i-1]
    
    # Fill the rest
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = ((dp[i-1][j] and s1[i-1] == s3[i+j-1]) or
                       (dp[i][j-1] and s2[j-1] == s3[i+j-1]))
    
    return dp[m][n]


def regular_expression_matching(s: str, p: str) -> bool:
    """Check if string matches pattern with . and *.
    
    Time Complexity: O(mn)
    Space Complexity: O(mn)
    """
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    
    dp[0][0] = True
    
    # Handle patterns like a*, a*b*, a*b*c*
    for j in range(2, n + 1):
        if p[j-1] == '*':
            dp[0][j] = dp[0][j-2]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j-1] == '*':
                # Zero occurrences
                dp[i][j] = dp[i][j-2]
                # One or more occurrences
                if p[j-2] == '.' or p[j-2] == s[i-1]:
                    dp[i][j] = dp[i][j] or dp[i-1][j]
            elif p[j-1] == '.' or p[j-1] == s[i-1]:
                dp[i][j] = dp[i-1][j-1]
    
    return dp[m][n]


def wildcard_matching(s: str, p: str) -> bool:
    """Check if string matches pattern with ? and *.
    
    Time Complexity: O(mn)
    Space Complexity: O(mn)
    """
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    
    dp[0][0] = True
    
    # Handle leading *
    for j in range(1, n + 1):
        if p[j-1] == '*':
            dp[0][j] = dp[0][j-1]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j-1] == '*':
                dp[i][j] = dp[i-1][j] or dp[i][j-1]
            elif p[j-1] == '?' or p[j-1] == s[i-1]:
                dp[i][j] = dp[i-1][j-1]
    
    return dp[m][n]


def burst_balloons(nums: List[int]) -> int:
    """Maximum coins from bursting balloons.
    
    Time Complexity: O(n³)
    Space Complexity: O(n²)
    """
    # Add boundary balloons
    balloons = [1] + nums + [1]
    n = len(balloons)
    
    dp = [[0] * n for _ in range(n)]
    
    for length in range(3, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1
            
            for k in range(left + 1, right):
                coins = (balloons[left] * balloons[k] * balloons[right] +
                        dp[left][k] + dp[k][right])
                dp[left][right] = max(dp[left][right], coins)
    
    return dp[0][n-1]


def stone_game_range(stones: List[int]) -> int:
    """Minimum cost to merge stones in range.
    
    Time Complexity: O(n³)
    Space Complexity: O(n²)
    """
    n = len(stones)
    prefix_sum = [0] * (n + 1)
    
    for i in range(n):
        prefix_sum[i + 1] = prefix_sum[i] + stones[i]
    
    dp = [[0] * n for _ in range(n)]
    
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            
            for k in range(i, j):
                cost = (dp[i][k] + dp[k+1][j] + 
                       prefix_sum[j+1] - prefix_sum[i])
                dp[i][j] = min(dp[i][j], cost)
    
    return dp[0][n-1]


def count_vowel_permutation(n: int) -> int:
    """Count vowel permutations of length n with rules.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    MOD = 10**9 + 7
    
    # a, e, i, o, u
    dp = [1, 1, 1, 1, 1]
    
    for _ in range(n - 1):
        new_dp = [0] * 5
        new_dp[0] = (dp[1] + dp[2] + dp[4]) % MOD  # a follows e, i, u
        new_dp[1] = (dp[0] + dp[2]) % MOD          # e follows a, i
        new_dp[2] = (dp[1] + dp[3]) % MOD          # i follows e, o
        new_dp[3] = dp[2] % MOD                    # o follows i
        new_dp[4] = (dp[2] + dp[3]) % MOD          # u follows i, o
        dp = new_dp
    
    return sum(dp) % MOD