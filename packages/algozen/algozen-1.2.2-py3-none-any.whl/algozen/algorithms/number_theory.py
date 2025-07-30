"""
Number theory and mathematical algorithms for AlgoZen.

This module provides various number theory and mathematical algorithms.
"""
from typing import List, Tuple
import math


def sieve_of_eratosthenes(n: int) -> List[int]:
    """Generate all prime numbers up to n using Sieve of Eratosthenes.
    
    Time Complexity: O(n log log n)
    Space Complexity: O(n)
    """
    if n < 2:
        return []
    
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    
    return [i for i in range(2, n + 1) if is_prime[i]]


def gcd(a: int, b: int) -> int:
    """Calculate GCD using Euclidean algorithm.
    
    Time Complexity: O(log min(a,b))
    Space Complexity: O(1)
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm: ax + by = gcd(a,b).
    
    Returns: (gcd, x, y)
    Time Complexity: O(log min(a,b))
    Space Complexity: O(1)
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def modular_exponentiation(base: int, exp: int, mod: int) -> int:
    """Calculate (base^exp) % mod efficiently.
    
    Time Complexity: O(log exp)
    Space Complexity: O(1)
    """
    result = 1
    base %= mod
    
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        exp >>= 1
        base = (base * base) % mod
    
    return result


def modular_inverse(a: int, m: int) -> int:
    """Find modular inverse of a modulo m.
    
    Time Complexity: O(log m)
    Space Complexity: O(1)
    """
    gcd_val, x, _ = extended_gcd(a, m)
    if gcd_val != 1:
        raise ValueError("Modular inverse doesn't exist")
    return (x % m + m) % m


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> int:
    """Solve system of congruences using Chinese Remainder Theorem.
    
    Time Complexity: O(n²)
    Space Complexity: O(1)
    """
    if len(remainders) != len(moduli):
        raise ValueError("Lists must have same length")
    
    total = 0
    prod = 1
    for m in moduli:
        prod *= m
    
    for r, m in zip(remainders, moduli):
        p = prod // m
        total += r * modular_inverse(p, m) * p
    
    return total % prod


def prime_factorization(n: int) -> List[Tuple[int, int]]:
    """Find prime factorization of n.
    
    Returns: List of (prime, power) tuples
    Time Complexity: O(√n)
    Space Complexity: O(log n)
    """
    factors = []
    d = 2
    
    while d * d <= n:
        count = 0
        while n % d == 0:
            n //= d
            count += 1
        if count > 0:
            factors.append((d, count))
        d += 1
    
    if n > 1:
        factors.append((n, 1))
    
    return factors


def euler_totient(n: int) -> int:
    """Calculate Euler's totient function φ(n).
    
    Time Complexity: O(√n)
    Space Complexity: O(1)
    """
    result = n
    p = 2
    
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    
    if n > 1:
        result -= result // n
    
    return result


def miller_rabin_primality(n: int, k: int = 5) -> bool:
    """Miller-Rabin primality test.
    
    Time Complexity: O(k log³ n)
    Space Complexity: O(1)
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as d * 2^r
    r = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        r += 1
    
    # Witness loop
    import random
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = modular_exponentiation(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = modular_exponentiation(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def fibonacci_matrix(n: int) -> int:
    """Calculate nth Fibonacci number using matrix exponentiation.
    
    Time Complexity: O(log n)
    Space Complexity: O(1)
    """
    if n <= 1:
        return n
    
    def matrix_multiply(A, B):
        return [[A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
                [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]]
    
    def matrix_power(mat, power):
        if power == 1:
            return mat
        if power % 2 == 0:
            half = matrix_power(mat, power // 2)
            return matrix_multiply(half, half)
        else:
            return matrix_multiply(mat, matrix_power(mat, power - 1))
    
    base_matrix = [[1, 1], [1, 0]]
    result_matrix = matrix_power(base_matrix, n)
    return result_matrix[0][1]


def catalan_number(n: int) -> int:
    """Calculate nth Catalan number.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if n <= 1:
        return 1
    
    catalan = 1
    for i in range(n):
        catalan = catalan * (2 * n - i) // (i + 1)
    
    return catalan // (n + 1)


def josephus_problem(n: int, k: int) -> int:
    """Solve Josephus problem: last person standing.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    result = 0
    for i in range(2, n + 1):
        result = (result + k) % i
    return result + 1  # Convert to 1-indexed


def perfect_squares_count(n: int) -> int:
    """Find minimum number of perfect squares that sum to n.
    
    Time Complexity: O(n√n)
    Space Complexity: O(n)
    """
    dp = [float('inf')] * (n + 1)
    dp[0] = 0
    
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            dp[i] = min(dp[i], dp[i - j * j] + 1)
            j += 1
    
    return dp[n]