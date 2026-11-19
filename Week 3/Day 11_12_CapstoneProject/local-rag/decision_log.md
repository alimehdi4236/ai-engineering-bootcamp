

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

### Ingestion Configuration Decisions:
#### Embedding Model (nomic-embed-text) and Vector Database:
I selected nomic-embed-text as the local embedding model for initial RAG implementation. I used this local embedding model because project required a local RAG pipeline and we wanted to avoid sending document content to an external embedding API. I did not conduct a comparative benchmark of multiple embedding models but for future I would be considering it an initial choice rather than a proven optimal model.

#### Vector database: ChromaDB
I used ChromaDB as the vector database because the project is designed as a local RAG application and it allows to store the document embeddings together with their associated text and metadata allowing the retriever to return the original chunk, source filename and page information. Our project uses a ChromaDB collection named novatech_documents which allows the indexed document data to remain available between application runs instead of requiring the documents to be embedded again for every question.

#### Similarity metric

My retrieval implementation uses cosine distance to compare the question embedding with stored document-chunk embeddings.
A lower cosine distance usually indicates that two vectors are more similar which is important because the retrieval threshold is based on distance and how it is: chunks with a distance greater than the configured maximum are filtered out means they are cut.

#### Chunking Strategy
The current implementation uses the following configuration:
- Chunk size: 1,000 characters.
- Chunk overlap: 150 characters.
- Ingestion batch size: 32.
The reason for using chunks is that embedding and retrieving entire PDF documents would make it difficult to identify specific passages relevant to an individual question. Smaller chunks allow the retriever to identify more focused pieces of evidence.
The 150-character overlap preserves some context between neighbouring chunks and without it information located near the end of one chunk and the beginning of the next could will become separate during retrieval. The batch size of 32 controls how many chunks are processed together during ingestion and important fact these values were used as the initial implementation configuration. I didnt conduct a separate controlled experiment comparing multiple chunk sizes or overlap values so I cannot claim that 1000 characters and 150 characters are the optimal settings.

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

#### Improvement Direction

For an initial experiment we'll use MAX_DISTANCE = 0.35 in main retrieve.py script as a provisional cutoff. We'll tune it using more test questions. For example, the bonus question's first result has distance 0.3710 so it would be filtered out

### Retrieval Configuration: TOP_K and MAX_DISTANCE
The initial retrieval configuration uses:

- TOP_K = 5
- MAX_DISTANCE = 0.35

Why TOP_K = 5?
I selected 5 as the initial retrieval candidate limit which provides the generator with several relevant passages instead of relying on only one retrieved chunk. It is particularly useful for questions that require information from multiple sections or documents. But the catch is, retrieving more chunks does not automatically improve answer quality. Additional chunks can contain unrelated information.

Why MAX_DISTANCE = 0.35 

The vector search uses cosine distance to measure the difference between the question embedding and each document-chunk embedding so here the maximum distance threshold acts as a relevance filter in which:

- A chunk with distance less than or equal to 0.35 is remained.
- A chunk with distance greater than 0.35 is removed.

In here a distance of 0.35 does not mean that the system is 35% confident in the answer. It is simply the cutoff used by my retrieval implementation. The annual-leave question returned two relevant chunks after filtering while the encryption and ProjectHub questions still returned five chunks in the test. The unanswerable bonus-payment question returned no chunks because its retrieved results did not pass the threshold. But important to note that the threshold also introduced a trade-off like for example a relevant chunk could be removed if its distance was slightly above the selected cutoff. This is demonstrated in the later Q07 evaluation test experiment.


#### Retrieval Tests After Improvement with thresold
So now the difference happened when we applied thresold filter while it converts the questions into 768 vector embeddings and after searching the ChromaDB retrieves five closest chunks after applying the MAX_DISTANCE = 0.35 threshold the retrieval results became more controlled. The annual leave question returned 2 relevant chunks instead of 5 and the encryption and ProjectHub questions still returned 5 chunks and the unanswerable bonus question returned 0 chunks. The threshold was a useful first improvement but it still needs further testing with the complete test Here below is the complete testing result:

#### Experiment retrieval testing
**1st test**: I repeated the first question from previous tests: How many days of annual leave do employees receive?
**results**: After applying the threshold of 0.35, the retriever returned 2 chunks instead of 5. Both results came from company_handbook.pdf page 5. Result 1 contained the exact answer of 25 days of paid time off while Result 2 also contained relevant information about sick leave and PTO requests. The irrelevant results were successfully filtered out.

**2nd test**: I repeated the second question: What encryption requirements apply to confidential data?
**results**: The retriever gave output 5 chunks because all of them had a distance below 0.35. The results from security_policy.pdf had the relevant encryption requirements, including AES-256 encryption at rest, TLS 1.3 for data in transit and automatic encryption key rotation every 90 days. The threshold did not remove any of the useful evidence in this test.

**3rd test**: I again asked the third question: What are the main features of NovaTech ProjectHub?

**results**: The retriever gave 5 chunks because all results were within the selected threshold. Result 1 from product_guide.pdf was still the most relevant result which describes the ProjectHub overview and support methodologies. Other results also contained some related information but not all of them directly answered the question. So threshold improved filtering in some cases but it did not completely remove every less relevant chunk in this

**4th test**: asked the same unanswerable question: What is the company's employee bonus payment date?

**results**: This time the retriever returned 0 chunks because none of the five results passed the maximum distance threshold of 0.35. That is the behaviour we wanted because the system no longer returns unrelated document chunks when it cant find sufficient similar evidence. However it doesnt prove that the information is absent from all five PDFs. It only meant that no retrieved chunk passed my current threshold.

### Generation Test
#### Experiment testing

After completing the retrieval stage I created generate.py to connect the retrieved document chunks with local LLM. The main task was to generate answers based only on the retrieved evidence which includes source citations and avoid making up stuff when the documents do not contain an answer.
For this test I used qwen3.5:4b-q4_K_M with a temperature of 0.1 and the reason to choose this temperature value because it is more suitable for our rag since priority is factual accuracy and consistency. 

**1st test**: I asked: How many days of annual leave do employees receive?

**results**: The model generated the correct answer that all full-time employees receive twenty-five (25) days of paid time off per calendar year. It also correctly mentioned that part-time employees receive PTO on a pro-rata basis. The answer was suitable and supported by company_handbook.pdf, page 5 and model finished successfully with finish_reason=stop.

**2nd test**: For second test I asked: What is the company's employee bonus payment date?

**results**: I asked this question which was intentionally unanswerable because the retrieval stage didnt find any relevant chunks within the selected distance threshold. The system returned an insufficient-evidence message instead of sending the question to the LLM. Its important because it prevents the model from inventing a bonus payment date. No sources were returned and the finish_reason was None because generation got skipped

**3rd test**: In third test I asked: What encryption requirements apply to confidential data?

**results**: The model correctly explained that confidential data must be encrypted at rest using AES-256 or an equivalent approved algorithm and that data transmitted across networks must use TLS 1.3. It also mentioned that encryption keys are managed through a centralized KMS with automatic rotation every 90 days. The answer supports by security_policy.pdf, pages 3, 8 and 9 and it completed the response with finish_reason=stop.

**4th test**: For fourth test the question was: What are the main features of NovaTech ProjectHub?

**results**: It generated a detailed answer covering the supported project management methodologies, sharing analytics dashboard, dashboard customization, data scope, sharing and export options. It correctly used product_guide.pdf pages 2 and 9 as the main sources. It also mentioned that NovaTech Copilot is still in the design phase and is not yet a current feature using quarterly_report_q1_2026.pdf, page 6 as supporting evidence.

In the begining model used generic references like Source 1 and Source 2 inside its answer. Then I improved the system prompt in generate.py by instructing the model to cite the exact PDF filename and page number and not to use generic source references. After this change the model generated citations in the required format making the answers easier to verify against the original documents.

**Conclusion for generation**: The initial generation tests shows that the local Qwen 4B model can produce useful document-based answers when its provided with relevant evidence. But these are only initial manual tests, and the complete pipeline will need further evaluation using the full test-question set.

### End-to-End Pipeline Tests 

#### Experiment testing 1

After completing the ingestion, retrieval and generation I created pipeline.py to connect everything into one complete RAG workflow. The idea was to test whether the system could take a user question retrieve relevant document chunks, generate an answer using the local LLM and return the answer together with its source information.
Pipeline uses the existing retrieve.py and generate.py functions instead of duplicating their logic and pasting the whole code into one single script. For these tests I continued using the local model qwen3.5:4b-q4_K_M.

**1st test**: I asked: How many days of annual leave do employees receive in the company?

**results**: The pipeline correctly retrieved the relevant information from company_handbook.pdf, page 5 and the model generated correct answer that all full-time employees receive twenty-five (25) days of paid time off per calendar year, in addition to public holidays. It also correctly mentioned that part-time employees receive PTO on a pro-rata basis. Retriever returned 2 relevant chunks with distances of 0.2367 and 0.2840 and completed the response successfully with finish_reason=stop.

**2nd test**: For the second test I asked: What is the company's employee bonus payment date and how much is it?

**results**: It was an unanswerable question and the complete pipeline returned an insufficient-evidence response. No relevant chunks passed the retrieval threshold so the LLM was not called and no sources were returned. The system didnt invent a bonus payment date or amount. The finish_reason was None because generation got skipped.

**Conclusion for Orchestration Pipeline**:
The end-to-end pipeline successfully connected all the previously developed components into one workflow. Both tests behaved as expected and it confirms that initial local RAG pipeline is working end to end but further testing with the complete test-question set is still required to evaluate retrieval quality and answer accuracy as well as overall performance.

### Retrieval Threshold Experiment 
#### For Q07 -

**Baseline configuration:**
- TOP_K: 5
- MAX_DISTANCE: 0.35

**Problem observed:**
The expected proof was present in raw top-five retrieval results but the relevant chunk from company_handbook.pdf, page 6, had a cosine distance of 0.36455 and got removed by the 0.35 threshold which i selected.

**Experimental configuration:**
- TOP_K: 5
- MAX_DISTANCE: 0.37

**Observed result:**
The page 6 chunk survived filtering and the generated answer correctly identified the 30-calendar-day submission deadline and the consequences of late submissions.

#### For Q11 -
**Query wording and retrieval sensitivity**

The original question retrieved the quarterly report's employee count (412) but got failed to retrieve the handbook chunk containing the approximate employee count (400). I increased the distance threshold to 10 did not solve the issue but also increased time to process because the relevant chunk was outside the top five results.
I did reformulate in a simple way again asking for both employee counts then it retrieved the relevant handbook and quarterly report chunks. The model then generated the correct answer with citations to handbook page 1 and quarterly report page 8.

**Observation:** Retrieval quality is sensitive to query wording. A simpler question can produce better document coverage than a more complex one.

### Final Retrieval Configuration and Decision

After the initial retrieval experiments and the Q07 and Q11 investigations the final retrieval configuration used for the full evaluation was:

| Parameter | Final value |
|---|---|
| Embedding model | nomic-embed-text |
| Vector database | ChromaDB |
| Collection | novatech_documents |
| Similarity metric | Cosine distance |
| TOP_K | 5 |
| MAX_DISTANCE | 0.37 |
| Chunk size | 1,000 characters |
| Chunk overlap | 150 characters |

**Why was MAX_DISTANCE changed from 0.35 to 0.37?**

The main reason was the Q07 retrieval experiment. With the original threshold of 0.35, the relevant chunk from company_handbook.pdf, page 6, had a cosine distance of 0.36455. Even we observed that this chunk contained the expected evidence about the expense-submission deadline it was removed because its distance exceeded the configured threshold. Then I increased the threshold to 0.37 while keeping TOP_K at 5 and finally then with this configuration the relevant page 6 chunk passed the filter and the generated answer correctly identified the 30-calendar-day submission deadline and the consequences of late submissions.

**Why I did not increase the threshold further?**

In the Q11 experiment showed that increasing the threshold alone didnt solve every retrieval problem. The original comparative question failed to retrieve the handbook chunk containing the approximate employee count so here increasing the threshold to 10 did not solve the problem because the relevant chunk was outside the top-five candidate results. Remaking the question produced better retrieval results without increasing TOP_K. Thats why the final threshold of 0.37 was selected based on the observed Q07 improvement and selected configuration based on the experiments performed while keeping the initial TOP_K value of 5.

## Full RAG Pipeline Evaluation

#### Evaluation Dataset

After the initial component tests and retrieval experiments i evaluated the complete RAG pipeline using a dataset of 20 questions.

The dataset contains four categories:

- Direct factual questions.
- Detailed questions.
- Cross-document questions.
- Unanswerable questions.

The questions were designed to test different areas of the pipeline, including factual retrieval, multi-part answers, information from multiple documents and the ability to refuse questions when the documents do not contain sufficient information and having no clues.

#### Execution Results

The final evaluation output recorded:

| Metric | Result |
|---|---:|
| Total questions | 20 |
| Successful pipeline runs | 20 |
| Failed pipeline runs | 0 |
| Manually evaluated passed answers | 16 |
| Manually evaluated failed answers | 4 |
| Answer pass rate | 80% |

I calculated the answer pass rate using the manually completed passed fields in `pipeline_outputs.json`.

A successful pipeline run does not necessarily mean that the answer was correct. All 20 questions completed successfully but I wasnt satisfied with four generated answers which did not reach the expected answer criteria.

#### Performance Observations

The saved evaluation output contains numeric execution times for 19 questions. Q14 was manually retried by running the script through terminal because it gave an earlier timeout and its successful retry does not have a recorded execution time in the final JSON.

For the 19 questions with recorded durations:

- Average execution time: approximately 317.88 seconds.
- Median execution time: 214.77 seconds.
- Fastest recorded execution: 2.27 seconds.
- Slowest recorded execution: 1,785.25 seconds.

These measurements show that response time varied considerably across questions on the local machine.

The average and median above are calculated from the 19 recorded durations, not all 20 questions.

#### Analysis of Failed Answers

I marked four questions as failed during manual answer evaluation.

| Question | Main issue |
|---|---|
| Q01 | The answer neglected that annual leave is additional to public holidays. |
| Q03 | The answer i got gave the 99.95% uptime SLA but missed that it is measured monthly. |
| Q12 | The generated answer omitted the additional in-office requirements that department heads may establish with HR approval. |
| Q13 | The answer incorrectly claimed that the handbook contained no ARR information and missed the approximately EUR 17 million FY2025 ARR figure. |

These failures demonstrate that retrieving relevant documents cant guarantee that the generator will include every required detail.
Q13 was particularly important because generated answer incorrectly stated that the handbook does not contain ARR information even though the expected evidence was in the handbook. From this its observed that a retrieval and evidence-selection problem is also a generation-quality problem.

#### Observations from Unanswerable Questions

I tested the unanswerable questions to see whether the system could avoid inventing information that was not available in the supplied documents.
Our pipeline correctly refused to provide unsupported answers for the tested questions about:

- The exact annual employee bonus payment date.
- The exact Q1 2026 net profit after tax.
- CEO's personal mobile phone number.
- An individual employee's exact annual base salary.
- And the CEO's residential street address.

The generated answers didnt invent the missing dates, financial figures or personal information.

However, a fair refusal should not be automatically interpreted as proof that retrieval was perfect from what I can say. For example, Q16 returned an irrelevant handbook passage but still correctly stated that the exact bonus payment date could not be determined.

### Important Retrieval and Generation Limitations

The several observed limitations are:

- **Retrieval coverage:** The Q13 answer missed the handbook evidence containing the FY2025 ARR figure.
- **Answer completeness:** Q01, Q03 and Q12 contained mostly correct information but didnt notice details required by the expected answers.
- **Query sensitivity:** The Q11 experiment demonstrated that query wording can influence which documents are retrieved.
- **Threshold sensitivity:** Q07 demonstrated that an overly restrictive distance threshold can remove relevant evidence.
- **Execution time:** The local 4B model had highly variable response times, including a very long execution for Q13.
- **Unanswerable questions:** Our system refused the tested unsupported questions successfully but stil I think a refusal alone does not establish tthe retrieval stage found all relevant evidence.

#### Overall Evaluation Conclusion

After full evaluation it was demonstrated that the local RAG pipeline successfully execute all 20 test questions and achieved an 80% manually evaluated answer pass rate. Our designed system performed well on several direct factual questions, detailed questions and cross-document questions. It also showed the ability to refuse unsupported questions instead of inventing some new answers.
However, the failed answers proves the pipeline still has limitations in retrieval coverage and answer completeness and most of the time it does have limitations since it has alot of important factors to make it better with less limitations.