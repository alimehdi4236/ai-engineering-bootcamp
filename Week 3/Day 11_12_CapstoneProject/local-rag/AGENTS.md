# AGENTS.md — Local RAG Capstone

## Project Objective

Build a local document question-answering RAG pipeline for five PDF documents from a fictional technology company.

The application must run locally and generate answers grounded in retrieved document evidence. The project is part of the Accenture AI Engineering Bootcamp Day 11–12 capstone.

## Technology Stack

- Python 3.12
- `uv` for dependency and environment management
- Ollama for local LLM inference
- OpenAI-compatible Python client
- ChromaDB for vector storage
- LangChain text splitters for document chunking
- pypdf for PDF text extraction

## Project Architecture

The application code is maintained in `src/local_rag/`.

- `config.py` (project root): Central configuration for the LLM provider, model, embedding model, retrieval settings and generation parameters.
- `src/local_rag/ingest.py`: PDF extraction, text chunking, embedding generation and ChromaDB storage.
- `src/local_rag/retrieve.py`: Embeds user questions and retrieves relevant document chunks.
- `src/local_rag/generate.py`: Generates answers using retrieved evidence and the configured LLM.
- `src/local_rag/pipeline.py`: Connects the retrieval and generation stages into one workflow.
- `benchmark.py`: Compares local models.
- `evaluate_pipeline.py`: Runs the pipeline against the test-question dataset and saves structured results.

## Project Structure

- `documents/`: Source PDF documents.
- `src/local_rag/`: Python application package.
- `config.py`: Central project configuration.
- `benchmark.py`: Model benchmarking script.
- `test_api.py`: Ollama API verification script.
- `evaluate_pipeline.py`: Pipeline evaluation script.
- `test_questions.json`: Test-question dataset.
- `benchmark_results.json`: Saved model benchmark results.
- `pipeline_outputs.json`: Saved pipeline evaluation results, including manually reviewed ratings.
- `decision_log.md`: Student-maintained experiment notes and technical decisions.
- `README.md`: Setup, execution and project documentation.
- `pyproject.toml`: Project metadata and dependencies.
- `uv.lock`: Locked dependency versions.
- `chroma_db/`: Locally generated vector database; rebuildable and not submitted.

## Development Rules

1. Work one stage at a time.
2. Run and verify each stage before proceeding.
3. Preserve working code when adding functionality.
4. Keep model and pipeline settings centralized in `config.py`.
5. Do not hardcode real credentials or API keys.
6. Use local Ollama models for the Day 11 pipeline.
7. Do not use cloud-tagged Ollama models.
8. Do not commit `.env`, `.venv/` or `chroma_db/`.
9. Keep benchmark and evaluation outputs reproducible.
10. Every reported experimental measurement must be traceable to a saved output file.
11. Do not invent benchmark results, evaluation scores or performance measurements.
12. Keep functions focused and handle errors explicitly.
13. Do not overwrite manually reviewed evaluation results without first preserving the ratings.
14. Keep document evidence and generated answers distinguishable.

## Required Artifacts

- `benchmark_results.json`
- `test_questions.json`
- `pipeline_outputs.json`
- `decision_log.md`
- `README.md`
- `AGENTS.md`

## Execution

Run all commands from the project root.

Install project dependencies:

```powershell
uv sync
```

Verify the Ollama API:

```powershell
uv run python test_api.py
```

Rebuild the vector database from the source PDFs:

```powershell
uv run python -m local_rag.ingest
```

Run the interactive generation module:

```powershell
uv run python -m local_rag.generate
```

Run the end-to-end RAG assistant:

```powershell
uv run python -m local_rag.pipeline
```

Run the model benchmark:

```powershell
uv run python benchmark.py
```

Run the complete test-question evaluation:

```powershell
uv run python evaluate_pipeline.py
```

**Important:** `evaluate_pipeline.py` writes to `pipeline_outputs.json`. Running it again replaces the existing output file. Preserve or back up manually reviewed `passed` and `rating_note` fields before regenerating the results.

Only run a command after its corresponding script and dependencies are available.

## Validation Checklist

- Check extracted PDF text before chunking.
- Verify embedding generation and dimensions.
- Verify ChromaDB collection counts after ingestion.
- Inspect retrieved evidence for test questions.
- Check that generated answers are supported by retrieved sources.
- Verify refusal behaviour for unanswerable questions.
- Record model name, thinking state and actual finish reason.
- Record available token and timing measurements.
- Validate generated JSON files.
- Review manual answer ratings against the actual generated answers.

## Local-Only and Security Requirements

- The Day 11 pipeline must use a local model through Ollama.
- Do not use cloud-tagged Ollama models.
- Do not expose proprietary document content to external providers during the local-only evaluation.
- Keep credentials outside source code.
- Do not commit local databases, virtual environments or secrets.

## AI Assistance

AI coding assistants may help with implementation, debugging, explanations and documentation.

The student must understand and be able to explain the implementation and technical decisions.

The decision log and Day 12 evaluation report must reflect the student's own observations and actual experiments. AI assistance must be disclosed in the README.