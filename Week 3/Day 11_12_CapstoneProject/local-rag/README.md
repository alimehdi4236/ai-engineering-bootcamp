# NovaTech Local RAG Assistant

A local Retrieval-Augmented Generation (RAG) application developed as part of the Accenture AI Engineering Bootcamp Day 11–12 capstone.

The application answers questions using information extracted from a collection of company PDF documents. It retrieves relevant document chunks from a local vector database and uses a locally running language model to generate evidence-grounded answers.

## Project Objective

The goal is to build a document question-answering system that can operate locally without sending company documents to cloud AI providers.

The assistant should:

- Extract and process PDF documents.
- Split extracted text into smaller chunks.
- Generate embeddings using a local embedding model.
- Store document vectors in ChromaDB.
- Retrieve relevant evidence for a user's question.
- Generate answers using a local LLM.
- Identify insufficient evidence instead of inventing information.
- Provide source document names and page references.

## Architecture

```text
                  PDF Documents
                       |
                       v
                PDF Text Extraction
                       |
                       v
                  Text Chunking
                       |
                       v
             Local Embedding Model
                       |
                       v
                 ChromaDB Store
                       |
                       |
User Question ---------+
       |
       v
Question Embedding
       |
       v
Vector Retrieval
       |
       v
Relevant Document Chunks
       |
       v
       Local LLM
       |
       v
Grounded Answer + Sources
```

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Dependency management | uv |
| LLM runtime | Ollama |
| LLM API interface | OpenAI-compatible Python client |
| Vector database | ChromaDB |
| Text splitting | LangChain text splitters |
| PDF extraction | pypdf |
| Embedding model | nomic-embed-text |
| Generation model | qwen3.5:4b-q4_K_M |

## Project Structure

```text
local-rag/
│
├── documents/
│   ├── company_handbook.pdf
│   ├── meeting_notes.pdf
│   ├── product_guide.pdf
│   ├── quarterly_report_q1_2026.pdf
│   └── security_policy.pdf
│
├── src/
│   └── local_rag/
│       ├── __init__.py
│       ├── ingest.py
│       ├── retrieve.py
│       ├── generate.py
│       └── pipeline.py
│
├── config.py
├── benchmark.py
├── evaluate_pipeline.py
├── test_api.py
├── test_questions.json
├── benchmark_results.json
├── pipeline_outputs.json
├── decision_log.md
├── AGENTS.md
├── pyproject.toml
└── uv.lock
```

The `chroma_db/` directory is generated locally during ingestion. It is not included in the repository and can be rebuilt from the source PDFs.

## Requirements

Before running the application, install:

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/download)

Ollama must be installed and running on the same machine as the Python application.

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/alimehdi4236/ai-engineering-bootcamp/tree/main/Week%203/Day%2011_12_CapstoneProject/local-rag
cd local-rag
```

### 2. Install Python dependencies

```powershell
uv sync
```

This creates or updates the project environment using the dependency versions recorded in `uv.lock`.

### 3. Download the local models

Open PowerShell and run:

```powershell
ollama pull qwen3.5:4b-q4_K_M
ollama pull nomic-embed-text
```

Check that the models are available:

```powershell
ollama list
```

Make sure the Ollama service is running before starting the application.

### 4. Verify the Ollama API

```powershell
uv run python test_api.py
```

## Rebuild the Vector Database

The vector database is not committed to the repository. It must be generated from the source PDFs after cloning the project.

From the project root, execute:

```powershell
uv run python -m local_rag.ingest
```

This process:

1. Reads the PDF documents from `documents/`.
2. Extracts their text.
3. Splits the text into chunks.
4. Generates embeddings using the configured local embedding model.
5. Stores the chunks, embeddings and metadata in ChromaDB.

The resulting database is stored in `chroma_db/`.

Run ingestion again whenever the source documents or ingestion configuration changes.

## Run the Application

Start the interactive RAG assistant:

```powershell
uv run python -m local_rag.pipeline
```

Enter a question when prompted.

The assistant returns an answer, supporting document references, model information and execution metadata.

You can also run the generation module directly:

```powershell
uv run python -m local_rag.generate
```

## Benchmarking and Evaluation

### Model Benchmark

Run:

```powershell
uv run python benchmark.py
```

The benchmark compares the configured local models and saves the results in:

```text
benchmark_results.json
```

### Pipeline Evaluation

Run:

```powershell
uv run python evaluate_pipeline.py
```

This evaluates the pipeline against the questions in `test_questions.json` and saves generated answers and execution metadata in:

```text
pipeline_outputs.json
```

The evaluation file also contains manually reviewed answer ratings.

**Warning:** Running the evaluator again overwrites `pipeline_outputs.json`. Back up the file first if you need to preserve manually entered ratings.

## Configuration

Project settings are centralized in the root-level `config.py`.

The configuration controls:

- LLM provider endpoint and API key.
- Generation model.
- Embedding model and endpoint.
- Chunk size and overlap.
- Retrieval top-K and distance threshold.
- Collection name.
- Temperature and reasoning effort.
- Maximum token limit and the corresponding API parameter name.

Environment variables can override selected configuration defaults.

The default Day 11 setup uses local Ollama endpoints and local models. The configuration layer is intended to support a provider change for the Day 12 comparison. Any cloud-provider comparison must be configured and evaluated separately; the Day 11 local-only pipeline remains the baseline.

## Evaluation Artifacts

| File | Purpose |
|---|---|
| `test_questions.json` | Test questions and expected answers |
| `benchmark_results.json` | Results from comparing local models |
| `pipeline_outputs.json` | Generated answers and pipeline execution results |
| `decision_log.md` | Student's technical decisions and experiment observations |

## Privacy and Local Execution

The Day 11 pipeline uses local Ollama models for embedding and generation.

The source PDFs, vector database and inference workflow remain on the local machine during this configuration.

Do not use cloud-tagged Ollama models for the local-only capstone evaluation.

## AI Assistance Disclosure

ChatGPT (GPT-6) was used as an AI coding assistant for implementation guidance, debugging, and documentation formatting support.

The project was executed and tested locally by the student. Model experiments, technical decisions and manual evaluation ratings are based on the student's own observations.

## Author

Ali Mehdi

Accenture AI Engineering Bootcamp — Day 11–12 Capstone