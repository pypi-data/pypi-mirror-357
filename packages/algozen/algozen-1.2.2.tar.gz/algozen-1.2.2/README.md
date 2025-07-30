# 🚀 AlgoZen - Comprehensive Data Structures & Algorithms Package

[![PyPI version](https://badge.fury.io/py/algozen.svg)](https://badge.fury.io/py/algozen)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AlgoZen** is a comprehensive Python package providing efficient implementations of data structures, algorithms, design patterns, and common programming problems. Perfect for learning, coding interviews, competitive programming, and production use.

## ✨ Features

### 🏗️ **Data Structures** (12 implementations)
- **Heaps**: MinHeap, MaxHeap with O(log n) operations
- **Linear**: Stack, Queue, LinkedList with full functionality
- **Trees**: BinaryTree, BinarySearchTree, AVLTree, Trie
- **Advanced**: SegmentTree, FenwickTree, UnionFind
- **Graphs**: Comprehensive graph representation with algorithms

### 🔧 **Algorithms** (11 categories)
- **Sorting**: Bubble, Selection, Insertion, Merge, Quick, Heap, Counting, Radix
- **Searching**: Linear, Binary, Interpolation, Exponential, Jump
- **String**: KMP, Rabin-Karp, Z-Algorithm, Edit Distance
- **Graph**: DFS, BFS, Dijkstra, Bellman-Ford, Floyd-Warshall
- **Tree**: Traversals, LCA, Path algorithms
- **Mathematical**: GCD, LCM, Prime algorithms, Number theory

### 🎯 **Patterns** (14 problem-solving patterns)
- **Bit Manipulation**: Count bits, XOR operations, bit tricks
- **Sliding Window**: Maximum sum, substring problems
- **Two Pointers**: Pair finding, array manipulation
- **Fast/Slow Pointers**: Cycle detection, middle finding
- **Merge Intervals**: Overlapping intervals, scheduling
- **Dynamic Programming**: Advanced DP patterns and optimizations

### 🏛️ **Design Patterns** (9 classic patterns)
- **Creational**: Factory, Builder patterns
- **Behavioral**: Observer, Strategy, Command, State
- **Structural**: Decorator, Adapter patterns

### 💡 **Problems** (9 categories, 200+ solutions)
- **Arrays**: Two sum, maximum subarray, product problems
- **Strings**: Palindromes, anagrams, pattern matching
- **Trees**: Traversals, path problems, validation
- **Graphs**: Shortest paths, connectivity, topological sort
- **Dynamic Programming**: Classic DP problems and variations

## 🚀 Installation

```bash
# Install from PyPI
pip install algozen

# Or install the latest version
pip install --upgrade algozen
```

## 🏃 Quick Start

```python
# Import the package
import algozen

# Use data structures
from algozen.data_structures import MinHeap, BinarySearchTree, Graph

# Create and use a MinHeap
heap = MinHeap()
heap.insert(5)
heap.insert(3)
heap.insert(8)
print(heap.extract_min())  # Output: 3

# Use algorithms
from algozen.algorithms import quick_sort, binary_search

# Sort an array
arr = [64, 34, 25, 12, 22, 11, 90]
sorted_arr = quick_sort(arr)
print(sorted_arr)  # Output: [11, 12, 22, 25, 34, 64, 90]

# Search in sorted array
index = binary_search(sorted_arr, 25)
print(index)  # Output: 3

# Use patterns
from algozen.patterns.sliding_window import max_sum_subarray_of_size_k
from algozen.patterns.two_pointers import pair_with_target_sum

# Sliding window pattern
max_sum = max_sum_subarray_of_size_k([2, 1, 5, 1, 3, 2], 3)
print(max_sum)  # Output: 9

# Two pointers pattern
indices = pair_with_target_sum([1, 2, 3, 4, 6], 6)
print(indices)  # Output: [1, 3]

# Use design patterns
from algozen.design_patterns.factory import AnimalFactory, AnimalType

factory = AnimalFactory()
dog = factory.create_animal(AnimalType.DOG, "Buddy")
print(dog.make_sound())  # Output: Woof!

# Solve problems
from algozen.problems.arrays import two_sum, max_subarray_sum

# Two sum problem
result = two_sum([2, 7, 11, 15], 9)
print(result)  # Output: [0, 1]

# Maximum subarray sum (Kadane's algorithm)
max_sum = max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4])
print(max_sum)  # Output: 6
```

## 📚 Documentation

### Data Structures

#### MinHeap / MaxHeap
```python
from algozen.data_structures import MinHeap, MaxHeap

# MinHeap operations
heap = MinHeap()
heap.insert(10)      # Insert element
heap.insert(5)
min_val = heap.extract_min()  # Remove and return minimum
top = heap.peek()    # View minimum without removing
size = heap.size()   # Get number of elements
empty = heap.is_empty()  # Check if empty
```

#### Binary Search Tree
```python
from algozen.data_structures import BinarySearchTree

bst = BinarySearchTree()
bst.insert(50)       # Insert key
bst.insert(30)
bst.insert(70)
found = bst.search(30)     # Search for key
bst.delete(30)       # Delete key
min_key = bst.min()  # Find minimum key
max_key = bst.max()  # Find maximum key
```

#### Graph
```python
from algozen.data_structures import Graph

graph = Graph()
graph.add_vertex("A")        # Add vertex
graph.add_vertex("B")
graph.add_edge("A", "B", 5)  # Add weighted edge
neighbors = graph.get_neighbors("A")  # Get adjacent vertices
```

### Algorithms

#### Sorting Algorithms
```python
from algozen.algorithms.sorting import quick_sort, merge_sort, heap_sort

arr = [64, 34, 25, 12, 22, 11, 90]

# All sorting functions modify and return the array
sorted_arr = quick_sort(arr.copy())    # O(n log n) average
sorted_arr = merge_sort(arr.copy())    # O(n log n) guaranteed
sorted_arr = heap_sort(arr.copy())     # O(n log n) in-place
```

#### String Algorithms
```python
from algozen.algorithms.string_algorithms import kmp_search, rabin_karp_search

text = "ababcababa"
pattern = "aba"

# Find all occurrences of pattern in text
matches = kmp_search(text, pattern)        # KMP algorithm
matches = rabin_karp_search(text, pattern) # Rabin-Karp algorithm
```

### Patterns

#### Sliding Window
```python
from algozen.patterns.sliding_window import (
    max_sum_subarray_of_size_k,
    longest_substring_with_k_distinct,
    longest_substring_without_repeating_chars
)

# Maximum sum of subarray of size k
max_sum = max_sum_subarray_of_size_k([2, 1, 5, 1, 3, 2], 3)

# Longest substring with k distinct characters
length = longest_substring_with_k_distinct("araaci", 2)

# Longest substring without repeating characters
length = longest_substring_without_repeating_chars("abcabcbb")
```

#### Two Pointers
```python
from algozen.patterns.two_pointers import (
    pair_with_target_sum,
    remove_duplicates,
    search_triplets
)

# Find pair with target sum in sorted array
indices = pair_with_target_sum([1, 2, 3, 4, 6], 6)

# Remove duplicates from sorted array in-place
arr = [2, 3, 3, 3, 6, 9, 9]
new_length = remove_duplicates(arr)

# Find all triplets that sum to target
triplets = search_triplets([-3, 0, 1, 2, -1, 1, -2], 0)
```

### Design Patterns

#### Factory Pattern
```python
from algozen.design_patterns.factory import AnimalFactory, AnimalType

factory = AnimalFactory()
dog = factory.create_animal(AnimalType.DOG, "Buddy")
cat = factory.create_animal(AnimalType.CAT, "Whiskers")

print(dog.make_sound())  # Woof!
print(cat.make_sound())  # Meow!
```

#### Observer Pattern
```python
from algozen.design_patterns.observer import Subject, Observer

# Create subject and observers
subject = Subject()
observer1 = Observer("Observer1")
observer2 = Observer("Observer2")

# Attach observers
subject.attach(observer1)
subject.attach(observer2)

# Notify all observers
subject.notify("data_changed", {"new_value": 42})
```

## 🧪 Testing

AlgoZen comes with comprehensive test coverage ensuring all functionality works correctly:

```python
# All modules are thoroughly tested
import algozen

# Test data structures
from algozen.data_structures import MinHeap
heap = MinHeap()
heap.insert(5)
assert heap.extract_min() is not None

# Test algorithms  
from algozen.algorithms.sorting import quick_sort
result = quick_sort([3, 1, 4, 1, 5])
assert result == [1, 1, 3, 4, 5]
```

## 📊 Performance Characteristics

| Data Structure | Insert | Delete | Search | Space |
|---------------|--------|--------|--------|-------|
| MinHeap/MaxHeap | O(log n) | O(log n) | O(n) | O(n) |
| Stack | O(1) | O(1) | O(n) | O(n) |
| Queue | O(1) | O(1) | O(n) | O(n) |
| BST | O(log n)* | O(log n)* | O(log n)* | O(n) |
| Graph | O(1) | O(V) | O(V) | O(V+E) |

*Average case. Worst case is O(n) for unbalanced trees.

| Algorithm | Best | Average | Worst | Space |
|-----------|------|---------|-------|-------|
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Binary Search | O(1) | O(log n) | O(log n) | O(1) |
| KMP Search | O(n+m) | O(n+m) | O(n+m) | O(m) |

## 🏗️ Project Structure

```
algozen/
├── data_structures/     # Core data structure implementations
│   ├── heap.py         # MinHeap, MaxHeap
│   ├── stack.py        # Stack implementation
│   ├── queue.py        # Queue implementation
│   ├── linked_list.py  # LinkedList with Node
│   ├── binary_search_tree.py  # BST implementation
│   ├── graph.py        # Graph with Edge
│   ├── trie.py         # Trie with TrieNode
│   └── ...            # Other data structures
├── algorithms/          # Algorithm implementations
│   ├── sorting.py      # All sorting algorithms
│   ├── searching.py    # All searching algorithms
│   ├── string_algorithms.py  # String processing
│   └── ...            # Other algorithm categories
├── patterns/           # DSA patterns and techniques
│   ├── bit_manipulation.py   # Bit manipulation patterns
│   ├── sliding_window.py     # Sliding window technique
│   ├── two_pointers.py       # Two pointers technique
│   └── ...            # Other patterns
├── design_patterns/    # Software design patterns
│   ├── factory.py      # Factory pattern
│   ├── observer.py     # Observer pattern
│   ├── strategy.py     # Strategy pattern
│   └── ...            # Other design patterns
├── problems/          # Common DSA problems
│   ├── arrays.py      # Array problems
│   ├── strings.py     # String problems
│   ├── trees.py       # Tree problems
│   └── ...           # Other problem categories
└── test_comprehensive.py  # Complete test suite
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive docstrings with time/space complexity
- Include examples in docstrings
- Ensure backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by classic algorithms and data structures textbooks
- Built with modern Python best practices
- Designed for both learning and production use

## 📈 Stats

- **55 Python modules** with comprehensive implementations
- **900+ functions and classes** covering all major CS concepts
- **Zero dependencies** for core functionality
- **Production-ready** code with proper error handling
- **Extensive documentation** with examples and complexity analysis
- **MIT Licensed** - free for commercial and personal use

## 🔄 Changelog

### Version 1.2.2
- Complete reorganization with perfect module structure
- Added comprehensive design patterns module
- Enhanced all data structures with full functionality
- Improved algorithm implementations with better performance
- Added 200+ problem solutions across 9 categories
- Zero duplicate code - clean, maintainable codebase
- Full test coverage ensuring reliability

---

**Made with ❤️ by moah0911**

*AlgoZen - Where algorithms meet zen-like simplicity* 🧘‍♂️