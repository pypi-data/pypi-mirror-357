# -*- coding: utf-8 -*-
# chuk_artifacts/batch.py
"""
Batch operations for multiple artifacts.
Now uses chuk_sessions for session management.
"""

from __future__ import annotations

import uuid, hashlib, json, logging, asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .store import ArtifactStore

from .exceptions import ArtifactStoreError, ProviderError, SessionError

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 900


class BatchOperations:
    """Handles batch operations for multiple artifacts."""

    def __init__(self, artifact_store: 'ArtifactStore'):
        self.artifact_store = artifact_store

    async def store_batch(
        self,
        items: List[Dict[str, Any]],
        session_id: str | None = None,
        ttl: int = _DEFAULT_TTL,
    ) -> List[str]:
        """Store multiple artifacts in a batch operation."""
        if self.artifact_store._closed:
            raise ArtifactStoreError("Store is closed")
        
        # Ensure session is allocated using chuk_sessions
        if session_id is None:
            session_id = await self.artifact_store._session_manager.allocate_session()
        else:
            session_id = await self.artifact_store._session_manager.allocate_session(session_id=session_id)
        
        artifact_ids = []
        failed_items = []
        
        for i, item in enumerate(items):
            try:
                artifact_id = uuid.uuid4().hex
                key = self.artifact_store.generate_artifact_key(session_id, artifact_id)
                
                # Store in object storage
                await self._store_with_retry(
                    item["data"], key, item["mime"], 
                    item.get("filename"), session_id
                )
                
                # Prepare metadata record
                record = {
                    "artifact_id": artifact_id,
                    "session_id": session_id,
                    "sandbox_id": self.artifact_store.sandbox_id,
                    "key": key,
                    "mime": item["mime"],
                    "summary": item["summary"],
                    "meta": item.get("meta", {}),
                    "filename": item.get("filename"),
                    "bytes": len(item["data"]),
                    "sha256": hashlib.sha256(item["data"]).hexdigest(),
                    "stored_at": datetime.utcnow().isoformat() + "Z",
                    "ttl": ttl,
                    "storage_provider": self.artifact_store._storage_provider_name,
                    "session_provider": self.artifact_store._session_provider_name,
                    "batch_operation": True,
                    "batch_index": i,
                }
                
                # Store metadata via session provider
                session_ctx_mgr = self.artifact_store._session_factory()
                async with session_ctx_mgr as session:
                    await session.setex(artifact_id, ttl, json.dumps(record))
                
                artifact_ids.append(artifact_id)
                
            except Exception as e:
                logger.error(f"Batch item {i} failed: {e}")
                failed_items.append(i)
                artifact_ids.append(None)  # Placeholder
        
        if failed_items:
            logger.warning(f"Batch operation completed with {len(failed_items)} failures")
        
        return artifact_ids

    async def _store_with_retry(self, data: bytes, key: str, mime: str, filename: str, session_id: str):
        """Store data with retry logic (copied from core for batch operations)."""
        last_exception = None
        
        for attempt in range(self.artifact_store.max_retries):
            try:
                storage_ctx_mgr = self.artifact_store._s3_factory()
                async with storage_ctx_mgr as s3:
                    await s3.put_object(
                        Bucket=self.artifact_store.bucket,
                        Key=key,
                        Body=data,
                        ContentType=mime,
                        Metadata={
                            "filename": filename or "", 
                            "session_id": session_id,
                            "sandbox_id": self.artifact_store.sandbox_id,
                        },
                    )
                return  # Success
                
            except Exception as e:
                last_exception = e
                if attempt < self.artifact_store.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Batch storage attempt {attempt + 1} failed, retrying in {wait_time}s",
                        extra={"error": str(e), "attempt": attempt + 1}
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {self.artifact_store.max_retries} batch storage attempts failed")
        
        raise last_exception