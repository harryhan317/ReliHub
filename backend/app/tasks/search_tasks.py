"""
Celery tasks for search module.

Tasks:
- update_trending_searches: Periodic task to update trending search cache
"""
from app.celery_app import celery_app


@celery_app.task(bind=True, priority=8)
def update_trending_searches_task(self, default_limit: int = 10):
    """
    Celery task to pre-calculate and cache trending searches.
    
    This task should be run periodically (e.g., every 5 minutes) to:
    1. Calculate trending searches from search history
    2. Cache the results in Redis for fast retrieval
    3. Invalidate old cache
    
    Args:
        self: Celery task instance
        default_limit: Default number of trending terms to cache (default: 10)
    
    Returns:
        dict: Task result with trending count and cache status
    """
    import logging
    from datetime import datetime
    
    from app.core.database import SessionLocal
    from app.services.search_cache_service import SearchCacheService
    
    logger = logging.getLogger(__name__)
    start_time = datetime.utcnow()
    
    db = SessionLocal()
    cache_service = SearchCacheService()
    
    try:
        # Check if Redis is available
        if not cache_service.redis.is_available:
            logger.warning("Redis not available, skipping trending cache update")
            return {
                'status': 'SKIPPED',
                'reason': 'Redis not available',
                'timestamp': start_time.isoformat()
            }
        
        # Query search history to find most frequent keywords
        from sqlalchemy import func, select
        from app.models.search_history import SearchHistory
        
        stmt = select(
            SearchHistory.keyword,
            func.count(SearchHistory.id).label('search_count')
        ).group_by(SearchHistory.keyword)
        
        # Order by search count descending
        stmt = stmt.order_by(func.count(SearchHistory.id).desc())
        
        # Limit results
        stmt = stmt.limit(default_limit)
        
        results = db.execute(stmt).all()
        
        trending = [
            {
                "keyword": row.keyword,
                "count": row.search_count,
                "rank": idx + 1
            }
            for idx, row in enumerate(results)
        ]
        
        # Cache the trending searches
        cache_service.set_trending(trending, limit=default_limit)
        
        logger.info(
            f"Updated trending searches cache: {len(trending)} terms, "
            f"duration: {(datetime.utcnow() - start_time).total_seconds()}s"
        )
        
        return {
            'status': 'SUCCESS',
            'trending_count': len(trending),
            'top_keyword': trending[0]['keyword'] if trending else None,
            'timestamp': start_time.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error updating trending searches: {e}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'timestamp': start_time.isoformat()
        }
    
    finally:
        db.close()


@celery_app.task(bind=True, priority=8)
def cleanup_search_cache_task(self):
    """
    Celery task to cleanup expired search cache entries.
    
    This task should be run periodically (e.g., every hour) to:
    1. Clean up old cache entries
    2. Report cache statistics
    
    Args:
        self: Celery task instance
    
    Returns:
        dict: Task result with cache statistics
    """
    import logging
    from datetime import datetime
    
    from app.services.search_cache_service import SearchCacheService
    
    logger = logging.getLogger(__name__)
    start_time = datetime.utcnow()
    
    cache_service = SearchCacheService()
    
    try:
        # Check if Redis is available
        if not cache_service.redis.is_available:
            logger.warning("Redis not available, skipping cache cleanup")
            return {
                'status': 'SKIPPED',
                'reason': 'Redis not available',
                'timestamp': start_time.isoformat()
            }
        
        # Get cache statistics
        stats = cache_service.get_cache_stats()
        
        logger.info(
            f"Search cache stats: {stats.get('total_cache_keys', 0)} keys, "
            f"duration: {(datetime.utcnow() - start_time).total_seconds()}s"
        )
        
        return {
            'status': 'SUCCESS',
            'cache_stats': stats,
            'timestamp': start_time.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error cleaning up search cache: {e}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'timestamp': start_time.isoformat()
        }
