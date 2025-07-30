"""
Mathematical patterns and algorithms for AlgoZen.

This module provides various mathematical algorithmic patterns.
"""
from typing import List, Tuple, Dict
import math
from collections import defaultdict


def fast_fourier_transform(coeffs: List[complex]) -> List[complex]:
    """Compute FFT of polynomial coefficients.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n log n)
    """
    n = len(coeffs)
    if n <= 1:
        return coeffs
    
    # Ensure n is power of 2
    if n & (n - 1) != 0:
        next_power = 1 << (n - 1).bit_length()
        coeffs.extend([0] * (next_power - n))
        n = next_power
    
    # Divide
    even = [coeffs[i] for i in range(0, n, 2)]
    odd = [coeffs[i] for i in range(1, n, 2)]
    
    # Conquer
    y_even = fast_fourier_transform(even)
    y_odd = fast_fourier_transform(odd)
    
    # Combine
    y = [0] * n
    for j in range(n // 2):
        t = complex(math.cos(-2 * math.pi * j / n), math.sin(-2 * math.pi * j / n)) * y_odd[j]
        y[j] = y_even[j] + t
        y[j + n // 2] = y_even[j] - t
    
    return y


def polynomial_multiply_fft(a: List[int], b: List[int]) -> List[int]:
    """Multiply polynomials using FFT.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    n = len(a) + len(b) - 1
    size = 1 << (n - 1).bit_length()
    
    # Convert to complex and pad
    fa = [complex(x, 0) for x in a] + [0] * (size - len(a))
    fb = [complex(x, 0) for x in b] + [0] * (size - len(b))
    
    # Forward FFT
    fa = fast_fourier_transform(fa)
    fb = fast_fourier_transform(fb)
    
    # Point-wise multiplication
    for i in range(size):
        fa[i] *= fb[i]
    
    # Inverse FFT (conjugate, FFT, conjugate, scale)
    fa = [x.conjugate() for x in fa]
    fa = fast_fourier_transform(fa)
    fa = [x.conjugate() / size for x in fa]
    
    return [int(round(x.real)) for x in fa[:n]]


def matrix_determinant(matrix: List[List[float]]) -> float:
    """Calculate matrix determinant using LU decomposition.
    
    Time Complexity: O(n³)
    Space Complexity: O(n²)
    """
    n = len(matrix)
    # Create copy
    mat = [row[:] for row in matrix]
    
    det = 1.0
    for i in range(n):
        # Find pivot
        max_row = i
        for k in range(i + 1, n):
            if abs(mat[k][i]) > abs(mat[max_row][i]):
                max_row = k
        
        # Swap rows
        if max_row != i:
            mat[i], mat[max_row] = mat[max_row], mat[i]
            det *= -1
        
        # Check for singular matrix
        if abs(mat[i][i]) < 1e-10:
            return 0
        
        det *= mat[i][i]
        
        # Eliminate column
        for k in range(i + 1, n):
            factor = mat[k][i] / mat[i][i]
            for j in range(i, n):
                mat[k][j] -= factor * mat[i][j]
    
    return det


def gaussian_elimination(matrix: List[List[float]]) -> List[float]:
    """Solve system of linear equations using Gaussian elimination.
    
    Time Complexity: O(n³)
    Space Complexity: O(n²)
    """
    n = len(matrix)
    # Create augmented matrix copy
    aug = [row[:] for row in matrix]
    
    # Forward elimination
    for i in range(n):
        # Find pivot
        max_row = i
        for k in range(i + 1, n):
            if abs(aug[k][i]) > abs(aug[max_row][i]):
                max_row = k
        
        aug[i], aug[max_row] = aug[max_row], aug[i]
        
        # Make diagonal 1
        for k in range(i + 1, n + 1):
            aug[i][k] /= aug[i][i]
        aug[i][i] = 1
        
        # Eliminate column
        for k in range(i + 1, n):
            factor = aug[k][i]
            for j in range(i, n + 1):
                aug[k][j] -= factor * aug[i][j]
    
    # Back substitution
    solution = [0] * n
    for i in range(n - 1, -1, -1):
        solution[i] = aug[i][n]
        for j in range(i + 1, n):
            solution[i] -= aug[i][j] * solution[j]
    
    return solution


def convex_hull_jarvis(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Find convex hull using Jarvis march (Gift wrapping).
    
    Time Complexity: O(nh) where h is hull size
    Space Complexity: O(h)
    """
    def orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if abs(val) < 1e-10:
            return 0  # Collinear
        return 1 if val > 0 else 2  # Clockwise or Counterclockwise
    
    n = len(points)
    if n < 3:
        return points
    
    # Find leftmost point
    l = 0
    for i in range(1, n):
        if points[i][0] < points[l][0]:
            l = i
        elif points[i][0] == points[l][0] and points[i][1] < points[l][1]:
            l = i
    
    hull = []
    p = l
    
    while True:
        hull.append(points[p])
        
        # Find most counterclockwise point
        q = (p + 1) % n
        for i in range(n):
            if orientation(points[p], points[i], points[q]) == 2:
                q = i
        
        p = q
        if p == l:  # Back to start
            break
    
    return hull


def linear_programming_simplex(c: List[float], A: List[List[float]], b: List[float]) -> Tuple[List[float], float]:
    """Solve linear programming using Simplex method.
    
    Time Complexity: O(2^n) worst case, polynomial average
    Space Complexity: O(mn)
    """
    m, n = len(A), len(c)
    
    # Create tableau
    tableau = []
    for i in range(m):
        row = A[i][:] + [0] * m + [b[i]]
        row[n + i] = 1  # Slack variable
        tableau.append(row)
    
    # Objective row
    obj_row = [-x for x in c] + [0] * (m + 1)
    tableau.append(obj_row)
    
    while True:
        # Find entering variable (most negative in objective row)
        entering = -1
        min_val = 0
        for j in range(n + m):
            if tableau[m][j] < min_val:
                min_val = tableau[m][j]
                entering = j
        
        if entering == -1:  # Optimal solution found
            break
        
        # Find leaving variable (minimum ratio test)
        leaving = -1
        min_ratio = float('inf')
        for i in range(m):
            if tableau[i][entering] > 0:
                ratio = tableau[i][n + m] / tableau[i][entering]
                if ratio < min_ratio:
                    min_ratio = ratio
                    leaving = i
        
        if leaving == -1:  # Unbounded solution
            return [], float('inf')
        
        # Pivot operation
        pivot = tableau[leaving][entering]
        for j in range(n + m + 1):
            tableau[leaving][j] /= pivot
        
        for i in range(m + 1):
            if i != leaving:
                factor = tableau[i][entering]
                for j in range(n + m + 1):
                    tableau[i][j] -= factor * tableau[leaving][j]
    
    # Extract solution
    solution = [0] * n
    for i in range(m):
        # Find basic variable in this row
        basic_var = -1
        for j in range(n):
            if abs(tableau[i][j] - 1) < 1e-10:
                # Check if this is the only non-zero in column
                is_basic = True
                for k in range(m + 1):
                    if k != i and abs(tableau[k][j]) > 1e-10:
                        is_basic = False
                        break
                if is_basic:
                    basic_var = j
                    break
        
        if basic_var != -1:
            solution[basic_var] = tableau[i][n + m]
    
    optimal_value = tableau[m][n + m]
    return solution, optimal_value


def karatsuba_multiply(x: int, y: int) -> int:
    """Multiply large integers using Karatsuba algorithm.
    
    Time Complexity: O(n^1.585)
    Space Complexity: O(log n)
    """
    if x < 10 or y < 10:
        return x * y
    
    # Calculate size of numbers
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    
    # Split numbers
    high1, low1 = divmod(x, 10**m)
    high2, low2 = divmod(y, 10**m)
    
    # Three recursive calls
    z0 = karatsuba_multiply(low1, low2)
    z1 = karatsuba_multiply(low1 + high1, low2 + high2)
    z2 = karatsuba_multiply(high1, high2)
    
    return z2 * 10**(2*m) + (z1 - z2 - z0) * 10**m + z0


def baby_step_giant_step(g: int, h: int, p: int) -> int:
    """Solve discrete logarithm using Baby-step Giant-step.
    
    Time Complexity: O(√p)
    Space Complexity: O(√p)
    """
    n = int(math.sqrt(p)) + 1
    
    # Baby steps
    baby_steps = {}
    gamma = 1
    for j in range(n):
        if gamma == h:
            return j
        baby_steps[gamma] = j
        gamma = (gamma * g) % p
    
    # Giant steps
    factor = pow(g, n * (p - 2), p)  # g^(-n) mod p
    y = h
    
    for i in range(n):
        if y in baby_steps:
            return i * n + baby_steps[y]
        y = (y * factor) % p
    
    return -1  # No solution found


def pollard_rho_factorization(n: int) -> int:
    """Find factor using Pollard's rho algorithm.
    
    Time Complexity: O(n^(1/4))
    Space Complexity: O(1)
    """
    if n % 2 == 0:
        return 2
    
    x = 2
    y = 2
    d = 1
    
    def f(x):
        return (x * x + 1) % n
    
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = math.gcd(abs(x - y), n)
    
    return d if d != n else -1