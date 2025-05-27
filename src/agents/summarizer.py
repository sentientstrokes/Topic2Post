import logfire
from pydantic import BaseModel
from pydantic_ai import PydanticAI
from typing import List

# Define a simple Pydantic model for the summary output
class ArticleSummary(BaseModel):
    """
    Represents the summary of an article.
    """
    summary: str

class SummarizationAgent:
    """
    Agent for summarizing text using pydantic-ai.
    """
    def __init__(self):
        """
        Initializes the SummarizationAgent.
        """
        # Placeholder prompt template - will be refined based on Brave Search results
        self.prompt_template = """
        Summarize the following article text concisely, focusing on the main points and key information.
        The summary should be easy to read and understand.

        Text to summarize:
        {text_chunk}
        """
        self.ai = PydanticAI(output_model=ArticleSummary)

    async def summarize_chunk(self, text_chunk: str) -> str:
        """
        Summarizes a single text chunk.

        Args:
            text_chunk (str): The text chunk to summarize.

        Returns:
            str: The summary of the text chunk.
        """
        logfire.info("Summarizing text chunk.")
        try:
            # Format the prompt with the text chunk
            prompt = self.prompt_template.format(text_chunk=text_chunk)
            # Use pydantic-ai to generate the summary
            result: ArticleSummary = await self.ai.generate(prompt=prompt)
            logfire.debug("Chunk summarization completed.")
            return result.summary
        except Exception as e:
            logfire.error("Error summarizing text chunk: {error}", error=e, exc_info=True)
            # Depending on error handling strategy, might return empty string or re-raise
            return "" # Return empty string for now on error

    async def summarize_chunks(self, text_chunks: List[str]) -> str:
        """
        Summarizes a list of text chunks and combines the summaries.

        Args:
            text_chunks (List[str]): A list of text chunks to summarize.

        Returns:
            str: The combined summary of all chunks.
        """
        logfire.info("Summarizing multiple text chunks.", num_chunks=len(text_chunks))
        summaries = []
        for i, chunk in enumerate(text_chunks):
            logfire.debug("Summarizing chunk {index}/{total}", index=i+1, total=len(text_chunks))
            summary = await self.summarize_chunk(chunk)
            if summary:
                summaries.append(summary)

        # Combine summaries (simple concatenation for now, can be refined)
        combined_summary = "\n\n".join(summaries)
        logfire.info("Combined summaries from {num_chunks} chunks.", num_chunks=len(text_chunks))
        return combined_summary