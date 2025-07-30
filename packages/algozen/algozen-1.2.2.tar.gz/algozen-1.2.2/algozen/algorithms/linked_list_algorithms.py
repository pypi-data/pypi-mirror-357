"""
Advanced linked list algorithms for AlgoZen.

This module provides various advanced linked list manipulation algorithms.
"""
from typing import Optional


class ListNode:
    """Singly linked list node."""
    def __init__(self, val: int = 0, next: 'ListNode' = None):
        self.val = val
        self.next = next


def reverse_linked_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """Reverse a linked list iteratively.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    prev = None
    current = head
    
    while current:
        next_temp = current.next
        current.next = prev
        prev = current
        current = next_temp
    
    return prev


def reverse_k_group(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    """Reverse nodes in k-group.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    def get_length(node):
        length = 0
        while node:
            length += 1
            node = node.next
        return length
    
    def reverse_group(start, k):
        prev = None
        current = start
        for _ in range(k):
            next_temp = current.next
            current.next = prev
            prev = current
            current = next_temp
        return prev, current
    
    length = get_length(head)
    if length < k:
        return head
    
    dummy = ListNode(0)
    dummy.next = head
    prev_group_end = dummy
    
    while length >= k:
        group_start = prev_group_end.next
        group_end, next_group_start = reverse_group(group_start, k)
        
        prev_group_end.next = group_end
        group_start.next = next_group_start
        prev_group_end = group_start
        
        length -= k
    
    return dummy.next


def detect_cycle(head: Optional[ListNode]) -> Optional[ListNode]:
    """Detect cycle in linked list and return starting node.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not head or not head.next:
        return None
    
    # Phase 1: Detect if cycle exists
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None
    
    # Phase 2: Find cycle start
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    
    return slow


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """Merge k sorted linked lists.
    
    Time Complexity: O(n log k)
    Space Complexity: O(log k)
    """
    if not lists:
        return None
    
    def merge_two(l1, l2):
        dummy = ListNode(0)
        current = dummy
        
        while l1 and l2:
            if l1.val <= l2.val:
                current.next = l1
                l1 = l1.next
            else:
                current.next = l2
                l2 = l2.next
            current = current.next
        
        current.next = l1 or l2
        return dummy.next
    
    while len(lists) > 1:
        merged_lists = []
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            merged_lists.append(merge_two(l1, l2))
        lists = merged_lists
    
    return lists[0]


def remove_nth_from_end(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    """Remove nth node from end of list.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    dummy = ListNode(0)
    dummy.next = head
    first = second = dummy
    
    # Move first n+1 steps ahead
    for _ in range(n + 1):
        first = first.next
    
    # Move both until first reaches end
    while first:
        first = first.next
        second = second.next
    
    # Remove nth node
    second.next = second.next.next
    return dummy.next


def copy_random_list(head: Optional['Node']) -> Optional['Node']:
    """Copy linked list with random pointers.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not head:
        return None
    
    # Step 1: Create cloned nodes
    current = head
    while current:
        cloned = ListNode(current.val)
        cloned.next = current.next
        current.next = cloned
        current = cloned.next
    
    # Step 2: Set random pointers
    current = head
    while current:
        if current.random:
            current.next.random = current.random.next
        current = current.next.next
    
    # Step 3: Separate lists
    dummy = ListNode(0)
    cloned_current = dummy
    current = head
    
    while current:
        cloned_current.next = current.next
        current.next = current.next.next
        current = current.next
        cloned_current = cloned_current.next
    
    return dummy.next


def add_two_numbers(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """Add two numbers represented as linked lists.
    
    Time Complexity: O(max(m,n))
    Space Complexity: O(max(m,n))
    """
    dummy = ListNode(0)
    current = dummy
    carry = 0
    
    while l1 or l2 or carry:
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        
        total = val1 + val2 + carry
        carry = total // 10
        current.next = ListNode(total % 10)
        
        current = current.next
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    
    return dummy.next


def partition_list(head: Optional[ListNode], x: int) -> Optional[ListNode]:
    """Partition list around value x.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    before_head = ListNode(0)
    after_head = ListNode(0)
    before = before_head
    after = after_head
    
    while head:
        if head.val < x:
            before.next = head
            before = before.next
        else:
            after.next = head
            after = after.next
        head = head.next
    
    after.next = None
    before.next = after_head.next
    
    return before_head.next


def rotate_right(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    """Rotate list to the right by k places.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not head or not head.next or k == 0:
        return head
    
    # Find length and make circular
    length = 1
    tail = head
    while tail.next:
        tail = tail.next
        length += 1
    
    tail.next = head  # Make circular
    
    # Find new tail (length - k % length - 1 steps from head)
    k = k % length
    steps_to_new_tail = length - k
    new_tail = head
    
    for _ in range(steps_to_new_tail - 1):
        new_tail = new_tail.next
    
    new_head = new_tail.next
    new_tail.next = None
    
    return new_head


def sort_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """Sort linked list using merge sort.
    
    Time Complexity: O(n log n)
    Space Complexity: O(log n)
    """
    if not head or not head.next:
        return head
    
    # Find middle using slow/fast pointers
    slow = fast = head
    prev = None
    
    while fast and fast.next:
        prev = slow
        slow = slow.next
        fast = fast.next.next
    
    # Split list
    prev.next = None
    
    # Recursively sort both halves
    left = sort_list(head)
    right = sort_list(slow)
    
    # Merge sorted halves
    return merge_two_sorted_lists(left, right)


def merge_two_sorted_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """Merge two sorted linked lists.
    
    Time Complexity: O(m + n)
    Space Complexity: O(1)
    """
    dummy = ListNode(0)
    current = dummy
    
    while l1 and l2:
        if l1.val <= l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next
    
    current.next = l1 or l2
    return dummy.next