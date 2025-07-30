"""
Trie (Prefix Tree) implementation for AlgoZen.

A trie is a tree-like data structure used to store a dynamic set of strings,
where the keys are usually strings. It's particularly useful for prefix-based operations.
"""
from typing import Dict, List, Optional


class TrieNode:
    """Node class for Trie implementation."""
    
    def __init__(self) -> None:
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word: bool = False


class Trie:
    """Trie (Prefix Tree) data structure implementation."""
    
    def __init__(self) -> None:
        """Initialize the trie with an empty root node."""
        self.root = TrieNode()
    
    def insert(self, word: str) -> None:
        """Insert a word into the trie.
        
        Args:
            word: The word to insert
            
        Time Complexity: O(m) where m is the length of the word
        Space Complexity: O(m) in worst case
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
    
    def search(self, word: str) -> bool:
        """Search for a word in the trie.
        
        Args:
            word: The word to search for
            
        Returns:
            True if the word exists in the trie, False otherwise
            
        Time Complexity: O(m) where m is the length of the word
        Space Complexity: O(1)
        """
        node = self._find_node(word)
        return node is not None and node.is_end_of_word
    
    def starts_with(self, prefix: str) -> bool:
        """Check if any word in the trie starts with the given prefix.
        
        Args:
            prefix: The prefix to check
            
        Returns:
            True if any word starts with the prefix, False otherwise
            
        Time Complexity: O(m) where m is the length of the prefix
        Space Complexity: O(1)
        """
        return self._find_node(prefix) is not None
    
    def delete(self, word: str) -> bool:
        """Delete a word from the trie.
        
        Args:
            word: The word to delete
            
        Returns:
            True if the word was deleted, False if it wasn't found
            
        Time Complexity: O(m) where m is the length of the word
        Space Complexity: O(m) due to recursion
        """
        def _delete_helper(node: TrieNode, word: str, index: int) -> bool:
            if index == len(word):
                if not node.is_end_of_word:
                    return False
                node.is_end_of_word = False
                return len(node.children) == 0
            
            char = word[index]
            if char not in node.children:
                return False
            
            should_delete_child = _delete_helper(node.children[char], word, index + 1)
            
            if should_delete_child:
                del node.children[char]
                return not node.is_end_of_word and len(node.children) == 0
            
            return False
        
        return _delete_helper(self.root, word, 0) or self.search(word)
    
    def get_all_words_with_prefix(self, prefix: str) -> List[str]:
        """Get all words in the trie that start with the given prefix.
        
        Args:
            prefix: The prefix to search for
            
        Returns:
            List of all words with the given prefix
            
        Time Complexity: O(p + n) where p is prefix length, n is number of nodes in subtree
        Space Complexity: O(n) for the result list
        """
        node = self._find_node(prefix)
        if node is None:
            return []
        
        words = []
        self._collect_words(node, prefix, words)
        return words
    
    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        """Find the node corresponding to the given prefix.
        
        Args:
            prefix: The prefix to find
            
        Returns:
            The node if found, None otherwise
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
    
    def _collect_words(self, node: TrieNode, prefix: str, words: List[str]) -> None:
        """Collect all words starting from the given node.
        
        Args:
            node: The starting node
            prefix: The current prefix
            words: List to collect words into
        """
        if node.is_end_of_word:
            words.append(prefix)
        
        for char, child_node in node.children.items():
            self._collect_words(child_node, prefix + char, words)
    
    def count_words(self) -> int:
        """Count the total number of words in the trie.
        
        Returns:
            Total number of words
            
        Time Complexity: O(n) where n is the number of nodes
        Space Complexity: O(h) where h is the height of the trie
        """
        def _count_helper(node: TrieNode) -> int:
            count = 1 if node.is_end_of_word else 0
            for child in node.children.values():
                count += _count_helper(child)
            return count
        
        return _count_helper(self.root)
    
    def is_empty(self) -> bool:
        """Check if the trie is empty.
        
        Returns:
            True if the trie contains no words, False otherwise
        """
        return len(self.root.children) == 0