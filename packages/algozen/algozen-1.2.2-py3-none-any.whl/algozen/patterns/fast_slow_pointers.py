"""
Fast and Slow Pointers Pattern implementations.

This module provides functions that demonstrate the fast and slow pointers technique,
which is useful for cycle detection, finding middle elements, and solving various
linked list and array problems efficiently.
"""
from typing import List, Optional, Tuple, TypeVar, Any, Callable, Generic
from functools import wraps
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class ListNode(Generic[T]):
    """Node class for linked list implementations."""
    val: T
    next: Optional['ListNode[T]'] = None

def validate_linked_list(func: Callable) -> Callable:
    """Decorator to validate linked list input for cycle detection functions."""
    @wraps(func)
    def wrapper(head: Optional[ListNode], *args, **kwargs) -> Any:
        if head is None:
            raise ValueError("Head node cannot be None")
        return func(head, *args, **kwargs)
    return wrapper

def create_linked_list(values: List[T]) -> Optional[ListNode[T]]:
    """Helper function to create a linked list from a list of values."""
    if not values:
        return None
    
    head = ListNode(values[0])
    current = head
    
    for val in values[1:]:
        current.next = ListNode(val)
        current = current.next
    
    return head

def create_cycle(head: ListNode[T], pos: int) -> None:
    """
    Create a cycle in a linked list at the specified position.
    
    Args:
        head: Head of the linked list
        pos: 0-based index of the node where the tail connects to form a cycle.
             If pos is -1, no cycle is created.
    """
    if pos == -1:
        return
        
    # Find the tail and the node at position pos
    tail = head
    cycle_node = None
    current = head
    index = 0
    
    while tail.next is not None:
        if index == pos:
            cycle_node = current
        current = tail
        tail = tail.next
        index += 1
    
    # If pos is 0, cycle starts at head
    if pos == 0:
        tail.next = head
    # If pos is within bounds, create cycle
    elif cycle_node is not None:
        tail.next = cycle_node

@validate_linked_list
def has_cycle(head: ListNode[T]) -> bool:
    """
    Detect if a linked list has a cycle using Floyd's Cycle-Finding Algorithm.
    
    Args:
        head: Head node of the linked list
        
    Returns:
        True if a cycle exists, False otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    slow = fast = head
    
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        
        if slow == fast:
            return True
            
    return False

@validate_linked_list
def find_cycle_start(head: ListNode[T]) -> Optional[ListNode[T]]:
    """
    Find the starting node of the cycle in a linked list.
    
    Args:
        head: Head node of the linked list
        
    Returns:
        The starting node of the cycle if it exists, None otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    # First, determine if a cycle exists and find the meeting point
    slow = fast = head
    has_cycle = False
    
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        
        if slow == fast:
            has_cycle = True
            break
    
    if not has_cycle:
        return None
    
    # Find the start of the cycle
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    
    return slow

@validate_linked_list
def find_middle(head: ListNode[T]) -> ListNode[T]:
    """
    Find the middle node of a linked list using fast and slow pointers.
    If the list has even number of nodes, returns the first middle node.
    
    Args:
        head: Head node of the linked list
        
    Returns:
        The middle node of the linked list
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    slow = fast = head
    
    while fast.next is not None and fast.next.next is not None:
        slow = slow.next
        fast = fast.next.next
    
    return slow

@validate_linked_list
def is_palindrome(head: ListNode[T]) -> bool:
    """
    Check if a linked list is a palindrome using fast and slow pointers.
    
    Args:
        head: Head node of the linked list
        
    Returns:
        True if the linked list is a palindrome, False otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if head.next is None:
        return True
    
    # Find the middle of the linked list
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    
    # Reverse the second half
    prev = None
    current = slow
    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    
    # Compare first half with reversed second half
    left, right = head, prev
    while right:
        if left.val != right.val:
            return False
        left = left.next
        right = right.next
    
    return True

def find_duplicate(nums: List[int]) -> int:
    """
    Find the duplicate number in an array of integers where:
    - There is exactly one duplicate number
    - The array length is n+1 and contains numbers from 1 to n
    
    Args:
        nums: List of integers with one duplicate
        
    Returns:
        The duplicate number
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not nums or len(nums) < 2:
        raise ValueError("Input list must contain at least 2 elements")
    
    # Phase 1: Find the intersection point of the two runners
    slow = fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    
    # Phase 2: Find the entrance to the cycle
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    
    return slow

def find_duplicate_cyclic_sort(nums: List[int]) -> int:
    """
    Find the duplicate number using cyclic sort approach.
    
    Args:
        nums: List of integers with one duplicate
        
    Returns:
        The duplicate number
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    i = 0
    n = len(nums)
    
    while i < n:
        if nums[i] != i + 1:
            j = nums[i] - 1
            if nums[i] != nums[j]:
                # Swap
                nums[i], nums[j] = nums[j], nums[i]
            else:
                return nums[i]
        else:
            i += 1
    
    return -1  # No duplicate found (shouldn't happen per problem constraints)
