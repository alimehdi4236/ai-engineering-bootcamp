
import json
from pathlib import Path

from local_rag.retrieve import retrieve


INPUT_FILE = Path("pipeline_outputs_local.json")


def main():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    results = data["results"]

    print(f"Preparing retrieval context for {len(results)} questions...")

    for index, row in enumerate(results, start=1):
        question = row["question"]

        # Reuse the existing retrieval pipeline; no LLM generation.
        chunks = retrieve(question)

        row["retrieved_context"] = [
            chunk["text"] for chunk in chunks
        ]

        row["reconstructed_context_sources"] = [
            {
                "source": chunk["metadata"]["source"],
                "page": chunk["metadata"]["page"],
                "distance": chunk["distance"],
            }
            for chunk in chunks
        ]

        row["retrieval_context_reconstructed"] = True

        print(
            f"[{index}/{len(results)}] {row['id']}: "
            f"{len(chunks)} chunks retrieved"
        )

    # Save only after all questions have been processed.
    with INPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print(f"\nUpdated: {INPUT_FILE}")
    print("Original answers and manual ratings preserved.")


if __name__ == "__main__":
    main()
