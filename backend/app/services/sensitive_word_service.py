"""
Sensitive Word Management Service

Manages sensitive words and provides filtering functionality.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sensitive_word import (
    SensitiveWord,
    SensitiveWordCategory,
    SensitiveWordLevel,
    SensitiveWordLog,
)
from app.services.ac_automaton import SensitiveWordFilter

logger = logging.getLogger(__name__)


class SensitiveWordService:
    """
    Service for sensitive word management
    
    Features:
    - CRUD operations for sensitive words
    - AC automaton for efficient filtering
    - Hit logging and statistics
    - Category and level management
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.filter = SensitiveWordFilter()
        self._last_load_time: Optional[datetime] = None
    
    def load_sensitive_words(self) -> int:
        """
        Load sensitive words from database to AC automaton
        
        Returns:
            Number of words loaded
        """
        query = select(SensitiveWord).where(SensitiveWord.enabled == True)
        result = self.db.execute(query)
        words = list(result.scalars().all())
        
        word_list = [word.word for word in words]
        
        self.filter.build(word_list)
        self._last_load_time = datetime.now()
        
        logger.info(f"Loaded {len(word_list)} sensitive words to AC automaton")
        return len(word_list)
    
    def list_sensitive_words(
        self,
        category: Optional[SensitiveWordCategory] = None,
        level: Optional[SensitiveWordLevel] = None,
        enabled: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[SensitiveWord], int]:
        """
        List sensitive words with filters (alias for get_sensitive_words)
        
        Args:
            category: Filter by category
            level: Filter by level
            enabled: Filter by enabled status
            page: Page number
            page_size: Page size
            
        Returns:
            List of SensitiveWord and total count
        """
        return self.get_sensitive_words(
            category=category,
            level=level,
            enabled=enabled,
            page=page,
            page_size=page_size
        )
    
    def get_sensitive_words(
        self,
        category: Optional[SensitiveWordCategory] = None,
        level: Optional[SensitiveWordLevel] = None,
        enabled: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[SensitiveWord], int]:
        """
        Get sensitive words with filters
        
        Args:
            category: Filter by category
            level: Filter by level
            enabled: Filter by enabled status
            page: Page number
            page_size: Page size
            
        Returns:
            List of SensitiveWord and total count
        """
        query = select(SensitiveWord)
        
        if category:
            query = query.where(SensitiveWord.category == category)
        if level:
            query = query.where(SensitiveWord.level == level)
        if enabled is not None:
            query = query.where(SensitiveWord.enabled == enabled)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar()
        
        query = query.order_by(SensitiveWord.hit_count.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = self.db.execute(query)
        words = list(result.scalars().all())
        
        return words, total
    
    def add_sensitive_word(
        self,
        word: str,
        category: SensitiveWordCategory = SensitiveWordCategory.OTHER,
        level: SensitiveWordLevel = SensitiveWordLevel.LOW,
        reason: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> SensitiveWord:
        """
        Add a sensitive word
        
        Args:
            word: Sensitive word
            category: Word category
            level: Word level
            reason: Reason for marking as sensitive
            tags: Tags for the word
            
        Returns:
            Created SensitiveWord instance
        """
        existing = self.get_word_by_text(word)
        if existing:
            logger.warning(f"Sensitive word '{word}' already exists")
            return None
        
        sensitive_word = SensitiveWord(
            word=word,
            category=category,
            level=level,
            reason=reason,
            tags=",".join(tags) if tags else None,
            enabled=True
        )
        
        self.db.add(sensitive_word)
        self.db.commit()
        self.db.refresh(sensitive_word)
        
        self.load_sensitive_words()
        
        logger.info(f"Added sensitive word: {word}")
        return sensitive_word
    
    def remove_sensitive_word(self, word_id: int) -> bool:
        """
        Remove a sensitive word
        
        Args:
            word_id: Word ID
            
        Returns:
            True if removed, False if not found
        """
        query = select(SensitiveWord).where(SensitiveWord.id == word_id)
        result = self.db.execute(query)
        word = result.scalar_one_or_none()
        
        if not word:
            return False
        
        self.db.delete(word)
        self.db.commit()
        
        self.load_sensitive_words()
        
        logger.info(f"Removed sensitive word: {word.word}")
        return True
    
    def update_sensitive_word(
        self,
        word_id: int,
        enabled: Optional[bool] = None,
        level: Optional[SensitiveWordLevel] = None,
        category: Optional[SensitiveWordCategory] = None,
        reason: Optional[str] = None
    ) -> Optional[SensitiveWord]:
        """
        Update sensitive word
        
        Args:
            word_id: Word ID
            enabled: New enabled status
            level: New level
            category: New category
            reason: New reason
            
        Returns:
            Updated SensitiveWord or None
        """
        query = select(SensitiveWord).where(SensitiveWord.id == word_id)
        result = self.db.execute(query)
        word = result.scalar_one_or_none()
        
        if not word:
            return None
        
        if enabled is not None:
            word.enabled = enabled
        if level:
            word.level = level
        if category:
            word.category = category
        if reason:
            word.reason = reason
        
        self.db.commit()
        self.db.refresh(word)
        
        self.load_sensitive_words()
        
        logger.info(f"Updated sensitive word: {word.word}")
        return word
    
    def get_word_by_text(self, word: str) -> Optional[SensitiveWord]:
        """
        Get sensitive word by text
        
        Args:
            word: Word text
            
        Returns:
            SensitiveWord or None
        """
        query = select(SensitiveWord).where(SensitiveWord.word == word)
        result = self.db.execute(query)
        return result.scalar_one_or_none()
    
    def check_text(
        self,
        text: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Tuple[bool, str, List[Tuple[str, int]]]:
        """
        Check text for sensitive words
        
        Args:
            text: Text to check
            user_id: User ID (for logging)
            session_id: Session ID (for logging)
            
        Returns:
            Tuple of (is_safe, filtered_text, matches)
        """
        if not self.filter.ac.is_built:
            self.load_sensitive_words()
        
        is_safe, filtered_text, matches = self.filter.filter(text)
        
        if matches:
            self._log_hit(
                user_id=user_id,
                session_id=session_id,
                original_text=text,
                matched_words=matches,
                action="replaced" if not is_safe else "logged"
            )
            
            for word, _ in matches:
                self._increment_hit_count(word)
        
        return is_safe, filtered_text, matches
    
    def should_block_text(
        self,
        matches: List[Tuple[str, int]]
    ) -> bool:
        """
        Check if text should be blocked based on matches
        
        Args:
            matches: List of (word, position) tuples
            
        Returns:
            True if should block, False otherwise
        """
        for word, _ in matches:
            sensitive_word = self.get_word_by_text(word)
            if sensitive_word and sensitive_word.level in [
                SensitiveWordLevel.MEDIUM,
                SensitiveWordLevel.HIGH
            ]:
                return True
        
        return False
    
    def _log_hit(
        self,
        user_id: Optional[str],
        session_id: Optional[str],
        original_text: str,
        matched_words: List[Tuple[str, int]],
        action: str
    ) -> None:
        """
        Log sensitive word hit
        
        Args:
            user_id: User ID
            session_id: Session ID
            original_text: Original text
            matched_words: Matched words
            action: Action taken
        """
        content_hash = hashlib.sha256(original_text.encode()).hexdigest()
        
        log = SensitiveWordLog(
            user_id=user_id,
            session_id=session_id,
            original_text=original_text[:5000],
            matched_words=json.dumps(matched_words),
            action=action,
            content_hash=content_hash
        )
        
        self.db.add(log)
        self.db.commit()
        
        logger.debug(f"Logged sensitive word hit: {len(matched_words)} matches")
    
    def _increment_hit_count(self, word: str) -> None:
        """
        Increment hit count for a word
        
        Args:
            word: Sensitive word
        """
        sensitive_word = self.get_word_by_text(word)
        if sensitive_word:
            sensitive_word.hit_count += 1
            self.db.commit()
    
    def get_hit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[SensitiveWordLog], int]:
        """
        Get sensitive word hit logs
        
        Args:
            user_id: Filter by user ID
            action: Filter by action
            page: Page number
            page_size: Page size
            
        Returns:
            List of logs and total count
        """
        query = select(SensitiveWordLog)
        
        if user_id:
            query = query.where(SensitiveWordLog.user_id == user_id)
        if action:
            query = query.where(SensitiveWordLog.action == action)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar()
        
        query = query.order_by(SensitiveWordLog.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = self.db.execute(query)
        logs = list(result.scalars().all())
        
        return logs, total
    
    def get_stats(self) -> Dict:
        """
        Get sensitive word statistics
        
        Returns:
            Dict with statistics
        """
        ac_stats = self.filter.get_stats()
        
        category_query = select(
            SensitiveWord.category,
            func.count()
        ).group_by(SensitiveWord.category)
        category_result = self.db.execute(category_query)
        category_counts = dict(category_result.all())
        
        level_query = select(
            SensitiveWord.level,
            func.count()
        ).group_by(SensitiveWord.level)
        level_result = self.db.execute(level_query)
        level_counts = dict(level_result.all())
        
        return {
            "ac_automaton": ac_stats,
            "categories": {
                cat.value: count for cat, count in category_counts.items()
            },
            "levels": {
                lvl.value: count for lvl, count in level_counts.items()
            },
            "last_load_time": self._last_load_time.isoformat() if self._last_load_time else None
        }
