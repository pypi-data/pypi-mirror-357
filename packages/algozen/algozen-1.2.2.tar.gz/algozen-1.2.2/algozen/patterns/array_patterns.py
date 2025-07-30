"""
Advanced array patterns for AlgoZen.

This module provides various advanced array algorithmic patterns.
"""
from typing import List, Tuple, Dict
from collections import defaultdict, deque
import heapq


def mo_algorithm(queries: List[Tuple[int, int]], arr: List[int]) -> List[int]:
    """Answer range queries using Mo's algorithm.
    
    Time Complexity: O((n + q) * sqrt(n))
    Space Complexity: O(n)
    """
    import math
    
    n = len(arr)
    block_size = int(math.sqrt(n))
    
    # Sort queries by Mo's order
    def mo_cmp(query):
        idx, l, r = query
        return (l // block_size, r if (l // block_size) % 2 == 0 else -r)
    
    indexed_queries = [(i, l, r) for i, (l, r) in enumerate(queries)]
    indexed_queries.sort(key=mo_cmp)
    
    # Initialize data structure
    freq = defaultdict(int)
    current_answer = 0
    
    def add(x):
        nonlocal current_answer
        freq[x] += 1
        if freq[x] == 1:
            current_answer += 1
    
    def remove(x):
        nonlocal current_answer
        freq[x] -= 1
        if freq[x] == 0:
            current_answer -= 1
    
    answers = [0] * len(queries)
    current_l = 0
    current_r = -1
    
    for query_idx, l, r in indexed_queries:
        # Expand/contract the window
        while current_r < r:
            current_r += 1
            add(arr[current_r])
        
        while current_r > r:
            remove(arr[current_r])
            current_r -= 1
        
        while current_l < l:
            remove(arr[current_l])
            current_l += 1
        
        while current_l > l:
            current_l -= 1
            add(arr[current_l])
        
        answers[query_idx] = current_answer
    
    return answers


def sqrt_decomposition(arr: List[int]) -> Dict:
    """Build sqrt decomposition for range queries.
    
    Time Complexity: O(n)
    Space Complexity: O(sqrt(n))
    """
    import math
    
    n = len(arr)
    block_size = int(math.sqrt(n))
    blocks = []
    
    for i in range(0, n, block_size):
        block_sum = sum(arr[i:i + block_size])
        blocks.append(block_sum)
    
    def range_sum(l: int, r: int) -> int:
        result = 0
        
        while l <= r:
            if l % block_size == 0 and l + block_size - 1 <= r:
                # Full block
                result += blocks[l // block_size]
                l += block_size
            else:
                # Partial block
                result += arr[l]
                l += 1
        
        return result
    
    def update(idx: int, val: int):
        old_val = arr[idx]
        arr[idx] = val
        blocks[idx // block_size] += val - old_val
    
    return {
        'range_sum': range_sum,
        'update': update,
        'blocks': blocks
    }


def coordinate_compression(values: List[int]) -> Tuple[Dict[int, int], List[int]]:
    """Compress coordinates to smaller range.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    sorted_unique = sorted(set(values))
    compress_map = {val: i for i, val in enumerate(sorted_unique)}
    compressed = [compress_map[val] for val in values]
    
    return compress_map, compressed


def sliding_window_maximum(nums: List[int], k: int) -> List[int]:
    """Find maximum in each sliding window using deque.
    
    Time Complexity: O(n)
    Space Complexity: O(k)
    """
    if not nums or k == 0:
        return []
    
    dq = deque()  # Store indices
    result = []
    
    for i in range(len(nums)):
        # Remove indices outside window
        while dq and dq[0] <= i - k:
            dq.popleft()
        
        # Remove smaller elements from back
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()
        
        dq.append(i)
        
        # Add to result when window is full
        if i >= k - 1:
            result.append(nums[dq[0]])
    
    return result


def range_minimum_query_sparse_table(arr: List[int]) -> Dict:
    """Build sparse table for RMQ.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n log n)
    """
    import math
    
    n = len(arr)
    LOG = int(math.log2(n)) + 1
    st = [[0] * LOG for _ in range(n)]
    
    # Initialize for intervals of length 1
    for i in range(n):
        st[i][0] = arr[i]
    
    # Build sparse table
    j = 1
    while (1 << j) <= n:
        i = 0
        while (i + (1 << j) - 1) < n:
            st[i][j] = min(st[i][j-1], st[i + (1 << (j-1))][j-1])
            i += 1
        j += 1
    
    def query(l: int, r: int) -> int:
        length = r - l + 1
        k = int(math.log2(length))
        return min(st[l][k], st[r - (1 << k) + 1][k])
    
    return {'query': query, 'table': st}


def longest_increasing_subsequence_patience(arr: List[int]) -> Tuple[int, List[int]]:
    """Find LIS using patience sorting with reconstruction.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not arr:
        return 0, []
    
    import bisect
    
    tails = []
    predecessors = [-1] * len(arr)
    tail_indices = []
    
    for i, num in enumerate(arr):
        pos = bisect.bisect_left(tails, num)
        
        if pos == len(tails):
            tails.append(num)
            tail_indices.append(i)
        else:
            tails[pos] = num
            tail_indices[pos] = i
        
        if pos > 0:
            predecessors[i] = tail_indices[pos - 1]
    
    # Reconstruct LIS
    lis = []
    current = tail_indices[-1] if tail_indices else -1
    
    while current != -1:
        lis.append(arr[current])
        current = predecessors[current]
    
    lis.reverse()
    return len(lis), lis


def maximum_subarray_kadane_2d(matrix: List[List[int]]) -> int:
    """Find maximum sum submatrix using Kadane's algorithm.
    
    Time Complexity: O(n² * m)
    Space Complexity: O(m)
    """
    if not matrix or not matrix[0]:
        return 0
    
    rows, cols = len(matrix), len(matrix[0])
    max_sum = float('-inf')
    
    def kadane_1d(arr: List[int]) -> int:
        max_ending_here = max_so_far = arr[0]
        for i in range(1, len(arr)):
            max_ending_here = max(arr[i], max_ending_here + arr[i])
            max_so_far = max(max_so_far, max_ending_here)
        return max_so_far
    
    for top in range(rows):
        temp = [0] * cols
        
        for bottom in range(top, rows):
            # Add current row to temp array
            for j in range(cols):
                temp[j] += matrix[bottom][j]
            
            # Find maximum subarray in temp
            current_max = kadane_1d(temp)
            max_sum = max(max_sum, current_max)
    
    return max_sum


def count_inversions_merge_sort(arr: List[int]) -> Tuple[List[int], int]:
    """Count inversions using merge sort.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    def merge_and_count(left: List[int], right: List[int]) -> Tuple[List[int], int]:
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
    
    def merge_sort_and_count(arr: List[int]) -> Tuple[List[int], int]:
        if len(arr) <= 1:
            return arr, 0
        
        mid = len(arr) // 2
        left, inv_left = merge_sort_and_count(arr[:mid])
        right, inv_right = merge_sort_and_count(arr[mid:])
        merged, inv_merge = merge_and_count(left, right)
        
        return merged, inv_left + inv_right + inv_merge
    
    return merge_sort_and_count(arr)


def kth_largest_quickselect(nums: List[int], k: int) -> int:
    """Find kth largest element using quickselect.
    
    Time Complexity: O(n) average, O(n²) worst
    Space Complexity: O(log n)
    """
    import random
    
    def partition(arr: List[int], low: int, high: int) -> int:
        # Random pivot for better average case
        pivot_idx = random.randint(low, high)
        arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
        
        pivot = arr[high]
        i = low - 1
        
        for j in range(low, high):
            if arr[j] >= pivot:  # For kth largest
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def quickselect(arr: List[int], low: int, high: int, k: int) -> int:
        if low == high:
            return arr[low]
        
        pivot_idx = partition(arr, low, high)
        
        if k == pivot_idx:
            return arr[k]
        elif k < pivot_idx:
            return quickselect(arr, low, pivot_idx - 1, k)
        else:
            return quickselect(arr, pivot_idx + 1, high, k)
    
    return quickselect(nums[:], 0, len(nums) - 1, k - 1)


def dutch_national_flag(nums: List[int], pivot: int) -> None:
    """Partition array around pivot (Dutch National Flag problem).
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    low = mid = 0
    high = len(nums) - 1
    
    while mid <= high:
        if nums[mid] < pivot:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == pivot:
            mid += 1
        else:  # nums[mid] > pivot
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
            # Don't increment mid as we need to check swapped element