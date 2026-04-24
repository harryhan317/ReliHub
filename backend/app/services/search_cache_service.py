"""
Search Cache Service - Redis caching for search operations.

Provides caching for:
1. Trending searches (热搜榜单)
2. Search suggestions (搜索建议)
3. Search result caching (optional)

Cache keys format:
- trending:search:{limit} - Trending searches with specific limit
- suggestions:{query}:{limit} - Search suggestions for query
"""
import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


class SearchCacheService:
    """Service for caching search-related data"""
    
    # Cache key prefixes
    TRENDING_KEY_PREFIX = "trending:search:"
    SUGGESTIONS_KEY_PREFIX = "suggestions:"
    SEARCH_RESULT_KEY_PREFIX = "search:result:"
    
    # Cache TTL (Time To Live)
    TRENDING_TTL = timedelta(minutes=5)  # 5 minutes for trending
    SUGGESTIONS_TTL = timedelta(minutes=10)  # 10 minutes for suggestions
    SEARCH_RESULT_TTL = timedelta(minutes=1)  # 1 minute for search results
    
    def __init__(self):
        self.redis = redis_client
    
    def get_trending(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached trending searches.
        
        Args:
            limit: Number of trending terms to return
            
        Returns:
            List of trending searches or None if not cached
        """
        if not self.redis.is_available:
            return None
        
        try:
            key = f"{self.TRENDING_KEY_PREFIX}{limit}"
            cached = self.redis.get(key)
            
            if cached:
                logger.info(f"Cache hit for trending searches (limit={limit})")
                return json.loads(cached)
            
            logger.info(f"Cache miss for trending searches (limit={limit})")
            return None
        except Exception as e:
            logger.error(f"Error getting cached trending searches: {e}")
            return None
    
    def set_trending(
        self,
        trending: List[Dict[str, Any]],
        limit: int = 10
    ) -> bool:
        """
        Cache trending searches.
        
        Args:
            trending: List of trending search terms
            limit: Number of trending terms
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis.is_available:
            return False
        
        try:
            key = f"{self.TRENDING_KEY_PREFIX}{limit}"
            value = json.dumps(trending)
            ttl_seconds = int(self.TRENDING_TTL.total_seconds())
            
            self.redis.setex(key, ttl_seconds, value)
            logger.info(f"Cached trending searches (limit={limit}, TTL={ttl_seconds}s)")
            return True
        except Exception as e:
            logger.error(f"Error caching trending searches: {e}")
            return False
    
    def get_suggestions(
        self,
        query: str,
        limit: int = 5
    ) -> Optional[List[str]]:
        """
        Get cached search suggestions.
        
        Args:
            query: Search query
            limit: Number of suggestions to return
            
        Returns:
            List of suggestions or None if not cached
        """
        if not self.redis.is_available:
            return None
        
        try:
            # Normalize query for cache key
            normalized_query = query.lower().strip()
            key = f"{self.SUGGESTIONS_KEY_PREFIX}{normalized_query}:{limit}"
            
            cached = self.redis.get(key)
            
            if cached:
                logger.info(f"Cache hit for suggestions (query={normalized_query}, limit={limit})")
                return json.loads(cached)
            
            logger.info(f"Cache miss for suggestions (query={normalized_query}, limit={limit})")
            return None
        except Exception as e:
            logger.error(f"Error getting cached suggestions: {e}")
            return None
    
    def set_suggestions(
        self,
        query: str,
        suggestions: List[str],
        limit: int = 5
    ) -> bool:
        """
        Cache search suggestions.
        
        Args:
            query: Search query
            suggestions: List of suggestions
            limit: Number of suggestions
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis.is_available:
            return False
        
        try:
            # Normalize query for cache key
            normalized_query = query.lower().strip()
            key = f"{self.SUGGESTIONS_KEY_PREFIX}{normalized_query}:{limit}"
            value = json.dumps(suggestions)
            ttl_seconds = int(self.SUGGESTIONS_TTL.total_seconds())
            
            self.redis.setex(key, ttl_seconds, value)
            logger.info(f"Cached suggestions (query={normalized_query}, limit={limit}, TTL={ttl_seconds}s)")
            return True
        except Exception as e:
            logger.error(f"Error caching suggestions: {e}")
            return False
    
    def get_search_result(
        self,
        cache_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached search result.
        
        Args:
            cache_key: Custom cache key for search result
            
        Returns:
            Cached search result or None if not cached
        """
        if not self.redis.is_available:
            return None
        
        try:
            key = f"{self.SEARCH_RESULT_KEY_PREFIX}{cache_key}"
            cached = self.redis.get(key)
            
            if cached:
                logger.info(f"Cache hit for search result (key={cache_key})")
                return json.loads(cached)
            
            logger.info(f"Cache miss for search result (key={cache_key})")
            return None
        except Exception as e:
            logger.error(f"Error getting cached search result: {e}")
            return None
    
    def set_search_result(
        self,
        cache_key: str,
        result: Dict[str, Any]
    ) -> bool:
        """
        Cache search result.
        
        Args:
            cache_key: Custom cache key for search result
            result: Search result data
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis.is_available:
            return False
        
        try:
            key = f"{self.SEARCH_RESULT_KEY_PREFIX}{cache_key}"
            value = json.dumps(result, default=str)  # Handle datetime objects
            ttl_seconds = int(self.SEARCH_RESULT_TTL.total_seconds())
            
            self.redis.setex(key, ttl_seconds, value)
            logger.info(f"Cached search result (key={cache_key}, TTL={ttl_seconds}s)")
            return True
        except Exception as e:
            logger.error(f"Error caching search result: {e}")
            return False
    
    def invalidate_trending_cache(self, limit: Optional[int] = None) -> bool:
        """
        Invalidate trending searches cache.
        
        Args:
            limit: Specific limit to invalidate, or None for all
            
        Returns:
            True if invalidated successfully
        """
        if not self.redis.is_available:
            return False
        
        try:
            if limit is not None:
                key = f"{self.TRENDING_KEY_PREFIX}{limit}"
                self.redis.delete(key)
                logger.info(f"Invalidated trending cache for limit={limit}")
            else:
                # Delete all trending cache keys
                pattern = f"{self.TRENDING_KEY_PREFIX}*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
                    logger.info(f"Invalidated all trending cache keys ({len(keys)} keys)")
            
            return True
        except Exception as e:
            logger.error(f"Error invalidating trending cache: {e}")
            return False
    
    def invalidate_suggestions_cache(self, query: Optional[str] = None) -> bool:
        """
        Invalidate suggestions cache.
        
        Args:
            query: Specific query to invalidate, or None for all
            
        Returns:
            True if invalidated successfully
        """
        if not self.redis.is_available:
            return False
        
        try:
            if query is not None:
                normalized_query = query.lower().strip()
                pattern = f"{self.SUGGESTIONS_KEY_PREFIX}{normalized_query}:*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
                    logger.info(f"Invalidated suggestions cache for query={query} ({len(keys)} keys)")
            else:
                # Delete all suggestions cache keys
                pattern = f"{self.SUGGESTIONS_KEY_PREFIX}*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
                    logger.info(f"Invalidated all suggestions cache keys ({len(keys)} keys)")
            
            return True
        except Exception as e:
            logger.error(f"Error invalidating suggestions cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.redis.is_available:
            return {"available": False}
        
        try:
            # Count cache keys
            trending_keys = len(self.redis.keys(f"{self.TRENDING_KEY_PREFIX}*"))
            suggestions_keys = len(self.redis.keys(f"{self.SUGGESTIONS_KEY_PREFIX}*"))
            search_result_keys = len(self.redis.keys(f"{self.SEARCH_RESULT_KEY_PREFIX}*"))
            
            return {
                "available": True,
                "trending_cache_count": trending_keys,
                "suggestions_cache_count": suggestions_keys,
                "search_result_cache_count": search_result_keys,
                "total_cache_keys": trending_keys + suggestions_keys + search_result_keys
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"available": False, "error": str(e)}


# Global cache service instance
search_cache = SearchCacheService()
