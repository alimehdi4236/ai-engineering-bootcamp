
# AGENTS.md — Local RAG Capstone

## Project objective
Build a local document question-answering RAG pipeline
for five PDF documents from a fictional technology company.

The application must run locally and provide answers
grounded in retrieved document evidence.

## Technology
- Python 3.12
- uv for dependency and environment management
- Ollama for local model inference
- OpenAI-compatible Python client
- ChromaDB for vector storage
- LangChain text splitters
- pypdf for PDF extraction

## Project architecture
- config.py: Central configuration and provider selection
- ingest.py: PDF extraction, chunking, embedding and storage
- retrieve.py: Retrieve relevant chunks and evidence
- generate.py: Generate grounded answers using an LLM
- pipeline.py: Connect retrieval and generation
- benchmark.py: Compare at least two models

## Development rules
1. Work one stage at a time.
2. Run and verify each stage before proceeding.
3. Preserve working code when adding new functionality.
4. Keep configuration in config.py.
5. Do not hardcode credentials or API keys.
6. Use local Ollama models for the Day 11 pipeline.
7. Never use cloud-tagged Ollama models.
8. Do not commit .env, .venv or chroma_db.
9. Keep generated evidence and benchmark outputs reproducible.
10. Every reported measurement must come from a saved output file.
11. Do not invent benchmark results or evaluation scores.
12. Keep functions focused and handle errors explicitly.

## Required artifacts
- benchmark_results.json
- test_questions.json
- pipeline_outputs.json
- decision_log.md
- README.md

## Execution
Run Python scripts through:

uv run python <script_name>.py

Rebuild the vector database by running:

uv run python ingest.py

Run the end-to-end pipeline using:

uv run python pipeline.py

Run model comparisons using:

uv run python benchmark.py

## Validation
- Check extracted PDF text before chunking.
- Verify embedding dimensions are consistent.
- Verify ChromaDB collection counts after ingestion.
- Inspect retrieved evidence for every test question.
- Check that answers are supported by retrieved sources.
- Verify refusal behaviour for unanswerable questions.
- Record actual model finish reasons and token usage.
- Validate generated JSON files before submission.

## AI assistance
AI coding assistants may help with implementation.
The student must understand and explain every line of code.
The decision log and Day 12 evaluation report must be
written by the student based on actual experiments.
