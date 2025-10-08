"""
Batch processing system with Redis queue for large-scale document processing
"""

from typing import List, Dict, Optional, Callable
import asyncio
from datetime import datetime
import uuid
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchProcessor:
    """
    Queue-based batch processor for FRA documents
    Uses Redis for job queue and status tracking
    """
    
    def __init__(self, redis_client=None, max_workers: int = 3):
        """
        Initialize batch processor
        
        Args:
            redis_client: Redis client instance (optional for in-memory mode)
            max_workers: Number of parallel processing workers
        """
        self.redis = redis_client
        self.max_workers = max_workers
        self.jobs = {}  # In-memory fallback if no Redis
        self.use_redis = redis_client is not None
        
        if self.use_redis:
            logger.info(f"Batch processor initialized with Redis (workers: {max_workers})")
        else:
            logger.warning("Running in in-memory mode (no Redis). Jobs won't persist across restarts.")
    
    async def create_batch_job(
        self, 
        documents: List[Dict],
        job_type: str = "document_ocr",
        priority: int = 5,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create a new batch processing job
        
        Args:
            documents: List of document metadata (file_path, document_id, etc.)
            job_type: Type of processing (document_ocr, entity_extraction, etc.)
            priority: Job priority (1-10, higher = more important)
            callback_url: Optional webhook URL for completion notification
            metadata: Additional metadata
        
        Returns:
            batch_id: Unique identifier for the batch job
        """
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        
        job_data = {
            "batch_id": batch_id,
            "job_type": job_type,
            "status": JobStatus.PENDING,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
            "total_documents": len(documents),
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "documents": documents,
            "callback_url": callback_url,
            "metadata": metadata or {},
            "results": [],
            "errors": []
        }
        
        if self.use_redis:
            # Store in Redis with TTL (7 days)
            await self._redis_set(f"batch:{batch_id}", job_data, expire=604800)
            # Add to priority queue
            await self._redis_zadd("batch:queue", {batch_id: priority})
        else:
            # Store in memory
            self.jobs[batch_id] = job_data
        
        logger.info(f"Created batch job {batch_id} with {len(documents)} documents")
        return batch_id
    
    async def get_job_status(self, batch_id: str) -> Optional[Dict]:
        """Get current status of a batch job"""
        if self.use_redis:
            job_data = await self._redis_get(f"batch:{batch_id}")
        else:
            job_data = self.jobs.get(batch_id)
        
        if not job_data:
            return None
        
        # Calculate progress percentage
        progress = 0
        if job_data['total_documents'] > 0:
            progress = (job_data['processed'] / job_data['total_documents']) * 100
        
        return {
            "batch_id": batch_id,
            "status": job_data['status'],
            "progress": round(progress, 2),
            "total_documents": job_data['total_documents'],
            "processed": job_data['processed'],
            "successful": job_data['successful'],
            "failed": job_data['failed'],
            "created_at": job_data['created_at'],
            "started_at": job_data.get('started_at'),
            "completed_at": job_data.get('completed_at'),
            "metadata": job_data.get('metadata', {})
        }
    
    async def get_job_results(self, batch_id: str, limit: int = 100, offset: int = 0) -> Optional[Dict]:
        """Get detailed results of a batch job"""
        if self.use_redis:
            job_data = await self._redis_get(f"batch:{batch_id}")
        else:
            job_data = self.jobs.get(batch_id)
        
        if not job_data:
            return None
        
        results = job_data.get('results', [])
        errors = job_data.get('errors', [])
        
        return {
            "batch_id": batch_id,
            "status": job_data['status'],
            "results": results[offset:offset + limit],
            "errors": errors[offset:offset + limit],
            "total_results": len(results),
            "total_errors": len(errors)
        }
    
    async def process_batch(
        self, 
        batch_id: str,
        processor_func: Callable,
        **processor_kwargs
    ) -> Dict:
        """
        Process a batch job using the provided processor function
        
        Args:
            batch_id: Batch job identifier
            processor_func: Async function to process each document
            processor_kwargs: Additional arguments for processor function
        
        Returns:
            Final job status
        """
        # Get job data
        if self.use_redis:
            job_data = await self._redis_get(f"batch:{batch_id}")
        else:
            job_data = self.jobs.get(batch_id)
        
        if not job_data:
            raise ValueError(f"Batch job {batch_id} not found")
        
        if job_data['status'] != JobStatus.PENDING:
            raise ValueError(f"Batch job {batch_id} is not in pending state")
        
        # Update status to processing
        job_data['status'] = JobStatus.PROCESSING
        job_data['started_at'] = datetime.utcnow().isoformat()
        await self._update_job(batch_id, job_data)
        
        logger.info(f"Starting batch processing for {batch_id}")
        
        # Process documents in parallel with worker pool
        documents = job_data['documents']
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_with_semaphore(doc, index):
            async with semaphore:
                try:
                    result = await processor_func(doc, **processor_kwargs)
                    
                    # Update job progress
                    job_data['processed'] += 1
                    job_data['successful'] += 1
                    job_data['results'].append({
                        "document_id": doc.get('document_id', f"doc_{index}"),
                        "status": "success",
                        "result": result,
                        "processed_at": datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing document {index}: {str(e)}")
                    
                    job_data['processed'] += 1
                    job_data['failed'] += 1
                    job_data['errors'].append({
                        "document_id": doc.get('document_id', f"doc_{index}"),
                        "error": str(e),
                        "failed_at": datetime.utcnow().isoformat()
                    })
                
                # Update job status every 10 documents
                if job_data['processed'] % 10 == 0:
                    await self._update_job(batch_id, job_data)
                    logger.info(f"Batch {batch_id}: {job_data['processed']}/{job_data['total_documents']} processed")
        
        # Process all documents
        tasks = [process_with_semaphore(doc, i) for i, doc in enumerate(documents)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Mark as completed
        job_data['status'] = JobStatus.COMPLETED
        job_data['completed_at'] = datetime.utcnow().isoformat()
        await self._update_job(batch_id, job_data)
        
        logger.info(f"Batch {batch_id} completed: {job_data['successful']} successful, {job_data['failed']} failed")
        
        # Send callback if provided
        if job_data.get('callback_url'):
            await self._send_callback(job_data['callback_url'], job_data)
        
        return await self.get_job_status(batch_id)
    
    async def cancel_job(self, batch_id: str) -> bool:
        """Cancel a pending or processing job"""
        if self.use_redis:
            job_data = await self._redis_get(f"batch:{batch_id}")
        else:
            job_data = self.jobs.get(batch_id)
        
        if not job_data:
            return False
        
        if job_data['status'] in [JobStatus.COMPLETED, JobStatus.FAILED]:
            return False
        
        job_data['status'] = JobStatus.CANCELLED
        job_data['cancelled_at'] = datetime.utcnow().isoformat()
        await self._update_job(batch_id, job_data)
        
        logger.info(f"Batch job {batch_id} cancelled")
        return True
    
    async def list_jobs(
        self, 
        status: Optional[JobStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """List batch jobs with optional status filter"""
        if self.use_redis:
            # Get all batch job IDs from Redis
            keys = await self._redis_keys("batch:batch_*")
            jobs = []
            for key in keys[offset:offset + limit]:
                job_data = await self._redis_get(key.replace("batch:", ""))
                if job_data and (not status or job_data['status'] == status):
                    jobs.append(await self.get_job_status(job_data['batch_id']))
        else:
            # Filter from in-memory jobs
            jobs = []
            for job_data in list(self.jobs.values())[offset:offset + limit]:
                if not status or job_data['status'] == status:
                    jobs.append(await self.get_job_status(job_data['batch_id']))
        
        return jobs
    
    # Helper methods
    async def _update_job(self, batch_id: str, job_data: Dict):
        """Update job data in storage"""
        if self.use_redis:
            await self._redis_set(f"batch:{batch_id}", job_data)
        else:
            self.jobs[batch_id] = job_data
    
    async def _send_callback(self, callback_url: str, job_data: Dict):
        """Send completion webhook"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    callback_url,
                    json={
                        "batch_id": job_data['batch_id'],
                        "status": job_data['status'],
                        "total_documents": job_data['total_documents'],
                        "successful": job_data['successful'],
                        "failed": job_data['failed'],
                        "completed_at": job_data.get('completed_at')
                    },
                    timeout=10.0
                )
                logger.info(f"Callback sent to {callback_url}")
        except Exception as e:
            logger.error(f"Failed to send callback: {str(e)}")
    
    # Redis helper methods
    async def _redis_set(self, key: str, value: Dict, expire: int = None):
        """Set value in Redis"""
        await self.redis.set(key, json.dumps(value))
        if expire:
            await self.redis.expire(key, expire)
    
    async def _redis_get(self, key: str) -> Optional[Dict]:
        """Get value from Redis"""
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def _redis_zadd(self, key: str, mapping: Dict):
        """Add to sorted set"""
        await self.redis.zadd(key, mapping)
    
    async def _redis_keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern"""
        return await self.redis.keys(pattern)


# Simple in-memory queue for basic usage (no Redis required)
class SimpleQueue:
    """In-memory queue for development/testing without Redis"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.jobs = {}
    
    async def enqueue(self, job_id: str, job_data: Dict):
        """Add job to queue"""
        self.jobs[job_id] = job_data
        await self.queue.put(job_id)
    
    async def dequeue(self) -> Optional[str]:
        """Get next job from queue"""
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job data"""
        return self.jobs.get(job_id)
