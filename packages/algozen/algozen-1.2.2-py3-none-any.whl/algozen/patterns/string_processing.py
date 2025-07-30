"""
Advanced string processing patterns for AlgoZen.

This module provides various advanced string processing algorithms.
"""
from typing import List, Dict, Tuple, Set
from collections import defaultdict, deque


def suffix_array(s: str) -> List[int]:
    """Build suffix array using radix sort.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    n = len(s)
    suffixes = [(s[i:], i) for i in range(n)]
    suffixes.sort()
    return [suffix[1] for suffix in suffixes]


def lcp_array(s: str, sa: List[int]) -> List[int]:
    """Build LCP array from suffix array.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    n = len(s)
    rank = [0] * n
    for i in range(n):
        rank[sa[i]] = i
    
    lcp = [0] * (n - 1)
    h = 0
    
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i] - 1] = h
            if h > 0:
                h -= 1
    
    return lcp


def aho_corasick(patterns: List[str]) -> Dict:
    """Build Aho-Corasick automaton for multiple pattern matching.
    
    Time Complexity: O(sum of pattern lengths)
    Space Complexity: O(sum of pattern lengths)
    """
    class TrieNode:
        def __init__(self):
            self.children = {}
            self.failure = None
            self.output = []
    
    root = TrieNode()
    
    # Build trie
    for i, pattern in enumerate(patterns):
        node = root
        for char in pattern:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.output.append(i)
    
    # Build failure links
    queue = deque()
    for child in root.children.values():
        child.failure = root
        queue.append(child)
    
    while queue:
        node = queue.popleft()
        
        for char, child in node.children.items():
            queue.append(child)
            
            # Find failure link
            failure = node.failure
            while failure and char not in failure.children:
                failure = failure.failure
            
            child.failure = failure.children.get(char, root) if failure else root
            child.output.extend(child.failure.output)
    
    return {'root': root, 'patterns': patterns}


def search_multiple_patterns(text: str, automaton: Dict) -> List[Tuple[int, int]]:
    """Search multiple patterns using Aho-Corasick.
    
    Time Complexity: O(n + m + z) where z is number of matches
    Space Complexity: O(1)
    """
    root = automaton['root']
    patterns = automaton['patterns']
    matches = []
    
    node = root
    for i, char in enumerate(text):
        while node and char not in node.children:
            node = node.failure
        
        node = node.children.get(char, root) if node else root
        
        for pattern_idx in node.output:
            pattern_len = len(patterns[pattern_idx])
            start_pos = i - pattern_len + 1
            matches.append((start_pos, pattern_idx))
    
    return matches


def longest_repeated_substring(s: str) -> str:
    """Find longest repeated substring using suffix array.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not s:
        return ""
    
    sa = suffix_array(s)
    lcp = lcp_array(s, sa)
    
    max_len = 0
    max_idx = 0
    
    for i, length in enumerate(lcp):
        if length > max_len:
            max_len = length
            max_idx = sa[i]
    
    return s[max_idx:max_idx + max_len]


def minimum_window_substring(s: str, t: str) -> str:
    """Find minimum window substring containing all characters of t.
    
    Time Complexity: O(|s| + |t|)
    Space Complexity: O(|t|)
    """
    if not s or not t:
        return ""
    
    dict_t = defaultdict(int)
    for char in t:
        dict_t[char] += 1
    
    required = len(dict_t)
    left = right = 0
    formed = 0
    window_counts = defaultdict(int)
    
    ans = float('inf'), None, None
    
    while right < len(s):
        char = s[right]
        window_counts[char] += 1
        
        if char in dict_t and window_counts[char] == dict_t[char]:
            formed += 1
        
        while left <= right and formed == required:
            char = s[left]
            
            if right - left + 1 < ans[0]:
                ans = (right - left + 1, left, right)
            
            window_counts[char] -= 1
            if char in dict_t and window_counts[char] < dict_t[char]:
                formed -= 1
            
            left += 1
        
        right += 1
    
    return "" if ans[0] == float('inf') else s[ans[1]:ans[2] + 1]


def palindromic_substrings_count(s: str) -> int:
    """Count all palindromic substrings using expand around centers.
    
    Time Complexity: O(n²)
    Space Complexity: O(1)
    """
    def expand_around_center(left: int, right: int) -> int:
        count = 0
        while left >= 0 and right < len(s) and s[left] == s[right]:
            count += 1
            left -= 1
            right += 1
        return count
    
    total = 0
    for i in range(len(s)):
        # Odd length palindromes
        total += expand_around_center(i, i)
        # Even length palindromes
        total += expand_around_center(i, i + 1)
    
    return total


def string_compression(chars: List[str]) -> int:
    """Compress string array in-place.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    write = 0
    i = 0
    
    while i < len(chars):
        char = chars[i]
        count = 1
        
        while i + count < len(chars) and chars[i + count] == char:
            count += 1
        
        chars[write] = char
        write += 1
        
        if count > 1:
            for digit in str(count):
                chars[write] = digit
                write += 1
        
        i += count
    
    return write


def group_anagrams(strs: List[str]) -> List[List[str]]:
    """Group anagrams together.
    
    Time Complexity: O(n * k log k) where k is max string length
    Space Complexity: O(n * k)
    """
    anagram_map = defaultdict(list)
    
    for s in strs:
        key = ''.join(sorted(s))
        anagram_map[key].append(s)
    
    return list(anagram_map.values())


def longest_substring_k_distinct(s: str, k: int) -> int:
    """Find longest substring with at most k distinct characters.
    
    Time Complexity: O(n)
    Space Complexity: O(k)
    """
    if k == 0:
        return 0
    
    left = 0
    max_len = 0
    char_count = defaultdict(int)
    
    for right in range(len(s)):
        char_count[s[right]] += 1
        
        while len(char_count) > k:
            char_count[s[left]] -= 1
            if char_count[s[left]] == 0:
                del char_count[s[left]]
            left += 1
        
        max_len = max(max_len, right - left + 1)
    
    return max_len


def decode_string(s: str) -> str:
    """Decode string with nested brackets and numbers.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    stack = []
    current_string = ""
    current_num = 0
    
    for char in s:
        if char.isdigit():
            current_num = current_num * 10 + int(char)
        elif char == '[':
            stack.append((current_string, current_num))
            current_string = ""
            current_num = 0
        elif char == ']':
            prev_string, num = stack.pop()
            current_string = prev_string + current_string * num
        else:
            current_string += char
    
    return current_string


def valid_parentheses_score(s: str) -> int:
    """Calculate score of valid parentheses string.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    stack = [0]
    
    for char in s:
        if char == '(':
            stack.append(0)
        else:  # char == ')'
            v = stack.pop()
            stack[-1] += max(2 * v, 1)
    
    return stack[0]


def text_justification(words: List[str], max_width: int) -> List[str]:
    """Justify text to given width.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    result = []
    i = 0
    
    while i < len(words):
        # Find words that fit in current line
        line_words = [words[i]]
        line_length = len(words[i])
        i += 1
        
        while i < len(words) and line_length + 1 + len(words[i]) <= max_width:
            line_words.append(words[i])
            line_length += 1 + len(words[i])
            i += 1
        
        # Justify the line
        if i == len(words) or len(line_words) == 1:
            # Last line or single word - left justify
            line = ' '.join(line_words)
            line += ' ' * (max_width - len(line))
        else:
            # Distribute spaces evenly
            total_spaces = max_width - sum(len(word) for word in line_words)
            gaps = len(line_words) - 1
            
            line = ""
            for j in range(len(line_words) - 1):
                line += line_words[j]
                spaces = total_spaces // gaps
                if j < total_spaces % gaps:
                    spaces += 1
                line += ' ' * spaces
                gaps -= 1
                total_spaces -= spaces
            line += line_words[-1]
        
        result.append(line)
    
    return result