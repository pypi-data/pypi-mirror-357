"""
String algorithms implementation for AlgoZen.

This module provides various string matching and processing algorithms.
"""
from typing import List, Tuple, Optional


def kmp_search(text: str, pattern: str) -> List[int]:
    """Find all occurrences of pattern in text using KMP algorithm.
    
    Args:
        text: Text to search in
        pattern: Pattern to search for
        
    Returns:
        List of starting indices where pattern occurs
        
    Time Complexity: O(n + m) where n = len(text), m = len(pattern)
    Space Complexity: O(m)
    """
    if not pattern:
        return []
    
    # Build failure function (LPS array)
    lps = _build_lps(pattern)
    
    matches = []
    i = j = 0  # i for text, j for pattern
    
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
        
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return matches


def _build_lps(pattern: str) -> List[int]:
    """Build Longest Proper Prefix which is also Suffix array.
    
    Args:
        pattern: Pattern string
        
    Returns:
        LPS array for the pattern
    """
    m = len(pattern)
    lps = [0] * m
    length = 0  # length of previous longest prefix suffix
    i = 1
    
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    
    return lps


def rabin_karp_search(text: str, pattern: str, prime: int = 101) -> List[int]:
    """Find all occurrences using Rabin-Karp rolling hash algorithm.
    
    Args:
        text: Text to search in
        pattern: Pattern to search for
        prime: Prime number for hashing
        
    Returns:
        List of starting indices where pattern occurs
        
    Time Complexity: O(n + m) average, O(nm) worst case
    Space Complexity: O(1)
    """
    if not pattern or len(pattern) > len(text):
        return []
    
    n, m = len(text), len(pattern)
    base = 256  # Number of characters in alphabet
    h = pow(base, m - 1) % prime  # Hash value for removing leading digit
    
    pattern_hash = text_hash = 0
    matches = []
    
    # Calculate hash for pattern and first window of text
    for i in range(m):
        pattern_hash = (base * pattern_hash + ord(pattern[i])) % prime
        text_hash = (base * text_hash + ord(text[i])) % prime
    
    # Slide pattern over text
    for i in range(n - m + 1):
        # Check if hash values match
        if pattern_hash == text_hash:
            # Check characters one by one
            if text[i:i + m] == pattern:
                matches.append(i)
        
        # Calculate hash for next window
        if i < n - m:
            text_hash = (base * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % prime
            if text_hash < 0:
                text_hash += prime
    
    return matches


def z_algorithm(s: str) -> List[int]:
    """Compute Z array for string s using Z algorithm.
    
    Z[i] = length of longest substring starting from s[i] which is also prefix of s
    
    Args:
        s: Input string
        
    Returns:
        Z array
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    n = len(s)
    z = [0] * n
    l = r = 0
    
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    
    return z


def manacher_palindromes(s: str) -> List[int]:
    """Find all palindromic substrings using Manacher's algorithm.
    
    Args:
        s: Input string
        
    Returns:
        Array where result[i] = radius of longest palindrome centered at i
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    # Transform string: "abc" -> "^#a#b#c#$"
    transformed = "^#" + "#".join(s) + "#$"
    n = len(transformed)
    p = [0] * n  # palindrome radius array
    center = right = 0
    
    for i in range(1, n - 1):
        # Mirror of i with respect to center
        mirror = 2 * center - i
        
        if i < right:
            p[i] = min(right - i, p[mirror])
        
        # Try to expand palindrome centered at i
        while transformed[i + p[i] + 1] == transformed[i - p[i] - 1]:
            p[i] += 1
        
        # If palindrome centered at i extends past right, adjust center and right
        if i + p[i] > right:
            center, right = i, i + p[i]
    
    return p


def longest_common_prefix(strs: List[str]) -> str:
    """Find the longest common prefix among array of strings.
    
    Args:
        strs: List of strings
        
    Returns:
        Longest common prefix
        
    Time Complexity: O(S) where S is sum of all characters
    Space Complexity: O(1)
    """
    if not strs:
        return ""
    
    prefix = strs[0]
    for s in strs[1:]:
        i = 0
        while i < len(prefix) and i < len(s) and prefix[i] == s[i]:
            i += 1
        prefix = prefix[:i]
        if not prefix:
            break
    
    return prefix


def edit_distance_operations(word1: str, word2: str) -> List[str]:
    """Get the sequence of operations to transform word1 to word2.
    
    Args:
        word1: Source string
        word2: Target string
        
    Returns:
        List of operations needed
        
    Time Complexity: O(mn)
    Space Complexity: O(mn)
    """
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    # Backtrack to find operations
    operations = []
    i, j = m, n
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and word1[i-1] == word2[j-1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
            operations.append(f"Replace '{word1[i-1]}' with '{word2[j-1]}' at position {i-1}")
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            operations.append(f"Delete '{word1[i-1]}' at position {i-1}")
            i -= 1
        else:
            operations.append(f"Insert '{word2[j-1]}' at position {i}")
            j -= 1
    
    return operations[::-1]