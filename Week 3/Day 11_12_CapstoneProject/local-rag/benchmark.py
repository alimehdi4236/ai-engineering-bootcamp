
import json
import time
from datetime import datetime, timezone

from openai import OpenAI

# Models specified in the capstone brief
MODELS = [
    "qwen3.5:4b-q4_K_M",
    "qwen3.5:2b-q4_K_M",
]

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
REASONING_EFFORT = "none"

# Six prompts covering the required capabilities
PROMPTS = [
    {
        "category": "factual",
        "prompt": (
            "What causes tides on Earth? "
            "Answer in 2-3 sentences."
        ),
    },
    {
        "category": "reasoning",
        "prompt": (
            "A train travels 120 km in 1.5 hours, "
            "then 80 km in 1 hour. "
            "Calculate its average speed for the entire journey. "
            "Show the calculation."
        ),
    },
    {
        "category": "summarization",
        "prompt": (
            "Summarize the following paragraph in exactly "
            "three bullet points:\n\n"
            "A small technology company migrated its customer "
            "support platform to a new infrastructure. During "
            "the first month, response times improved by 20%, "
            "but the migration also introduced temporary login "
            "problems. The engineering team resolved most issues "
            "within two weeks. The company plans to continue "
            "monitoring system reliability before expanding "
            "the migration to other departments."
        ),
    },
    {
        "category": "structured",
        "prompt": (
            'List three European capitals. Respond ONLY with '
            'valid JSON using this structure: '
            '[{"city": "name", "country": "name"}]. '
            "Do not include Markdown or explanations."
        ),
    },
    {
        "category": "code_generation",
        "prompt": (
            "Write a Python function called count_words(text) "
            "that returns the number of words in a string. "
            "Handle an empty string. Include one example call."
        ),
    },
    {
        "category": "instruction_following",
        "prompt": (
            "Explain what an API is. Use exactly three numbered "
            "points. Each point must contain exactly one sentence. "
            "Do not write an introduction or conclusion."
        ),
    },
]


def run_benchmark(model: str, prompt_item: dict) -> dict:
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        timeout=300.0,
    )

    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt_item["prompt"],
            }
        ],
        temperature=0.7,
        reasoning_effort=REASONING_EFFORT,
        max_tokens=1024,
    )

    elapsed = time.perf_counter() - start_time

    choice = response.choices[0]
    usage = response.usage

    completion_tokens = (
        usage.completion_tokens if usage else None
    )

    tokens_per_second = (
        round(completion_tokens / elapsed, 2)
        if completion_tokens is not None and elapsed > 0
        else None
    )

    answer = choice.message.content or ""

    if not answer.strip():
        print(
            f"WARNING: Empty response from {model} "
            f"for category {prompt_item['category']}. "
            f"finish_reason={choice.finish_reason}"
        )

    return {
        "model": model,
        "category": prompt_item["category"],
        "prompt": prompt_item["prompt"],
        "response": answer,
        "thinking": REASONING_EFFORT != "none",
        "reasoning_effort": REASONING_EFFORT,
        "finish_reason": choice.finish_reason,
        "time_seconds": round(elapsed, 2),
        "prompt_tokens": (
            usage.prompt_tokens if usage else None
        ),
        "completion_tokens": completion_tokens,
        "tokens_per_second": tokens_per_second,
        "quality_rating": None,
        "rating_note": "",
    }


def main():
    results = []

    total_runs = len(MODELS) * len(PROMPTS)
    current_run = 0

    print(f"Starting benchmark: {total_runs} model-prompt runs")

    for model in MODELS:
        print(f"\nTesting model: {model}")

        for prompt_item in PROMPTS:
            current_run += 1

            print(
                f"[{current_run}/{total_runs}] "
                f"{prompt_item['category']}..."
            )

            try:
                result = run_benchmark(model, prompt_item)
                results.append(result)

                print(
                    f"Finished in {result['time_seconds']}s | "
                    f"{result['tokens_per_second']} tokens/s | "
                    f"finish={result['finish_reason']}"
                )

            except Exception as error:
                print(
                    f"ERROR: {model} / "
                    f"{prompt_item['category']}: {error}"
                )

                results.append({
                    "model": model,
                    "category": prompt_item["category"],
                    "prompt": prompt_item["prompt"],
                    "response": "",
                    "thinking": False,
                    "reasoning_effort": REASONING_EFFORT,
                    "finish_reason": "error",
                    "time_seconds": None,
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "tokens_per_second": None,
                    "quality_rating": None,
                    "rating_note": f"Execution error: {error}",
                })

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reasoning_effort": REASONING_EFFORT,
        "models": MODELS,
        "prompt_count": len(PROMPTS),
        "results": results,
    }

    with open(
        "benchmark_results.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print("\nBenchmark completed.")
    print(f"Saved {len(results)} results to benchmark_results.json")


if __name__ == "__main__":
    main()
