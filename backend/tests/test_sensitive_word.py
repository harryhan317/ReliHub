"""
Tests for AC Automaton sensitive word filtering algorithm.
"""

import pytest

from app.services.ac_automaton import ACAutomaton, SensitiveWordFilter


class TestACAutomaton:
    """Test AC Automaton implementation"""
    
    def test_init(self):
        """Test AC automaton initialization"""
        ac = ACAutomaton()
        
        assert ac.root is not None
        assert ac.is_built is False
        assert ac.patterns == []
    
    def test_build_empty(self):
        """Test building with empty patterns"""
        ac = ACAutomaton()
        ac.build([])
        
        assert ac.is_built is True
        assert ac.patterns == []
    
    def test_build_single_pattern(self):
        """Test building with single pattern"""
        ac = ACAutomaton()
        ac.build(["hello"])
        
        assert ac.is_built is True
        assert len(ac.patterns) == 1
        assert "hello" in ac.patterns
    
    def test_build_multiple_patterns(self):
        """Test building with multiple patterns"""
        ac = ACAutomaton()
        patterns = ["hello", "world", "test"]
        ac.build(patterns)
        
        assert ac.is_built is True
        assert len(ac.patterns) == 3
        assert all(p in ac.patterns for p in patterns)
    
    def test_search_empty_text(self):
        """Test searching empty text"""
        ac = ACAutomaton()
        ac.build(["hello", "world"])
        
        matches = ac.search("")
        assert len(matches) == 0
    
    def test_search_no_matches(self):
        """Test searching with no matches"""
        ac = ACAutomaton()
        ac.build(["hello", "world"])
        
        matches = ac.search("foo bar baz")
        assert len(matches) == 0
    
    def test_search_single_match(self):
        """Test searching with single match"""
        ac = ACAutomaton()
        ac.build(["hello"])
        
        matches = ac.search("hello world")
        assert len(matches) == 1
        assert matches[0] == ("hello", 0)
    
    def test_search_multiple_matches(self):
        """Test searching with multiple matches"""
        ac = ACAutomaton()
        ac.build(["hello", "world"])
        
        matches = ac.search("hello world hello")
        assert len(matches) == 3
        assert ("hello", 0) in matches
        assert ("world", 6) in matches
        assert ("hello", 12) in matches
    
    def test_search_overlapping_patterns(self):
        """Test searching with overlapping patterns"""
        ac = ACAutomaton()
        ac.build(["abc", "bc", "c"])
        
        matches = ac.search("abc")
        assert len(matches) >= 1
        assert ("abc", 0) in matches or ("bc", 1) in matches or ("c", 2) in matches
    
    def test_search_chinese(self):
        """Test searching Chinese text"""
        ac = ACAutomaton()
        ac.build(["敏感词", "测试"])
        
        matches = ac.search("这是一个敏感词测试")
        assert len(matches) == 2
        assert ("敏感词", 4) in matches
        assert ("测试", 7) in matches
    
    def test_search_without_build(self):
        """Test searching without building automaton"""
        ac = ACAutomaton()
        
        with pytest.raises(RuntimeError) as exc_info:
            ac.search("test")
        
        assert "not built" in str(exc_info.value)
    
    def test_build_trie_structure(self):
        """Test trie structure after building"""
        ac = ACAutomaton()
        ac.build(["abc", "abd"])
        
        # Both patterns share 'ab' prefix
        assert 'a' in ac.root.children
        assert 'b' in ac.root.children['a'].children
        
        # Then they diverge
        node_b = ac.root.children['a'].children['b']
        assert 'c' in node_b.children
        assert 'd' in node_b.children


class TestSensitiveWordFilter:
    """Test Sensitive Word Filter"""
    
    def test_init(self):
        """Test filter initialization"""
        filter = SensitiveWordFilter()
        
        assert filter.ac is not None
        assert filter.ac.is_built is False
    
    def test_init_with_patterns(self):
        """Test initialization with patterns"""
        filter = SensitiveWordFilter(["test", "敏感词"])
        
        assert filter.ac.is_built is True
        assert len(filter.ac.patterns) == 2
    
    def test_filter_empty_text(self):
        """Test filtering empty text"""
        filter = SensitiveWordFilter()
        filter.build(["test"])
        
        is_safe, filtered, matches = filter.filter("")
        assert is_safe is True
        assert filtered == ""
        assert len(matches) == 0
    
    def test_filter_no_sensitive_words(self):
        """Test filtering text without sensitive words"""
        filter = SensitiveWordFilter()
        filter.build(["bad", "evil"])
        
        is_safe, filtered, matches = filter.filter("good text")
        assert is_safe is True
        assert filtered == "good text"
        assert len(matches) == 0
    
    def test_filter_single_sensitive_word(self):
        """Test filtering single sensitive word"""
        filter = SensitiveWordFilter()
        filter.build(["bad"])
        
        is_safe, filtered, matches = filter.filter("This is bad text")
        assert is_safe is False
        assert filtered == "This is *** text"
        assert len(matches) == 1
        assert matches[0] == ("bad", 8)
    
    def test_filter_multiple_sensitive_words(self):
        """Test filtering multiple sensitive words"""
        filter = SensitiveWordFilter()
        filter.build(["bad", "evil"])
        
        is_safe, filtered, matches = filter.filter("bad and evil")
        assert is_safe is False
        assert "*** and ****" == filtered
        assert len(matches) == 2
    
    def test_filter_chinese(self):
        """Test filtering Chinese text"""
        filter = SensitiveWordFilter()
        filter.build(["敏感词"])
        
        is_safe, filtered, matches = filter.filter("这是敏感词测试")
        assert is_safe is False
        assert filtered == "这是***测试"
        assert len(matches) == 1
        assert matches[0] == ("敏感词", 2)
    
    def test_filter_overlapping(self):
        """Test filtering overlapping patterns"""
        filter = SensitiveWordFilter()
        filter.build(["abc", "bc"])
        
        is_safe, filtered, matches = filter.filter("abc")
        # Should match at least one pattern
        assert len(matches) >= 1
    
    def test_filter_case_sensitive(self):
        """Test case sensitivity"""
        filter = SensitiveWordFilter()
        filter.build(["BAD"])
        
        is_safe, filtered, matches = filter.filter("bad")
        # Should be case sensitive by default
        assert len(matches) == 0 or is_safe is True
    
    def test_build_empty_list(self):
        """Test building with empty word list"""
        filter = SensitiveWordFilter()
        filter.build([])
        
        is_safe, filtered, matches = filter.filter("any text")
        assert is_safe is True
        assert filtered == "any text"
    
    def test_filter_custom_replacement(self):
        """Test custom replacement character"""
        filter = SensitiveWordFilter(["bad"])
        
        is_safe, filtered, matches = filter.filter("bad text", replacement='#')
        assert is_safe is False
        assert filtered == "### text"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
