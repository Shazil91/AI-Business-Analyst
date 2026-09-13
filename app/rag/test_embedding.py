from app.rag.embedding import LocalEmbedding


def main():

    embedding = LocalEmbedding()

    text = """
    North region generated strong revenue from enterprise customers.
    """

    vector = embedding.create_embedding(text)

    print("Embedding created successfully")
    print("Vector dimensions:", len(vector))
    print("First 10 values:", vector[:10])


if __name__ == "__main__":
    main()
    