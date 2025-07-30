"""
DSA Patterns Module

This module provides implementations of common Data Structures and Algorithms patterns.
For design patterns, see algozen.design_patterns.
"""

# DSA Patterns
from algozen.patterns.array_patterns import *
from algozen.patterns.bit_manipulation import *
from algozen.patterns.cyclic_sort import *
from algozen.patterns.divide_conquer import *
from algozen.patterns.fast_slow_pointers import *
from algozen.patterns.graph_patterns import *
from algozen.patterns.mathematical_patterns import *
from algozen.patterns.merge_intervals import *
from algozen.patterns.optimization_patterns import *
from algozen.patterns.sliding_window import *
from algozen.patterns.string_processing import *
from algozen.patterns.tree_patterns import *
from algozen.patterns.two_pointers import *
from algozen.patterns.advanced_dp import *

__all__ = []

# Collect all exports from DSA pattern modules
for module_name in [
    'array_patterns', 'bit_manipulation', 'cyclic_sort', 'divide_conquer',
    'fast_slow_pointers', 'graph_patterns', 'mathematical_patterns',
    'merge_intervals', 'optimization_patterns', 'sliding_window',
    'string_processing', 'tree_patterns', 'two_pointers', 'advanced_dp'
]:
    try:
        module = __import__(f'algozen.patterns.{module_name}', fromlist=['*'])
        if hasattr(module, '__all__'):
            __all__.extend(module.__all__)
        else:
            __all__.extend([name for name in dir(module) if not name.startswith('_')])
    except ImportError:
        pass

__all__ = list(dict.fromkeys(__all__))  # Remove duplicates
