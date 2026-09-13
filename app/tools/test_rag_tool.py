import asyncio

from app.tools.rag_tools import RAGTools


async def main():

    rag = RAGTools()

    query = "What information is available about customers?"

    print("Searching Qdrant...")
    print("Query:", query)

    result = await rag.search_documents(
        query=query,
        limit=5,
    )

    print("\nRESULT")
    print("======")

    for item in result["results"]:

        print("\nScore:", item["score"])
        print("Source:", item["payload"].get("source"))
        print("Filename:", item["payload"].get("filename"))
        print("Page:", item["payload"].get("page_number"))
        print("Row:", item["payload"].get("row_number"))
        print("Text:", item["payload"].get("text"))


if __name__ == "__main__":
    asyncio.run(main())