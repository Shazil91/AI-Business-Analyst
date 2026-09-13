import os
from typing import Any

from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)


load_dotenv()


class QdrantDB:

    COLLECTION_NAME = os.getenv(
        "QDRANT_COLLECTION_NAME",
        "business-analyst-mpnet",
    )

    VECTOR_SIZE = 768

    def __init__(self):

        url = os.getenv(
            "QDRANT_URL",
            "http://localhost:6333",
        )

        api_key = os.getenv("QDRANT_API_KEY")

        client_kwargs: dict[str, Any] = {
            "url": url,
        }

        if api_key:
            client_kwargs["api_key"] = api_key

        self.client = AsyncQdrantClient(
            **client_kwargs
        )

        self._initialized = False

    async def ensure_collection(self) -> None:

        if self._initialized:
            return

        exists = await self.client.collection_exists(
            collection_name=self.COLLECTION_NAME
        )

        if not exists:
            await self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

        self._initialized = True

    async def save(
        self,
        record_id: int | str,
        vector: list[float],
        payload: dict,
    ) -> bool:

        if len(vector) != self.VECTOR_SIZE:
            raise ValueError(
                f"Expected vector size "
                f"{self.VECTOR_SIZE}, "
                f"got {len(vector)}."
            )

        await self.ensure_collection()

        await self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                PointStruct(
                    id=record_id,
                    vector=vector,
                    payload=payload,
                )
            ],
            wait=True,
        )

        return True

    async def save_many(
        self,
        points: list[PointStruct],
    ) -> bool:

        if not points:
            return True

        await self.ensure_collection()

        await self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
            wait=True,
        )

        return True

    async def search(
        self,
        vector: list[float],
        limit: int = 5,
        score_threshold: float | None = None,
    ):

        if not 1 <= limit <= 100:
            raise ValueError(
                "limit must be between 1 and 100."
            )

        if len(vector) != self.VECTOR_SIZE:
            raise ValueError(
                f"Expected vector size "
                f"{self.VECTOR_SIZE}, "
                f"got {len(vector)}."
            )

        await self.ensure_collection()

        result = await self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )

        return result.points

    async def delete(
    self,
    point_id: int | str,
    ) -> bool:

     await self.ensure_collection()

     await self.client.delete(
        collection_name=self.COLLECTION_NAME,
        points_selector=[point_id],
        wait=True,
    )

     return True

    async def recreate_collection(self) -> None:

        if await self.client.collection_exists(
            collection_name=self.COLLECTION_NAME
        ):
            await self.client.delete_collection(
                collection_name=self.COLLECTION_NAME
            )

        await self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=self.VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        self._initialized = True

    async def close(self) -> None:
        await self.client.close()