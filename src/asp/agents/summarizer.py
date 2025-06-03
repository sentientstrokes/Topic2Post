import os
import logfire
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain # Import LLMChain for manual summarization

# Environment variable name for the OpenRouter API key
OPENROUTER_API_KEY_ENV_VAR = "OPENROUTER_API_KEY"

async def summarize_chunks_langchain(text_chunks: List[str]) -> str:
    """
    Summarizes a list of text chunks using a manual Langchain approach.

    Args:
        text_chunks (List[str]): A list of text chunks to summarize.

    Returns:
        str: The combined summary of all chunks.
    """
    logfire.info("Summarizing multiple text chunks using manual Langchain approach.", num_chunks=len(text_chunks))

    openrouter_api_key = os.environ.get(OPENROUTER_API_KEY_ENV_VAR)
    if not openrouter_api_key:
        logfire.error("OpenRouter API key not found in environment variables.")
        raise ValueError(f"{OPENROUTER_API_KEY_ENV_VAR} environment variable not set.")

    # Configure the LLM to use OpenRouter
    llm = ChatOpenAI(
        model="gpt-3.5-turbo", # Using a standard model name
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key
    )

    # Define the summarization prompt template for individual chunks
    summarize_prompt_template = """
    Summarize the following text chunk concisely, focusing on the main points.

    Text chunk:
    {text_chunk}
    """
    summarize_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that summarizes text chunks."),
        ("human", summarize_prompt_template)
    ])

    # Create an LLMChain for summarizing individual chunks
    summarize_chain = LLMChain(llm=llm, prompt=summarize_prompt)

    chunk_summaries = []
    for i, chunk in enumerate(text_chunks):
        logfire.debug("Summarizing chunk {index}/{total}", index=i+1, total=len(text_chunks))
        try:
            # Invoke the LLMChain for the current chunk
            # The result from LLMChain.ainvoke is a dictionary, the summary is in the 'text' key
            result = await summarize_chain.ainvoke({"text_chunk": chunk})
            chunk_summary = result.get('text', '') # Get the summary text

            if chunk_summary:
                chunk_summaries.append(chunk_summary)
            else:
                 logfire.warn("Summarization returned empty for chunk {index}.", index=i+1)

        except Exception as e:
            logfire.error("Error summarizing chunk {index}: {error}", index=i+1, error=e, exc_info=True)
            # Continue to the next chunk even if one fails

    # Manually combine the individual chunk summaries
    combined_summary = "\n\n".join(chunk_summaries)

    logfire.info("Manual Langchain summarization completed. Combined summaries from {num_successful_chunks} chunks.", num_successful_chunks=len(chunk_summaries))

    return combined_summary

# The old SummarizationAgent class and document chain logic are replaced