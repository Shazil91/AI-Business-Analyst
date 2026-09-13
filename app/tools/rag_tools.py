from collections import defaultdict

from app.rag.embedding import LocalEmbedding
from app.rag.qdrantdb import QdrantDB


class RAGTools:

    def __init__(self):
        self.embedding = LocalEmbedding()
        self.qdrant = QdrantDB()

    async def search_documents(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> dict:

        if not query or not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty.",
                "results": [],
            }

        if not 1 <= limit <= 20:
            return {
                "success": False,
                "error": "limit must be between 1 and 20.",
                "results": [],
            }

        # Convert the user's question into an embedding
        vector = self.embedding.create_embedding(
            query.strip()
        )

        # Search Qdrant
        results = await self.qdrant.search(
            vector=vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        documents = []

        for point in results:

            payload = point.payload or {}

            documents.append(
                {
                    "id": point.id,
                    "score": float(point.score),
                    "filename": payload.get("filename"),
                    "page_number": payload.get("page_number"),
                    "row_number": payload.get("row_number"),
                    "source": payload.get("source"),
                    "text": payload.get("text", ""),
                }
            )

        # Group results by source file
        grouped = defaultdict(list)

        for document in documents:
            filename = document.get("filename") or "unknown"
            grouped[filename].append(document)

        return {
            "success": True,
            "query": query.strip(),
            "count": len(documents),
            "sources": list(grouped.keys()),
            "results": documents,
            "grouped_results": dict(grouped),
}