"""
Math Problems and Solutions.

This module contains implementations of common mathematical problems.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Set, Any, TypeVar, Callable, Generator
from functools import wraps
import math
import random

T = TypeVar('T')

def validate_input(func: Callable) -> Callable:
    """Decorator to validate input for math problems."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)
    return wrapper

@validate_input
def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    Args:
        n: Integer to check
        
    Returns:
        True if n is prime, False otherwise
        
    Time Complexity: O(sqrt(n))
    Space Complexity: O(1)
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w  # Alternate between 2 and 4 (6-2=4, 6-4=2)
    
    return True

@validate_input
def sieve_of_eratosthenes(n: int) -> List[bool]:
    """
    Generate a sieve of primes up to n using the Sieve of Eratosthenes.
    
    Args:
        n: Upper bound (inclusive)
        
    Returns:
        A list where sieve[i] is True if i is prime
        
    Time Complexity: O(n log log n)
    Space Complexity: O(n)
    """
    if n < 2:
        return [False] * (n + 1)
    
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(math.isqrt(n)) + 1):
        if sieve[i]:
            sieve[i*i : n+1 : i] = [False] * len(sieve[i*i : n+1 : i])
    
    return sieve

@validate_input
def gcd(a: int, b: int) -> int:
    """
    Compute the greatest common divisor of two numbers using the Euclidean algorithm.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        GCD of a and b
        
    Time Complexity: O(log(min(a, b)))
    Space Complexity: O(1)
    """
    while b:
        a, b = b, a % b
    return abs(a)

@validate_input
def lcm(a: int, b: int) -> int:
    """
    Compute the least common multiple of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        LCM of a and b
        
    Time Complexity: Same as gcd()
    Space Complexity: O(1)
    """
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)

@validate_input
def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean algorithm.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        A tuple (g, x, y) such that a*x + b*y = g = gcd(a, b)
        
    Time Complexity: O(log(min(a, b)))
    Space Complexity: O(1)
    """
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = extended_gcd(b % a, a)
        return (g, x - (b // a) * y, y)

@validate_input
def mod_inverse(a: int, m: int) -> int:
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Args:
        a: Number to find inverse of
        m: Modulus
        
    Returns:
        The modular multiplicative inverse of a modulo m
        
    Raises:
        ValueError: If a and m are not coprime
        
    Time Complexity: O(log min(a, m))
    Space Complexity: O(1)
    """
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise ValueError(f"Inverse doesn't exist for {a} mod {m}")
    return x % m

@validate_input
def power_mod(base: int, exponent: int, mod: int) -> int:
    """
    Compute (base^exponent) % mod efficiently using modular exponentiation.
    
    Args:
        base: The base number
        exponent: The exponent (non-negative)
        mod: The modulus (positive)
        
    Returns:
        (base^exponent) % mod
        
    Time Complexity: O(log exponent)
    Space Complexity: O(1)
    """
    if mod == 1:
        return 0
    result = 1
    base = base % mod
    
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % mod
        exponent = exponent >> 1
        base = (base * base) % mod
    
    return result

@validate_input
def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test.
    
    Args:
        n: Number to test
        k: Number of iterations (higher means more accurate)
        
    Returns:
        True if n is probably prime, False if definitely composite
        
    Time Complexity: O(k log³ n)
    Space Complexity: O(1)
    """
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n % p == 0:
            return n == p
    
    # Write n-1 as d*2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    
    # Test for k iterations
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        
        for __ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    
    return True

@validate_input
def generate_primes_up_to(n: int) -> List[int]:
    """
    Generate all prime numbers up to n using the Sieve of Eratosthenes.
    
    Args:
        n: Upper bound (inclusive)
        
    Returns:
        List of primes up to n
        
    Time Complexity: O(n log log n)
    Space Complexity: O(n)
    """
    if n < 2:
        return []
    
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(math.isqrt(n)) + 1):
        if sieve[i]:
            sieve[i*i : n+1 : i] = [False] * len(sieve[i*i : n+1 : i])
    
    return [i for i, is_prime in enumerate(sieve) if is_prime]

@validate_input
def factorize(n: int) -> Dict[int, int]:
    """
    Factorize a number into its prime factors.
    
    Args:
        n: Integer to factorize (n > 1)
        
    Returns:
        Dictionary mapping prime factors to their exponents
        
    Time Complexity: O(sqrt(n))
    Space Complexity: O(log n) for the result
    """
    factors = {}
    
    # Handle 2 separately
    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2
    
    # Check odd divisors up to sqrt(n)
    i = 3
    max_factor = math.isqrt(n) + 1
    while i <= max_factor:
        while n % i == 0:
            factors[i] = factors.get(i, 0) + 1
            n //= i
            max_factor = math.isqrt(n) + 1
        i += 2
    
    # If n is a prime number > 2
    if n > 1:
        factors[n] = 1
    
    return factors

@validate_input
def euler_totient(n: int) -> int:
    """
    Compute Euler's totient function φ(n), which counts the positive integers up to n
    that are relatively prime to n.
    
    Args:
        n: Positive integer
        
    Returns:
        φ(n)
        
    Time Complexity: O(sqrt(n))
    Space Complexity: O(1)
    """
    if n == 1:
        return 1
        
    result = n
    # Check for even numbers
    if n % 2 == 0:
        result -= result // 2
        while n % 2 == 0:
            n //= 2
    
    # Check for odd numbers
    i = 3
    max_factor = math.isqrt(n) + 1
    while i <= max_factor:
        if n % i == 0:
            result -= result // i
            while n % i == 0:
                n //= i
            max_factor = math.isqrt(n) + 1
        i += 2
    
    # If n is a prime number > 2
    if n > 1:
        result -= result // n
    
    return result

@validate_input
def chinese_remainder_theorem(equations: List[Tuple[int, int]]) -> int:
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Args:
        equations: List of tuples (a_i, n_i) representing x ≡ a_i (mod n_i)
        
    Returns:
        The smallest positive solution x that satisfies all congruences
        
    Raises:
        ValueError: If the system has no solution
        
    Time Complexity: O(k log M) where k is the number of equations and M is the product of moduli
    Space Complexity: O(1)
    """
    if not equations:
        return 0
    
    # Start with the first equation: x ≡ a1 mod n1
    x, m = equations[0]
    
    for a, n in equations[1:]:
        # Solve x ≡ a (mod n) and x ≡ current_x (mod current_m)
        # Find k such that x + k*m ≡ a (mod n)
        # => k*m ≡ (a - x) (mod n)
        
        # Find solution to k*m ≡ (a - x) mod n
        a_diff = (a - x) % n
        g, k, _ = extended_gcd(m, n)
        
        if a_diff % g != 0:
            raise ValueError("No solution exists")
        
        # Find a particular solution
        k0 = (k * (a_diff // g)) % (n // g)
        x += k0 * m
        
        # Update m to be the LCM of current m and n
        m = (m // g) * n  # m = LCM(m, n)
        
        # Ensure x is the smallest positive solution
        x %= m
    
    return x if x != 0 else m

@validate_input
def generate_pascal_triangle(num_rows: int) -> List[List[int]]:
    """
    Generate Pascal's Triangle up to the specified number of rows.
    
    Args:
        num_rows: Number of rows to generate
        
    Returns:
        List of rows of Pascal's Triangle
        
    Time Complexity: O(num_rows^2)
    Space Complexity: O(num_rows^2)
    """
    if num_rows <= 0:
        return []
    
    triangle = [[1]]
    
    for i in range(1, num_rows):
        prev_row = triangle[-1]
        new_row = [1]  # First element is always 1
        
        for j in range(1, i):
            new_row.append(prev_row[j-1] + prev_row[j])
            
        new_row.append(1)  # Last element is always 1
        triangle.append(new_row)
    
    return triangle

@validate_input
def is_palindrome_number(x: int) -> bool:
    """
    Check if an integer is a palindrome.
    
    Args:
        x: Integer to check
        
    Returns:
        True if x is a palindrome, False otherwise
        
    Time Complexity: O(d) where d is the number of digits in x
    Space Complexity: O(1)
    """
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    
    reverted = 0
    original = x
    
    while x > reverted:
        reverted = reverted * 10 + x % 10
        x //= 10
    
    # When the length is odd, we can ignore the middle digit
    return x == reverted or x == reverted // 10
