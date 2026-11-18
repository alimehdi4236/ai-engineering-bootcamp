
from openai import OpenAI

from local_rag.retrieve import retrieve


GENERATION_MODEL = "qwen3.5:4b-q4_K_M"

ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


def generate_answer(question: str) -> dict:
    """Generate an answer grounded in retrieved document evidence."""

    chunks = retrieve(question)

    if not chunks:
        return {
            "question": question,
            "answer": "I could not find sufficient relevant evidence in the provided documents to answer this question.",
            "sources": [],
            "model": GENERATION_MODEL,
            "finish_reason": None,
        }

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]

        context_parts.append(
            f"[Source {index}: {metadata['source']}, "
            f"Page {metadata['page']}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    system_prompt = """
You are a document question-answering assistant.

Answer the user's question using ONLY the provided document evidence.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts or missing information.
3. If the evidence does not contain the answer, say that there is
   insufficient information in the provided documents.
4. Keep the answer clear and concise.
5. Cite sources using the exact PDF filename and page number,
   for example: (company_handbook.pdf, page 5).
6. Never use generic references such as "Source 1" or "Source 2".
7. Only cite sources that directly support the statement.
8. If different sources disagree, explain the disagreement.
"""

    user_prompt = f"""
DOCUMENT EVIDENCE:

{context}

USER QUESTION:
{question}

Provide an answer grounded in the evidence.
Include source document names and page numbers.
"""

    response = ollama_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    answer = response.choices[0].message.content

    sources = [
        {
            "source": chunk["metadata"]["source"],
            "page": chunk["metadata"]["page"],
            "distance": chunk["distance"],
        }
        for chunk in chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "model": GENERATION_MODEL,
        "finish_reason": response.choices[0].finish_reason,
    }


def main() -> None:
    question = input("Enter your question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    result = generate_answer(question)

    print("\nQuestion:", result["question"])
    print("\nAnswer:\n", result["answer"])
    print("\nSources:")

    for source in result["sources"]:
        print(
            f"- {source['source']}, "
            f"Page {source['page']}, "
            f"Distance: {source['distance']:.4f}"
        )

    print("\nModel:", result["model"])
    print("Finish reason:", result["finish_reason"])


if __name__ == "__main__":
    main()
