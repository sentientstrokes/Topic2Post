import asyncio
import logfire
from dotenv import load_dotenv
import os

# Import modules
from src.db.supabase_client import SupabaseClient
from src.search.google_search import perform_search, extract_urls_from_html
from src.scraper.retrieve_articles import fetch_valid_articles
from src.nlp.splitter import split_text
from src.agents.summarizer import SummarizationAgent
from src.pipeline.exporter import export_article_to_txt, export_summary_to_txt

load_dotenv()

async def main():
    """
    Main function to run the article extraction and summarization pipeline.
    """
    logfire.info("Starting the article extraction and summarization pipeline.")

    # 1. Fetch unprocessed topics from Supabase
    supabase_client = SupabaseClient()
    topics = supabase_client.fetch_unprocessed_topics(limit=1) # Fetch one topic for now
    
    if not topics:
        logfire.info("No unprocessed topics found. Exiting.")
        return

    for topic_data in topics:
        topic_id = topic_data.get('id')
        topic_name = topic_data.get('topic_name')
        
        if not topic_id or not topic_name:
            logfire.error("Skipping invalid topic data: {data}", data=topic_data)
            continue

        logfire.info("Processing topic: {topic_name}", topic_name=topic_name, topic_id=topic_id)

        try:
            # 2. Search the web for relevant articles
            search_html = await perform_search(topic_name)

            # 3. Extract and rank URLs
            article_urls = extract_urls_from_html(search_html)

            # 4. Retrieve and clean the top 3 articles
            valid_articles = await fetch_valid_articles(article_urls, max_count=3)

            if not valid_articles:
                logfire.warn("No valid articles found for topic: {topic_name}. Skipping summarization.", topic_name=topic_name)
                # Optionally mark as processed with a note about no articles found
                # supabase_client.mark_as_processed(topic_id, "No valid articles found.")
                continue

            # 5. Export raw articles for review
            for article in valid_articles:
                export_article_to_txt(article, topic_name)

            # 6. Summarize them via an LLM
            summarizer_agent = SummarizationAgent()
            full_summary = ""
            for article in valid_articles:
                logfire.info("Summarizing article: {article_url}", article_url=article.url)
                chunks = split_text(article.content)
                article_summary = await summarizer_agent.summarize_chunks(chunks)
                full_summary += f"Summary for {article.title} ({article.url}):\n{article_summary}\n\n"

            # 7. Export summaries
            summary_filepath = export_summary_to_txt(full_summary, topic_name)

            # 8. Save the results back to Supabase and mark as processed
            update_success = supabase_client.mark_as_processed(topic_id, full_summary)

            if update_success:
                logfire.info("Successfully processed and updated topic: {topic_name}", topic_name=topic_name, topic_id=topic_id)
            else:
                logfire.error("Failed to update topic in Supabase: {topic_name}", topic_name=topic_name, topic_id=topic_id)

        except Exception as e:
            logfire.error("An error occurred while processing topic {topic_name}: {error}",
                          topic_name=topic_name, error=e, exc_info=True)
            # Consider marking the topic as errored in Supabase if needed

    logfire.info("Article extraction and summarization pipeline finished.")

if __name__ == "__main__":
    asyncio.run(main())
