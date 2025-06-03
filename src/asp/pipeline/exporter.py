import logfire
import os
import re
from asp.scraper.retrieve_articles import Article

def export_article_to_txt(article: Article, topic: str) -> str:
    """
    Exports a validated article to a text file.

    Args:
        article (Article): The Article object to export.
        topic (str): The topic name to use for the filename.

    Returns:
        str: The path to the exported file.
    """
    logfire.info("Exporting article to text file.", article_url=article.url, topic=topic)

    # Create a safe filename from the topic
    safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().lower()
    safe_topic = re.sub(r'[-\s]+', '-', safe_topic)
    filename = f"{safe_topic}.txt"
    filepath = os.path.join(os.getcwd(), filename) # Export to current working directory

    content = f"Title: {article.title}\n"
    content += f"Link: {article.url}\n"
    content += "Content:\n"
    content += article.content
    content += "\n---\n" # Separator as specified

    try:
        with open(filepath, "a", encoding="utf-8") as f: # Use "a" for append mode
            f.write(content)
        logfire.info("Successfully exported article to {filepath}", filepath=filepath)
        return filepath
    except IOError as e:
        logfire.error("Error exporting article to file {filepath}: {error}", filepath=filepath, error=e, exc_info=True)
        raise # Re-raise the exception to be handled by the caller

def export_summary_to_txt(summary: str, topic: str) -> str:
    """
    Exports the article summary to a text file.

    Args:
        summary (str): The summary content.
        topic (str): The topic name to use for the filename.

    Returns:
        str: The path to the exported summary file.
    """
    logfire.info("Exporting summary to text file.", topic=topic)

    # Create a safe filename for the summary
    safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().lower()
    safe_topic = re.sub(r'[-\s]+', '-', safe_topic)
    filename = f"{safe_topic}_summed.txt"
    filepath = os.path.join(os.getcwd(), filename) # Export to current working directory

    try:
        with open(filepath, "w", encoding="utf-8") as f: # Use "w" for write mode (overwrite if exists)
            f.write(summary)
        logfire.info("Successfully exported summary to {filepath}", filepath=filepath)
        return filepath
    except IOError as e:
        logfire.error("Error exporting summary to file {filepath}: {error}", filepath=filepath, error=e, exc_info=True)
        raise # Re-raise the exception to be handled by the caller