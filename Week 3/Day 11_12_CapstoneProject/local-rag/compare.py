import json
import math
import statistics
from pathlib import Path

METRICS = [
    "Faithfulness",
    "Answer Relevancy",
    "Contextual Relevancy",
    "Contextual Recall",
    "Contextual Precision",
]

EVALUATION_FILES = {
    "local": "eval_results_local.json",
    "cloud": "eval_results_cloud.json",
}

PIPELINE_FILES = {
    "local": "pipeline_outputs_local.json",
    "cloud": "pipeline_outputs_cloud.json",
}


def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def load_rows(filename):
    data = load_json(filename)

    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict) and isinstance(data.get("results"), list):
        rows = data["results"]
    else:
        raise ValueError(f"Unexpected JSON structure in {filename}")

    if not rows:
        raise ValueError(f"No records found in {filename}")

    return rows


def mean_and_margin(values):
    """Return mean and approximate 95% margin (mean ± 2 SE)."""
    if not values:
        return None, None

    mean = statistics.mean(values)

    if len(values) < 2:
        return mean, 0.0

    standard_error = statistics.stdev(values) / math.sqrt(len(values))
    return mean, 2 * standard_error


def format_interval(mean, margin):
    if mean is None:
        return "N/A"

    return f"{mean:.3f} ± {margin:.3f}"


def get_metric_rows(rows, metric):
    return {
        row["id"]: row["metrics"][metric]["score"]
        for row in rows
        if metric in row.get("metrics", {})
        and row["metrics"][metric].get("score") is not None
    }


def compare_metrics(local_rows, cloud_rows):
    lines = [
        "## Evaluation metrics",
        "",
        "| Metric | n | Local mean ± 2 SE | Cloud mean ± 2 SE | Cloud − Local ± 2 SE | Verdict |",
        "|---|---:|---:|---:|---:|---|",
    ]

    for metric in METRICS:
        local_scores = get_metric_rows(local_rows, metric)
        cloud_scores = get_metric_rows(cloud_rows, metric)

        common_ids = sorted(set(local_scores) & set(cloud_scores))

        if not common_ids:
            lines.append(
                f"| {metric} | 0 | N/A | N/A | N/A | No paired data |"
            )
            continue

        local_values = [local_scores[qid] for qid in common_ids]
        cloud_values = [cloud_scores[qid] for qid in common_ids]
        differences = [
            cloud_scores[qid] - local_scores[qid]
            for qid in common_ids
        ]

        local_mean, local_margin = mean_and_margin(local_values)
        cloud_mean, cloud_margin = mean_and_margin(cloud_values)
        diff_mean, diff_margin = mean_and_margin(differences)

        lower = diff_mean - diff_margin
        upper = diff_mean + diff_margin

        if lower <= 0 <= upper:
            verdict = "No clear difference"
        elif diff_mean > 0:
            verdict = "Cloud higher"
        else:
            verdict = "Local higher"

        lines.append(
            f"| {metric} | {len(common_ids)} "
            f"| {format_interval(local_mean, local_margin)} "
            f"| {format_interval(cloud_mean, cloud_margin)} "
            f"| {format_interval(diff_mean, diff_margin)} "
            f"| {verdict} |"
        )

    return lines


def get_completion_tokens(row):
    """Return completion plus separately reported reasoning tokens."""
    usage = row.get("usage") or {}

    completion = row.get("completion_tokens")
    if completion is None:
        completion = usage.get("completion_tokens")

    reasoning = row.get("reasoning_tokens")
    if reasoning is None:
        details = usage.get("completion_tokens_details") or {}
        reasoning = details.get("reasoning_tokens", 0)

    if completion is None:
        return None

    return completion + (reasoning or 0)


def get_pipeline_stats(label, pipeline_rows, evaluation_rows):
    # Evaluation generation_time_ms is available for both models.
    times = [
        row["generation_time_ms"] / 1000
        for row in evaluation_rows
        if row.get("generation_time_ms") is not None
    ]

    token_values = [
        tokens
        for row in pipeline_rows
        if (tokens := get_completion_tokens(row)) is not None
    ]

    empty_or_failed = 0

    for row in pipeline_rows:
        answer = row.get("actual_answer")
        if answer is None:
            answer = row.get("generated_answer", "")

        status = str(row.get("status", "")).lower()

        if status not in ("success", "completed", "ok") or not str(answer).strip():
            empty_or_failed += 1

    lines = [
        f"### {label.capitalize()} pipeline",
        "",
        f"- Questions: {len(pipeline_rows)}",
        f"- Median elapsed time: {statistics.median(times):.2f} seconds"
        if times else "- Median elapsed time: N/A",
        f"- Slowest elapsed time: {max(times):.2f} seconds"
        if times else "- Slowest elapsed time: N/A",
        f"- Average completion tokens (including separately reported reasoning tokens): {statistics.mean(token_values):.1f}"
        if token_values else "- Average completion tokens: Not available in this pipeline file",
        f"- Empty or failed answers: {empty_or_failed}",
        "",
    ]

    return lines


def main():
    local_eval = load_rows(EVALUATION_FILES["local"])
    cloud_eval = load_rows(EVALUATION_FILES["cloud"])

    local_pipeline = load_rows(PIPELINE_FILES["local"])
    cloud_pipeline = load_rows(PIPELINE_FILES["cloud"])

    report = [
        "# Local vs Cloud Comparison",
        "",
        f"- Local evaluation records: {len(local_eval)}",
        f"- Cloud evaluation records: {len(cloud_eval)}",
        "",
        "The difference is calculated as cloud score minus local score.",
        "The uncertainty shown is approximately mean ± 2 standard errors.",
        "",
    ]

    report.extend(compare_metrics(local_eval, cloud_eval))
    report.extend([
        "",
        "## Pipeline performance",
        "",
        "Elapsed time is taken from the evaluation records for consistency.",
        "",
    ])

    report.extend(
        get_pipeline_stats("local", local_pipeline, local_eval)
    )
    report.extend(
        get_pipeline_stats("cloud", cloud_pipeline, cloud_eval)
    )

    output = "\n".join(report)
    Path("comparison_results.md").write_text(output, encoding="utf-8")

    print(output)
    print("\nSaved comparison to comparison_results.md")


if __name__ == "__main__":
    main()