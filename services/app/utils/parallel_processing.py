"""
Parallel Processing Utilities
Provides high-performance parallel processing for workflow nodes
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Callable, Awaitable, Optional
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class ParallelProcessor:
    """High-performance parallel processor for batch operations"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._semaphore = asyncio.Semaphore(max_workers)
    
    async def process_jobs_in_batches(
        self,
        jobs: List[Dict[str, Any]],
        processor_func: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]],
        batch_size: int = 10,
        max_concurrent_batches: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Process jobs in parallel batches for optimal performance
        
        Args:
            jobs: List of job dictionaries to process
            processor_func: Async function to process each job
            batch_size: Number of jobs per batch
            max_concurrent_batches: Maximum number of concurrent batches
            
        Returns:
            List of processed job dictionaries
        """
        if not jobs:
            return []
        
        logger.info(f"Processing {len(jobs)} jobs in batches of {batch_size} with {max_concurrent_batches} concurrent batches")
        
        # Split jobs into batches
        batches = [jobs[i:i + batch_size] for i in range(0, len(jobs), batch_size)]
        
        # Process batches with concurrency limit
        semaphore = asyncio.Semaphore(max_concurrent_batches)
        
        async def process_batch(batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            async with semaphore:
                # Process all jobs in the batch concurrently
                tasks = [processor_func(job) for job in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Filter out exceptions and convert to proper return type
                processed_results = []
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Job processing failed: {result}")
                        # Return empty dict for failed jobs to maintain list structure
                        processed_results.append({})
                    else:
                        processed_results.append(result)

                return processed_results
        
        # Process all batches
        batch_results = await asyncio.gather(*[process_batch(batch) for batch in batches])
        
        # Flatten results and handle exceptions
        processed_jobs = []
        for batch_result in batch_results:
            for result in batch_result:
                if isinstance(result, Exception):
                    logger.error(f"Job processing failed: {result}")
                    # Return original job if processing failed
                    processed_jobs.append({})
                else:
                    processed_jobs.append(result)
        
        logger.info(f"Successfully processed {len(processed_jobs)} jobs")
        return processed_jobs
    
    async def process_single_item(
        self,
        item: Any,
        processor_func: Callable[[Any], Awaitable[Any]]
    ) -> Any:
        """Process a single item with semaphore control"""
        async with self._semaphore:
            return await processor_func(item)
    
    def cleanup(self):
        """Cleanup resources"""
        if self._executor:
            self._executor.shutdown(wait=True)


def performance_monitor(operation_name: str):
    """
    Decorator to monitor performance of async functions
    
    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_id = f"{operation_name}_{int(start_time)}"
            
            logger.info(f"🚀 Starting {operation_name} (ID: {operation_id})")
            
            try:
                result = await func(*args, **kwargs)
                
                end_time = time.time()
                duration = end_time - start_time
                
                logger.info(f"✅ {operation_name} completed in {duration:.2f}s (ID: {operation_id})")
                
                return result
                
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                
                logger.error(f"❌ {operation_name} failed after {duration:.2f}s: {e} (ID: {operation_id})")
                raise
        
        return wrapper
    return decorator


class AsyncBatchProcessor:
    """Advanced async batch processor with configurable concurrency"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(
        self,
        items: List[Any],
        processor: Callable[[Any], Awaitable[Any]],
        batch_size: int = 50
    ) -> List[Any]:
        """Process items in batches with concurrency control"""
        if not items:
            return []
        
        results = []
        
        # Process in chunks
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Process batch items concurrently
            async def process_with_semaphore(item):
                async with self.semaphore:
                    return await processor(item)
            
            batch_results = await asyncio.gather(
                *[process_with_semaphore(item) for item in batch],
                return_exceptions=True
            )
            
            # Handle exceptions and collect results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                    results.append(None)  # or handle as needed
                else:
                    results.append(result)
        
        return results


# Global instances
parallel_processor = ParallelProcessor(max_workers=20)
batch_processor = AsyncBatchProcessor(max_concurrent=15)

# Cleanup function for graceful shutdown
def cleanup_parallel_processing():
    """Cleanup parallel processing resources"""
    parallel_processor.cleanup()
    logger.info("Parallel processing resources cleaned up")


# Performance monitoring utilities
class PerformanceTracker:
    """Track performance metrics for operations"""
    
    def __init__(self):
        self.metrics = {}
        self._lock = threading.Lock()
    
    def record_operation(self, operation_name: str, duration: float, success: bool = True):
        """Record operation metrics"""
        with self._lock:
            if operation_name not in self.metrics:
                self.metrics[operation_name] = {
                    'total_calls': 0,
                    'total_duration': 0.0,
                    'success_count': 0,
                    'failure_count': 0,
                    'avg_duration': 0.0
                }
            
            metrics = self.metrics[operation_name]
            metrics['total_calls'] += 1
            metrics['total_duration'] += duration
            
            if success:
                metrics['success_count'] += 1
            else:
                metrics['failure_count'] += 1
            
            metrics['avg_duration'] = metrics['total_duration'] / metrics['total_calls']
    
    def get_metrics(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics"""
        with self._lock:
            if operation_name:
                return self.metrics.get(operation_name, {})
            return self.metrics.copy()


# Global performance tracker
performance_tracker = PerformanceTracker()
