"""
Data Structures Module

This module contains various data structure implementations.
Includes:
- Heaps (MinHeap, MaxHeap)
- Stack
- Queue
- BinaryTree
- Graph
- LinkedList
- BinarySearchTree
- Trie
"""

from algozen.data_structures.heap import MinHeap, MaxHeap
from algozen.data_structures.stack import Stack
from algozen.data_structures.queue import Queue
from algozen.data_structures.binary_tree import BinaryTree
from algozen.data_structures.binary_search_tree import BinarySearchTree
from algozen.data_structures.linked_list import LinkedList, Node
from algozen.data_structures.graph import Graph, Edge
from algozen.data_structures.trie import Trie, TrieNode
from algozen.data_structures.segment_tree import SegmentTree, LazySegmentTree
from algozen.data_structures.union_find import UnionFind, WeightedUnionFind
from algozen.data_structures.fenwick_tree import FenwickTree, FenwickTree2D
from algozen.data_structures.avl_tree import AVLTree, AVLNode

__all__ = [
    'MinHeap', 'MaxHeap',
    'Stack',
    'Queue',
    'BinaryTree',
    'BinarySearchTree',
    'LinkedList', 'Node',
    'Graph', 'Edge',
    'Trie', 'TrieNode',
    'SegmentTree', 'LazySegmentTree',
    'UnionFind', 'WeightedUnionFind',
    'FenwickTree', 'FenwickTree2D',
    'AVLTree', 'AVLNode'
]
