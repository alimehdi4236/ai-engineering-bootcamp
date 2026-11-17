

# Decision Log: Local RAG Pipeline

## Machine

- Hardware: Intel Core i5-1145G7, 4 cores / 8 threads, 16 GB RAM, Intel Iris Xe integrated graphics.
- Runtime: Native Windows Ollama.
- Main model test: qwen3.5:4b-q4\_K\_M.
- ollama ps: 3.4 GB, 100% CPU, context 8192.

## Environment and API Verification

- Python: 3.12.16
- Ollama: 0.40.16
- Embedding model installed: nomic-embed-text
- Comparison model installed: qwen3.5:2b-q4\_K\_M
- API test: Successful.
- Test response: "Hello! How can I help you today?"
- Finish reason: stop.
- Reasoning effort: none.



## Model Benchmark — Initial Results

- Tested two local models using six identical prompts each.
- All 12 requests completed with finish_reason=stop.
- Qwen 4B average request time: 18.45 seconds.
- Qwen 2B average request time: 11.47 seconds.
- Qwen 4B average quality rating: 4.50/5.
- Qwen 2B average quality rating: 3.83/5.

### Observations
All the observation rating are written under each prompt response of models 4b and 2b in benchmark_result.JSON file whereas these are the general findings below:
- Qwen 2B was overall faster in this test.
- Qwen 4B gave clearer reasoning and summarization.
- Qwen 2B produced a factual error and a unit error.
- Qwen 4B produced an incorrect example output in its code response.
- Both models produced valid JSON.

### Preliminary decision
Qwen 4B is the stronger initial option for answer quality even though Qwen 2B remains a faster alternative.
Final selection will be based on RAG evaluation using the five PDFs.



