"""
Production-Grade Caching Layer for LangGraph Workflow Optimization
Implements in-memory and persistent caching for expensive operations
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union, Callable, Awaitable
from functools import wraps
from datetime import datetime, timedelta
import pickle
import os

logger = logging.getLogger(__name__)

class MemoryCache:
    """High-performance in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 3600):  # 1 hour default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, dict):
            # Sort dict for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True)
        else:
            sorted_data = str(data)
        
        hash_obj = hashlib.md5(sorted_data.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check TTL
            if time.time() > entry['expires_at']:
                del self.cache[key]
                return None
            
            entry['last_accessed'] = time.time()
            return entry['value']
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        async with self._lock:
            expires_at = time.time() + (ttl or self.default_ttl)
            self.cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time(),
                'last_accessed': time.time()
            }
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self.cache.clear()
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self.cache.items()
                if current_time > entry['expires_at']
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'memory_usage_mb': len(str(self.cache)) / (1024 * 1024),
            'oldest_entry': min(
                (entry['created_at'] for entry in self.cache.values()),
                default=0
            )
        }

class CompanyEnrichmentCache:
    """Specialized cache for company enrichment data"""
    
    def __init__(self, ttl: int = 86400):  # 24 hours for company data
        self.cache = MemoryCache(default_ttl=ttl)
    
    async def get_company_data(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get cached company enrichment data"""
        key = self.cache._generate_key("company", company_name.lower().strip())
        return await self.cache.get(key)
    
    async def set_company_data(self, company_name: str, data: Dict[str, Any]) -> None:
        """Cache company enrichment data"""
        key = self.cache._generate_key("company", company_name.lower().strip())
        await self.cache.set(key, data)
        logger.info(f"Cached company data for: {company_name}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.cache.get_stats()
        stats['cache_type'] = 'company_enrichment'
        return stats

class EmbeddingCache:
    """Specialized cache for sentence transformer embeddings"""
    
    def __init__(self, ttl: int = 604800):  # 7 days for embeddings
        self.cache = MemoryCache(default_ttl=ttl)
    
    async def get_embedding(self, text: str, model_name: str = "default") -> Optional[List[float]]:
        """Get cached embedding"""
        key = self.cache._generate_key(f"embedding:{model_name}", text.strip())
        return await self.cache.get(key)
    
    async def set_embedding(self, text: str, embedding: List[float], model_name: str = "default") -> None:
        """Cache embedding"""
        key = self.cache._generate_key(f"embedding:{model_name}", text.strip())
        await self.cache.set(key, embedding)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.cache.get_stats()
        stats['cache_type'] = 'embeddings'
        return stats

class CacheManager:
    """Central cache manager for all workflow caches"""
    
    def __init__(self):
        self.company_cache = CompanyEnrichmentCache()
        self.embedding_cache = EmbeddingCache()
        self._cleanup_task = None
        self._cleanup_started = False

    def _start_cleanup_task(self):
        """Start background cleanup task (only when event loop is available)"""
        if self._cleanup_started:
            return

        try:
            # Only start if we have a running event loop
            loop = asyncio.get_running_loop()
            if self._cleanup_task is None or self._cleanup_task.done():
                async def cleanup_loop():
                    while True:
                        try:
                            await asyncio.sleep(300)  # Cleanup every 5 minutes
                            company_cleaned = await self.company_cache.cache.cleanup_expired()
                            embedding_cleaned = await self.embedding_cache.cache.cleanup_expired()

                            if company_cleaned > 0 or embedding_cleaned > 0:
                                logger.info(f"Cache cleanup: {company_cleaned} company entries, {embedding_cleaned} embedding entries removed")

                        except Exception as e:
                            logger.error(f"Cache cleanup error: {e}")

                self._cleanup_task = asyncio.create_task(cleanup_loop())
                self._cleanup_started = True
                logger.info("Cache cleanup task started")
        except RuntimeError:
            # No event loop running, cleanup will be started later
            logger.debug("No event loop available, cleanup task will start later")

    def ensure_cleanup_started(self):
        """Ensure cleanup task is started (call this when event loop is available)"""
        if not self._cleanup_started:
            self._start_cleanup_task()

    async def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches"""
        return {
            'company_cache': await self.company_cache.get_stats(),
            'embedding_cache': await self.embedding_cache.get_stats(),
            'total_memory_usage_mb': sum([
                (await self.company_cache.get_stats())['memory_usage_mb'],
                (await self.embedding_cache.get_stats())['memory_usage_mb']
            ])
        }
    
    async def clear_all(self) -> None:
        """Clear all caches"""
        await self.company_cache.cache.clear()
        await self.embedding_cache.cache.clear()
        logger.info("All caches cleared")

# Global cache manager instance
cache_manager = CacheManager()

def cached_company_enrichment(ttl: Optional[int] = None):
    """Decorator for caching company enrichment results"""
    def decorator(func: Callable[..., Awaitable[Dict[str, Any]]]):
        @wraps(func)
        async def wrapper(company_name: str, *args, **kwargs) -> Dict[str, Any]:
            # Try cache first
            cached_result = await cache_manager.company_cache.get_company_data(company_name)
            if cached_result is not None:
                logger.info(f"Cache HIT for company: {company_name}")
                return cached_result
            
            # Cache miss - call original function
            logger.info(f"Cache MISS for company: {company_name}")
            result = await func(company_name, *args, **kwargs)
            
            # Cache the result if successful
            if result and result.get("company_id"):
                await cache_manager.company_cache.set_company_data(company_name, result)
            
            return result
        
        return wrapper
    return decorator

def cached_embedding(model_name: str = "default", ttl: Optional[int] = None):
    """Decorator for caching embeddings"""
    def decorator(func: Callable[..., Awaitable[List[float]]]):
        @wraps(func)
        async def wrapper(text: str, *args, **kwargs) -> List[float]:
            # Try cache first
            cached_result = await cache_manager.embedding_cache.get_embedding(text, model_name)
            if cached_result is not None:
                return cached_result
            
            # Cache miss - call original function
            result = await func(text, *args, **kwargs)
            
            # Cache the result
            if result:
                await cache_manager.embedding_cache.set_embedding(text, result, model_name)
            
            return result
        
        return wrapper
    return decorator
