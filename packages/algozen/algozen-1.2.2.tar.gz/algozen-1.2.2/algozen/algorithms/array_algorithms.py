"""
Advanced array algorithms implementation for AlgoZen.

This module provides various advanced array manipulation algorithms.
"""
from typing import List, Tuple, Dict
from collections import defaultdict


def next_greater_element(nums: List[int]) -> List[int]:
    """Find next greater element for each element using stack.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    result = [-1] * len(nums)
    stack = []
    
    for i in range(len(nums)):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)
    
    return result


def largest_rectangle_histogram(heights: List[int]) -> int:
    """Find largest rectangle area in histogram.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    stack = []
    max_area = 0
    
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    
    while stack:
        height = heights[stack.pop()]
        width = len(heights) if not stack else len(heights) - stack[-1] - 1
        max_area = max(max_area, height * width)
    
    return max_area


def trapping_rain_water(height: List[int]) -> int:
    """Calculate trapped rainwater using two pointers.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not height:
        return 0
    
    left, right = 0, len(height) - 1
    left_max = right_max = water = 0
    
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    
    return water


def find_duplicate_number(nums: List[int]) -> int:
    """Find duplicate in array using Floyd's cycle detection.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    # Phase 1: Find intersection point
    slow = fast = nums[0]
    
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    
    # Phase 2: Find entrance to cycle
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    
    return slow


def product_except_self(nums: List[int]) -> List[int]:
    """Calculate product of array except self without division.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    n = len(nums)
    result = [1] * n
    
    # Left products
    for i in range(1, n):
        result[i] = result[i-1] * nums[i-1]
    
    # Right products
    right = 1
    for i in range(n-1, -1, -1):
        result[i] *= right
        right *= nums[i]
    
    return result


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    """Merge overlapping intervals.
    
    Time Complexity: O(n log n)
    Space Complexity: O(1)
    """
    if not intervals:
        return []
    
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    
    for current in intervals[1:]:
        if current[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], current[1])
        else:
            merged.append(current)
    
    return merged


def find_missing_positive(nums: List[int]) -> int:
    """Find first missing positive integer.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    n = len(nums)
    
    # Place each positive integer i at index i-1
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1]
    
    # Find first missing positive
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    
    return n + 1


def subarray_sum_equals_k(nums: List[int], k: int) -> int:
    """Count subarrays with sum equal to k.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    count = 0
    prefix_sum = 0
    sum_count = defaultdict(int)
    sum_count[0] = 1
    
    for num in nums:
        prefix_sum += num
        count += sum_count[prefix_sum - k]
        sum_count[prefix_sum] += 1
    
    return count


def longest_consecutive_sequence(nums: List[int]) -> int:
    """Find length of longest consecutive sequence.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not nums:
        return 0
    
    num_set = set(nums)
    max_length = 0
    
    for num in num_set:
        if num - 1 not in num_set:  # Start of sequence
            current_num = num
            current_length = 1
            
            while current_num + 1 in num_set:
                current_num += 1
                current_length += 1
            
            max_length = max(max_length, current_length)
    
    return max_length


def three_sum(nums: List[int]) -> List[List[int]]:
    """Find all unique triplets that sum to zero.
    
    Time Complexity: O(n²)
    Space Complexity: O(1)
    """
    nums.sort()
    result = []
    
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        
        left, right = i + 1, len(nums) - 1
        
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                
                left += 1
                right -= 1
    
    return result


def container_with_most_water(height: List[int]) -> int:
    """Find container that holds most water.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    left, right = 0, len(height) - 1
    max_area = 0
    
    while left < right:
        width = right - left
        area = width * min(height[left], height[right])
        max_area = max(max_area, area)
        
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_area


def rotate_array(nums: List[int], k: int) -> None:
    """Rotate array to the right by k steps in-place.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    n = len(nums)
    k %= n
    
    def reverse(start, end):
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start += 1
            end -= 1
    
    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)