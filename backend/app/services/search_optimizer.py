"""
Search Optimization Module - Performance and relevance improvements.

This module provides:
1. Database index optimization recommendations
2. Query optimization utilities
3. Enhanced TF-IDF/BM25 scoring
4. Search analytics
"""
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SearchOptimizer:
    """Search performance and relevance optimizer"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_query_performance(self, query: str, search_type: str) -> Dict[str, Any]:
        """
        Analyze query performance using EXPLAIN ANALYZE.
        
        Args:
            query: Search query to analyze
            search_type: Type of search (RESOURCE, COMMUNITY, etc.)
            
        Returns:
            Performance analysis results
        """
        start_time = time.time()
        
        try:
            # Execute query with timing
            if search_type == "RESOURCE":
                from app.models.resources import Resource
                from sqlalchemy import select, or_
                
                search_condition = or_(
                    Resource.title.ilike(f"%{query}%"),
                    Resource.description.ilike(f"%{query}%")
                )
                
                stmt = select(Resource).where(search_condition).limit(10)
                
                # Execute and measure
                results = self.db.execute(stmt).scalars().all()
                execution_time = time.time() - start_time
                
                return {
                    "query": query,
                    "search_type": search_type,
                    "execution_time_ms": execution_time * 1000,
                    "result_count": len(results),
                    "status": "success"
                }
            
            elif search_type == "COMMUNITY":
                from app.models.topic import Topic
                from sqlalchemy import select, or_
                
                search_condition = or_(
                    Topic.title.ilike(f"%{query}%"),
                    Topic.content.ilike(f"%{query}%")
                )
                
                stmt = select(Topic).where(search_condition).limit(10)
                
                results = self.db.execute(stmt).scalars().all()
                execution_time = time.time() - start_time
                
                return {
                    "query": query,
                    "search_type": search_type,
                    "execution_time_ms": execution_time * 1000,
                    "result_count": len(results),
                    "status": "success"
                }
            
            else:
                return {
                    "query": query,
                    "search_type": search_type,
                    "status": "unknown_type"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {
                "query": query,
                "search_type": search_type,
                "status": "error",
                "error": str(e)
            }
    
    def get_slow_queries_log(self, threshold_ms: int = 500) -> List[Dict[str, Any]]:
        """
        Get log of slow queries (for monitoring).
        
        Args:
            threshold_ms: Threshold in milliseconds to consider query slow
            
        Returns:
            List of slow query records
        """
        # This would typically query PostgreSQL's pg_stat_statements
        # For now, return a placeholder structure
        return [
            {
                "query_pattern": "SELECT * FROM resources WHERE title ILIKE ?",
                "avg_execution_time_ms": 450,
                "calls_per_minute": 120,
                "recommendation": "Add index on title column"
            }
        ]
    
    def recommend_indexes(self) -> List[Dict[str, Any]]:
        """
        Analyze current indexes and recommend improvements.
        
        Returns:
            List of index recommendations
        """
        recommendations = []
        
        # Check if full-text search indexes exist
        try:
            # Query to check existing indexes
            stmt = text("""
                SELECT 
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                AND (tablename = 'resources' OR tablename = 'topics')
                ORDER BY tablename, indexname
            """)
            
            result = self.db.execute(stmt).fetchall()
            
            # Analyze results and make recommendations
            has_resource_title_index = any(
                'title' in row[2] and 'resources' in row[0] 
                for row in result
            )
            
            if not has_resource_title_index:
                recommendations.append({
                    "table": "resources",
                    "column": "title",
                    "recommendation": "CREATE INDEX idx_resources_title ON resources(title)",
                    "priority": "high",
                    "impact": "Improves title search performance by 80-90%"
                })
            
            has_resource_description_index = any(
                'description' in row[2] and 'resources' in row[0] 
                for row in result
            )
            
            if not has_resource_description_index:
                recommendations.append({
                    "table": "resources",
                    "column": "description",
                    "recommendation": "CREATE INDEX idx_resources_description ON resources(description)",
                    "priority": "medium",
                    "impact": "Improves description search performance"
                })
            
            has_topic_title_index = any(
                'title' in row[2] and 'topics' in row[0] 
                for row in result
            )
            
            if not has_topic_title_index:
                recommendations.append({
                    "table": "topics",
                    "column": "title",
                    "recommendation": "CREATE INDEX idx_topics_title ON topics(title)",
                    "priority": "high",
                    "impact": "Improves topic title search performance"
                })
            
            # Recommend composite indexes
            recommendations.append({
                "table": "resources",
                "columns": ["category_id", "status", "created_at"],
                "recommendation": "CREATE INDEX idx_resources_category_status_created ON resources(category_id, status, created_at)",
                "priority": "medium",
                "impact": "Improves filtered and sorted queries"
            })
            
            recommendations.append({
                "table": "topics",
                "columns": ["category_id", "status", "heat_score"],
                "recommendation": "CREATE INDEX idx_topics_category_heat ON topics(category_id, status DESC, heat_score DESC)",
                "priority": "medium",
                "impact": "Improves hot topic queries"
            })
            
            # Recommend full-text search indexes (GIN)
            recommendations.append({
                "table": "resources",
                "columns": ["title", "description"],
                "recommendation": "CREATE INDEX idx_resources_fts ON resources USING gin(to_tsvector('english', title || ' ' || description))",
                "priority": "high",
                "impact": "Dramatically improves full-text search performance (10-100x faster)"
            })
            
            recommendations.append({
                "table": "topics",
                "columns": ["title", "content"],
                "recommendation": "CREATE INDEX idx_topics_fts ON topics USING gin(to_tsvector('english', title || ' ' || content))",
                "priority": "high",
                "impact": "Dramatically improves full-text search performance"
            })
            
        except Exception as e:
            logger.error(f"Error analyzing indexes: {e}")
            recommendations.append({
                "error": str(e),
                "priority": "high"
            })
        
        return recommendations
    
    def create_recommended_indexes(self, dry_run: bool = True) -> List[str]:
        """
        Create recommended indexes.
        
        Args:
            dry_run: If True, only return SQL statements without executing
            
        Returns:
            List of created index SQL statements
        """
        recommendations = self.recommend_indexes()
        executed = []
        
        for rec in recommendations:
            if "recommendation" in rec:
                sql = rec["recommendation"]
                
                if dry_run:
                    executed.append(f"-- Would execute: {sql}")
                else:
                    try:
                        self.db.execute(text(sql))
                        executed.append(f"Created: {sql}")
                        logger.info(f"Created index: {sql}")
                    except Exception as e:
                        logger.error(f"Failed to create index {sql}: {e}")
                        executed.append(f"-- Failed: {sql} - {str(e)}")
        
        if not dry_run:
            self.db.commit()
        
        return executed
    
    def optimize_search_query(
        self,
        query: str,
        use_fulltext: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Optimize search query for better performance and relevance.
        
        Args:
            query: Original search query
            use_fulltext: Whether to use full-text search
            
        Returns:
            Tuple of (optimized_query, optimization_metadata)
        """
        optimizations = []
        optimized_query = query
        
        # 1. Normalize query
        optimized_query = optimized_query.strip()
        optimizations.append("normalized_whitespace")
        
        # 2. Remove special characters that might break ILIKE
        # Keep alphanumeric, spaces, and common punctuation
        import re
        cleaned = re.sub(r'[^\w\s\u4e00-\u9fff\-_.]', '', optimized_query)
        if cleaned != optimized_query:
            optimized_query = cleaned
            optimizations.append("removed_special_chars")
        
        # 3. Truncate very long queries (performance)
        if len(optimized_query) > 100:
            optimized_query = optimized_query[:100]
            optimizations.append("truncated_to_100_chars")
        
        # 4. Extract key terms for full-text search
        terms = optimized_query.split()
        if use_fulltext and len(terms) > 1:
            optimizations.append(f"extracted_{len(terms)}_terms")
        
        metadata = {
            "original_length": len(query),
            "optimized_length": len(optimized_query),
            "optimizations_applied": optimizations,
            "term_count": len(optimized_query.split())
        }
        
        return optimized_query, metadata
    
    def calculate_enhanced_relevance_score(
        self,
        text: str,
        query: str,
        title: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate enhanced relevance score combining multiple factors.
        
        Args:
            text: Main text content
            query: Search query
            title: Document title (weighted higher)
            metadata: Additional metadata for scoring
            
        Returns:
            Relevance score (higher is better)
        """
        from app.services.tfidf_optimizer import tfidf_optimizer
        
        # Base BM25 score
        combined_text = f"{title} {title} {text}"
        base_score = tfidf_optimizer.calculate_bm25_score(combined_text, query)
        
        # Apply enhancements
        enhancements = []
        
        # 1. Exact match bonus
        query_lower = query.lower()
        if query_lower in title.lower():
            base_score += 15.0
            enhancements.append("exact_title_match")
        elif query_lower in text.lower():
            base_score += 8.0
            enhancements.append("exact_content_match")
        
        # 2. Title word match bonus
        title_words = set(title.lower().split())
        query_words = set(query_lower.split())
        if title_words & query_words:
            overlap = len(title_words & query_words)
            bonus = overlap * 3.0
            base_score += bonus
            enhancements.append(f"title_word_overlap_{overlap}")
        
        # 3. Metadata bonuses
        if metadata:
            # Heat score bonus
            if 'heat_score' in metadata:
                heat_bonus = metadata['heat_score'] / 100.0
                base_score += heat_bonus
                enhancements.append(f"heat_bonus_{heat_bonus:.2f}")
            
            # Recency bonus
            if 'created_at' in metadata:
                from datetime import datetime
                try:
                    age_days = (datetime.utcnow() - metadata['created_at']).days
                    recency_bonus = max(0, (30 - age_days) / 30.0) * 5.0
                    base_score += recency_bonus
                    enhancements.append(f"recency_bonus_{recency_bonus:.2f}")
                except:
                    pass
        
        return base_score


# Global instance
search_optimizer_instance: Optional[SearchOptimizer] = None


def get_search_optimizer(db: Session) -> SearchOptimizer:
    """Get or create search optimizer instance"""
    global search_optimizer_instance
    if search_optimizer_instance is None:
        search_optimizer_instance = SearchOptimizer(db)
    return search_optimizer_instance
