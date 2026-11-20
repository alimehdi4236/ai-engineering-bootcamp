
"""
Runs five DeepEval RAG metrics over pipeline_outputs_<label>.json
and writes eval_results_<label>.json.

Usage:
    python eval_pipeline.py local
    python eval_pipeline.py cloud

Required .env variables:
    JUDGE_BASE_URL
    OPENAI_API_KEY (or AZURE_OPENAI_API_KEY)

Optional:
    JUDGE_MODEL (default: gpt-5.4-mini)
    EVAL_CONCURRENCY (default: 2)
"""

import sys
import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Project directory and environment configuration.
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

# Allow Python to find DeepEval installed in this project folder.
DEEPEVAL_DIR = PROJECT_DIR / "_deepeval_packages"
sys.path.insert(0, str(DEEPEVAL_DIR))

# DeepEval retry and telemetry settings.
os.environ.setdefault("DEEPEVAL_RETRY_MAX_ATTEMPTS", "6")
os.environ.setdefault("DEEPEVAL_RETRY_CAP_SECONDS", "30")
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")

from deepeval import evaluate
from deepeval.evaluate import AsyncConfig, DisplayConfig, ErrorConfig
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.models import OpenAIModel
from deepeval.test_case import LLMTestCase


JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gpt-5.4-mini")


def make_judge():
    """Create the Azure OpenAI judge model."""

    base_url = os.environ.get("JUDGE_BASE_URL")

    api_key = (
        os.environ.get("AZURE_OPENAI_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )

    if not base_url:
        raise ValueError(
            "Missing JUDGE_BASE_URL. Check your .env file."
        )

    if not api_key:
        raise ValueError(
            "Missing OPENAI_API_KEY or AZURE_OPENAI_API_KEY. "
            "Check your .env file."
        )

    extra = (
        {}
        if JUDGE_MODEL.startswith("gpt-4")
        else {"reasoning_effort": "low"}
    )

    return OpenAIModel(
        model=JUDGE_MODEL,
        base_url=base_url,
        api_key=api_key,
        generation_kwargs=extra,
    )


def load_pipeline_results(label):
    filename = f"pipeline_outputs_{label}.json"

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Accept either a top-level list or an object containing "results".
    if isinstance(data, list):
        rows = data

    elif isinstance(data, dict) and isinstance(data.get("results"), list):
        rows = data["results"]

    else:
        raise ValueError(
            "Unexpected JSON structure: expected a list "
            "or an object containing 'results'."
        )

    if not rows:
        raise ValueError(f"No evaluation results found in {filename}")

    print(f"Loaded {len(rows)} questions from {filename}")

    return rows


def build_test_cases(rows):
    """Convert pipeline results into DeepEval test cases."""

    test_cases = []

    for row in rows:
        context = row["retrieved_context"]

        if not isinstance(context, list):
            raise ValueError(
                f"Retrieved context for {row['id']} must be a list."
            )

        test_case = LLMTestCase(
            name=row["id"],
            input=row["question"],
            actual_output=row["generated_answer"],
            expected_output=row["expected_answer"],
            retrieval_context=context,
        )

        test_cases.append(test_case)

    return test_cases


def main(label="local"):

    print(f"\nStarting DeepEval evaluation: {label}")

    # 1. Load Day 11 pipeline results.
    rows = load_pipeline_results(label)
    print(f"Loaded {len(rows)} questions.")

    # 2. Convert results into DeepEval test cases.
    test_cases = build_test_cases(rows)
    print("DeepEval test cases created.")

    # 3. Create the judge.
    judge = make_judge()
    print(f"Judge model: {judge.get_model_name()}")

    # 4. Configure the five required RAG metrics.
    metrics = [
        FaithfulnessMetric(
            threshold=0.7,
            model=judge,
            penalize_ambiguous_claims=True,
        ),
        AnswerRelevancyMetric(
            threshold=0.7,
            model=judge,
        ),
        ContextualRelevancyMetric(
            threshold=0.7,
            model=judge,
        ),
        ContextualRecallMetric(
            threshold=0.7,
            model=judge,
        ),
        ContextualPrecisionMetric(
            threshold=0.7,
            model=judge,
        ),
    ]

    # 5. Run evaluation.
    result = evaluate(
        test_cases,
        metrics,
        async_config=AsyncConfig(
            max_concurrent=int(
                os.environ.get("EVAL_CONCURRENCY", "2")
            )
        ),
        error_config=ErrorConfig(ignore_errors=True),
        display_config=DisplayConfig(print_results=False),
    )

    # 6. Match DeepEval results with original pipeline results.
    by_id = {row["id"]: row for row in rows}

    output_rows = []

    for test_result in result.test_results:

        original = by_id[test_result.name]

        # Convert Day 11 seconds into milliseconds.
        seconds = original.get("time_seconds")

        generation_time_ms = (
            round(seconds * 1000, 2)
            if isinstance(seconds, (int, float))
            else None
        )

        metrics_output = {}

        for metric in test_result.metrics_data or []:
            metrics_output[metric.name] = {
                "score": metric.score,
                "success": metric.success,
                "reason": metric.reason,
                "error": metric.error,
            }

        output_rows.append({
            "id": test_result.name,
            "question": original["question"],
            "model": original.get("model"),
            "generation_time_ms": generation_time_ms,
            "judge": judge.get_model_name(),
            "metrics": metrics_output,
        })

    # 7. Save evaluation results.
    output_file = PROJECT_DIR / f"eval_results_{label}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            output_rows,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # 8. Count metric errors.
    error_count = sum(
        1
        for row in output_rows
        for metric in row["metrics"].values()
        if metric["error"]
    )

    print("\nEvaluation completed.")
    print(f"Questions evaluated: {len(output_rows)}")
    print(f"Metric errors: {error_count}")
    print(f"Results saved to: {output_file.name}")


if __name__ == "__main__":

    selected_label = (
        sys.argv[1] if len(sys.argv) > 1 else "local"
    )

    if selected_label not in ("local", "cloud"):
        raise ValueError(
            "Label must be either 'local' or 'cloud'."
        )

    main(selected_label)
