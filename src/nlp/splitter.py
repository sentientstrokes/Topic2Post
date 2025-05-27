import logfire
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text(text: str) -> List[str]:
    """
    Splits text content into chunks using recursive character splitting.

    Args:
        text (str): The text content to split.

    Returns:
        List[str]: A list of text chunks.
    """
    logfire.info("Splitting text content into chunks.")
    # Configure the text splitter (example values, can be made configurable)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    chunks = text_splitter.split_text(text)
    logfire.info("Text splitting completed. Created {count} chunks.", count=len(chunks))
    return chunks