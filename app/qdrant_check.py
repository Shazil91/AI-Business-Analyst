import asyncio

from app.rag.qdrantdb import QdrantDB


async def main():

    qdrant = QdrantDB()

    print("\n===== QDRANT CONFIGURATION =====\n")

    print("Collection:")
    print(qdrant.COLLECTION_NAME)

    print("\nQdrant client:")
    print(qdrant.client)

    print("\n===== COLLECTIONS =====\n")

    collections = await qdrant.client.get_collections()

    for collection in collections.collections:
        print(collection.name)

    print("\n===== COLLECTION INFO =====\n")

    exists = await qdrant.client.collection_exists(
        collection_name=qdrant.COLLECTION_NAME
    )

    print("Collection exists:")
    print(exists)

    if exists:

        info = await qdrant.client.get_collection(
            collection_name=qdrant.COLLECTION_NAME
        )

        print("\nPoints count:")
        print(info.points_count)

        print("\nVectors:")
        print(info.config.params.vectors)

    await qdrant.close()


if __name__ == "__main__":
    asyncio.run(main())