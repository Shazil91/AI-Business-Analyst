import asyncio

from app.ingestion.rag_ingestion import RAGIngestion


async def main():

    print("Starting RAG ingestion...")

    ingestion = RAGIngestion()

    result = await ingestion.run()

    print("\nRAG INGESTION RESULT")
    print("====================")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())