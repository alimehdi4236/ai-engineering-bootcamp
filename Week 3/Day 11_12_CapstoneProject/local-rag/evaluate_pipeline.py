
import json
import time
from pathlib import Path

from local_rag.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parent
QUESTIONS_FILE = PROJECT_ROOT / "test_questions.json"
OUTPUT_FILE = PROJECT_ROOT / "pipeline_outputs.json"


def main() -> None:
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    results = []

    questions = dataset["questions"]

    print(f"Starting RAG evaluation: {len(questions)} questions")

    for index, item in enumerate(questions, start=1):
        question = item["question"]

        print(f"\n[{index}/{len(questions)}] {item['id']}: {question}")

        start_time = time.perf_counter()

        try:
            pipeline_result = run_pipeline(question)
            elapsed = time.perf_counter() - start_time

            result = {
                **item,
                "generated_answer": pipeline_result["answer"],
                "retrieved_sources": pipeline_result["sources"],
                "model": pipeline_result["model"],
                "thinking": pipeline_result["thinking"],
                "finish_reason": pipeline_result["finish_reason"],
                "time_seconds": round(elapsed, 2),
                "retrieval_time_seconds": pipeline_result["retrieval_time_seconds"],
                "generation_time_seconds": pipeline_result["generation_time_seconds"],
                "prompt_tokens": pipeline_result["prompt_tokens"],
                "completion_tokens": pipeline_result["completion_tokens"],
                "status": "success",
            }

        except Exception as error:
            elapsed = time.perf_counter() - start_time

            result = {
                **item,
                "generated_answer": None,
                "retrieved_sources": [],
                "model": None,
                "thinking": None,
                "finish_reason": "error",
                "time_seconds": round(elapsed, 2),
                "retrieval_time_seconds": None,
                "generation_time_seconds": None,
                "prompt_tokens": None,
                "completion_tokens": None,
                "status": "error",
                "error": str(error),
            }

        results.append(result)

        print(f"Status: {result['status']}")
        print(f"Time: {result['time_seconds']} seconds")

    output = {
        "dataset_name": dataset.get("dataset_name"),
        "total_questions": len(questions),
        "successful_runs": sum(
            result["status"] == "success" for result in results
        ),
        "failed_runs": sum(
            result["status"] == "error" for result in results
        ),
        "results": results,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print("\nEvaluation completed.")
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"Successful runs: {output['successful_runs']}")
    print(f"Failed runs: {output['failed_runs']}")


if __name__ == "__main__":
    main()
