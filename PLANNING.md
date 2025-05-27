# PLANNING.md

<!--
  This file describes the project context, architecture, style guidelines and constraints to guide RooCode in generating production-ready code.
-->

## 1. Project Overview

**Name:** Article Extraction & Summarization Pipeline
**Purpose:** Automate fetching unprocessed article topics from Supabase, retrieve candidate URLs via Google search, extract and validate the top 3 articles per topic, export raw articles for manual review, summarize validated content, and store results.

## 2. High-Level Goals

* **Reliability:** Robust error handling, retries, and detailed step-by-step logging via `logfire`.
* **Maintainability:** Clear, modular sections in code (or well‑demarcated sections if in one file), PEP8 compliance, and thorough docstrings.
* **Scalability:** Async HTTP fetching, batch-limited loops (top 3), and flexible plug‑in validation/summarization.
* **Observability:** Log every stage (success or error) with context: topic name, URL, iteration index.

## 3. System Architecture & Data Flow

```mermaid
flowchart TD
    A[Supabase: Fetch Unprocessed Topics] --> B[Google Search Client: Retrieve Search HTML]
    B --> C[URL Extractor: parse HTML ➔ 10 candidate URLs]
    C --> D[Select Top 3 Valid URLs]
    D --> E[Async Scraper: crawl4ai ➔ raw HTML]
    E --> F[Parser & Cleaner: bs4 cleaning & validation]
    F --> G[Export Raw Articles .txt (topic.txt)]
    G --> H[Text Splitter & Summarization Chain: pydantic_ai via Brave Search + Context7]
    H --> I[Export Summaries .txt (topic_summed.txt)]
    I --> J[Supabase: Store Summaries & Mark Processed]
```

1. **Fetch Unprocessed**: Query Supabase for `Processed = false`. Save topic string.
2. **Search & URL Extraction**: Async HTTP call to Google; extract and score 10 candidate links.
3. **Top‑3 Selection**: Validate each URL; stop once 3 successful extractions are validated.
4. **Content Retrieval**: Use `crawl4ai` to fetch HTML.
5. **Validation & Cleaning**: BS4 routines for tag stripping, length, structure, language.
6. **Raw Export**: Write each validated article to `<topic>.txt` with `Title`, `Link`, and `Content`.
7. **Summarization**: Split text, then run a pydantic\_ai summarization agent—prompts and best practices retrieved via Brave Search MCP and orchestrated via Context7 MCP.
8. **Summary Export**: Write summaries to `<topic>_summed.txt`.
9. **Persistence & Cleanup**: Update Supabase record (summary field, processed flag), log completion.

## 4. Temporary Validation & Review Steps

* **Loop Limit:** Only first 3 validated articles per topic.
* **Export Files:** Two TXT exports for manual QA: raw and summed. Filenames derived from topic name.
* **Logging:** At each node—fetch, extract, validate, export, summarize—emit a `logfire` event (INFO for success, ERROR for failure).

## 5. Core Sections (Single‑File or Modules)

If collapsed into one file, demarcate with headers. Otherwise, follow module breakdown:

* **entrypoint.py** / **# SECTION: Entry**
* **Config & Env** / **# SECTION: Config**
* **DB Client** / **# SECTION: Supabase**
* **Search & Extraction** / **# SECTION: Search**
* **Validation** / **# SECTION: Validation & Cleaning**
* **Export Logic** / **# SECTION: File Export**
* **Summarization** / **# SECTION: Summarization**
* **Utils & Logging** / **# SECTION: Utils**

## 6. Tech Stack & Dependencies

* Python 3.13+
* `httpx`, `crawl4ai`, `beautifulsoup4`
* `pydantic`, `pydantic_ai`
* `logfire`
* `supabase-py`
* Langchain components (splitter) as needed
* RooCode MCP Servers: Brave Search, Context7, Supabase, Filesystem, logfire

## 7. Validation & Export Requirements

* **Article Validation:** Tag blacklist, length ≥500 chars, heading/paragraph minimums, English detection, no suspicious patterns.
* **Export Format:**

  ```text
  Title: {article_title}
  Link: {url}
  Content:
  {cleaned_text}
  ---
  ```
* **Summarization Agent:** Use `pydantic_ai` with prompt templates refined via Brave Search MCP best practices, integrated through Context7 MCP.

## 8. Logging Standards

* **logfire.info()**: start/end of each major step with context.
* **logfire.error()**: catch exceptions, include stack trace, topic, URL, iteration index.

---

*This plan includes temporary manual QA steps (TXT exports) that can be removed once end-to-end flow is stable.*
