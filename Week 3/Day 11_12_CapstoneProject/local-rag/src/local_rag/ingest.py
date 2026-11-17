
from pathlib import Path

from openai import OpenAI
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
BATCH_SIZE = 32

EMBEDDING_MODEL = "nomic-embed-text"

ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


def extract_pages(documents_dir: Path) -> list[dict]:
    """Extract text from PDF pages and preserve source metadata."""

    pages = []
    pdf_files = sorted(documents_dir.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {documents_dir}")

    for pdf_path in pdf_files:
        reader = PdfReader(pdf_path)

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text(extraction_mode="layout") or ""
            text = text.strip()

            if not text:
                continue

            pages.append({
                "text": text,
                "source": pdf_path.name,
                "page": page_number,
            })

    return pages


def split_pages(pages: list[dict]) -> list[dict]:
    """Split page text into overlapping chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk_index, chunk_text in enumerate(page_chunks):
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": page["source"],
                    "page": page["page"],
                    "chunk_index": chunk_index,
                },
            })

    return chunks


def create_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings locally using Ollama."""

    response = ollama_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    return [item.embedding for item in response.data]


def store_chunks(chunks: list[dict]) -> chromadb.Collection:
    """Generate embeddings and store chunks in persistent ChromaDB."""

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = chroma_client.get_or_create_collection(
        name="novatech_documents",
        metadata={"hnsw:space": "cosine"},
    )

    # Remove previous records so rerunning ingestion rebuilds the collection.
    existing = collection.get(include=[])
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]

        texts = [chunk["text"] for chunk in batch]
        embeddings = create_embeddings(texts)

        ids = [
            f"{chunk['metadata']['source']}_page_{chunk['metadata']['page']}_chunk_{chunk['metadata']['chunk_index']}"
            for chunk in batch
        ]

        metadatas = [chunk["metadata"] for chunk in batch]

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"Stored {min(start + BATCH_SIZE, len(chunks))}/{len(chunks)} chunks")

    return collection


def main() -> None:
    pages = extract_pages(DOCUMENTS_DIR)
    chunks = split_pages(pages)

    print(f"PDF files found: {len(list(DOCUMENTS_DIR.glob('*.pdf')))}")
    print(f"Pages extracted: {len(pages)}")
    print(f"Chunks created: {len(chunks)}")

    collection = store_chunks(chunks)

    print("\nIngestion completed.")
    print(f"ChromaDB location: {CHROMA_DIR}")
    print(f"Collection: {collection.name}")
    print(f"Stored documents: {collection.count()}")


if __name__ == "__main__":
    main()
