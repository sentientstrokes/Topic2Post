import os
import httpx
from typing import List, Dict, Any
import logfire

# Environment variable name for the Brave Search API key
BRAVE_API_KEY_ENV_VAR = "BRAVE_API_KEY"
BRAVE_SEARCH_API_URL = "https://api.search.brave.com/res/v1/web/search"

async def perform_brave_search(topic: str) -> List[Dict[str, Any]]:
    """
    Performs a web search for a given topic using the Brave Search API.

    Args:
        topic (str): The topic to search for.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a search result.
                                Expected keys: 'url', 'title', 'description'.
    """
    logfire.info("Performing web search for topic: {topic} using Brave Search API", topic=topic)

    brave_api_key = os.getenv(BRAVE_API_KEY_ENV_VAR)
    if not brave_api_key:
        logfire.error("Brave Search API key not found in environment variables.")
        raise ValueError(f"{BRAVE_API_KEY_ENV_VAR} environment variable not set.")

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": brave_api_key,
    }

    params = {
        "q": f"{topic} blog article", # Added keywords to query
        "count": 10 # Request 10 results
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BRAVE_SEARCH_API_URL, headers=headers, params=params)
            response.raise_for_status() # Raise an exception for bad status codes

            search_results = response.json()

            if search_results and 'web' in search_results and 'results' in search_results['web']:
                results_list = search_results['web']['results']
                logfire.info("Brave Search API call successful. Found {count} results.", count=len(results_list))
                return results_list
            else:
                logfire.warn("Brave Search API returned no results or unexpected format for topic {topic}.", topic=topic)
                return []

        except httpx.HTTPStatusError as e:
            logfire.error("HTTP error during Brave Search API call for topic {topic}: {error}",
                          topic=topic, error=e, exc_info=True)
            raise # Re-raise the exception
        except httpx.RequestError as e:
            logfire.error("Request error during Brave Search API call for topic {topic}: {error}",
                          topic=topic, error=e, exc_info=True)
            raise # Re-raise the exception
        except Exception as e:
            logfire.error("An unexpected error occurred during Brave Search API call for topic {topic}: {error}",
                          topic=topic, error=e, exc_info=True)
            raise # Re-raise the exception

def score_and_rank_urls(search_results: List[Dict[str, Any]]) -> List[str]:
    """
    Scores and ranks search result URLs based on content and structure.

    Args:
        search_results (List[Dict[str, Any]]): A list of dictionaries, each representing a search result.
                                                Expected keys: 'url', 'title', 'description'.

    Returns:
        List[str]: A list of the top 10 ranked URLs.
    """
    logfire.info("Scoring and ranking search results from Brave Search.")
    scored_urls = []

    for result in search_results:
        url = result.get('url')
        title = result.get('title', '')
        description = result.get('description', '')

        if url:
            score = 0
            # Basic scoring based on keywords in URL, title, and description
            content_to_score = f"{url.lower()} {title.lower()} {description.lower()}"
            if 'blog' in content_to_score or 'article' in content_to_score:
                score += 2
            if 'daily' in content_to_score:
                score += 1
            # Add more scoring criteria based on relevance to the topic if needed

            scored_urls.append((url, score))

    # Sort URLs by score in descending order and get the top 10
    scored_urls.sort(key=lambda item: item[1], reverse=True)
    top_10_urls = [url for url, score in scored_urls[:10]]

    logfire.info("Scored and ranked {total_count} potential URLs. Returning top {top_count}.",
                 total_count=len(scored_urls), top_count=len(top_10_urls))

    # Log top 3 examples with scores
    for i, (url, score) in enumerate(scored_urls[:3]):
        logfire.debug("Top URL {index}: {url} (Score: {score})", index=i+1, url=url, score=score)

    # Log if fewer than 3 valid URLs found
    if len(top_10_urls) < 3:
        logfire.warn("Fewer than 3 potential URLs found after scoring and ranking. Found {count}.", count=len(top_10_urls))

    return top_10_urls

# The extract_urls_from_html function is no longer needed
# def extract_urls_from_html(html: str) -> List[str]:
#     pass # This function is deprecated