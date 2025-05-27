import asyncio
import os
from dotenv import load_dotenv
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from bs4 import BeautifulSoup # Potentially needed for fallback parsing

# 1. Project Setup & 2. Logfire Integration
# Ensure you have a .env file in the same directory with OPENROUTER_API_KEY="your_key_here"
load_dotenv()
logfire.configure() # Configure Logfire early
# logfire.instrument_pydantic_ai() # Instrument Pydantic-AI
logfire.instrument_pydantic()
logfire.info("Logfire configured and application started.")

# 3. OpenRouter Model Configuration
openrouter_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_key:
    logfire.error("OPENROUTER_API_KEY not found in .env file.")
    raise ValueError("OPENROUTER_API_KEY not found in .env file.")

model = OpenAIModel(
    model_name="meta-llama/llama-4-maverick:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_key
)

# 4. Define Article Data Structure
class ArticleContent(BaseModel):
    title: str = Field(description="The title of the article.")
    content: str = Field(description="The main body content of the article.")

# 5. Create Article Extraction Tool
async def extract_article_tool(ctx: RunContext, url: str) -> ArticleContent | str: # Unused
    """
    Extracts the main article title and content from a given URL.

    Args:
        ctx: The Pydantic-AI run context.
        url: The URL of the article to extract.

    Returns:
        An ArticleContent object with title and content, or a string with cleaned content if structured extraction fails.
    """
    try:
        logfire.debug("Extracting article for URL: {url} with context: {ctx}", url=url, ctx=ctx)
        browser_config = BrowserConfig(headless=True) # Run browser in headless mode
        # Configure LLM Extraction Strategy
        llm_strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="openrouter/quasar-alpha",
                api_token=openrouter_key,
                base_url="https://openrouter.ai/api/v1"
            ),
            schema=ArticleContent.model_json_schema(),
            extraction_type="schema",
            instruction="Extract ONLY the main article title and content from the provided webpage. Ignore headers, footers, sidebars, ads, comments, and any other non-article content. Provide the output as a JSON object matching the ArticleContent schema.",
            extra_args={"temperature": 0} # Keep temperature low for focused extraction
        )

        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS, # Bypass cache to get fresh content
            extraction_strategy=llm_strategy,
            page_timeout=60000 # Increase timeout for potentially slow pages
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=crawler_config)

        if result.success and result.extracted_content:
            try:
                # Attempt to parse the structured output
                article_data = ArticleContent.model_validate_json(result.extracted_content)
                logfire.info("Successfully extracted structured article content.")
                return article_data
            except Exception as e:
                logfire.error(f"Failed to parse structured content: {e}. Falling back to cleaning HTML.")
                # Fallback to BeautifulSoup if structured extraction fails
                if result.cleaned_html:
                    soup = BeautifulSoup(result.cleaned_html, 'html.parser')
                    # Basic attempt to find article-like content - this might need refinement
                    article_text = soup.find('article') or soup.find('main') or soup.find('div', class_='article-content') # Example selectors
                    if article_text:
                        logfire.info("Successfully extracted content using BeautifulSoup fallback.")
                        return article_text.get_text(separator='\n', strip=True)
                    else:
                        logfire.warn("Could not find main article content with BeautifulSoup.")
                        return "Could not extract article content."
                else:
                    logfire.warn("No cleaned HTML available for BeautifulSoup fallback.")
                    return "Could not extract article content."
        elif result.success:
             logfire.warn("Extraction successful, but no content was extracted by the LLM strategy.")
             # Consider BeautifulSoup fallback here as well if needed
             if result.cleaned_html:
                    soup = BeautifulSoup(result.cleaned_html, 'html.parser')
                    article_text = soup.find('article') or soup.find('main') or soup.find('div', class_='article-content') # Example selectors
                    if article_text:
                        logfire.info("Successfully extracted content using BeautifulSoup fallback.")
                        return article_text.get_text(separator='\n', strip=True)
                    else:
                        logfire.warn("Could not find main article content with BeautifulSoup.")
                        return "Could not extract article content."
             else:
                 logfire.warn("No cleaned HTML available for BeautifulSoup fallback.")
                 return "Could not extract article content."
        else:
            logfire.error(f"Crawling failed: {result.error_message}")
            return f"Error: Could not crawl the URL. {result.error_message}"

    except Exception as e:
        logfire.exception("An error occurred during article extraction.")
        return f"An unexpected error occurred: {e}"

# 6. Define the Main AI Agent
article_agent = Agent(
    model=model,
    tools=[extract_article_tool], # Register the extraction tool
    system_prompt=(
        "You are an AI assistant specialized in extracting article content from provided URLs. "
        "Your goal is to use the available tool to get the main title and content of the article "
        "and then present it clearly to the user."
    ),
)

# 7. Implement Main Script Logic & 8. Save Extracted Content
async def main():
    article_url = "https://www.zesteq.com/blogs/essential-oil/captivating-cinnamon-essential-oil-is-a-nature-s-superpower" # Hardcoded URL - REPLACE WITH ACTUAL URL

    logfire.info(f"Starting article extraction for URL: {article_url}")

    # Run the agent with the URL as the user prompt
    result = await article_agent.run(f"Please extract the article content from this URL: {article_url}")

    extracted_data = result.data

    if isinstance(extracted_data, ArticleContent):
        logfire.info("Agent successfully returned structured ArticleContent.")
        output_filename = "extracted_article.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(f"Title: {extracted_data.title}\n\n")
            f.write(extracted_data.content)
        logfire.info(f"Article content saved to {output_filename}")
        print(f"Article content saved to {output_filename}")
    elif isinstance(extracted_data, str):
        logfire.info("Agent returned cleaned text content.")
        output_filename = "extracted_article.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(extracted_data)
        logfire.info(f"Article content saved to {output_filename}")
        print(f"Article content saved to {output_filename}")
    else:
        logfire.error("Agent returned unexpected output type.")
        print("Failed to extract article content.")

if __name__ == "__main__":
    asyncio.run(main())