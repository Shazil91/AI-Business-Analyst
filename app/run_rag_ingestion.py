import asyncio

from app.ingestion.rag_ingestion import RAGIngestion


async def main():

    ingestion = RAGIngestion()

    result = await ingestion.run()

    print("\n===== RAG INGESTION RESULT =====")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())