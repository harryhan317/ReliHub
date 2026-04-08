"""
Tests for Sensitive Word Management Service.

Uses PostgreSQL test database via conftest.py fixtures.
"""

import pytest
from sqlalchemy import select

from app.services.sensitive_word_service import SensitiveWordService
from app.models.sensitive_word import (
    SensitiveWord,
    SensitiveWordLog,
    SensitiveWordCategory,
    SensitiveWordLevel
)


class TestSensitiveWordService:
    """Test Sensitive Word Service"""
    
    def test_init(self, db_session):
        """Test service initialization"""
        service = SensitiveWordService(db_session)
        
        assert service.db == db_session
        assert service.filter is not None
        assert service._last_load_time is None
    
    def test_load_empty_database(self, db_session):
        """Test loading sensitive words from empty database"""
        service = SensitiveWordService(db_session)
        
        count = service.load_sensitive_words()
        
        assert count == 0
        assert service._last_load_time is not None
    
    def test_load_sensitive_words(self, db_session):
        """Test loading sensitive words"""
        word1 = SensitiveWord(
            word="敏感词",
            category=SensitiveWordCategory.POLITICAL,
            level=SensitiveWordLevel.HIGH,
            enabled=True
        )
        word2 = SensitiveWord(
            word="测试",
            category=SensitiveWordCategory.OTHER,
            level=SensitiveWordLevel.LOW,
            enabled=True
        )
        
        db_session.add(word1)
        db_session.add(word2)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        count = service.load_sensitive_words()
        
        assert count == 2
    
    def test_load_only_enabled_words(self, db_session):
        """Test loading only enabled words"""
        enabled_word = SensitiveWord(
            word="enabled",
            enabled=True
        )
        disabled_word = SensitiveWord(
            word="disabled",
            enabled=False
        )
        
        db_session.add(enabled_word)
        db_session.add(disabled_word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        count = service.load_sensitive_words()
        
        assert count == 1
    
    def test_check_text_clean(self, db_session):
        """Test checking clean text"""
        word = SensitiveWord(word="bad", enabled=True)
        db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        is_safe, filtered, matches = service.check_text("This is good text")
        
        assert is_safe is True
        assert filtered == "This is good text"
        assert len(matches) == 0
    
    def test_check_text_with_sensitive_word(self, db_session):
        """Test checking text with sensitive word"""
        word = SensitiveWord(word="bad", enabled=True)
        db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        is_safe, filtered, matches = service.check_text("This is bad text")
        
        assert is_safe is False
        assert "***" in filtered
        assert len(matches) == 1
    
    def test_check_text_chinese(self, db_session):
        """Test checking Chinese text"""
        word = SensitiveWord(word="敏感词", enabled=True)
        db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        is_safe, filtered, matches = service.check_text("这是敏感词测试")
        
        assert is_safe is False
        assert "***" in filtered
        assert len(matches) == 1
    
    def test_check_text_auto_load(self, db_session):
        """Test auto-loading sensitive words"""
        word = SensitiveWord(word="test", enabled=True)
        db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        is_safe, filtered, matches = service.check_text("test text")
        
        assert len(matches) == 1
    
    def test_add_sensitive_word(self, db_session):
        """Test adding sensitive word"""
        service = SensitiveWordService(db_session)
        
        word = service.add_sensitive_word(
            word="newword",
            category=SensitiveWordCategory.VIOLENCE,
            level=SensitiveWordLevel.MEDIUM,
            reason="测试原因"
        )
        
        assert word is not None
        assert word.word == "newword"
        assert word.category == SensitiveWordCategory.VIOLENCE
        assert word.level == SensitiveWordLevel.MEDIUM
        assert word.reason == "测试原因"
        assert word.enabled is True
    
    def test_add_duplicate_word(self, db_session):
        """Test adding duplicate sensitive word"""
        word1 = SensitiveWord(word="duplicate", enabled=True)
        db_session.add(word1)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        result = service.add_sensitive_word(
            word="duplicate",
            category=SensitiveWordCategory.OTHER
        )
        
        assert result is None
    
    def test_delete_sensitive_word(self, db_session):
        """Test deleting sensitive word"""
        word = SensitiveWord(word="todelete", enabled=True)
        db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        success = service.remove_sensitive_word(word.id)
        
        assert success is True
        
        result = db_session.execute(
            select(SensitiveWord).where(SensitiveWord.id == word.id)
        )
        deleted_word = result.scalar_one_or_none()
        assert deleted_word is None
    
    def test_update_sensitive_word(self, db_session):
        """Test updating sensitive word"""
        word = SensitiveWord(
            word="toupdate",
            enabled=True,
            level=SensitiveWordLevel.LOW
        )
        db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        updated = service.update_sensitive_word(
            word_id=word.id,
            level=SensitiveWordLevel.HIGH,
            reason="Updated reason"
        )
        
        assert updated is not None
        assert updated.level == SensitiveWordLevel.HIGH
        assert updated.reason == "Updated reason"
    
    def test_enable_disable_word(self, db_session):
        """Test enabling/disabling sensitive word"""
        word = SensitiveWord(word="toggle", enabled=True)
        db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        updated = service.update_sensitive_word(word.id, enabled=False)
        
        assert updated is not None
        assert updated.enabled is False
        
        updated = service.update_sensitive_word(word.id, enabled=True)
        assert updated.enabled is True
    
    def test_list_sensitive_words(self, db_session):
        """Test listing sensitive words"""
        for i in range(5):
            word = SensitiveWord(word=f"word{i}", enabled=True)
            db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        words, total = service.list_sensitive_words(page=1, page_size=10)
        
        assert len(words) == 5
        assert total == 5
    
    def test_list_with_pagination(self, db_session):
        """Test listing with pagination"""
        for i in range(20):
            word = SensitiveWord(word=f"word{i}", enabled=True)
            db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        words, total = service.list_sensitive_words(page=1, page_size=10)
        
        assert len(words) == 10
        assert total == 20
        
        words, total = service.list_sensitive_words(page=2, page_size=10)
        assert len(words) == 10
    
    def test_list_by_category(self, db_session):
        """Test listing by category"""
        word1 = SensitiveWord(word="political", category=SensitiveWordCategory.POLITICAL)
        word2 = SensitiveWord(word="violence", category=SensitiveWordCategory.VIOLENCE)
        word3 = SensitiveWord(word="other1", category=SensitiveWordCategory.POLITICAL)
        
        db_session.add_all([word1, word2, word3])
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        words, total = service.list_sensitive_words(
            page=1,
            page_size=10,
            category=SensitiveWordCategory.POLITICAL
        )
        
        assert len(words) == 2
        assert total == 2
    
    def test_increment_hit_count(self, db_session):
        """Test incrementing hit count"""
        word = SensitiveWord(word="hitme", enabled=True, hit_count=0)
        db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        service._increment_hit_count("hitme")
        
        result = db_session.execute(
            select(SensitiveWord).where(SensitiveWord.word == "hitme")
        )
        updated = result.scalar_one()
        assert updated.hit_count == 1
    
    def test_log_hit(self, db_session):
        """Test logging sensitive word hit"""
        word = SensitiveWord(word="logme", enabled=True)
        db_session.add(word)
        db_session.commit()
        
        service = SensitiveWordService(db_session)
        service._log_hit(
            user_id="user123",
            session_id="session456",
            original_text="logme test",
            matched_words=[("logme", 0)],
            action="replaced"
        )
        
        result = db_session.execute(
            select(SensitiveWordLog).where(SensitiveWordLog.user_id == "user123")
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].action == "replaced"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
