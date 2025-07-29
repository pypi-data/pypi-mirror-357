from datetime import datetime, UTC
from typing import List, Dict, Any
from uuid import UUID

from src.bases.memory_manager_abc import MemoryManagerABC
from src.schemas.chunk import Chunk, ChunkPayload

class MemoryManagerQdrant(MemoryManagerABC):
    def __init__(self, qdrant_adapter, embedding_provider, archive_storage=None):
        self.qdrant = qdrant_adapter
        self.embed = embedding_provider
        self.archive = archive_storage  # твой модуль S3/minio (интерфейс: save(user_id, List[ChunkPayload]), load(user_id) -> List[ChunkPayload])

    async def upsert_chunk(self, user_id: int, chunk: Chunk) -> None:
        embedding = await self.embed.get_embedding(chunk.text)
        await self.qdrant.upsert(chunk.chunk_id, embedding, chunk.to_payload())

    async def upsert_chunk_with_vector(
            self,
            user_id: int,
            chunk: Chunk,
            embedding: list[float]
    ) -> None:
        await self.qdrant.upsert(chunk.chunk_id, embedding, chunk.to_payload())

    async def upsert_chunks(self, user_id: int, chunks: List[Chunk]) -> None:
        texts = [c.text for c in chunks]
        embeddings = await self.embed.get_embeddings(texts)
        points = [
            {"point_id": c.chunk_id, "embedding": emb, "payload": c.to_payload()}
            for c, emb in zip(chunks, embeddings)
        ]
        await self.qdrant.upsert_batch(points)

    async def retrieve_by_embedding(self, user_id: int, embedding: List[float], topk: int = 3, filter_: Dict[str, Any] = None) -> List[ChunkPayload]:
        # Фильтр по user_id + кастомные условия
        filter_ = filter_ or {}
        filter_["user_id"] = user_id
        return await self.qdrant.search(embedding, filter_, topk)

    async def retrieve_by_type(self, user_id: int, chunk_type: str, topk: int = 3) -> List[ChunkPayload]:
        # Заглушка embedding (пустой вектор не сработает, нужно реальный запрос!):
        # Лучше использовать scroll по фильтру
        filter_ = {"user_id": user_id, "chunk_type": chunk_type}
        return await self.qdrant.get_all_chunks_with_filter(filter_)

    async def merge_old_chunks(self, user_id: int, chunk_type: str, n: int = 5) -> None:
        # 1. Получить n старых чанков нужного типа
        chunks = await self.qdrant.get_n_oldest_chunks(user_id, chunk_type, n)
        if len(chunks) < n:
            return
        # 2. Суммаризация (mock или через LLM)
        merged_text = " | ".join([c.text for c in chunks])
        from uuid import uuid4
        from datetime import datetime
        summary_chunk = Chunk(
            chunk_id=uuid4(),
            user_id=user_id,
            chunk_type=self._next_type(chunk_type),
            created_at=datetime.now(UTC),
            last_hit=datetime.now(UTC),
            hit_count=0,
            text=merged_text,
            persistent=False,
            summary_of=[c.chunk_id for c in chunks],
        )
        await self.upsert_chunk(user_id, summary_chunk)
        # 3. Удалить исходники
        await self.delete_chunks(user_id, [c.chunk_id for c in chunks])

    async def archive_user(self, user_id: int) -> None:
        all_chunks = await self.qdrant.get_all_chunks(user_id)
        await self.archive.save(user_id, all_chunks)
        await self.delete_all(user_id)

    async def restore_user(self, user_id: int) -> None:
        chunks = await self.archive.load(user_id)
        await self.upsert_chunks(
            user_id,
            [Chunk(**c.dict(), last_hit=datetime.now(UTC), hit_count=0) for c in chunks]
        )

    async def delete_chunk(self, user_id: int, chunk_id: UUID) -> None:
        await self.qdrant.delete(chunk_id)

    async def delete_chunks(self, user_id: int, chunk_ids: List[UUID]) -> None:
        await self.qdrant.delete_batch(chunk_ids)

    async def delete_all(self, user_id: int) -> None:
        all_chunks = await self.qdrant.get_all_chunks(user_id)
        await self.delete_chunks(user_id, [c.chunk_id for c in all_chunks])

    # Доп. методы поиска (по времени, hit_count, last_hit)
    async def retrieve_filtered(self, user_id: int, filter_: Dict[str, Any], topk: int = 10) -> List[ChunkPayload]:
        return await self.qdrant.get_all_chunks_with_filter({"user_id": user_id, **filter_}, topk=topk)

    def _next_type(self, chunk_type: str) -> str:
        # Логика типа next_type
        mapping = {"type0": "type1", "type1": "type2"}
        return mapping.get(chunk_type, "summary")
