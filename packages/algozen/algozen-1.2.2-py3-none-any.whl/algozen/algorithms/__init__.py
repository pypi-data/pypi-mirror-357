"""Algorithms module for AlgoZen."""

# Import sorting algorithms
from algozen.algorithms.sorting import (
    bubble_sort, selection_sort, insertion_sort, merge_sort,
    quick_sort, heap_sort, counting_sort, radix_sort
)

# Import searching algorithms
from algozen.algorithms.searching import (
    binary_search, linear_search, interpolation_search,
    exponential_search, jump_search, string_search
)

# Import other algorithm categories
from algozen.algorithms import (
    array_algorithms, geometry, graph_algorithms, greedy,
    linked_list_algorithms, matrix, number_theory,
    string_algorithms, tree_algorithms
)

__all__ = [
    # Sorting algorithms
    'bubble_sort', 'selection_sort', 'insertion_sort', 'merge_sort',
    'quick_sort', 'heap_sort', 'counting_sort', 'radix_sort',
    
    # Searching algorithms
    'binary_search', 'linear_search', 'interpolation_search',
    'exponential_search', 'jump_search', 'string_search',
    
    # Algorithm modules
    'array_algorithms', 'geometry', 'graph_algorithms', 'greedy',
    'linked_list_algorithms', 'matrix', 'number_theory',
    'string_algorithms', 'tree_algorithms'
]
