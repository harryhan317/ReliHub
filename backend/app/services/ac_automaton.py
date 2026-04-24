"""
AC Automaton (Aho-Corasick Algorithm)

Efficient multi-pattern string matching algorithm.
Time Complexity: O(n + m + z) where n=text length, m=pattern total length, z=matches
"""

import logging
from collections import deque
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ACNode:
    """
    AC Automaton Node
    
    Attributes:
        char: Character for this node
        fail: Failure link
        children: Child nodes
        is_end: Whether this node marks end of a pattern
        pattern: Pattern that ends at this node (if any)
    """
    
    def __init__(self, char: str = ''):
        self.char = char
        self.fail: Optional['ACNode'] = None
        self.children: Dict[str, 'ACNode'] = {}
        self.is_end: bool = False
        self.pattern: Optional[str] = None
    
    def __repr__(self):
        return f"ACNode('{self.char}', end={self.is_end})"


class ACAutomaton:
    """
    Aho-Corasick Automaton
    
    Features:
    - Build trie from patterns
    - Build failure links
    - Search all occurrences
    - Support Chinese and English
    
    Usage:
        ac = ACAutomaton()
        ac.build(['敏感词', '违禁词', 'illegal'])
        matches = ac.search('这段文字包含敏感词')
        # matches: [('敏感词', position)]
    """
    
    def __init__(self):
        self.root = ACNode()
        self.patterns: List[str] = []
        self.is_built: bool = False
    
    def build(self, patterns: List[str]) -> None:
        """
        Build AC automaton from patterns
        
        Args:
            patterns: List of patterns to match
        """
        self.patterns = patterns
        self._build_trie()
        self._build_failure_links()
        self.is_built = True
        
        logger.info(f"AC automaton built with {len(patterns)} patterns")
    
    def _build_trie(self) -> None:
        """Build trie from patterns"""
        for pattern in self.patterns:
            if not pattern:
                continue
            
            node = self.root
            for char in pattern:
                if char not in node.children:
                    node.children[char] = ACNode(char)
                node = node.children[char]
            
            node.is_end = True
            node.pattern = pattern
    
    def _build_failure_links(self) -> None:
        """Build failure links using BFS"""
        queue = deque()
        
        # Initialize: set fail links for root's children
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)
        
        # BFS to build fail links
        while queue:
            current_node = queue.popleft()
            
            for char, child_node in current_node.children.items():
                # Find fail node
                fail_node = current_node.fail
                while fail_node and char not in fail_node.children:
                    fail_node = fail_node.fail
                
                # Set fail link
                child_node.fail = fail_node.children[char] if fail_node else self.root
                
                # Inherit output from fail node
                if child_node.fail and child_node.fail.is_end:
                    # If fail node is end of pattern, mark this node too
                    pass  # We'll handle this in search
                
                queue.append(child_node)
    
    def search(self, text: str) -> List[Tuple[str, int]]:
        """
        Search all pattern occurrences in text
        
        Args:
            text: Text to search
            
        Returns:
            List of (pattern, start_position) tuples
        """
        if not self.is_built:
            raise RuntimeError("AC automaton not built. Call build() first.")
        
        matches = []
        node = self.root
        
        for i, char in enumerate(text):
            # Follow fail links until match found or root reached
            while node and char not in node.children:
                node = node.fail
            
            # Move to child node
            if node and char in node.children:
                node = node.children[char]
            else:
                node = self.root  # No match, back to root
            
            # Check if current node marks end of pattern
            if node and node.is_end:
                start_pos = i - len(node.pattern) + 1
                matches.append((node.pattern, start_pos))
            
            # Check fail chain for additional matches
            if node:
                fail_node = node.fail
                while fail_node and fail_node != self.root:
                    if fail_node.is_end:
                        start_pos = i - len(fail_node.pattern) + 1
                        matches.append((fail_node.pattern, start_pos))
                    fail_node = fail_node.fail
        
        return matches
    
    def contains(self, text: str) -> bool:
        """
        Check if text contains any pattern
        
        Args:
            text: Text to check
            
        Returns:
            True if any pattern found, False otherwise
        """
        matches = self.search(text)
        return len(matches) > 0
    
    def replace(self, text: str, replacement: str = '*') -> str:
        """
        Replace all matched patterns in text
        
        Args:
            text: Text to process
            replacement: Replacement character
            
        Returns:
            Text with patterns replaced
        """
        matches = self.search(text)
        
        if not matches:
            return text
        
        # Sort by position (descending) to replace from end to start
        matches.sort(key=lambda x: x[1], reverse=True)
        
        result = text
        for pattern, start_pos in matches:
            end_pos = start_pos + len(pattern)
            result = result[:start_pos] + (replacement * len(pattern)) + result[end_pos:]
        
        return result
    
    def filter(self, text: str) -> Tuple[bool, str, List[Tuple[str, int]]]:
        """
        Filter text for sensitive words
        
        Args:
            text: Text to filter
            
        Returns:
            Tuple of (is_safe, filtered_text, matches)
            - is_safe: True if no sensitive words found
            - filtered_text: Text with sensitive words replaced
            - matches: List of (pattern, position) tuples
        """
        matches = self.search(text)
        is_safe = len(matches) == 0
        filtered_text = self.replace(text) if not is_safe else text
        
        return is_safe, filtered_text, matches
    
    def get_stats(self) -> Dict:
        """
        Get automaton statistics
        
        Returns:
            Dict with statistics
        """
        def count_nodes(node: ACNode) -> int:
            count = 1  # Count current node
            for child in node.children.values():
                count += count_nodes(child)
            return count
        
        total_nodes = count_nodes(self.root)
        
        return {
            "patterns": len(self.patterns),
            "total_nodes": total_nodes,
            "is_built": self.is_built
        }


class SensitiveWordFilter:
    """
    Sensitive Word Filter
    
    High-level API for sensitive word filtering.
    
    Usage:
        filter = SensitiveWordFilter(['敏感词', '违禁词'])
        
        # Check if text is safe
        is_safe = filter.is_safe("这段文字没问题")
        
        # Get filtered text
        is_safe, filtered = filter.filter("这段文字包含敏感词")
        
        # Get detailed matches
        is_safe, filtered, matches = filter.filter("这段文字包含敏感词")
    """
    
    def __init__(self, patterns: Optional[List[str]] = None):
        """
        Initialize sensitive word filter
        
        Args:
            patterns: List of sensitive words
        """
        self.ac = ACAutomaton()
        if patterns:
            self.build(patterns)
    
    def build(self, patterns: List[str]) -> None:
        """
        Build filter with patterns
        
        Args:
            patterns: List of sensitive words
        """
        # Remove duplicates and empty strings
        unique_patterns = list(set(p for p in patterns if p))
        self.ac.build(unique_patterns)
    
    def is_safe(self, text: str) -> bool:
        """
        Check if text is safe (no sensitive words)
        
        Args:
            text: Text to check
            
        Returns:
            True if safe, False otherwise
        """
        return not self.ac.contains(text)
    
    def filter(self, text: str, replacement: str = '*') -> Tuple[bool, str, List[Tuple[str, int]]]:
        """
        Filter text for sensitive words
        
        Args:
            text: Text to filter
            replacement: Replacement character
            
        Returns:
            Tuple of (is_safe, filtered_text, matches)
        """
        is_safe_flag = self.is_safe(text)
        filtered_text = self.ac.replace(text, replacement) if not is_safe_flag else text
        matches = self.ac.search(text)
        
        return is_safe_flag, filtered_text, matches
    
    def add_patterns(self, patterns: List[str]) -> None:
        """
        Add new patterns to filter
        
        Args:
            patterns: List of sensitive words to add
        """
        existing = set(self.ac.patterns)
        new_patterns = [p for p in patterns if p and p not in existing]
        
        if new_patterns:
            all_patterns = self.ac.patterns + new_patterns
            self.build(all_patterns)
    
    def remove_patterns(self, patterns: List[str]) -> None:
        """
        Remove patterns from filter
        
        Args:
            patterns: List of patterns to remove
        """
        remaining = [p for p in self.ac.patterns if p not in patterns]
        self.build(remaining)
    
    def get_stats(self) -> Dict:
        """
        Get filter statistics
        
        Returns:
            Dict with statistics
        """
        return self.ac.get_stats()
