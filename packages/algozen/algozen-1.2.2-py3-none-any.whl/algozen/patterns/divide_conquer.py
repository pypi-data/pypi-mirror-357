"""
Divide and Conquer pattern implementations for AlgoZen.

This module provides various divide and conquer algorithmic patterns.
"""
from typing import List, Tuple, Optional


def merge_sort_inversions(arr: List[int]) -> Tuple[List[int], int]:
    """Merge sort with inversion count.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if len(arr) <= 1:
        return arr, 0
    
    mid = len(arr) // 2
    left, inv_left = merge_sort_inversions(arr[:mid])
    right, inv_right = merge_sort_inversions(arr[mid:])
    
    merged, inv_merge = merge_and_count(left, right)
    return merged, inv_left + inv_right + inv_merge


def merge_and_count(left: List[int], right: List[int]) -> Tuple[List[int], int]:
    """Merge two sorted arrays and count inversions."""
    result = []
    i = j = inv_count = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            inv_count += len(left) - i
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result, inv_count


def maximum_subarray_divide_conquer(arr: List[int]) -> int:
    """Find maximum subarray sum using divide and conquer.
    
    Time Complexity: O(n log n)
    Space Complexity: O(log n)
    """
    def max_crossing_sum(arr, low, mid, high):
        left_sum = float('-inf')
        total = 0
        for i in range(mid, low - 1, -1):
            total += arr[i]
            left_sum = max(left_sum, total)
        
        right_sum = float('-inf')
        total = 0
        for i in range(mid + 1, high + 1):
            total += arr[i]
            right_sum = max(right_sum, total)
        
        return left_sum + right_sum
    
    def max_subarray_rec(arr, low, high):
        if low == high:
            return arr[low]
        
        mid = (low + high) // 2
        
        left_sum = max_subarray_rec(arr, low, mid)
        right_sum = max_subarray_rec(arr, mid + 1, high)
        cross_sum = max_crossing_sum(arr, low, mid, high)
        
        return max(left_sum, right_sum, cross_sum)
    
    return max_subarray_rec(arr, 0, len(arr) - 1)


def quick_select(arr: List[int], k: int) -> int:
    """Find kth smallest element using quickselect.
    
    Time Complexity: O(n) average, O(n²) worst
    Space Complexity: O(log n)
    """
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def quickselect_rec(arr, low, high, k):
        if low == high:
            return arr[low]
        
        pivot_idx = partition(arr, low, high)
        
        if k == pivot_idx:
            return arr[k]
        elif k < pivot_idx:
            return quickselect_rec(arr, low, pivot_idx - 1, k)
        else:
            return quickselect_rec(arr, pivot_idx + 1, high, k)
    
    return quickselect_rec(arr[:], 0, len(arr) - 1, k - 1)


def strassen_matrix_multiply(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    """Matrix multiplication using Strassen's algorithm.
    
    Time Complexity: O(n^2.807)
    Space Complexity: O(n²)
    """
    n = len(A)
    
    # Base case
    if n == 1:
        return [[A[0][0] * B[0][0]]]
    
    # Pad matrices to power of 2 if needed
    if n & (n - 1) != 0:
        next_power = 1 << (n - 1).bit_length()
        A = pad_matrix(A, next_power)
        B = pad_matrix(B, next_power)
        n = next_power
    
    mid = n // 2
    
    # Divide matrices
    A11 = [[A[i][j] for j in range(mid)] for i in range(mid)]
    A12 = [[A[i][j] for j in range(mid, n)] for i in range(mid)]
    A21 = [[A[i][j] for j in range(mid)] for i in range(mid, n)]
    A22 = [[A[i][j] for j in range(mid, n)] for i in range(mid, n)]
    
    B11 = [[B[i][j] for j in range(mid)] for i in range(mid)]
    B12 = [[B[i][j] for j in range(mid, n)] for i in range(mid)]
    B21 = [[B[i][j] for j in range(mid)] for i in range(mid, n)]
    B22 = [[B[i][j] for j in range(mid, n)] for i in range(mid, n)]
    
    # Strassen's 7 multiplications
    M1 = strassen_matrix_multiply(matrix_add(A11, A22), matrix_add(B11, B22))
    M2 = strassen_matrix_multiply(matrix_add(A21, A22), B11)
    M3 = strassen_matrix_multiply(A11, matrix_subtract(B12, B22))
    M4 = strassen_matrix_multiply(A22, matrix_subtract(B21, B11))
    M5 = strassen_matrix_multiply(matrix_add(A11, A12), B22)
    M6 = strassen_matrix_multiply(matrix_subtract(A21, A11), matrix_add(B11, B12))
    M7 = strassen_matrix_multiply(matrix_subtract(A12, A22), matrix_add(B21, B22))
    
    # Combine results
    C11 = matrix_add(matrix_subtract(matrix_add(M1, M4), M5), M7)
    C12 = matrix_add(M3, M5)
    C21 = matrix_add(M2, M4)
    C22 = matrix_add(matrix_subtract(matrix_add(M1, M3), M2), M6)
    
    # Combine quadrants
    result = [[0] * n for _ in range(n)]
    for i in range(mid):
        for j in range(mid):
            result[i][j] = C11[i][j]
            result[i][j + mid] = C12[i][j]
            result[i + mid][j] = C21[i][j]
            result[i + mid][j + mid] = C22[i][j]
    
    return result


def matrix_add(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    """Add two matrices."""
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]


def matrix_subtract(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    """Subtract two matrices."""
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]


def pad_matrix(matrix: List[List[int]], size: int) -> List[List[int]]:
    """Pad matrix to given size with zeros."""
    n = len(matrix)
    result = [[0] * size for _ in range(size)]
    for i in range(n):
        for j in range(n):
            result[i][j] = matrix[i][j]
    return result


def count_smaller_after_self(nums: List[int]) -> List[int]:
    """Count smaller elements after each element using divide and conquer.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    def merge_sort_count(enum_arr):
        if len(enum_arr) <= 1:
            return enum_arr
        
        mid = len(enum_arr) // 2
        left = merge_sort_count(enum_arr[:mid])
        right = merge_sort_count(enum_arr[mid:])
        
        merged = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i][1] <= right[j][1]:
                counts[left[i][0]] += j
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        
        while i < len(left):
            counts[left[i][0]] += j
            merged.append(left[i])
            i += 1
        
        merged.extend(right[j:])
        return merged
    
    counts = [0] * len(nums)
    enum_nums = list(enumerate(nums))
    merge_sort_count(enum_nums)
    return counts


def power_function(base: int, exp: int) -> int:
    """Calculate base^exp using divide and conquer.
    
    Time Complexity: O(log exp)
    Space Complexity: O(log exp)
    """
    if exp == 0:
        return 1
    if exp == 1:
        return base
    
    if exp % 2 == 0:
        half = power_function(base, exp // 2)
        return half * half
    else:
        return base * power_function(base, exp - 1)