"""
Search Service - Global unified search across modules.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import uuid
import hashlib
import logging

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ErrorCode
from app.models.resources import Resource
from app.models.topic import Topic
from app.models.ai_session import AISession
from app.models.users import User
from app.models.search_history import SearchHistory
from app.schemas.search import SearchType, SortBy
from app.services.search_cache_service import search_cache
from app.services.tfidf_optimizer import tfidf_optimizer
from app.services.sensitive_word_filter import sensitive_word_filter
from app.services.search_optimizer import get_search_optimizer

logger = logging.getLogger(__name__)


class SearchService:
    """Service for global unified search"""

    def __init__(self, db: Session):
        self.db = db
        self.cache = search_cache

    def get_search_suggestions(
        self,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """
        Get search suggestions based on popular search terms.
        
        Args:
            query: Partial search query
            limit: Maximum number of suggestions to return
            
        Returns:
            List of suggested search terms
        """
        # Try to get from cache first
        cached = self.cache.get_suggestions(query, limit)
        if cached is not None:
            return cached
        
        suggestions = []
        
        if not query or len(query) < 2:
            return suggestions
        
        # Search for matching terms in resources
        resource_stmt = select(Resource.title).where(
            Resource.title.ilike(f"%{query}%")
        ).limit(limit)
        resource_results = self.db.execute(resource_stmt).scalars().all()
        suggestions.extend(resource_results)
        
        # Search for matching terms in topics
        if len(suggestions) < limit:
            remaining = limit - len(suggestions)
            topic_stmt = select(Topic.title).where(
                Topic.title.ilike(f"%{query}%")
            ).limit(remaining)
            topic_results = self.db.execute(topic_stmt).scalars().all()
            suggestions.extend(topic_results)
        
        # Remove duplicates and return
        result = list(dict.fromkeys(suggestions))[:limit]
        
        # Cache the result
        self.cache.set_suggestions(query, result, limit)
        
        return result

    def global_search(
        self,
        query: str,
        search_type: SearchType = SearchType.ALL,
        sort_by: SortBy = SortBy.RELEVANCE,
        page: int = 1,
        size: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Perform global search across all modules.

        Args:
            query: Search keyword
            search_type: Type of search (RESOURCE, COMMUNITY, AI, USER, ALL)
            sort_by: Sort method (relevance, heat, latest)
            page: Page number
            size: Page size
            start_date: Start date filter (for AI type)
            end_date: End date filter (for AI type)
            user_id: Current user ID (for permission check)

        Returns:
            Tuple of (results list, total count)
            
        Raises:
            BusinessException: If query contains sensitive words
        """
        # Check for sensitive words
        is_valid, rejection_reason = sensitive_word_filter.validate_search_query(query)
        if not is_valid:
            logger.warning(f"Search query blocked due to sensitive words: {query}")
            raise BusinessException(
                ErrorCode.INVALID_INPUT,
                rejection_reason or "搜索词包含敏感词汇"
            )
        
        results = []
        total = 0

        # Search resources
        if search_type in [SearchType.RESOURCE, SearchType.ALL]:
            resource_results, resource_total = self._search_resources(
                query, sort_by, page, size
            )
            results.extend([{"type": "RESOURCE", **r} for r in resource_results])
            total += resource_total

        # Search community topics
        if search_type in [SearchType.COMMUNITY, SearchType.ALL]:
            topic_results, topic_total = self._search_topics(
                query, sort_by, page, size
            )
            results.extend([{"type": "COMMUNITY", **t} for t in topic_results])
            total += topic_total

        # Search AI sessions (only user's own sessions)
        if search_type in [SearchType.AI, SearchType.ALL] and user_id:
            ai_results, ai_total = self._search_ai_sessions(
                query, sort_by, page, size, user_id, start_date, end_date
            )
            results.extend([{"type": "AI", **a} for a in ai_results])
            total += ai_total

        # Search users
        if search_type in [SearchType.USER, SearchType.ALL]:
            user_results, user_total = self._search_users(
                query, sort_by, page, size
            )
            results.extend([{"type": "USER", **u} for u in user_results])
            total += user_total

        # Sort results
        if sort_by == SortBy.HEAT:
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
        elif sort_by == SortBy.LATEST:
            results.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        else:  # RELEVANCE
            # Use TF-IDF/BM25 for relevance scoring
            ranked_results = tfidf_optimizer.rank_results(
                results,
                query,
                text_field='description',
                use_bm25=True  # BM25 is better for short texts
            )
            results = ranked_results
            
            # Log TF-IDF scoring for debugging
            if results:
                logger.debug(
                    f"TF-IDF ranked {len(results)} results, "
                    f"top score: {results[0].get('relevance_score', 0):.4f}"
                )

        return results, total

    def _search_resources(
        self,
        query: str,
        sort_by: SortBy,
        page: int,
        size: int
    ) -> Tuple[List[Dict], int]:
        """Search resources with optimized queries"""
        # Optimize query first
        optimizer = get_search_optimizer(self.db)
        optimized_query, _ = optimizer.optimize_search_query(query, use_fulltext=True)
        logger.info(f"Optimized search query: '{query}' -> '{optimized_query}'")
        
        # Build search condition with optimized query
        # Use trigram similarity for better performance with indexes
        search_condition = or_(
            Resource.title.ilike(f"%{optimized_query}%"),
            Resource.description.ilike(f"%{optimized_query}%"),
            Resource.tags.ilike(f"%{optimized_query}%")
        )

        # Build query
        stmt = select(Resource).where(search_condition)

        # Add sorting
        if sort_by == SortBy.LATEST:
            stmt = stmt.order_by(Resource.created_at.desc())
        elif sort_by == SortBy.HEAT:
            stmt = stmt.order_by(Resource.heat_score.desc())
        else:  # RELEVANCE - will be sorted globally with TF-IDF/BM25
            stmt = stmt.order_by(Resource.heat_score.desc())

        # Get total count
        count_stmt = select(func.count()).select_from(Resource).where(search_condition)
        total = self.db.execute(count_stmt).scalar() or 0

        # Apply pagination
        stmt = stmt.offset((page - 1) * size).limit(size)
        results = self.db.execute(stmt).scalars().all()

        # Calculate relevance scores with enhanced algorithm
        scored_results = []
        for r in results:
            metadata = {
                "heat_score": r.heat_score or 0,
                "created_at": r.created_at
            }
            
            score = optimizer.calculate_enhanced_relevance_score(
                text=r.description or "",
                query=optimized_query,
                title=r.title,
                metadata=metadata
            )
            
            scored_results.append({
                "id": r.id,
                "title": r.title,
                "description": r.description or "",
                "file_type": None,
                "download_count": r.download_count or 0,
                "created_at": r.created_at,
                "score": score
            })

        return scored_results, total

    def _search_topics(
        self,
        query: str,
        sort_by: SortBy,
        page: int,
        size: int
    ) -> Tuple[List[Dict], int]:
        """Search community topics with optimized queries"""
        # Optimize query first
        optimizer = get_search_optimizer(self.db)
        optimized_query, _ = optimizer.optimize_search_query(query, use_fulltext=True)
        
        # Build search condition
        search_condition = or_(
            Topic.title.ilike(f"%{optimized_query}%"),
            Topic.content.ilike(f"%{optimized_query}%")
        )

        stmt = select(Topic).where(search_condition)

        if sort_by == SortBy.LATEST:
            stmt = stmt.order_by(Topic.created_at.desc())
        elif sort_by == SortBy.HEAT:
            stmt = stmt.order_by(Topic.heat_score.desc())
        else:  # RELEVANCE
            stmt = stmt.order_by(Topic.heat_score.desc())

        count_stmt = select(func.count()).select_from(Topic).where(search_condition)
        total = self.db.execute(count_stmt).scalar() or 0

        stmt = stmt.offset((page - 1) * size).limit(size)
        results = self.db.execute(stmt).scalars().all()

        # Calculate relevance scores
        scored_results = []
        for t in results:
            metadata = {
                "heat_score": t.heat_score or 0,
                "created_at": t.created_at,
                "reply_count": t.post_count or 0
            }
            
            score = optimizer.calculate_enhanced_relevance_score(
                text=t.content,
                query=optimized_query,
                title=t.title,
                metadata=metadata
            )
            
            scored_results.append({
                "id": t.id,
                "title": t.title,
                "description": (t.content[:200] + "...") if len(t.content) > 200 else t.content,
                "reply_count": t.post_count or 0,
                "view_count": t.view_count or 0,
                "created_at": t.created_at,
                "score": score
            })

        return scored_results, total

    def _search_ai_sessions(
        self,
        query: str,
        sort_by: SortBy,
        page: int,
        size: int,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """Search user's AI sessions"""
        conditions = [AISession.user_id == user_id]

        # Add date filters if provided
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                conditions.append(AISession.created_at >= start)
            except ValueError:
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                conditions.append(AISession.created_at <= end)
            except ValueError:
                pass

        # Search in title
        conditions.append(AISession.title.ilike(f"%{query}%"))

        stmt = select(AISession).where(and_(*conditions))

        if sort_by == SortBy.LATEST:
            stmt = stmt.order_by(AISession.created_at.desc())

        count_stmt = select(func.count()).select_from(AISession).where(and_(*conditions))
        total = self.db.execute(count_stmt).scalar() or 0

        stmt = stmt.offset((page - 1) * size).limit(size)
        results = self.db.execute(stmt).scalars().all()

        return [
            {
                "id": s.id,
                "title": s.title,
                "description": "AI 对话会话",
                "message_count": s.message_count or 0,
                "created_at": s.created_at,
                "score": 0
            }
            for s in results
        ], total

    def _search_users(
        self,
        query: str,
        sort_by: SortBy,
        page: int,
        size: int
    ) -> Tuple[List[Dict], int]:
        """Search users by nickname"""
        search_condition = User.nickname.ilike(f"%{query}%")

        stmt = select(User).where(search_condition)

        if sort_by == SortBy.LATEST:
            stmt = stmt.order_by(User.created_at.desc())
        elif sort_by == SortBy.HEAT:
            # Sort by reputation points as a proxy for "heat"
            stmt = stmt.order_by(User.reputation_points.desc())

        count_stmt = select(func.count()).select_from(User).where(search_condition)
        total = self.db.execute(count_stmt).scalar() or 0

        stmt = stmt.offset((page - 1) * size).limit(size)
        results = self.db.execute(stmt).scalars().all()

        return [
            {
                "id": u.id,
                "title": u.nickname,
                "description": f"{u.rank or '新兵'} 用户",
                "avatar_url": u.avatar_url,
                "rank": u.rank or "新兵",
                "created_at": u.created_at,
                "score": 0
            }
            for u in results
        ], total

    def record_search_history(
        self,
        user_id: str,
        keyword: str,
        search_type: str = "ALL",
        result_count: int = 0
    ) -> SearchHistory:
        """
        Record a search query in user's search history.
        
        Args:
            user_id: User ID
            keyword: Search keyword
            search_type: Type of search performed
            result_count: Number of results returned
            
        Returns:
            Created SearchHistory object
        """
        history = SearchHistory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            keyword=keyword,
            search_type=search_type,
            result_count=result_count
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        
        # Invalidate trending cache since search history changed
        self.cache.invalidate_trending_cache()
        
        # Invalidate suggestions cache for this keyword
        self.cache.invalidate_suggestions_cache(keyword)
        
        return history

    def get_search_history(
        self,
        user_id: str,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[SearchHistory], int]:
        """
        Get user's search history.
        
        Args:
            user_id: User ID
            page: Page number
            size: Page size
            
        Returns:
            Tuple of (history list, total count)
        """
        stmt = select(SearchHistory).where(SearchHistory.user_id == user_id)
        stmt = stmt.order_by(SearchHistory.created_at.desc())
        
        count_stmt = select(func.count()).select_from(SearchHistory).where(
            SearchHistory.user_id == user_id
        )
        total = self.db.execute(count_stmt).scalar() or 0
        
        stmt = stmt.offset((page - 1) * size).limit(size)
        results = self.db.execute(stmt).scalars().all()
        
        return results, total

    def delete_search_history_item(
        self,
        user_id: str,
        history_id: str
    ) -> bool:
        """
        Delete a single search history item.
        
        Args:
            user_id: User ID (for ownership verification)
            history_id: Search history ID to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        history = self.db.query(SearchHistory).filter(
            SearchHistory.id == history_id,
            SearchHistory.user_id == user_id
        ).first()
        
        if not history:
            return False
        
        self.db.delete(history)
        self.db.commit()
        return True

    def clear_search_history(
        self,
        user_id: str
    ) -> int:
        """
        Clear all search history for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of deleted records
        """
        count = self.db.query(SearchHistory).filter(
            SearchHistory.user_id == user_id
        ).delete()
        self.db.commit()
        return count

    def get_trending_searches(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get trending search terms based on search frequency.
        
        Args:
            limit: Maximum number of trending terms to return
            
        Returns:
            List of trending search terms with counts
        """
        # Try to get from cache first
        cached = self.cache.get_trending(limit)
        if cached is not None:
            return cached
        
        # Query search history to find most frequent keywords
        stmt = select(
            SearchHistory.keyword,
            func.count(SearchHistory.id).label('search_count')
        ).group_by(SearchHistory.keyword)
        
        # Order by search count descending
        stmt = stmt.order_by(func.count(SearchHistory.id).desc())
        
        # Limit results
        stmt = stmt.limit(limit)
        
        results = self.db.execute(stmt).all()
        
        trending = [
            {
                "keyword": row.keyword,
                "count": row.search_count,
                "rank": idx + 1
            }
            for idx, row in enumerate(results)
        ]
        
        # Cache the result
        self.cache.set_trending(trending, limit)
        
        return trending
