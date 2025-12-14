"""
LLM Response Caching with Redis and Semantic Similarity

This module provides intelligent caching for LLM responses to reduce API costs
and improve performance by 10-100x for repeated or similar queries.
"""

import hashlib
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging


class LLMCache:
    """
    Intelligent caching layer for LLM responses
    
    Features:
    - Exact match caching (hash-based)
    - Semantic similarity caching (embedding-based)
    - TTL expiration
    - Cost tracking
    - Cache statistics
    """
    
    def __init__(self, 
                 redis_url: Optional[str] = None,
                 ttl_days: int = 30,
                 similarity_threshold: float = 0.95,
                 enable_semantic: bool = True):
        """
        Initialize LLM cache
        
        Args:
            redis_url: Redis connection URL (default: localhost:6379)
            ttl_days: Cache entry TTL in days
            similarity_threshold: Semantic similarity threshold (0.0-1.0)
            enable_semantic: Enable semantic similarity matching
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.ttl_seconds = ttl_days * 24 * 3600
        self.similarity_threshold = similarity_threshold
        self.enable_semantic = enable_semantic
        self.logger = logging.getLogger(__name__)
        
        self._redis_client = None
        self._embeddings_model = None
        self._stats = {
            "hits": 0,
            "misses": 0,
            "cost_saved": 0.0,
            "semantic_hits": 0
        }
        
        self._initialize()
    
    def _initialize(self):
        """Initialize Redis and embeddings model if available"""
        try:
            import redis
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self._redis_client.ping()
            self.logger.info(f"Redis cache connected: {self.redis_url}")
        except ImportError:
            self.logger.warning("Redis not installed. Install with: pip install redis")
            self.logger.info("Falling back to in-memory cache")
            self._redis_client = None
            self._memory_cache = {}
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
            self.logger.info("Falling back to in-memory cache")
            self._redis_client = None
            self._memory_cache = {}
        
        # Initialize embeddings for semantic caching
        if self.enable_semantic:
            try:
                from sentence_transformers import SentenceTransformer
                self._embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Semantic caching enabled (all-MiniLM-L6-v2)")
            except ImportError:
                self.logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")
                self.logger.info("Semantic caching disabled")
                self.enable_semantic = False
    
    def _hash_prompt(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate hash key for exact matching"""
        # Include relevant parameters in hash
        key_data = {
            "prompt": prompt,
            "temperature": params.get("temperature", 0.7),
            "model": params.get("model", ""),
            "max_tokens": params.get("max_tokens", 2000)
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector for semantic similarity"""
        if not self.enable_semantic or not self._embeddings_model:
            return None
        
        try:
            embedding = self._embeddings_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"⚠ Embedding generation failed: {e}")
            return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def get(self, prompt: str, params: Dict[str, Any]) -> Optional[str]:
        """
        Get cached response for prompt
        
        Args:
            prompt: LLM prompt
            params: LLM parameters (temperature, model, etc.)
            
        Returns:
            Cached response or None if not found
        """
        # Try exact match first
        cache_key = self._hash_prompt(prompt, params)
        
        if self._redis_client:
            try:
                cached = self._redis_client.get(f"llm:exact:{cache_key}")
                if cached:
                    self._stats["hits"] += 1
                    cached_data = json.loads(cached)
                    print(f"✓ Cache hit (exact) - saved ${cached_data.get('cost', 0):.4f}")
                    return cached_data["response"]
            except Exception as e:
                print(f"⚠ Cache retrieval error: {e}")
        else:
            # In-memory cache
            if cache_key in self._memory_cache:
                self._stats["hits"] += 1
                cached_data = self._memory_cache[cache_key]
                print(f"✓ Cache hit (memory) - saved ${cached_data.get('cost', 0):.4f}")
                return cached_data["response"]
        
        # Try semantic match if enabled
        if self.enable_semantic:
            similar_response = self._find_similar(prompt, params)
            if similar_response:
                self._stats["semantic_hits"] += 1
                return similar_response
        
        self._stats["misses"] += 1
        return None
    
    def _find_similar(self, prompt: str, params: Dict[str, Any]) -> Optional[str]:
        """Find semantically similar cached response"""
        if not self._redis_client:
            return None  # Semantic search only works with Redis
        
        query_embedding = self._get_embedding(prompt)
        if not query_embedding:
            return None
        
        try:
            # Scan for semantic keys (limited to last 100 for performance)
            keys = list(self._redis_client.scan_iter("llm:semantic:*", count=100))
            
            best_match = None
            best_similarity = 0.0
            
            for key in keys[:100]:  # Limit search for performance
                cached = self._redis_client.get(key)
                if not cached:
                    continue
                
                cached_data = json.loads(cached)
                cached_embedding = cached_data.get("embedding")
                
                if not cached_embedding:
                    continue
                
                similarity = self._cosine_similarity(query_embedding, cached_embedding)
                
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    # Check if parameters match
                    if (params.get("temperature") == cached_data.get("temperature") and
                        params.get("model") == cached_data.get("model")):
                        best_similarity = similarity
                        best_match = cached_data["response"]
            
            if best_match:
                print(f"✓ Cache hit (semantic, {best_similarity:.2%} similar)")
                return best_match
                
        except Exception as e:
            print(f"⚠ Semantic search error: {e}")
        
        return None
    
    def set(self, prompt: str, params: Dict[str, Any], response: str, cost: float = 0.0):
        """
        Cache LLM response
        
        Args:
            prompt: LLM prompt
            params: LLM parameters
            response: LLM response to cache
            cost: Estimated cost of this API call (for tracking)
        """
        cache_key = self._hash_prompt(prompt, params)
        
        cache_data = {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "cost": cost,
            "temperature": params.get("temperature"),
            "model": params.get("model")
        }
        
        # Store exact match
        if self._redis_client:
            try:
                self._redis_client.setex(
                    f"llm:exact:{cache_key}",
                    self.ttl_seconds,
                    json.dumps(cache_data)
                )
                
                # Store for semantic matching if enabled
                if self.enable_semantic:
                    embedding = self._get_embedding(prompt)
                    if embedding:
                        semantic_data = cache_data.copy()
                        semantic_data["embedding"] = embedding
                        semantic_data["prompt"] = prompt[:200]  # Store snippet for debugging
                        
                        self._redis_client.setex(
                            f"llm:semantic:{cache_key}",
                            self.ttl_seconds,
                            json.dumps(semantic_data)
                        )
                
                print(f"✓ Cached response (${cost:.4f})")
            except Exception as e:
                print(f"⚠ Cache storage error: {e}")
        else:
            # In-memory cache
            self._memory_cache[cache_key] = cache_data
            print(f"✓ Cached response in memory (${cost:.4f})")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "cache_hits": self._stats["hits"],
            "cache_misses": self._stats["misses"],
            "semantic_hits": self._stats["semantic_hits"],
            "hit_rate": f"{hit_rate:.1f}%",
            "estimated_cost_saved": f"${self._stats['cost_saved']:.2f}"
        }
    
    def clear(self):
        """Clear all cached entries"""
        if self._redis_client:
            try:
                # Clear all LLM cache keys
                keys = list(self._redis_client.scan_iter("llm:*"))
                if keys:
                    self._redis_client.delete(*keys)
                print(f"✓ Cleared {len(keys)} cache entries")
            except Exception as e:
                print(f"⚠ Cache clear error: {e}")
        else:
            self._memory_cache.clear()
            print("✓ Cleared in-memory cache")
        
        # Reset stats
        self._stats = {
            "hits": 0,
            "misses": 0,
            "cost_saved": 0.0,
            "semantic_hits": 0
        }


# Global cache instance
_global_cache = None


def get_cache() -> LLMCache:
    """Get or create global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = LLMCache()
    return _global_cache


def estimate_cost(prompt: str, response: str, model: str = "gpt-4") -> float:
    """
    Estimate API cost for a request
    
    NOTE: These are approximate estimates and should be verified against current pricing.
    Rough estimates (subject to change):
    - GPT-4: $0.03/1k input tokens, $0.06/1k output tokens
    - GPT-3.5: $0.001/1k input tokens, $0.002/1k output tokens
    - Claude: $0.008/1k input tokens, $0.024/1k output tokens
    """
    # Rough token estimation (1 token ≈ 4 characters)
    input_tokens = len(prompt) / 4
    output_tokens = len(response) / 4
    
    if "gpt-4" in model.lower():
        cost = (input_tokens / 1000 * 0.03) + (output_tokens / 1000 * 0.06)
    elif "gpt-3.5" in model.lower():
        cost = (input_tokens / 1000 * 0.001) + (output_tokens / 1000 * 0.002)
    elif "claude" in model.lower():
        cost = (input_tokens / 1000 * 0.008) + (output_tokens / 1000 * 0.024)
    else:
        # Default estimate
        cost = (input_tokens / 1000 * 0.01) + (output_tokens / 1000 * 0.03)
    
    return cost
