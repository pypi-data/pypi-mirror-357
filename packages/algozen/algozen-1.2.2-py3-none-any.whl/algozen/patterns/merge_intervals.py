"""
Merge Intervals Pattern implementations.

This module provides functions that demonstrate the merge intervals technique,
which is useful for solving problems involving overlapping intervals.
"""
from typing import List, Tuple, Optional, TypeVar, Callable, Any
from functools import wraps

T = TypeVar('T', int, float)

def validate_intervals(func: Callable) -> Callable:
    """Decorator to validate intervals input."""
    @wraps(func)
    def wrapper(intervals: List[List[T]], *args, **kwargs) -> Any:
        if not isinstance(intervals, list):
            raise TypeError("Input must be a list of intervals")
        for interval in intervals:
            if not isinstance(interval, list) or len(interval) != 2:
                raise ValueError("Each interval must be a list of [start, end]")
            if interval[0] > interval[1]:
                raise ValueError("Start must be <= end in each interval")
        return func(intervals, *args, **kwargs)
    return wrapper

@validate_intervals
def merge(intervals: List[List[T]]) -> List[List[T]]:
    """
    Merge overlapping intervals.
    
    Args:
        intervals: List of intervals where intervals[i] = [start_i, end_i]
        
    Returns:
        A new list of intervals where overlapping intervals are merged
        
    Time Complexity: O(n log n) due to sorting
    Space Complexity: O(n) for the result
    """
    if not intervals:
        return []
    
    # Sort intervals based on start time
    intervals.sort(key=lambda x: x[0])
    
    merged = [intervals[0]]
    
    for current in intervals[1:]:
        last = merged[-1]
        
        # If current interval overlaps with the last merged interval, merge them
        if current[0] <= last[1]:
            last[1] = max(last[1], current[1])
        else:
            merged.append(current)
    
    return merged

@validate_intervals
def insert_interval(existing_intervals: List[List[T]], new_interval: List[T]) -> List[List[T]]:
    """
    Insert a new interval into a list of non-overlapping intervals.
    
    Args:
        existing_intervals: List of non-overlapping intervals sorted by start time
        new_interval: The new interval to insert [start, end]
        
    Returns:
        A new list of intervals with the new interval inserted and merged if necessary
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not new_interval:
        return existing_intervals
    
    result = []
    i = 0
    n = len(existing_intervals)
    
    # Add all intervals that come before the new interval
    while i < n and existing_intervals[i][1] < new_interval[0]:
        result.append(existing_intervals[i])
        i += 1
    
    # Merge all overlapping intervals
    while i < n and existing_intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], existing_intervals[i][0])
        new_interval[1] = max(new_interval[1], existing_intervals[i][1])
        i += 1
    
    # Add the merged interval
    result.append(new_interval)
    
    # Add all the remaining intervals
    while i < n:
        result.append(existing_intervals[i])
        i += 1
    
    return result

@validate_intervals
def intervals_intersection(intervals_a: List[List[T]], intervals_b: List[List[T]]) -> List[List[T]]:
    """
    Find the intersection of two lists of intervals.
    
    Args:
        intervals_a: First list of intervals
        intervals_b: Second list of intervals
        
    Returns:
        A list of intervals representing the intersection
        
    Time Complexity: O(n + m) where n and m are the lengths of the two interval lists
    Space Complexity: O(1) excluding the result
    """
    result = []
    i = j = 0
    
    while i < len(intervals_a) and j < len(intervals_b):
        # Check if intervals overlap
        a_overlaps_b = (intervals_a[i][0] >= intervals_b[j][0] and 
                        intervals_a[i][0] <= intervals_b[j][1])
        
        b_overlaps_a = (intervals_b[j][0] >= intervals_a[i][0] and 
                        intervals_b[j][0] <= intervals_a[i][1])
        
        # If they overlap, add the intersection
        if a_overlaps_b or b_overlaps_a:
            start = max(intervals_a[i][0], intervals_b[j][0])
            end = min(intervals_a[i][1], intervals_b[j][1])
            result.append([start, end])
        
        # Move the pointer which is ending first
        if intervals_a[i][1] < intervals_b[j][1]:
            i += 1
        else:
            j += 1
    
    return result

@validate_intervals
def min_meeting_rooms(intervals: List[List[T]]) -> int:
    """
    Find the minimum number of conference rooms required.
    
    Args:
        intervals: List of meeting time intervals [start, end]
        
    Returns:
        The minimum number of rooms required
        
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not intervals:
        return 0
    
    # Separate start and end times
    start_times = sorted(interval[0] for interval in intervals)
    end_times = sorted(interval[1] for interval in intervals)
    
    start_ptr = end_ptr = 0
    rooms = available = 0
    
    while start_ptr < len(intervals):
        # If a meeting has ended by the time the current meeting starts
        if start_times[start_ptr] >= end_times[end_ptr]:
            available += 1
            end_ptr += 1
        else:
            if available > 0:
                available -= 1
            else:
                rooms += 1
            start_ptr += 1
    
    return rooms

@validate_intervals
def employee_free_time(schedule: List[List[List[T]]]) -> List[List[T]]:
    """
    Find the common free time between all employees' schedules.
    
    Args:
        schedule: List of employee schedules, where each schedule is a list of intervals
                 representing when the employee is busy
                 
    Returns:
        A list of intervals representing the common free time for all employees
        
    Time Complexity: O(n log n) where n is the total number of intervals
    Space Complexity: O(n)
    """
    if not schedule:
        return []
    
    # Flatten the schedule and sort all intervals
    all_intervals = [interval for emp in schedule for interval in emp]
    all_intervals.sort(key=lambda x: x[0])
    
    # Merge all intervals
    merged = []
    for interval in all_intervals:
        if not merged:
            merged.append(interval)
        else:
            last = merged[-1]
            if interval[0] <= last[1]:
                last[1] = max(last[1], interval[1])
            else:
                merged.append(interval)
    
    # Find the free time between merged intervals
    free_time = []
    for i in range(1, len(merged)):
        free_time.append([merged[i-1][1], merged[i][0]])
    
    return free_time
