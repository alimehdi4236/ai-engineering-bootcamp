
from pathlib import Path

from openai import OpenAI
import chromadb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "novatech_documents"
EMBEDDING_MODEL = "nomic-embed-text"
TOP_K = 5
MAX_DISTANCE = 0.35


ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


def create_query_embedding(question: str) -> list[float]:
    """Convert a user question into an embedding."""

    response = ollama_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=question,
    )

    return response.data[0].embedding


def retrieve(question: str, top_k: int = TOP_K) -> list[dict]:
    """Find the most relevant document chunks."""

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )

    query_embedding = create_query_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved_chunks = []

    for i in range(len(results["ids"][0])):
        retrieved_chunks.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })

    return [
    chunk for chunk in retrieved_chunks
    if chunk["distance"] <= MAX_DISTANCE]


def main() -> None:
    question = input("Enter your question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    results = retrieve(question)

    print(f"\nQuestion: {question}")
    print(f"Retrieved chunks: {len(results)}")

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print("\n" + "=" * 80)
        print(f"Result: {index}")
        print(f"Source: {metadata['source']}")
        print(f"Page: {metadata['page']}")
        print(f"Distance: {result['distance']:.4f}")
        print(f"Text:\n{result['text']}")


if __name__ == "__main__":
    main()
