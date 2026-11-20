# NovaTech Local RAG Assistant

A document question-answering system developed as part of the Accenture AI Engineering Bootcamp Day 11–12 capstone.

The project started as a fully local Retrieval-Augmented Generation (RAG) application and was extended to include cloud-based model comparison, automated evaluation, and security testing.

The system answers questions using information extracted from a collection of company PDF documents. It retrieves relevant document chunks from a vector database and uses a language model to generate evidence-grounded answers.

---

## Project Objective

The main objective was to build a document question-answering system that can retrieve information from company documents, generate answers based on supporting evidence, and identify situations where the available information is insufficient.

The project was developed in two stages:

### Day 11 – Local RAG Implementation

The first stage focused on building the complete RAG pipeline using locally running models.

The application was designed to:

- Extract and process PDF documents.
- Split extracted text into smaller chunks.
- Generate embeddings using a local embedding model.
- Store document vectors in ChromaDB.
- Retrieve relevant evidence for a user's question.
- Generate answers using a locally running LLM.
- Identify insufficient evidence instead of inventing information.
- Provide source document names and page references.
- Evaluate generated answers through manual review.

The Day 11 implementation established the local pipeline as the baseline for further development.

### Day 12 – Evaluation, Cloud Comparison and Security Testing

The second stage extended the existing application rather than replacing the original local implementation.

The following capabilities were added:

- A cloud-based generation configuration for comparison with the local model.
- Automated evaluation using DeepEval.
- Five evaluation metrics: Faithfulness, Answer Relevancy, Contextual Relevancy, Contextual Recall and Contextual Precision.
- Local and cloud evaluation results saved separately.
- A comparison script analysing model quality and execution performance.
- Security testing against prompt-based attacks.
- Manual security verdicts and notes for both configurations.
- A final evaluation report documenting findings, limitations and recommendations.

The same retrieval configuration was maintained for the local and cloud comparison to keep retrieval settings consistent while comparing generation performance.

---

## Architecture

### Day 11 – Local RAG Pipeline

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

### Day 12 – Extended Evaluation Workflow

```text
              Test Questions
                     |
          +----------+----------+
          |                     |
          v                     v
     Local Pipeline        Cloud Pipeline
          |                     |
          v                     v
   Local Answers           Cloud Answers
          |                     |
          v                     v
   DeepEval Results        DeepEval Results
          |                     |
          +----------+----------+
                     |
                     v
             Comparison Script
                     |
                     v
          Local vs Cloud Results
                     |
                     v
            Evaluation Report


       Local Pipeline       Cloud Pipeline
              |                    |
              v                    v
        Security Probes      Security Probes
              |                    |
              v                    v
       Manual Verdicts       Manual Verdicts
              |                    |
              +---------+----------+
                        |
                        v
                 Security Results
```

---

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.12 |
| Dependency management | uv |
| Local LLM runtime | Ollama |
| LLM API interface | OpenAI-compatible Python client |
| Vector database | ChromaDB |
| Text splitting | LangChain text splitters |
| PDF extraction | pypdf |
| Local embedding model | nomic-embed-text |
| Local generation model | qwen3.5:4b-q4_K_M |
| Evaluation framework | DeepEval |
| Local model evaluation | Ollama |
| Cloud model evaluation | Cloud-based LLM configuration |
| Version control | Git and GitHub |

---

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
├── eval_pipeline.py
├── security_probe.py
├── compare.py
├── test_api.py
├── test_questions.json
├── benchmark_results.json
├── pipeline_outputs_local.json
├── pipeline_outputs_cloud.json
├── eval_results_local.json
├── eval_results_cloud.json
├── security_results_local.json
├── security_results_cloud.json
├── comparison_results.md
├── evaluation_report.md
├── decision_log.md
├── AGENTS.md
├── pyproject.toml
└── uv.lock
```

**Note:** The `chroma_db/` directory is generated locally during ingestion. It is not included in the repository and can be rebuilt from the source PDFs.

---

## Requirements

Before running the application, install:

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/download)

Ollama must be installed and running on the same machine as the local Python application.

---

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

---

## Day 11 – Local RAG Pipeline

### Rebuild the Vector Database

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

### Run the Application

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

### Model Benchmark

Run:

```powershell
uv run python benchmark.py
```

The benchmark compares the configured local models and saves the results in:

```text
benchmark_results.json
```

### Local Pipeline Evaluation

Run:

```powershell
uv run python evaluate_pipeline.py
```

This evaluates the local pipeline against the questions in `test_questions.json` and saves generated answers and execution metadata.

The manually reviewed answer ratings are also stored in the local pipeline output file.

**Warning:** Running the evaluator again may overwrite existing pipeline outputs and manually entered ratings. Back up the file before rerunning it.

---

## Day 12 – Evaluation and Cloud Comparison

### Local and Cloud Pipeline Evaluation

The existing local pipeline was retained, and a cloud-based generation configuration was introduced for comparison.

Both configurations were evaluated against the same set of 20 test questions.

The evaluation process included:

- Generating answers using the local and cloud configurations.
- Saving answers and execution metadata separately.
- Evaluating the generated responses using DeepEval.
- Comparing the results to identify differences in quality and performance.

### DeepEval Metrics

Five metrics were used to evaluate the pipeline:

| Metric | What it evaluates |
|---|---|
| Faithfulness | Whether the generated answer is supported by the retrieved context |
| Answer Relevancy | Whether the answer addresses the user's question |
| Contextual Relevancy | Whether the retrieved context is relevant to the question |
| Contextual Recall | Whether the retrieved context contains the information needed for the expected answer |
| Contextual Precision | Whether relevant retrieved chunks are ranked above less useful chunks |

The evaluation results are saved separately:

```text
eval_results_local.json
eval_results_cloud.json
```

Pipeline outputs are saved in:

```text
pipeline_outputs_local.json
pipeline_outputs_cloud.json
```

### Local vs Cloud Comparison

The comparison script analyses the evaluation results and execution performance.

Run:

```powershell
python compare.py
```

The comparison includes:

- Number of evaluated questions.
- Mean evaluation scores and uncertainty intervals.
- Per-question local and cloud differences.
- Median and slowest generation time.
- Average completion tokens where available.
- Empty or failed answers.
- Overall comparison verdicts.

The results are saved in:

```text
comparison_results.md
```

The same retrieval configuration was maintained during this comparison. This allowed the generation configurations to be compared without intentionally changing the embedding model, chunking strategy or retrieval settings.

---

## Day 12 – Security Evaluation

Security testing was added to assess how the local and cloud configurations respond to prompt-based attacks.

### Security Test Scenarios

The tests included:

- Prompt extraction.
- Jailbreak attempts.
- Document injection.
- Instruction override.
- Data exfiltration.
- Knowledge poisoning.
- Additional custom attack scenarios.

The security probes were executed against both configurations.

Run the security testing script according to its configured local or cloud settings:

```powershell
python security_probe.py
```

### Manual Security Assessment

Each attack result was reviewed manually and assigned a verdict:

| Verdict | Meaning |
|---|---|
| `resistant` | The system resisted the tested attack |
| `partially resistant` | The system showed some resistance but still exposed potentially problematic behaviour |
| `vulnerable` | The system followed the malicious instruction or exposed protected information |

Manual verdicts and notes are stored in:

```text
security_results_local.json
security_results_cloud.json
```

These tests provide an initial assessment of the system's resistance to prompt-based attacks. They do not guarantee complete security.

---

## Evaluation Artifacts

The following files contain the outputs and results generated during the Day 11–12 capstone.

| File | Purpose |
|---|---|
| `test_questions.json` | Test questions and expected answers |
| `benchmark_results.json` | Results from local model benchmarking |
| `pipeline_outputs_local.json` | Local pipeline answers, execution details and manual ratings |
| `pipeline_outputs_cloud.json` | Cloud pipeline answers and execution details |
| `eval_results_local.json` | DeepEval results for the local pipeline |
| `eval_results_cloud.json` | DeepEval results for the cloud pipeline |
| `security_results_local.json` | Local security test results and manual verdicts |
| `security_results_cloud.json` | Cloud security test results and manual verdicts |
| `comparison_results.md` | Local vs cloud comparison |
| `evaluation_report.md` | Final evaluation findings, limitations and recommendations |
| `decision_log.md` | Technical decisions and experiment observations |

---

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

### Local Configuration

The Day 11 setup uses local Ollama endpoints and local models for embedding and generation.

The source PDFs, vector database and inference workflow remain on the local machine during this configuration.

### Cloud Comparison Configuration

Day 12 introduced a cloud-based generation configuration to compare answer quality and execution performance against the local model.

The local pipeline remains the baseline implementation.

Cloud evaluation requires the appropriate provider configuration and credentials. API keys should be stored in environment variables and must not be committed to GitHub.

---

## Privacy and Security Considerations

The Day 11 pipeline was designed to operate locally, avoiding the need to send company documents to cloud AI providers during local inference.

The Day 12 cloud comparison introduced a separate cloud-based generation workflow. Cloud usage should therefore be considered separately when evaluating document privacy and data handling.

Security testing was performed against both configurations, but the results should be treated as initial testing rather than proof of complete security.

The following files and directories should not be committed to the repository:

- `.env`
- `.venv/`
- `chroma_db/`

---

## AI Assistance Disclosure

ChatGPT (GPT-6) was used as an AI coding assistant for implementation guidance, debugging, evaluation support and documentation formatting.

The project was executed and tested locally by the author. Model experiments, technical decisions, manual answer ratings and security verdicts are based on the student's own observations and assessments.

---

## Author

Ali Mehdi

Accenture AI Engineering Bootcamp — Day 11–12 Capstone