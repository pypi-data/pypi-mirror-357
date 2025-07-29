"""Module providing stream worker functionality for parallel processing."""

import asyncio
import logging
import time
import uuid
import base64
from typing import Dict, Optional
from datetime import datetime, timezone
from matrice.deploy.utils.kafka_utils import MatriceKafkaDeployment
from matrice.deploy.server.inference.inference_interface import InferenceInterface


class StreamWorker:
    """Individual worker for processing stream messages in parallel."""
    
    def __init__(
        self,
        worker_id: str,
        session,
        deployment_id: str,
        deployment_instance_id: str,
        inference_interface: InferenceInterface,
        consumer_group_suffix: str = "",
    ):
        """Initialize stream worker.
        
        Args:
            worker_id: Unique identifier for this worker
            session: Session object for authentication and RPC
            deployment_id: ID of the deployment
            deployment_instance_id: ID of the deployment instance
            inference_interface: Inference interface to use for inference
            consumer_group_suffix: Optional suffix for consumer group ID
        """
        self.worker_id = worker_id
        self.session = session
        self.deployment_id = deployment_id
        self.deployment_instance_id = deployment_instance_id
        self.inference_interface = inference_interface
        
        # Kafka setup with unique consumer group for this worker
        consumer_group_id = f"{deployment_id}-worker-{worker_id}"
        if consumer_group_suffix:
            consumer_group_id += f"-{consumer_group_suffix}"
            
        self.kafka_deployment = MatriceKafkaDeployment(
            session,
            deployment_id,
            "server",
            consumer_group_id,
            f"{deployment_instance_id}-{worker_id}",
        )
        
        # Worker state
        self.is_running = False
        self.is_active = True
        
        # Processing control
        self._stop_event = asyncio.Event()
        self._processing_task: Optional[asyncio.Task] = None
        
        logging.info(f"Initialized StreamWorker: {worker_id}")
    
    async def start(self) -> None:
        """Start the worker."""
        if self.is_running:
            logging.warning(f"Worker {self.worker_id} is already running")
            return
        
        self.is_running = True
        self.is_active = True
        self._stop_event.clear()
        
        # Start the processing loop
        self._processing_task = asyncio.create_task(self._processing_loop())
        
        logging.info(f"Started StreamWorker: {self.worker_id}")
    
    async def stop(self) -> None:
        """Stop the worker."""
        if not self.is_running:
            return
        
        logging.info(f"Stopping StreamWorker: {self.worker_id}")
        
        self.is_running = False
        self.is_active = False
        self._stop_event.set()
        
        # Cancel and wait for processing task with timeout
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            try:
                # Wait for task cancellation with timeout
                await asyncio.wait_for(self._processing_task, timeout=5.0)
            except asyncio.CancelledError:
                logging.debug(f"Processing task for worker {self.worker_id} cancelled successfully")
            except asyncio.TimeoutError:
                logging.warning(f"Processing task for worker {self.worker_id} did not cancel within timeout")
            except Exception as exc:
                logging.error(f"Error while cancelling processing task for worker {self.worker_id}: {str(exc)}")
        
        # Close Kafka connections with proper error handling
        if self.kafka_deployment:
            try:
                logging.debug(f"Closing Kafka connections for worker {self.worker_id}")
                # Check if event loop is still running before attempting async close
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_closed():
                        logging.warning(f"Event loop closed, skipping Kafka close for worker {self.worker_id}")
                    else:
                        await self.kafka_deployment.close()
                        logging.debug(f"Kafka connections closed for worker {self.worker_id}")
                except RuntimeError:
                    logging.warning(f"No running event loop, skipping Kafka close for worker {self.worker_id}")
            except Exception as exc:
                logging.error(f"Error closing Kafka for worker {self.worker_id}: {str(exc)}")
        
        logging.info(f"Stopped StreamWorker: {self.worker_id}")
    
    async def _processing_loop(self) -> None:
        """Main processing loop for consuming and processing messages."""
        retry_delay = 1.0
        max_retry_delay = 30.0
        
        while self.is_running and not self._stop_event.is_set():
            try:
                # Consume message from Kafka
                message = await self.kafka_deployment.async_consume_message(timeout=1.0)
                
                if message:
                    await self._process_message(message)
                    retry_delay = 1.0  # Reset retry delay on success
                else:
                    # No message available, brief pause
                    await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logging.error(f"Error in processing loop for worker {self.worker_id}: {str(exc)}")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
        
        logging.debug(f"Processing loop ended for worker {self.worker_id}")
    
    def _extract_stream_key(self, message: Dict) -> str:
        """Extract stream key (camera_id/stream_id) from message for logging."""
        try:
            value = message.get("value", {})
            
            # Try different possible key fields for stream identification
            stream_key = (
                value.get("camera_id") or
                value.get("stream_id") or
                value.get("source_id") or
                value.get("key") or
                message.get("key")
            )
            
            if isinstance(stream_key, bytes):
                stream_key = stream_key.decode('utf-8')
            
            return str(stream_key) if stream_key else "default_stream"
                
        except Exception as exc:
            logging.error(f"Error extracting stream key: {str(exc)}")
            return "default_stream"
    
    async def _process_message(self, message: Dict) -> None:
        """Process a single message."""
        start_time = time.time()
        stream_key = self._extract_stream_key(message)
        
        try:
            # Process the message using the same logic as inference_interface
            processed_result = await self._process_kafka_message(message)
            
            # Produce result back to Kafka with stream key
            await self.kafka_deployment.async_produce_message(
                processed_result,
                key=stream_key
            )
            
            processing_time = time.time() - start_time
            
            logging.debug(f"Worker {self.worker_id} processed message for stream {stream_key} in {processing_time:.3f}s")
            
        except Exception as exc:
            logging.error(f"Worker {self.worker_id} failed to process message for stream {stream_key}: {str(exc)}")
    
    async def _process_kafka_message(self, message: Dict) -> Dict:
        """Process a message from Kafka (same logic as InferenceInterface).

        Args:
            message: Kafka message containing inference request

        Returns:
            Processed result

        Raises:
            ValueError: If message format is invalid
        """
        if not isinstance(message, dict):
            raise ValueError("Invalid message format: expected dictionary")

        # Extract stream key for logging and response
        stream_key = self._extract_stream_key(message)
        

        # Get the value and try to parse it if it's bytes
        value = message.get("value")
        if not value or not isinstance(value, dict):
            raise ValueError("Invalid message format: missing or invalid 'value' field")

        input_order = value.get("input_order")

        input_data = value.get("input")
        if not input_data:
            raise ValueError("Invalid message format: missing 'input' field")

        try:
            input_bytes = base64.b64decode(input_data)
        except Exception as exc:
            raise ValueError(f"Failed to decode base64 input: {str(exc)}")

        try:
            result, post_processing_result = await self.inference_interface.inference(
                input_bytes, 
                apply_post_processing=True
            )

            response = {
                **value,  # Include original request data
                "result": result,  # Add inference result
                "post_processing_result": post_processing_result,  # Add post-processing result
                "post_processing_applied": post_processing_result is not None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stream_key": stream_key,  # Include the stream key in response
                "worker_id": self.worker_id,  # Include worker ID for debugging
                "input_order": input_order,
            }
            return response
        except Exception as exc:
            error_response = {
                **value,
                "error": str(exc),
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stream_key": stream_key,
                "worker_id": self.worker_id,
                "input_order": input_order,
            }
            logging.error(f"Error processing Kafka message for stream {stream_key}: {str(exc)}")
            return error_response
    

class StreamWorkerManager:
    """Manages multiple stream workers for parallel processing."""
    
    def __init__(
        self,
        session,
        deployment_id: str,
        deployment_instance_id: str,
        inference_interface: InferenceInterface,
        num_workers: int = 1,
    ):
        """Initialize stream worker manager.
        
        Args:
            session: Session object for authentication and RPC
            deployment_id: ID of the deployment
            deployment_instance_id: ID of the deployment instance
            inference_interface: Inference interface to use for inference
            num_workers: Number of workers to create
        """
        self.session = session
        self.deployment_id = deployment_id
        self.deployment_instance_id = deployment_instance_id
        self.inference_interface = inference_interface
        self.num_workers = num_workers
        
        # Worker management
        self.workers: Dict[str, StreamWorker] = {}
        self.is_running = False
        
        logging.info(f"Initialized StreamWorkerManager with {num_workers} workers for deployment {deployment_id}")
    
    async def start(self) -> None:
        """Start all workers."""
        if self.is_running:
            logging.warning("StreamWorkerManager is already running")
            return
        
        self.is_running = True
        
        # Create and start workers with staggered delays to avoid race conditions
        for i in range(self.num_workers):
            worker_id = f"worker_{i}_{uuid.uuid4().hex[:8]}"
            worker = StreamWorker(
                worker_id=worker_id,
                session=self.session,
                deployment_id=self.deployment_id,
                deployment_instance_id=self.deployment_instance_id,
                inference_interface=self.inference_interface,
            )
            
            self.workers[worker_id] = worker
            
            # Start worker with error handling
            try:
                await worker.start()
                logging.info(f"Started worker {worker_id}")
                
                # Add staggered delay between worker startups to avoid race conditions
                if i < self.num_workers - 1:  # Don't delay after the last worker
                    await asyncio.sleep(2.0)  # 2 second delay between worker startups
                    
            except Exception as exc:
                logging.error(f"Failed to start worker {worker_id}: {str(exc)}")
                # Remove failed worker from workers dict
                del self.workers[worker_id]
        
        logging.info(f"Started StreamWorkerManager with {len(self.workers)} workers")
    
    async def stop(self) -> None:
        """Stop all workers."""
        if not self.is_running:
            return
        
        logging.info("Stopping StreamWorkerManager...")
        
        self.is_running = False
            
        # Stop all workers with timeout and error handling
        if self.workers:
            logging.info(f"Stopping {len(self.workers)} workers...")
            stop_tasks = []
            
            for worker_id, worker in self.workers.items():
                try:
                    stop_task = asyncio.create_task(worker.stop())
                    stop_tasks.append(stop_task)
                except Exception as exc:
                    logging.error(f"Error creating stop task for worker {worker_id}: {str(exc)}")
            
            # Wait for all workers to stop with timeout
            if stop_tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*stop_tasks, return_exceptions=True), 
                        timeout=30.0
                    )
                    logging.info("All workers stopped successfully")
                except asyncio.TimeoutError:
                    logging.warning("Some workers did not stop within timeout")
                    # Cancel remaining tasks
                    for task in stop_tasks:
                        if not task.done():
                            task.cancel()
                except Exception as exc:
                    logging.error(f"Error stopping workers: {str(exc)}")
        
        self.workers.clear()
        
        logging.info("Stopped StreamWorkerManager")
    
    async def add_worker(self) -> Optional[str]:
        """Add a new worker to the pool.
        
        Returns:
            Worker ID if successfully added, None otherwise
        """
        if not self.is_running:
            logging.warning("Cannot add worker: manager not running")
            return None
        
        worker_id = f"worker_{len(self.workers)}_{uuid.uuid4().hex[:8]}"
        worker = StreamWorker(
            worker_id=worker_id,
            session=self.session,
            deployment_id=self.deployment_id,
            deployment_instance_id=self.deployment_instance_id,
            inference_interface=self.inference_interface,
        )
        
        self.workers[worker_id] = worker
        await worker.start()
        
        logging.info(f"Added new worker: {worker_id}")
        return worker_id
    
    async def remove_worker(self, worker_id: str) -> bool:
        """Remove a worker from the pool.
        
        Args:
            worker_id: ID of the worker to remove
            
        Returns:
            True if successfully removed
        """
        if worker_id not in self.workers:
            return False
        
        worker = self.workers[worker_id]
        await worker.stop()
        del self.workers[worker_id]
        
        logging.info(f"Removed worker: {worker_id}")
        return True
    
    async def scale_workers(self, target_count: int) -> bool:
        """Scale workers to target count.
        
        Args:
            target_count: Target number of workers
            
        Returns:
            True if scaling was successful
        """
        if not self.is_running:
            logging.warning("Cannot scale workers: manager not running")
            return False
        
        current_count = len(self.workers)
        
        if target_count > current_count:
            # Scale up
            for _ in range(target_count - current_count):
                worker_id = await self.add_worker()
                if not worker_id:
                    logging.error("Failed to add worker during scale up")
                    return False
        
        elif target_count < current_count:
            # Scale down
            workers_to_remove = list(self.workers.keys())[:current_count - target_count]
            for worker_id in workers_to_remove:
                await self.remove_worker(worker_id)
        
        logging.info(f"Scaled workers from {current_count} to {target_count}")
        return True
