

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



### Model Benchmark — Initial Results

- Tested two local models using six identical prompts each.
- All 12 requests completed with finish_reason=stop.
- Qwen 4B average request time: 18.45 seconds.
- Qwen 2B average request time: 11.47 seconds.
- Qwen 4B average quality rating: 4.50/5.
- Qwen 2B average quality rating: 3.83/5.

### Observations for Initial Benchmark
All the observation rating are written under each prompt response of models 4b and 2b in benchmark_result.JSON file whereas these are the general findings below:
- Qwen 2B was overall faster in this test.
- Qwen 4B gave clearer reasoning and summarization.
- Qwen 2B produced a factual error and a unit error.
- Qwen 4B produced an incorrect example output in its code response.
- Both models produced valid JSON.

### Preliminary decision
Qwen 4B is the stronger initial option for answer quality even though Qwen 2B remains a faster alternative.
Final selection will be based on RAG evaluation using the five PDFs.

### PDF Extraction experiment:

#### Objective:
So before the implementation of Ingestion pipeline I tested the pdf text extraction to understand how well the supplied documents preserve ttheir structure mainly tables. Then to do that I have used the pypdf Library in python and used the standard extraction: extract_text(). for layout-aware extraction(extraction_mode="layout")

#### 1st Try with Financial Tables
Document used: quarterly_report_q1_2026.pdf
Page: 2
Observation: Standard extraction separated some table headings and values across lines making column relationships difficult to intrepret.
Result with Layout mode: column positioning and relationship between financial metrics, quarterly values,QoQ changes and YoY changes were clearer
##### Command Ran for Standard Extraction:
uv run --no-sync python -c "from pathlib import Path; from pypdf import PdfReader; [(print(f'\n--- {p.name} | Page {i+1}/{len(r.pages)} ---'), print((r.pages[i].extract_text() or '[NO TEXT]')[:1800])) for p in sorted(Path('documents').glob('*.pdf')) for r in [PdfReader(str(p))] for i in range(len(r.pages))]"
##### Command for Layout Extraction:
uv run --no-sync python -c "from pathlib import Path; from pypdf import PdfReader; p=Path('documents/quarterly_report_q1_2026.pdf'); r=PdfReader(str(p)); print(r.pages[1].extract_text(extraction_mode='layout'))"

#### 2nd try with Security Classification Matrix
Document: security_policy.pdf
Page: 3
Observation: The classification headings and security requirements were preserved in reading order while some long cell values were split across multiple lines. Whereas in layout extraction four columns were visually more clear but lost some spacing in words like Approved systems to Approvedsystems
Result with layout mode: layout-aware extraction improved visual alignment but standard extraction preserved some text relationships more clearly but neither method consistently reconstructed all table structures.
##### Command Ran for Standard Extraction:
uv run --no-sync python -c "from pathlib import Path; from pypdf import PdfReader; p=Path('documents/security_policy.pdf'); r=PdfReader(str(p)); print(r.pages[2].extract_text())"
##### Command for Layout Extraction:
uv run --no-sync python -c "from pathlib import Path; from pypdf import PdfReader; p=Path('documents/security_policy.pdf'); r=PdfReader(str(p)); print(r.pages[2].extract_text(extraction_mode='layout'))"

### Decision for Pdf Extraction mode:
I am using pypdf with extraction_mode="layout" as the initial extraction strategy because it improved the readability of financial table and it provides useful spatial information. But still even with that it alone cannot guarantee reliable table reconstruction. I would later source metadata and validate important table info during ingestion and retrieval test.

### Retrieval Tests
#### Experiment testing 1
I did 4 tests and from the architecture side what it does it converts the question into an embedding using nomic-embed-text and then it searches the ChromaDB vectors after that it find the five most semantically relevant document chunks and returns the text, document name, page number and similarity distance

**1st test**: From the first test I asked: How many days of annual leave do employees receive?
**results**: retriever found the correct answer in Result 1, from company_handbook.pdf, page 5 and also the Result 2 was relevant as it also searches the same pdf but the rest was irrelevant.

**2nd test**: for second test i asked: What encryption requirements apply to confidential data?
**results**: retriever found the relevant security policy like these 
Encryption at rest: AES-256. Encryption in transit: TLS 1.3. Encryption keys rotated every 90 days. so from those Results 3, 4 and 5 provide useful evidence

**3rd test**: for thrid test I asked: What are the main features of NovaTech ProjectHub?
**results**: it retrieved correct product guide first from Result 1. However, the retrieved chunk first describes the product's overview and supported methodologies. We should inspect the product-guide sections if we want a complete feature answer. Result 2 3 were slightly relevant but not the main features completely.

**4th test**: for fourth test the main qoal was to ask something which is unanswerable and the question was: What is the company's employee bonus payment date?
**results**: its the interesting one. The system returned unrelated chunks instead of recognizing that it had no reliable evidence. But as we know this is expected with basic vector retrieval: ChromaDB always returns the closest matches when asked for five results, even if none is genuinely relevant.

### Improvement Direction

For an initial experiment we'll use MAX_DISTANCE = 0.35 in main retrieve.py script as a provisional cutoff. We'll tune it using more test questions.
For example, the bonus question's first result has distance 0.3710 so it would be filtered out
