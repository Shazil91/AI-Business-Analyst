import asyncio

from app.agents.executor import Executor


async def main():

    executor = Executor()

    result = await executor.run(
        "rag",
        "search_documents",
        query=(
            "Compare Product F using the quarterly sales report, "
            "product performance report, and company strategy."
        ),
        limit=10,
    )

    print("=" * 80)
    print("EXECUTOR → RAG TEST")
    print("=" * 80)

    print("Success:", result.get("success"))
    print("Count:", result.get("count"))
    print("Sources:", result.get("sources"))

    for item in result.get("results", []):
        print()
        print("FILE:", item.get("filename"))
        print("SCORE:", item.get("score"))
        print("TEXT:", item.get("text"))


if __name__ == "__main__":
    asyncio.run(main())