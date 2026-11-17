
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


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


def main() -> None:
    pages = extract_pages(DOCUMENTS_DIR)
    chunks = split_pages(pages)

    print(f"PDF files found: {len(list(DOCUMENTS_DIR.glob('*.pdf')))}")
    print(f"Pages extracted: {len(pages)}")
    print(f"Chunks created: {len(chunks)}")

    for chunk in chunks[:3]:
        print("\n" + "=" * 80)
        print(f"Source: {chunk['metadata']['source']}")
        print(f"Page: {chunk['metadata']['page']}")
        print(f"Chunk: {chunk['metadata']['chunk_index']}")
        print(chunk["text"][:500])


if __name__ == "__main__":
    main()
