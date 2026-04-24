"""
Search History Model - Tracks user search history.
"""
from datetime import datetime
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin


class SearchHistory(Base, TimestampMixin):
    """Search history table - records user search queries"""
    
    __tablename__ = "search_history"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    search_type: Mapped[str] = mapped_column(String(20), nullable=True)  # RESOURCE, COMMUNITY, AI, USER, ALL
    result_count: Mapped[int] = mapped_column(default=0)  # Number of results returned
    
    # Relationships
    user = relationship("User", back_populates="search_histories")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_search_history_user_created", "user_id", "created_at"),
        Index("idx_search_history_keyword", "keyword"),
    )
    
    def __repr__(self) -> str:
        return f"<SearchHistory(id={self.id}, user_id={self.user_id}, keyword={self.keyword})>"
