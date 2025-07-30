"""
Linked List Problems and Solutions.

This module contains implementations of common linked list problems.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Set, Any, TypeVar, Callable, Generic
from functools import wraps
import random

T = TypeVar('T')

class ListNode(Generic[T]):
    """Node class for singly-linked list."""
    def __init__(self, val: T = None, next: Optional[ListNode[T]] = None):
        self.val = val
        self.next = next
    
    def __str__(self) -> str:
        return f"{self.val} -> {self.next}" if self.next else f"{self.val} -> None"
    
    @classmethod
    def from_list(cls, values: List[T]) -> Optional[ListNode[T]]:
        """Create a linked list from a list of values."""
        if not values:
            return None
            
        head = cls(values[0])
        current = head
        
        for val in values[1:]:
            current.next = cls(val)
            current = current.next
            
        return head
    
    def to_list(self) -> List[T]:
        """Convert linked list to a list of values."""
        result = []
        current = self
        
        while current is not None:
            result.append(current.val)
            current = current.next
            
        return result

def validate_linked_list(func: Callable) -> Callable:
    """Decorator to validate linked list input for linked list problems."""
    @wraps(func)
    def wrapper(head: Optional[ListNode], *args, **kwargs) -> Any:
        # Some functions might accept None as valid input
        return func(head, *args, **kwargs)
    return wrapper

@validate_linked_list
def reverse_linked_list(head: Optional[ListNode[T]]) -> Optional[ListNode[T]]:
    """
    Reverse a singly linked list.
    
    Args:
        head: Head of the linked list
        
    Returns:
        The new head of the reversed linked list
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    prev = None
    current = head
    
    while current is not None:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    
    return prev

@validate_linked_list
def has_cycle(head: Optional[ListNode[T]]) -> bool:
    """
    Determine if a linked list has a cycle using Floyd's Cycle-Finding Algorithm.
    
    Args:
        head: Head of the linked list
        
    Returns:
        True if the linked list has a cycle, False otherwise
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not head or not head.next:
        return False
    
    slow = head
    fast = head.next
    
    while fast and fast.next:
        if slow == fast:
            return True
        slow = slow.next
        fast = fast.next.next
    
    return False

@validate_linked_list
def get_intersection_node(
    headA: Optional[ListNode[T]], 
    headB: Optional[ListNode[T]]
) -> Optional[ListNode[T]]:
    """
    Find the node at which the intersection of two singly linked lists begins.
    
    Args:
        headA: Head of the first linked list
        headB: Head of the second linked list
        
    Returns:
        The intersection node if exists, None otherwise
        
    Time Complexity: O(m + n)
    Space Complexity: O(1)
    """
    if not headA or not headB:
        return None
    
    # Get lengths of both lists
    def get_length(node: Optional[ListNode[T]]) -> int:
        length = 0
        while node:
            length += 1
            node = node.next
        return length
    
    lenA, lenB = get_length(headA), get_length(headB)
    
    # Move the longer list's head forward by the difference in lengths
    currA, currB = headA, headB
    
    if lenA > lenB:
        for _ in range(lenA - lenB):
            currA = currA.next
    else:
        for _ in range(lenB - lenA):
            currB = currB.next
    
    # Move both pointers until they meet or reach the end
    while currA and currB and currA != currB:
        currA = currA.next
        currB = currB.next
    
    return currA if currA == currB else None

@validate_linked_list
def merge_two_sorted_lists(
    l1: Optional[ListNode[int]], 
    l2: Optional[ListNode[int]]
) -> Optional[ListNode[int]]:
    """
    Merge two sorted linked lists and return it as a new sorted list.
    
    Args:
        l1: Head of the first sorted linked list
        l2: Head of the second sorted linked list
        
    Returns:
        The head of the merged sorted linked list
        
    Time Complexity: O(n + m)
    Space Complexity: O(1)
    """
    dummy = ListNode(-1)
    current = dummy
    
    while l1 and l2:
        if l1.val <= l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next
    
    # Attach the remaining elements
    current.next = l1 if l1 else l2
    
    return dummy.next

@validate_linked_list
def remove_nth_from_end(head: Optional[ListNode[T]], n: int) -> Optional[ListNode[T]]:
    """
    Remove the nth node from the end of the list and return its head.
    
    Args:
        head: Head of the linked list
        n: The position from the end to remove (1-based indexing)
        
    Returns:
        The head of the modified linked list
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not head or n <= 0:
        return head
    
    dummy = ListNode(-1)
    dummy.next = head
    
    # Move fast pointer n nodes ahead
    fast = dummy
    for _ in range(n + 1):
        if not fast:
            return head  # n is larger than the list length
        fast = fast.next
    
    # Move both pointers until fast reaches the end
    slow = dummy
    while fast:
        slow = slow.next
        fast = fast.next
    
    # Remove the nth node from the end
    slow.next = slow.next.next
    
    return dummy.next

@validate_linked_list
def reorder_list(head: Optional[ListNode[T]]) -> None:
    """
    Reorder a linked list in the following order:
    L0 → L1 → … → Ln-1 → Ln → L0 → Ln-1 → L1 → Ln-2 → …
    
    Args:
        head: Head of the linked list (modified in-place)
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not head or not head.next:
        return
    
    # Find the middle of the linked list
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    
    # Reverse the second half
    prev, curr = None, slow
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    
    # Merge the two halves
    first, second = head, prev
    while second.next:
        temp1, temp2 = first.next, second.next
        first.next = second
        second.next = temp1
        first, second = temp1, temp2

@validate_linked_list
def copy_random_list(head: Optional[ListNode[T]]) -> Optional[ListNode[T]]:
    """
    A linked list is given such that each node contains an additional random pointer
    which could point to any node in the list or null.
    
    Args:
        head: Head of the linked list with random pointers
        
    Returns:
        A deep copy of the linked list
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not head:
        return None
    
    # Create a mapping from original nodes to their copies
    node_map = {}
    
    # First pass: create all nodes
    current = head
    while current:
        node_map[current] = ListNode(current.val)
        current = current.next
    
    # Second pass: set next and random pointers
    current = head
    while current:
        if current.next:
            node_map[current].next = node_map.get(current.next)
        if hasattr(current, 'random') and current.random:
            node_map[current].random = node_map.get(current.random)
        current = current.next
    
    return node_map[head]
