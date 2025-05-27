# Article Summarization Pipeline - Task List

## Current Tasks

### 1. Project Setup & Configuration

- [x] Create initial project structure
  - [x] Create root folder and `src/` directory
  - [x] Create `main.py` as application entry point
  - [x] Create `utils/`, `pipeline/`, and `agents/` folders
  - [x] Add `__init__.py` to all directories

- [x] Setup virtual environment
  - [x] Create venv (`python -m venv .venv`)
  - [x] Activate venv (`source .venv/bin/activate` or platform equivalent)
  - [x] Add `.venv/` to `.gitignore`

- [x] Install dependencies
  - [x] Create `requirements.txt` (placeholder)
  - [x] Add the following to `requirements.txt`:
    - `fastapi`  
    - `httpx`  
    - `beautifulsoup4`  
    - `pydantic`  
    - `logfire`  
    - `crawl4ai`  
    - `python-dotenv`  
    - `pydantic-ai`

- [x] Install development tools
  - [x] Add to `requirements.txt` or `dev-requirements.txt`:
    - `black`  
    - `pytest`  
    - `mypy`  
    - `ruff`  

- [x] Read `.env` file to provide runtime context
  - [x] Parse `.env` using `load_dotenv()`

- [x] Create `.gitignore`
  - [x] Ignore `.env`, `.venv/`, `__pycache__/`, `.DS_Store`, `*.txt` outputs
  - [x] Confirm structure with user before committing

- [x] Initialize logging with `logfire`
  - [x] Setup base logger in `logfire_config.py`
  - [x] Add structured logging context (e.g., step names, status)

### 2. Supabase Integration

- [x] Create Supabase client module
  - [x] Create file `db/supabase_client.py`
  - [x] Define `SupabaseClient` class
  - [x] Accept credentials from environment or passed config

- [x] Implement method to fetch unprocessed topics
  - [x] Method: `fetch_unprocessed_topics(limit: int) -> List[Dict]`
  - [x] Query `Test-Article to Social` table where `Processed = false`
  - [x] Sort by ID or created timestamp
  - [x] Limit the results to provided count (e.g., 1 or 5)
  - [x] Return topic `id` and `topic_name` as JSON-like dicts

- [x] Implement method to update a topic as processed
  - [x] Method: `mark_as_processed(id: str, summary: str) -> bool`
  - [x] Update row where `id = {id}`
  - [x] Set `Processed = true` and save generated `Summary`
  - [x] Return success flag or raise error

- [x] Handle connection errors or timeouts
  - [x] Log error if Supabase connection fails
  - [x] Use retry decorator (can be created in utils later)
  - [x] Include logfire context (e.g., `step=\"supabase.fetch\"`)

- [x] Add debug log outputs for:\n
  - [x] Fetched records
  - [x] Update status
  - [x] Payload validation (optional)

### 3. Topic-Based Article Search

- [x] Create Google search client
  - [x] Create file: `search/google_search.py`
  - [x] Define async function: `perform_search(topic: str) -> str`
  - [x] Construct Google search URL using topic string
  - [x] Use query filters to target blogs/articles (`inurl:blog OR inurl:article`)
  - [x] Add headers to mimic browser (User-Agent, Accept-Language, etc.)
  - [x] Use `httpx.AsyncClient` for the request
  - [x] Return full HTML string or raise error

- [x] Log all search activity
  - [x] Log start and end of search with topic name
  - [x] Log HTTP status code and any redirect URLs
  - [x] Capture exceptions using `logfire.error()`

- [x] Parse Google search HTML to extract URLs
  - [x] Create `extract_urls_from_html(html: str) -> List[str]`
  - [x] Use `bs4` to find anchor tags and URLs
  - [x] Clean and normalize links (remove `/url?q=` style wrappers)
  - [x] Apply exclusion filters (e.g., Google, Pinterest, YouTube)

- [x] Score and rank URLs by relevance
  - [x] Keywords: perfume, daily, blog, article, etc.
  - [x] Add bonus score for URLs with `/blog` or `/article`
  - [x] Return top 10 URLs sorted by score

- [x] Log all extraction outcomes
  - [x] Total URLs extracted
  - [x] Top 3 examples with scores
  - [x] Log if fewer than 3 valid URLs found

### 4. Article Retrieval Loop

- [x] Create article fetch loop controller
  - [x] Create `scraper/retrieve_articles.py`
  - [x] Function: `fetch_valid_articles(urls: List[str], max_count: int = 3) -> List[Article]`
  - [x] Initialize empty `valid_articles` list and `counter = 0`
  - [x] Loop through URLs one by one
    - [x] Fetch HTML using `crawl4ai`
    - [x] Validate content using custom parser (see section 5)
    - [x] If valid → `valid_articles.append(article)`, increment counter
    - [x] If invalid → log reason, move to next URL
    - [x] Exit loop once `counter == max_count`

- [x] Log loop activity
  - [x] For each URL: log attempt, status (valid/invalid), and reason if rejected
  - [x] On loop end: log total successful articles and how many were skipped

- [x] Define `Article` structure (can be dataclass or pydantic)
  - [x] Fields: `title: str`, `url: str`, `content: str`

- [x] Handle edge cases
  - [x] If fewer than 3 valid articles are available, proceed with what’s collected
  - [x] Log warning if successful count < 3

### 5. Parser & Cleaner

- [x] Create BS4 parser module
  - [x] File: `scraper/parser.py`
  - [x] Function `clean_html(html: str) -> str`
    - [x] Strip unwanted tags (`script`, `style`, `nav`, `footer`)
    - [x] Extract only `<p>`, `<h1–h6>`, `<ul>`, `<ol>` content
  - [x] Function `validate_text(text: str) -> Tuple[bool, List[str]]`
    - [x] Check length ≥ 500 chars
    - [x] Ensure ≥1 `<h1>` or ≥3 `<p>` tags
    - [x] Verify text/HTML ratio ≥ 0.7
    - [x] Confirm language is English

- [x] Log parsing results and validation failures via `logfire`

### 6. Article Export

- [x] Export validated articles to `<topic>.txt`
  - [x] Format: title, link, content with `---` separator
  - [x] Ensure filename is safe and unique
  - [x] Log success/failure of export

### 7. Summarization Pipeline

- [x] Chunk cleaned article content
  - [x] Create `nlp/splitter.py`
  - [x] Function: `split_text(text: str) -> List[str]`
    - [x] Use recursive character splitter logic with configurable chunk size and overlap
    - [x] Ensure chunks preserve semantic boundaries when possible

- [x] Retrieve summarization best practices via Brave Search MCP
  - [x] Query for LLM summarization prompt structures
  - [x] Extract combine-map-reduce style or alternative chaining formats
  - [x] Save/parse relevant prompt templates for agent use

- [x] Build summarization agent using pydantic_ai
  - [x] File: `agents/summarizer.py`
  - [x] Define `SummarizationAgent` class using `pydantic_ai`
  - [x] Use retrieved prompt as the template
  - [x] Accept chunked input and return summary string

- [x] Integrate Context7 MCP
  - [x] Translate prompt practices into Pydantic agent via MCP
  - [x] Wrap agent construction inside `context7.workflow` or MCP directive if applicable

- [x] Generate full summary
  - [x] Apply summarizer agent over all chunks
  - [x] Optionally combine outputs using `combine_map_prompt` style logic
  - [x] Log time taken and number of chunks processed

- [x] Export summary to `<topic>_summed.txt`
  - [x] Write final summary block to file
  - [x] Log export success and filepath


### 8. Final Update

### 8. Final Update

- [x] Update topic record in Supabase
  - [x] Reuse `SupabaseClient` from earlier step
  - [x] Method: `update_processed(id: str, summary: str) -> bool`
  - [x] Set `Processed = true` and store final summary in `Summary` field
  - [x] Log success or raise error on failure

- [x] Perform final cleanup
  - [x] Close any persistent HTTP sessions (e.g., `httpx.AsyncClient`)
  - [x] Ensure all file handles are closed
  - [x] Optionally delete TXT exports after review (configurable flag)

- [x] Log execution summary
  - [x] Topic name, number of articles processed, summary length
  - [x] Logfire final log: status = success or error
  - [x] Emit metrics for success/failure tracking (optional)


## Upcoming Tasks

*

## Discovered During Work

*

---

*Use this checklist to coordinate structured development. Each task corresponds to a critical step in building a production-grade article summarization pipeline.*
