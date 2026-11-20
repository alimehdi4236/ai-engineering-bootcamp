
import argparse
import json
import time
from pathlib import Path

from local_rag.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parent
QUESTIONS_FILE = PROJECT_ROOT / "test_questions.json"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the NovaTech RAG pipeline over the test questions."
    )

    parser.add_argument(
        "--output",
        default="pipeline_outputs.json",
        help="Output JSON filename (default: pipeline_outputs.json)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of questions to run")

    args = parser.parse_args()
    output_file = PROJECT_ROOT / args.output

    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(
            f"Test questions file not found: {QUESTIONS_FILE}"
        )

    with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    questions = dataset["questions"]
    if args.limit:
        questions = questions[:args.limit]
    results = []

    print(f"Starting RAG evaluation: {len(questions)} questions")
    print(f"Output file: {output_file.name}")

    for index, item in enumerate(questions, start=1):
        question = item["question"]

        print(f"\n[{index}/{len(questions)}] {item['id']}: {question}")

        start_time = time.perf_counter()

        try:
            pipeline_result = run_pipeline(question)
            elapsed = time.perf_counter() - start_time

            generation_time_seconds = pipeline_result[
                "generation_time_seconds"
            ]

            result = {
                **item,

                # Fields required by DeepEval
                "actual_answer": pipeline_result["answer"],
                "retrieved_context": pipeline_result["retrieved_context"],

                # Additional pipeline information
                "generated_answer": pipeline_result["answer"],
                "retrieved_sources": pipeline_result["sources"],
                "model": pipeline_result["model"],
                "thinking": pipeline_result["thinking"],
                "finish_reason": pipeline_result["finish_reason"],

                # Timing and token information
                "time_seconds": round(elapsed, 2),
                "retrieval_time_seconds": pipeline_result[
                    "retrieval_time_seconds"
                ],
                "generation_time_seconds": generation_time_seconds,
                "generation_time_ms": round(
                    generation_time_seconds * 1000, 2
                ),
                "prompt_tokens": pipeline_result["prompt_tokens"],
                "completion_tokens": pipeline_result["completion_tokens"],

                "status": "success",
            }

        except Exception as error:
            elapsed = time.perf_counter() - start_time

            result = {
                **item,
                "actual_answer": "",
                "retrieved_context": [],
                "generated_answer": "",
                "retrieved_sources": [],
                "model": None,
                "thinking": None,
                "finish_reason": "error",
                "time_seconds": round(elapsed, 2),
                "retrieval_time_seconds": None,
                "generation_time_seconds": None,
                "generation_time_ms": None,
                "prompt_tokens": None,
                "completion_tokens": None,
                "status": "error",
                "error": str(error),
            }

        results.append(result)

        print(f"Status: {result['status']}")
        print(f"Time: {result['time_seconds']} seconds")

    successful_runs = sum(
        result["status"] == "success" for result in results
    )

    failed_runs = sum(
        result["status"] == "error" for result in results
    )

    # DeepEval expects a list of question records.
    with output_file.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    print("\nEvaluation completed.")
    print(f"Results saved to: {output_file}")
    print(f"Successful runs: {successful_runs}")
    print(f"Failed runs: {failed_runs}")


if __name__ == "__main__":
    main()
