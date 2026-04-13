"""
TF-IDF Search Optimization - Improve search relevance scoring.

TF-IDF (Term Frequency-Inverse Document Frequency) algorithm for:
1. Calculating text relevance scores
2. Ranking search results by relevance
3. Supporting Chinese text search optimization

Features:
- TF-IDF scoring for search terms
- BM25 algorithm support (better for short texts)
- Chinese text segmentation support (optional)
- Caching for performance
"""
import logging
import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class TFIDFOptimizer:
    """TF-IDF based search relevance optimizer"""
    
    def __init__(self):
        # Document frequency cache
        self.document_frequency: Dict[str, int] = defaultdict(int)
        self.total_documents: int = 0
        
        # BM25 parameters
        self.k1 = 1.5  # Term frequency saturation parameter
        self.b = 0.75  # Length normalization parameter
        
        # Average document length (for BM25)
        self.avg_doc_length: float = 0.0
        self.total_doc_length: int = 0
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into terms.
        
        For Chinese text, this is a simple character-based tokenization.
        For production, consider using jieba or similar libraries.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Simple tokenization: split by non-alphanumeric characters
        # For Chinese, this extracts individual characters and words
        tokens = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        
        # Filter out very short tokens
        return [t for t in tokens if len(t) >= 1]
    
    def calculate_tf(self, text: str, query_terms: List[str]) -> Dict[str, float]:
        """
        Calculate Term Frequency for each query term in text.
        
        Args:
            text: Document text
            query_terms: Query terms
            
        Returns:
            Dictionary mapping terms to TF scores
        """
        tokens = self.tokenize(text)
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return {term: 0.0 for term in query_terms}
        
        tf_scores = {}
        for term in query_terms:
            term_lower = term.lower()
            count = token_counts.get(term_lower, 0)
            # Normalized TF
            tf_scores[term_lower] = count / total_tokens
        
        return tf_scores
    
    def calculate_idf(self, term: str) -> float:
        """
        Calculate Inverse Document Frequency for a term.
        
        IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5))
        
        Args:
            term: Query term
            
        Returns:
            IDF score for the term
        """
        term_lower = term.lower()
        df = self.document_frequency.get(term_lower, 0)
        
        # Smooth IDF to avoid division by zero
        idf = math.log((self.total_documents - df + 0.5) / (df + 0.5))
        
        return max(0.0, idf)  # IDF should not be negative
    
    def calculate_tfidf_score(
        self,
        text: str,
        query: str,
        doc_id: Optional[str] = None
    ) -> float:
        """
        Calculate TF-IDF relevance score for a document.
        
        Args:
            text: Document text
            query: Search query
            doc_id: Optional document ID for debugging
            
        Returns:
            TF-IDF relevance score
        """
        query_terms = self.tokenize(query)
        
        if not query_terms:
            return 0.0
        
        tf_scores = self.calculate_tf(text, query_terms)
        
        # Calculate combined TF-IDF score
        total_score = 0.0
        for term in query_terms:
            term_lower = term.lower()
            tf = tf_scores.get(term_lower, 0.0)
            idf = self.calculate_idf(term_lower)
            total_score += tf * idf
        
        # Normalize by number of query terms
        return total_score / len(query_terms)
    
    def calculate_bm25_score(
        self,
        text: str,
        query: str,
        doc_length: Optional[int] = None
    ) -> float:
        """
        Calculate BM25 relevance score (better for short texts).
        
        BM25 is generally better than TF-IDF for search ranking.
        
        Args:
            text: Document text
            query: Search query
            doc_length: Document length (optional, calculated if not provided)
            
        Returns:
            BM25 relevance score
        """
        query_terms = self.tokenize(query)
        
        if not query_terms:
            return 0.0
        
        tokens = self.tokenize(text)
        token_counts = Counter(tokens)
        
        if doc_length is None:
            doc_length = len(tokens)
        
        if doc_length == 0:
            return 0.0
        
        # Calculate BM25 score
        total_score = 0.0
        
        for term in query_terms:
            term_lower = term.lower()
            term_count = token_counts.get(term_lower, 0)
            
            if term_count == 0:
                continue
            
            idf = self.calculate_idf(term_lower)
            
            # BM25 TF component
            numerator = term_count * (self.k1 + 1)
            denominator = term_count + self.k1 * (
                1 - self.b + self.b * (doc_length / self.avg_doc_length)
                if self.avg_doc_length > 0 else 1
            )
            
            tf_bm25 = numerator / denominator if denominator > 0 else 0
            total_score += idf * tf_bm25
        
        return total_score
    
    def update_document_frequency(
        self,
        texts: List[str],
        clear_cache: bool = False
    ) -> None:
        """
        Update document frequency statistics from a corpus.
        
        Should be called periodically or when documents change.
        
        Args:
            texts: List of document texts
            clear_cache: Whether to clear existing cache
        """
        if clear_cache:
            self.document_frequency.clear()
            self.total_documents = 0
            self.total_doc_length = 0
        
        for text in texts:
            self.total_documents += 1
            tokens = set(self.tokenize(text))
            
            for token in tokens:
                self.document_frequency[token] += 1
            
            doc_length = len(self.tokenize(text))
            self.total_doc_length += doc_length
        
        # Update average document length
        if self.total_documents > 0:
            self.avg_doc_length = self.total_doc_length / self.total_documents
        
        logger.info(
            f"Updated document frequency: {self.total_documents} docs, "
            f"{len(self.document_frequency)} unique terms"
        )
    
    def rank_results(
        self,
        results: List[Dict],
        query: str,
        text_field: str = 'description',
        use_bm25: bool = True
    ) -> List[Dict]:
        """
        Rank search results by relevance score.
        
        Args:
            results: List of search result dictionaries
            query: Search query
            text_field: Field to use for scoring
            use_bm25: Use BM25 instead of TF-IDF
            
        Returns:
            Ranked list of results with scores
        """
        scored_results = []
        
        for result in results:
            text = result.get(text_field, '') or ''
            title = result.get('title', '') or ''
            
            # Combine title and description for scoring
            # Title matches are more important
            combined_text = f"{title} {title} {text}"
            
            if use_bm25:
                score = self.calculate_bm25_score(combined_text, query)
            else:
                score = self.calculate_tfidf_score(combined_text, query)
            
            # Add exact match bonus
            if query.lower() in title.lower():
                score += 10.0
            elif query.lower() in text.lower():
                score += 5.0
            
            result_with_score = result.copy()
            result_with_score['relevance_score'] = score
            scored_results.append(result_with_score)
        
        # Sort by relevance score descending
        scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return scored_results


# Global TF-IDF optimizer instance
tfidf_optimizer = TFIDFOptimizer()
