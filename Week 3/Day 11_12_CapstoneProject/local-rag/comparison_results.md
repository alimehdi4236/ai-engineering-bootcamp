# Local vs Cloud Comparison

- Local evaluation records: 20
- Cloud evaluation records: 20

The difference is calculated as cloud score minus local score.
The uncertainty shown is approximately mean ± 2 standard errors.

## Evaluation metrics

| Metric | n | Local mean ± 2 SE | Cloud mean ± 2 SE | Cloud − Local ± 2 SE | Verdict |
|---|---:|---:|---:|---:|---|
| Faithfulness | 20 | 0.630 ± 0.175 | 0.590 ± 0.176 | -0.041 ± 0.108 | No clear difference |
| Answer Relevancy | 20 | 0.978 ± 0.035 | 1.000 ± 0.000 | 0.022 ± 0.035 | No clear difference |
| Contextual Relevancy | 20 | 0.241 ± 0.112 | 0.241 ± 0.102 | 0.000 ± 0.040 | No clear difference |
| Contextual Recall | 20 | 0.717 ± 0.201 | 0.683 ± 0.196 | -0.033 ± 0.046 | No clear difference |
| Contextual Precision | 20 | 0.760 ± 0.158 | 0.770 ± 0.159 | 0.010 ± 0.146 | No clear difference |

## Pipeline performance

Elapsed time is taken from the evaluation records for consistency.

### Local pipeline

- Questions: 20
- Median elapsed time: 214.77 seconds
- Slowest elapsed time: 1785.25 seconds
- Average completion tokens: Not available in this pipeline file
- Empty or failed answers: 0

### Cloud pipeline

- Questions: 20
- Median elapsed time: 1.02 seconds
- Slowest elapsed time: 5.77 seconds
- Average completion tokens (including separately reported reasoning tokens): 60.2
- Empty or failed answers: 0
