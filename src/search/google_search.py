import httpx
import logfire
from bs4 import BeautifulSoup
from typing import List

async def perform_search(topic: str) -> str:
    """
    Performs a Google search for a given topic and returns the HTML content.

    Args:
        topic (str): The topic to search for.

    Returns:
        str: The HTML content of the search results page.
    """
    logfire.info("Performing Google search for topic: {topic}", topic=topic)
    search_url = f"https://www.google.com/search?q={topic} inurl:blog OR inurl:article"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(search_url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            logfire.info("Google search for topic {topic} completed with status code {status_code}",
                         topic=topic, status_code=response.status_code)
            return response.text
        except httpx.HTTPStatusError as e:
            logfire.error("HTTP error during Google search for topic {topic}: {error}",
                          topic=topic, error=e, exc_info=True)
            raise
        except httpx.RequestError as e:
            logfire.error("Request error during Google search for topic {topic}: {error}",
                          topic=topic, error=e, exc_info=True)
            raise

def extract_urls_from_html(html: str) -> List[str]:
    """
    Extracts, scores, and ranks URLs from Google search results HTML.

    Args:
        html (str): The HTML content of the search results page.

    Returns:
        List[str]: A list of the top 10 extracted and ranked URLs.
    """
    logfire.info("Extracting, scoring, and ranking URLs from search results HTML.")
    soup = BeautifulSoup(html, 'html.parser')
    scored_urls = []
    # Find all anchor tags
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            # Clean and normalize links (remove /url?q= wrappers)
            if href.startswith('/url?q='):
                href = href.split('/url?q=')[1].split('&')[0]

            # Apply exclusion filters (e.g., Google, Pinterest, YouTube)
            excluded_domains = ['google.com', 'pinterest.com', 'youtube.com']
            if not any(domain in href for domain in excluded_domains):
                score = 0
                # Basic scoring based on keywords and URL structure
                if 'blog' in href.lower() or 'article' in href.lower():
                    score += 2
                if 'daily' in href.lower():
                    score += 1
                # Add more scoring criteria based on relevance to the topic if needed

                scored_urls.append((href, score))

    # Sort URLs by score in descending order and get the top 10
    scored_urls.sort(key=lambda item: item[1], reverse=True)
    top_10_urls = [url for url, score in scored_urls[:10]]

    logfire.info("Extracted and ranked {total_count} potential URLs. Returning top {top_count}.",
                 total_count=len(scored_urls), top_count=len(top_10_urls))

    # Log top 3 examples with scores
    for i, (url, score) in enumerate(scored_urls[:3]):
        logfire.debug("Top URL {index}: {url} (Score: {score})", index=i+1, url=url, score=score)

    # Log if fewer than 3 valid URLs found
    if len(top_10_urls) < 3:
        logfire.warn("Fewer than 3 potential URLs found after extraction and ranking. Found {count}.", count=len(top_10_urls))

    return top_10_urls