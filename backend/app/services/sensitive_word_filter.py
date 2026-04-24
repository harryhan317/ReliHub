"""
Sensitive Word Filter Service - Filter sensitive words from search queries.

Features:
- Real-time sensitive word detection
- Word replacement/masking
- Search query validation
- Hit logging and statistics
- Trie-based efficient matching
"""
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.sensitive_word import SensitiveWord, SensitiveWordCategory, SensitiveWordLog

logger = logging.getLogger(__name__)


class SensitiveWordFilter:
    """Sensitive word filter using Trie algorithm"""
    
    def __init__(self):
        # Trie structure for efficient matching
        self.trie: Dict = {}
        self.word_set: Set[str] = set()
        self.enabled_words: int = 0
        
        # Cache statistics
        self.hit_count: int = 0
        self.last_update: Optional[datetime] = None
    
    def load_sensitive_words(self, db: SessionLocal) -> int:
        """
        Load sensitive words from database into Trie.
        
        Should be called on application startup and periodically.
        
        Args:
            db: Database session
            
        Returns:
            Number of loaded words
        """
        try:
            # Clear existing trie
            self.trie = {}
            self.word_set = set()
            
            # Load all enabled sensitive words
            stmt = select(SensitiveWord).where(SensitiveWord.enabled == True)
            results = db.execute(stmt).scalars().all()
            
            for word_obj in results:
                word = word_obj.word.lower()
                self.word_set.add(word)
                self._add_to_trie(word)
            
            self.enabled_words = len(self.word_set)
            self.last_update = datetime.utcnow()
            
            logger.info(f"Loaded {self.enabled_words} sensitive words into filter")
            return self.enabled_words
        
        except Exception as e:
            logger.error(f"Error loading sensitive words: {e}")
            return 0
    
    def _add_to_prue(self, word: str) -> None:
        """
        Add a word to the Trie structure.
        
        Args:
            word: Word to add
        """
        node = self.trie
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        # Mark end of word
        node['is_end'] = True
    
    def contains_sensitive_word(self, text: str) -> bool:
        """
        Check if text contains any sensitive word.
        
        Args:
            text: Text to check
            
        Returns:
            True if contains sensitive word, False otherwise
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for exact matches first (faster)
        for word in self.word_set:
            if word in text_lower:
                return True
        
        # Check using Trie for more complex patterns
        for i in range(len(text_lower)):
            node = self.trie
            for j in range(i, len(text_lower)):
                char = text_lower[j]
                if char not in node:
                    break
                node = node[char]
                if node.get('is_end'):
                    return True
        
        return False
    
    def find_sensitive_words(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Find all sensitive words in text.
        
        Args:
            text: Text to search
            
        Returns:
            List of (word, start_position, end_position) tuples
        """
        if not text:
            return []
        
        found_words = []
        text_lower = text.lower()
        
        # Find all matches using Trie
        for i in range(len(text_lower)):
            node = self.trie
            for j in range(i, len(text_lower)):
                char = text_lower[j]
                if char not in node:
                    break
                node = node[char]
                if node.get('is_end'):
                    word = text_lower[i:j+1]
                    found_words.append((word, i, j+1))
        
        return found_words
    
    def filter_text(
        self,
        text: str,
        replacement: str = '*',
        log_hits: bool = True
    ) -> Tuple[str, bool]:
        """
        Filter sensitive words from text.
        
        Args:
            text: Text to filter
            replacement: Character to replace sensitive words
            log_hits: Whether to log hits
            
        Returns:
            Tuple of (filtered_text, has_sensitive_words)
        """
        if not text:
            return text, False
        
        found_words = self.find_sensitive_words(text)
        
        if not found_words:
            return text, False
        
        # Replace sensitive words
        filtered_text = text
        for word, start, end in found_words:
            replacement_str = replacement * (end - start)
            filtered_text = (
                filtered_text[:start] + replacement_str + filtered_text[end:]
            )
        
        # Log hits
        if log_hits:
            self._log_hits(found_words)
        
        return filtered_text, True
    
    def validate_search_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a search query for sensitive words.
        
        Args:
            query: Search query to validate
            
        Returns:
            Tuple of (is_valid, rejection_reason)
        """
        if not query:
            return True, None
        
        found_words = self.find_sensitive_words(query)
        
        if not found_words:
            return True, None
        
        # Get the first sensitive word for the rejection reason
        word, _, _ = found_words[0]
        
        # Try to get the word's category from database
        try:
            db = SessionLocal()
            stmt = select(SensitiveWord).where(
                SensitiveWord.word.ilike(word)
            )
            word_obj = db.execute(stmt).scalar_one_or_none()
            
            if word_obj:
                reason = f"搜索词包含敏感词汇（类别：{word_obj.category.value}）"
            else:
                reason = "搜索词包含敏感词汇"
            
            db.close()
        except Exception as e:
            logger.error(f"Error getting sensitive word details: {e}")
            reason = "搜索词包含敏感词汇"
        
        return False, reason
    
    def _log_hits(self, found_words: List[Tuple[str, int, int]]) -> None:
        """
        Log sensitive word hits to database.
        
        Args:
            found_words: List of (word, start, end) tuples
        """
        try:
            db = SessionLocal()
            
            for word, _, _ in found_words:
                # Update hit count
                stmt = select(SensitiveWord).where(
                    SensitiveWord.word.ilike(word)
                )
                word_obj = db.execute(stmt).scalar_one_or_none()
                
                if word_obj:
                    word_obj.hit_count += 1
                    
                    # Create log entry
                    log = SensitiveWordLog(
                        word_id=word_obj.id,
                        matched_text=word,
                        context=f"Search query: {word}",
                        category=word_obj.category
                    )
                    db.add(log)
            
            db.commit()
            self.hit_count += len(found_words)
            
        except Exception as e:
            logger.error(f"Error logging sensitive word hits: {e}")
            try:
                db.rollback()
            except:
                pass
        finally:
            try:
                db.close()
            except:
                pass
    
    def get_stats(self) -> Dict:
        """
        Get filter statistics.
        
        Returns:
            Dictionary with filter statistics
        """
        return {
            'total_words': len(self.word_set),
            'enabled_words': self.enabled_words,
            'hit_count': self.hit_count,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }


# Global sensitive word filter instance
sensitive_word_filter = SensitiveWordFilter()


def init_sensitive_word_filter() -> int:
    """
    Initialize sensitive word filter on application startup.
    
    Returns:
        Number of loaded words
    """
    try:
        db = SessionLocal()
        count = sensitive_word_filter.load_sensitive_words(db)
        db.close()
        return count
    except Exception as e:
        logger.error(f"Error initializing sensitive word filter: {e}")
        return 0
