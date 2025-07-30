"""
Bit manipulation patterns for AlgoZen.

This module provides various bit manipulation techniques and algorithms.
"""
from typing import List


def count_set_bits(n: int) -> int:
    """Count number of set bits in integer.
    
    Time Complexity: O(log n)
    Space Complexity: O(1)
    """
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count


def count_set_bits_brian_kernighan(n: int) -> int:
    """Count set bits using Brian Kernighan's algorithm.
    
    Time Complexity: O(number of set bits)
    Space Complexity: O(1)
    """
    count = 0
    while n:
        n &= n - 1  # Clear the lowest set bit
        count += 1
    return count


def is_power_of_two(n: int) -> bool:
    """Check if number is power of 2.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return n > 0 and (n & (n - 1)) == 0


def find_single_number(nums: List[int]) -> int:
    """Find single number in array where others appear twice.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    result = 0
    for num in nums:
        result ^= num
    return result


def find_two_single_numbers(nums: List[int]) -> List[int]:
    """Find two single numbers where others appear twice.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    xor_all = 0
    for num in nums:
        xor_all ^= num
    
    # Find rightmost set bit
    rightmost_bit = xor_all & (-xor_all)
    
    num1 = num2 = 0
    for num in nums:
        if num & rightmost_bit:
            num1 ^= num
        else:
            num2 ^= num
    
    return [num1, num2]


def find_single_number_three_times(nums: List[int]) -> int:
    """Find single number where others appear three times.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    ones = twos = 0
    
    for num in nums:
        ones = (ones ^ num) & ~twos
        twos = (twos ^ num) & ~ones
    
    return ones


def reverse_bits(n: int) -> int:
    """Reverse bits of 32-bit integer.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result


def hamming_distance(x: int, y: int) -> int:
    """Calculate Hamming distance between two integers.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return count_set_bits_brian_kernighan(x ^ y)


def total_hamming_distance(nums: List[int]) -> int:
    """Calculate total Hamming distance between all pairs.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    total = 0
    n = len(nums)
    
    for i in range(32):
        ones = sum((num >> i) & 1 for num in nums)
        zeros = n - ones
        total += ones * zeros
    
    return total


def subsets_using_bits(nums: List[int]) -> List[List[int]]:
    """Generate all subsets using bit manipulation.
    
    Time Complexity: O(n * 2^n)
    Space Complexity: O(n * 2^n)
    """
    n = len(nums)
    result = []
    
    for mask in range(1 << n):
        subset = []
        for i in range(n):
            if mask & (1 << i):
                subset.append(nums[i])
        result.append(subset)
    
    return result


def gray_code(n: int) -> List[int]:
    """Generate Gray code sequence.
    
    Time Complexity: O(2^n)
    Space Complexity: O(2^n)
    """
    result = [0]
    
    for i in range(n):
        # Add MSB to existing codes in reverse order
        for j in range(len(result) - 1, -1, -1):
            result.append(result[j] | (1 << i))
    
    return result


def maximum_xor_pair(nums: List[int]) -> int:
    """Find maximum XOR of any two numbers using Trie.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    class TrieNode:
        def __init__(self):
            self.children = {}
    
    root = TrieNode()
    
    # Insert all numbers into Trie
    for num in nums:
        node = root
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            if bit not in node.children:
                node.children[bit] = TrieNode()
            node = node.children[bit]
    
    max_xor = 0
    
    # Find maximum XOR for each number
    for num in nums:
        node = root
        current_xor = 0
        
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            toggled_bit = 1 - bit
            
            if toggled_bit in node.children:
                current_xor |= (1 << i)
                node = node.children[toggled_bit]
            else:
                node = node.children[bit]
        
        max_xor = max(max_xor, current_xor)
    
    return max_xor


def count_bits_range(n: int) -> List[int]:
    """Count bits for numbers 0 to n.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    result = [0] * (n + 1)
    
    for i in range(1, n + 1):
        result[i] = result[i >> 1] + (i & 1)
    
    return result


def bitwise_and_range(left: int, right: int) -> int:
    """Bitwise AND of numbers in range [left, right].
    
    Time Complexity: O(log n)
    Space Complexity: O(1)
    """
    shift = 0
    while left != right:
        left >>= 1
        right >>= 1
        shift += 1
    
    return left << shift


def minimum_flips_to_make_or(a: int, b: int, c: int) -> int:
    """Minimum flips to make a | b == c.
    
    Time Complexity: O(log max(a,b,c))
    Space Complexity: O(1)
    """
    flips = 0
    
    while a or b or c:
        bit_a = a & 1
        bit_b = b & 1
        bit_c = c & 1
        
        if bit_c == 0:
            flips += bit_a + bit_b
        else:
            if bit_a == 0 and bit_b == 0:
                flips += 1
        
        a >>= 1
        b >>= 1
        c >>= 1
    
    return flips


def xor_queries_subarray(arr: List[int], queries: List[List[int]]) -> List[int]:
    """Answer XOR queries on subarrays.
    
    Time Complexity: O(n + q)
    Space Complexity: O(n)
    """
    n = len(arr)
    prefix_xor = [0] * (n + 1)
    
    for i in range(n):
        prefix_xor[i + 1] = prefix_xor[i] ^ arr[i]
    
    result = []
    for left, right in queries:
        result.append(prefix_xor[right + 1] ^ prefix_xor[left])
    
    return result


def decode_xored_array(encoded: List[int], first: int) -> List[int]:
    """Decode XORed array given first element.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    result = [first]
    
    for i in range(len(encoded)):
        result.append(result[-1] ^ encoded[i])
    
    return result