import asyncio

from app.tools.rag_tools import RAGTools


async def main():

    # ---------------------------------------------------------
    # Create RAG tool
    # ---------------------------------------------------------

    rag = RAGTools()

    # ---------------------------------------------------------
    # Test query
    # ---------------------------------------------------------

    query = (
        "Compare Product F using the quarterly sales report, "
        "product performance report, and company strategy."
    )

    print()
    print("=" * 80)
    print("QDRANT SEARCH DEBUG")
    print("=" * 80)

    print()
    print("Query:")
    print(query)

    # ---------------------------------------------------------
    # Search documents
    # ---------------------------------------------------------

    result = await rag.search_documents(
        query=query,
        limit=10,
        score_threshold=None,
    )

    # ---------------------------------------------------------
    # Print complete response
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("SEARCH RESPONSE")
    print("=" * 80)

    print()
    print("Success:")
    print(result["success"])

    print()
    print("Total results:")
    print(result["count"])

    print()
    print("Sources:")
    
    for source in result["sources"]:
        print(f"  - {source}")

    # ---------------------------------------------------------
    # Print individual results
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("DOCUMENT RESULTS")
    print("=" * 80)

    for index, document in enumerate(
        result["results"],
        start=1,
    ):

        print()
        print(f"Result {index}")
        print("-" * 80)

        print(
            f"Score: {document['score']}"
        )

        print(
            f"File: {document['filename']}"
        )

        print(
            f"Page: {document['page_number']}"
        )

        print(
            f"Row: {document['row_number']}"
        )

        print(
            f"Source: {document['source']}"
        )

        print()
        print("Text:")

        print(
            document["text"]
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())