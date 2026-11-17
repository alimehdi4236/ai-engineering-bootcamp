
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

## Current project structure
- documents/: Source PDF documents.
- src/local_rag/: Python package directory.
- benchmark.py: Initial local model benchmark.
- test_api.py: Ollama API verification.
- benchmark_results.json: Saved initial benchmark results.
- decision_log.md: Student-maintained experiment notes and decisions.
- README.md: Project documentation.
- pyproject.toml: Project configuration and dependencies.
- uv.lock: Locked dependency versions.

New pipeline components will be added as development progresses.

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
- AGENTS.md

## Execution
Run commands from the project root.
Use uv to run Python scripts:

uv run python <script_name>.py

Verify the Ollama API:

uv run python test_api.py

Run the initial model benchmark:

uv run python benchmark.py

As the pipeline scripts are implemented, run the relevant stages:

uv run python ingest.py
uv run python retrieve.py
uv run python generate.py
uv run python pipeline.py

Run model comparisons:

uv run python benchmark.py

Only run a command after its corresponding script has been created.

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
