
from local_rag.generate import generate_answer


def run_pipeline(question: str) -> dict:
    """
    Execute the complete RAG workflow for one question.

    1. Retrieve relevant document chunks.
    2. Generate an answer using the retrieved evidence.
    3. Return the answer and its metadata.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    result = generate_answer(question.strip())

    return result


def main() -> None:
    print("NovaTech Local RAG Assistant")
    print("-" * 40)

    question = input("Enter your question: ").strip()

    try:
        result = run_pipeline(question)

        print("\nQuestion:")
        print(result["question"])

        print("\nAnswer:")
        print(result["answer"])

        print("\nSources:")

        if result["sources"]:
            for source in result["sources"]:
                print(
                    f"- {source['source']}, "
                    f"Page {source['page']}, "
                    f"Distance: {source['distance']:.4f}"
                )
        else:
            print("No supporting sources found.")

        print("\nModel:", result["model"])
        print("Finish reason:", result["finish_reason"])

    except ValueError as error:
        print("\nExecution Metrics:")
        print("Model:", result["model"])
        print("Thinking enabled:", result["thinking"])
        print("Retrieval time:", result["retrieval_time_seconds"], "seconds")
        print("Generation time:", result["generation_time_seconds"], "seconds")
        print("Prompt tokens:", result["prompt_tokens"])
        print("Completion tokens:", result["completion_tokens"])
        print("Finish reason:", result["finish_reason"])


if __name__ == "__main__":
    main()
