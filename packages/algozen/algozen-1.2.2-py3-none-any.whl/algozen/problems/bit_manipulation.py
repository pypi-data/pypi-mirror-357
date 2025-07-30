"""
Bit Manipulation Problems and Solutions.

This module contains implementations of common bit manipulation problems.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Set, Any, TypeVar, Callable, Generic
from functools import wraps

T = TypeVar('T')

def validate_input(func: Callable) -> Callable:
    """Decorator to validate input for bit manipulation problems."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)
    return wrapper

@validate_input
def count_set_bits(n: int) -> int:
    """
    Count the number of set bits (1s) in the binary representation of a number.
    
    Args:
        n: Integer number
        
    Returns:
        Number of set bits in the binary representation of n
        
    Time Complexity: O(1) - as the number of bits is fixed (32 or 64)
    Space Complexity: O(1)
    """
    count = 0
    while n:
        n &= n - 1  # This clears the least significant set bit
        count += 1
    return count

@validate_input
def find_single_number(nums: List[int]) -> int:
    """
    Find the single number in an array where every element appears twice except for one.
    
    Args:
        nums: List of integers where every element appears twice except for one
        
    Returns:
        The single number that appears only once
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    result = 0
    for num in nums:
        result ^= num
    return result

@validate_input
def get_bit(num: int, i: int) -> bool:
    """
    Get the bit at position i (0-based from the right) in num.
    
    Args:
        num: The number
        i: Bit position (0-based from the right)
        
    Returns:
        True if the bit is set (1), False otherwise
        
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return (num & (1 << i)) != 0

@validate_input
def set_bit(num: int, i: int) -> int:
    """
    Set the bit at position i (0-based from the right) in num to 1.
    
    Args:
        num: The number
        i: Bit position (0-based from the right)
        
    Returns:
        The number with the bit set
        
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return num | (1 << i)

@validate_input
def clear_bit(num: int, i: int) -> int:
    """
    Clear the bit at position i (0-based from the right) in num (set to 0).
    
    Args:
        num: The number
        i: Bit position (0-based from the right)
        
    Returns:
        The number with the bit cleared
        
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    mask = ~(1 << i)
    return num & mask

@validate_input
def update_bit(num: int, i: int, bit_is_1: bool) -> int:
    """
    Update the bit at position i (0-based from the right) to the specified value.
    
    Args:
        num: The number
        i: Bit position (0-based from the right)
        bit_is_1: If True, set the bit to 1; if False, set to 0
        
    Returns:
        The number with the bit updated
        
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    value = 1 if bit_is_1 else 0
    mask = ~(1 << i)
    return (num & mask) | (value << i)

@validate_input
def toggle_bit(num: int, i: int) -> int:
    """
    Toggle the bit at position i (0-based from the right) in num.
    
    Args:
        num: The number
        i: Bit position (0-based from the right)
        
    Returns:
        The number with the bit toggled
        
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return num ^ (1 << i)

@validate_input
def is_power_of_two(n: int) -> bool:
    """
    Check if a number is a power of two.
    
    Args:
        n: The number to check
        
    Returns:
        True if n is a power of two, False otherwise
        
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    if n <= 0:
        return False
    return (n & (n - 1)) == 0

@validate_input
def find_missing_number(nums: List[int]) -> int:
    """
    Find the missing number in an array containing n distinct numbers 
    in the range [0, n].
    
    Args:
        nums: List of n distinct numbers in the range [0, n]
        
    Returns:
        The missing number
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    missing = len(nums)
    for i, num in enumerate(nums):
        missing ^= i ^ num
    return missing

@validate_input
def reverse_bits(n: int) -> int:
    """
    Reverse the bits of a 32-bit unsigned integer.
    
    Args:
        n: 32-bit unsigned integer
        
    Returns:
        The integer with its bits reversed
        
    Time Complexity: O(1) - always 32 iterations
    Space Complexity: O(1)
    """
    result = 0
    for i in range(32):
        # Shift result left and add the least significant bit of n
        result = (result << 1) | (n & 1)
        n >>= 1
    return result

@validate_input
def count_bits_range(n: int) -> List[int]:
    """
    Count the number of 1's in the binary representation of each number 
    from 0 to n (inclusive).
    
    Args:
        n: Non-negative integer
        
    Returns:
        A list where the element at index i is the count of 1's in the 
        binary representation of i
        
    Time Complexity: O(n)
    Space Complexity: O(n) for the result
    """
    result = [0] * (n + 1)
    for i in range(1, n + 1):
        # i & (i-1) drops the lowest set bit
        # So result[i] = result[i - (LSB)] + 1
        result[i] = result[i & (i - 1)] + 1
    return result

@validate_input
def single_number_ii(nums: List[int]) -> int:
    """
    Find the single number in an array where every element appears three times 
    except for one which appears exactly once.
    
    Args:
        nums: List of integers where every element appears three times except for one
        
    Returns:
        The single number that appears only once
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    ones = 0  # Tracks bits that have appeared once
    twos = 0  # Tracks bits that have appeared twice
    
    for num in nums:
        # Update 'twos' by adding the bits that have appeared twice
        twos |= (ones & num)
        
        # Update 'ones' using XOR to toggle bits that have appeared once
        ones ^= num
        
        # Bits that have appeared three times are in both 'ones' and 'twos'
        common_bits = ones & twos
        
        # Remove bits that have appeared three times from both 'ones' and 'twos'
        ones &= ~common_bits
        twos &= ~common_bits
    
    return ones

@validate_input
def single_number_iii(nums: List[int]) -> List[int]:
    """
    Find the two numbers that appear only once in an array where every other 
    number appears exactly twice.
    
    Args:
        nums: List of integers where every element appears twice except for two
        
    Returns:
        List containing the two numbers that appear only once
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    # XOR of all numbers
    xor = 0
    for num in nums:
        xor ^= num
    
    # Find the rightmost set bit
    rightmost_bit = xor & -xor
    
    # Partition the numbers into two groups
    num1, num2 = 0, 0
    for num in nums:
        if num & rightmost_bit:
            num1 ^= num
        else:
            num2 ^= num
    
    return [num1, num2]

@validate_input
def range_bitwise_and(m: int, n: int) -> int:
    """
    Find the bitwise AND of all numbers in the range [m, n].
    
    Args:
        m: Start of the range (inclusive)
        n: End of the range (inclusive)
        
    Returns:
        Bitwise AND of all numbers in the range [m, n]
        
    Time Complexity: O(1) - maximum 32 iterations
    Space Complexity: O(1)
    """
    shift = 0
    # Right shift both numbers until they are equal
    while m < n:
        m >>= 1
        n >>= 1
        shift += 1
    # Left shift the common prefix to get the result
    return m << shift

@validate_input
def hamming_distance(x: int, y: int) -> int:
    """
    Calculate the Hamming distance between two integers.
    
    Args:
        x: First integer
        y: Second integer
        
    Returns:
        The Hamming distance (number of differing bits)
        
    Time Complexity: O(1) - maximum 32 iterations
    Space Complexity: O(1)
    """
    xor = x ^ y
    distance = 0
    while xor:
        distance += 1
        xor &= (xor - 1)  # Clear the least significant set bit
    return distance

@validate_input
def total_hamming_distance(nums: List[int]) -> int:
    """
    Calculate the total Hamming distance between all pairs of numbers in the array.
    
    Args:
        nums: List of integers
        
    Returns:
        Total Hamming distance between all pairs
        
    Time Complexity: O(n * 32) = O(n)
    Space Complexity: O(1)
    """
    total = 0
    n = len(nums)
    
    for i in range(32):
        # Count numbers with the ith bit set
        count = 0
        for num in nums:
            if num & (1 << i):
                count += 1
        # Add the contribution of this bit position
        total += count * (n - count)
    
    return total
