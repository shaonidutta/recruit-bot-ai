"""
Production-Grade LangGraph Workflow Configuration
Optimized settings for maximum performance and scalability
"""

import os
from typing import Dict, Any

class WorkflowConfig:
    """Production workflow configuration with performance optimizations"""
    
    # Parallel Processing Settings
    ENRICHMENT_BATCH_SIZE = int(os.getenv("ENRICHMENT_BATCH_SIZE", "10"))
    ENRICHMENT_MAX_CONCURRENT = int(os.getenv("ENRICHMENT_MAX_CONCURRENT", "5"))
    
    PARSING_BATCH_SIZE = int(os.getenv("PARSING_BATCH_SIZE", "15"))
    PARSING_MAX_CONCURRENT = int(os.getenv("PARSING_MAX_CONCURRENT", "8"))
    
    MATCHING_BATCH_SIZE = int(os.getenv("MATCHING_BATCH_SIZE", "20"))
    MATCHING_MAX_CONCURRENT = int(os.getenv("MATCHING_MAX_CONCURRENT", "10"))
    
    # Cache Settings
    COMPANY_CACHE_TTL = int(os.getenv("COMPANY_CACHE_TTL", "86400"))  # 24 hours
    EMBEDDING_CACHE_TTL = int(os.getenv("EMBEDDING_CACHE_TTL", "604800"))  # 7 days
    
    # Performance Thresholds
    MATCHING_THRESHOLD = float(os.getenv("MATCHING_THRESHOLD", "0.4"))
    MAX_CANDIDATES_PER_JOB = int(os.getenv("MAX_CANDIDATES_PER_JOB", "3"))
    
    # Timeout Settings (Production: No timeouts for reliability)
    ENABLE_TIMEOUTS = os.getenv("ENABLE_TIMEOUTS", "false").lower() == "true"
    ENRICHMENT_TIMEOUT = int(os.getenv("ENRICHMENT_TIMEOUT", "30"))
    PARSING_TIMEOUT = int(os.getenv("PARSING_TIMEOUT", "15"))
    
    # Database Settings
    DB_CONNECTION_POOL_SIZE = int(os.getenv("DB_CONNECTION_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    # API Rate Limiting
    APOLLO_RATE_LIMIT_PER_MINUTE = int(os.getenv("APOLLO_RATE_LIMIT_PER_MINUTE", "60"))
    GEMINI_RATE_LIMIT_PER_MINUTE = int(os.getenv("GEMINI_RATE_LIMIT_PER_MINUTE", "60"))
    
    # Memory Management
    MAX_JOBS_IN_MEMORY = int(os.getenv("MAX_JOBS_IN_MEMORY", "1000"))
    CLEANUP_INTERVAL_SECONDS = int(os.getenv("CLEANUP_INTERVAL_SECONDS", "300"))
    
    @classmethod
    def get_enrichment_config(cls) -> Dict[str, Any]:
        """Get enrichment node configuration"""
        return {
            "batch_size": cls.ENRICHMENT_BATCH_SIZE,
            "max_concurrent_batches": cls.ENRICHMENT_MAX_CONCURRENT,
            "enable_timeout": cls.ENABLE_TIMEOUTS,
            "timeout_seconds": cls.ENRICHMENT_TIMEOUT,
            "cache_ttl": cls.COMPANY_CACHE_TTL
        }
    
    @classmethod
    def get_parsing_config(cls) -> Dict[str, Any]:
        """Get parsing node configuration"""
        return {
            "batch_size": cls.PARSING_BATCH_SIZE,
            "max_concurrent_batches": cls.PARSING_MAX_CONCURRENT,
            "enable_timeout": cls.ENABLE_TIMEOUTS,
            "timeout_seconds": cls.PARSING_TIMEOUT
        }
    
    @classmethod
    def get_matching_config(cls) -> Dict[str, Any]:
        """Get matching node configuration"""
        return {
            "batch_size": cls.MATCHING_BATCH_SIZE,
            "max_concurrent_batches": cls.MATCHING_MAX_CONCURRENT,
            "threshold": cls.MATCHING_THRESHOLD,
            "max_candidates": cls.MAX_CANDIDATES_PER_JOB,
            "cache_ttl": cls.EMBEDDING_CACHE_TTL
        }
    
    @classmethod
    def get_performance_config(cls) -> Dict[str, Any]:
        """Get overall performance configuration"""
        return {
            "max_jobs_in_memory": cls.MAX_JOBS_IN_MEMORY,
            "cleanup_interval": cls.CLEANUP_INTERVAL_SECONDS,
            "db_pool_size": cls.DB_CONNECTION_POOL_SIZE,
            "db_max_overflow": cls.DB_MAX_OVERFLOW,
            "apollo_rate_limit": cls.APOLLO_RATE_LIMIT_PER_MINUTE,
            "gemini_rate_limit": cls.GEMINI_RATE_LIMIT_PER_MINUTE
        }

class ProductionOptimizations:
    """Production-specific optimizations and best practices"""
    
    @staticmethod
    def get_langgraph_optimizations() -> Dict[str, Any]:
        """Get LangGraph-specific optimizations"""
        return {
            # State Management
            "enable_state_compression": True,
            "max_state_size_mb": 50,
            "enable_state_checkpointing": False,  # Disable for speed
            
            # Execution Optimizations
            "enable_parallel_execution": True,
            "max_parallel_nodes": 10,
            "enable_node_caching": True,
            
            # Memory Management
            "enable_garbage_collection": True,
            "gc_threshold": 1000,
            "enable_memory_profiling": False,  # Disable in production
            
            # Error Handling
            "max_retries": 2,
            "retry_delay_seconds": 1,
            "enable_circuit_breaker": True,
            
            # Monitoring
            "enable_performance_monitoring": True,
            "enable_detailed_logging": False,  # Reduce log overhead
            "log_level": "INFO"
        }
    
    @staticmethod
    def get_async_optimizations() -> Dict[str, Any]:
        """Get async/await optimizations"""
        return {
            # Event Loop Settings
            "event_loop_policy": "uvloop",  # Faster event loop
            "max_workers": 20,
            "thread_pool_size": 10,
            
            # Concurrency Limits
            "max_concurrent_requests": 100,
            "semaphore_limit": 50,
            "connection_pool_size": 25,
            
            # Timeout Settings
            "default_timeout": None,  # No timeouts in production
            "connection_timeout": 30,
            "read_timeout": 60
        }
    
    @staticmethod
    def get_caching_strategy() -> Dict[str, Any]:
        """Get production caching strategy"""
        return {
            # Cache Types
            "enable_memory_cache": True,
            "enable_redis_cache": False,  # Not implemented yet
            "enable_disk_cache": False,   # Not needed for this use case
            
            # Cache Policies
            "default_ttl": 3600,  # 1 hour
            "max_cache_size_mb": 500,
            "cache_cleanup_interval": 300,  # 5 minutes
            
            # Cache Strategies
            "company_cache_strategy": "write_through",
            "embedding_cache_strategy": "write_through",
            "job_cache_strategy": "write_behind"
        }

# Global configuration instances
workflow_config = WorkflowConfig()
production_optimizations = ProductionOptimizations()

# Performance monitoring settings
PERFORMANCE_MONITORING = {
    "enable_timing": True,
    "enable_memory_tracking": False,  # Disable in production
    "enable_cache_stats": True,
    "log_slow_operations": True,
    "slow_operation_threshold_seconds": 5.0
}

# Production deployment settings
DEPLOYMENT_CONFIG = {
    "environment": os.getenv("ENVIRONMENT", "production"),
    "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
    "enable_profiling": os.getenv("ENABLE_PROFILING", "false").lower() == "true",
    "max_request_size_mb": int(os.getenv("MAX_REQUEST_SIZE_MB", "10")),
    "request_timeout_seconds": int(os.getenv("REQUEST_TIMEOUT_SECONDS", "300"))  # 5 minutes
}

def get_optimized_workflow_settings() -> Dict[str, Any]:
    """Get complete optimized workflow settings for production"""
    return {
        "workflow": workflow_config.get_performance_config(),
        "enrichment": workflow_config.get_enrichment_config(),
        "parsing": workflow_config.get_parsing_config(),
        "matching": workflow_config.get_matching_config(),
        "langgraph": production_optimizations.get_langgraph_optimizations(),
        "async": production_optimizations.get_async_optimizations(),
        "caching": production_optimizations.get_caching_strategy(),
        "monitoring": PERFORMANCE_MONITORING,
        "deployment": DEPLOYMENT_CONFIG
    }
