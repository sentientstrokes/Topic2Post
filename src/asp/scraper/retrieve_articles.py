import logfire
from typing import List, Dict, Tuple
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from asp.scraper.parser import clean_html, validate_text # Import the functions

# Define Article structure
class Article(BaseModel):
    """
    Represents a scraped article.
    """
    title: str
    url: str
    content: str

async def fetch_valid_articles(urls: List[str], max_count: int = 3) -> List[Article]:
    """
    Fetches and validates articles from a list of URLs.

    Args:
        urls (List[str]): A list of URLs to fetch articles from.
        max_count (int): The maximum number of valid articles to fetch.

    Returns:
        List[Article]: A list of valid Article objects.
    """
    logfire.info("Starting article fetching loop.", max_count=max_count)
    valid_articles: List[Article] = []
    async with AsyncWebCrawler() as crawler:
        for i, url in enumerate(urls):
            if len(valid_articles) >= max_count:
                logfire.info("Reached maximum number of valid articles ({max_count}). Stopping fetch loop.", max_count=max_count)
                break

            logfire.info("Attempting to fetch article from URL {index}/{total}: {url}",
                         index=i + 1, total=len(urls), url=url)
            try:
                # Fetch HTML using crawl4ai
                result = await crawler.arun(url=url)
                html_content = result.html # Access raw HTML from the result object
                fetched_url = result.url # Access the final URL from the result object

                if not result.success:
                    logfire.warn("Crawl failed for URL {url}. Error: {error}", url=url, error=result.error_message)
                    continue

                if not html_content:
                    logfire.warn("No HTML content fetched for URL: {url}", url=url)
                    continue

                # Clean the HTML content
                cleaned_text = clean_html(html_content)

                # Validate the cleaned text
                is_valid, validation_results = validate_text(cleaned_text)

                if is_valid:
                    # Assuming validate_text returns cleaned text and title in validation_results
                    article_title = validation_results.get('title', 'No Title') # Get title from validation results
                    valid_articles.append(Article(title=article_title, url=fetched_url, content=cleaned_text))
                    logfire.info("Successfully fetched and validated article from URL: {url}", url=fetched_url)
                else:
                    logfire.info("Article from URL {url} is invalid. Reasons: {reasons}",
                                 url=fetched_url, reasons=validation_results)

            except Exception as e:
                logfire.error("Error fetching or processing article from URL {url}: {error}",
                              url=url, error=e, exc_info=True)

    logfire.info("Finished article fetching loop. Total valid articles fetched: {count}", count=len(valid_articles))

    # Log warning if successful count < max_count
    if len(valid_articles) < max_count:
        logfire.warn("Fewer than requested valid articles fetched. Fetched {fetched_count} out of {max_count}.",
                     fetched_count=len(valid_articles), max_count=max_count)

    return valid_articles