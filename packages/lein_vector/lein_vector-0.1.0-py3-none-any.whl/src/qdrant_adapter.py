from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import MatchText
from qdrant_client.models import (
    PointStruct, Filter, FieldCondition, MatchValue, Range,
    VectorParams, Distance
)
from src.schemas.chunk import ChunkPayload
from typing import List, Dict, Any
from uuid import UUID


class QdrantAdapter:
    def __init__(self, host: str, port: int, collection: str, vector_size: int):
        self.collection = collection
        self.client = AsyncQdrantClient(host=host, port=port)
        self.vector_size = vector_size

    async def init_collection(self):
        exists = await self.client.collection_exists(self.collection)
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )

    async def upsert(self, point_id: UUID, embedding: List[float], payload: ChunkPayload) -> None:
        await self.client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=str(point_id),
                    vector=embedding,
                    payload=payload.model_dump()
                )
            ]
        )

    async def upsert_batch(self, points: List[Dict[str, Any]]) -> None:
        structs = [
            PointStruct(
                id=str(point["point_id"]),
                vector=point["embedding"],
                payload=point["payload"].dict()
            )
            for point in points
        ]
        await self.client.upsert(collection_name=self.collection, points=structs)

    async def search(self, embedding: List[float], filter_: Dict[str, Any], topk: int) -> List[ChunkPayload]:
        # Пример фильтра {"user_id": 123, "chunk_type": "type1", "created_at_gt": "2024-01-01T00:00:00"}
        conditions = []
        for k, v in filter_.items():
            if k.endswith("_gt"):
                field = k[:-3]
                conditions.append(FieldCondition(key=field, range=Range(gt=v)))
            elif k.endswith("_lt"):
                field = k[:-3]
                conditions.append(FieldCondition(key=field, range=Range(lt=v)))
            else:
                if isinstance(v, str):
                    conditions.append(FieldCondition(key=k, match=MatchText(text=v)))
                else:
                    conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
        q_filter = Filter(must=conditions)
        result = await self.client.query_points(
            collection_name=self.collection,
            query=embedding,
            query_filter=q_filter,
            limit=topk,
        )
        points = result.points
        return [ChunkPayload(**point.payload) for point in points]

    async def delete(self, point_id: UUID) -> None:
        await self.client.delete(
            collection_name=self.collection,
            points_selector=[str(point_id)]
        )

    async def delete_batch(self, point_ids: List[UUID]) -> None:
        await self.client.delete(
            collection_name=self.collection,
            points_selector=[str(pid) for pid in point_ids]
        )

    async def delete_collection(self) -> None:
        await self.client.delete_collection(collection_name=self.collection)

    async def get_all_chunks(self, user_id: int) -> List[ChunkPayload]:
        q_filter = Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        )
        scroll = await self.client.scroll(
            collection_name=self.collection,
            scroll_filter=q_filter,
            limit=2048,
        )
        return [ChunkPayload(**p.payload) for p in scroll[0]]