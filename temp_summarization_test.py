import os
import logfire
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Attempt to import document chains for map-reduce/refine
try:
    from langchain.chains.combine_documents import create_map_reduce_documents_chain
    from langchain.chains.combine_documents import create_refine_documents_chain
    # create_stuff_documents_chain is also in combine_documents, but we focus on map-reduce/refine
    # from langchain.chains.combine_documents import create_stuff_documents_chain
    logfire.info("Successfully imported Langchain map-reduce/refine document chains.")
    IMPORT_SUCCESS = True
except ImportError as e:
    logfire.error("ImportError: Could not import necessary Langchain map-reduce/refine document chains: {error}", error=e, exc_info=True)
    IMPORT_SUCCESS = False

from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain # Keep if needed for other tests, otherwise remove
from langchain_community.vectorstores import FAISS # Keep if needed for other tests, otherwise remove
from langchain_openai import OpenAIEmbeddings # Keep if needed for other tests, otherwise remove


# Load environment variables from .env file
load_dotenv()

# Configure Logfire (optional, but good for debugging)
logfire.configure()

def test_langchain_summarization(file_path: str):
    """
    Tests Langchain document summarization imports and logic.
    """
    logfire.info("Starting Langchain summarization test with file: {file_path}", file_path=file_path)

    # Read the content from the specified file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logfire.info("Successfully read content from {file_path}. Content length: {length}", file_path=file_path, length=len(content))
    except FileNotFoundError:
        logfire.error("Error: File not found at {file_path}", file_path=file_path)
        return
    except Exception as e:
        logfire.error("Error reading file {file_path}: {error}", file_path=file_path, error=e, exc_info=True)
        return

    # Create a Document object
    docs = [Document(page_content=content)]

    # Split the content into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunked_docs = text_splitter.split_documents(docs)
    logfire.info("Split content into {num_chunks} chunks.", num_chunks=len(chunked_docs))

    # Initialize the LLM
    # Use the same model as in the main project
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.environ.get("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

    # Attempt to use load_summarize_chain with map-reduce if imports were successful
    if IMPORT_SUCCESS:
        try:
            # Define prompt for map-reduce
            map_prompt_template = """The following is a set of documents
{docs}
Based on these documents, please identify the key points.
Key Points:"""
            map_prompt = PromptTemplate.from_template(map_prompt_template)

            reduce_prompt_template = """The following is a set of summaries:
{docs}
Take these and consolidate them into a concise, aggregated summary of the original documents.
Aggregated Summary:"""
            reduce_prompt = PromptTemplate.from_template(reduce_prompt_template)

            # Create the load_summarize_chain with map_reduce type and custom prompts
            chain = load_summarize_chain(
                llm,
                chain_type="map_reduce",
                map_prompt=map_prompt,
                combine_prompt=reduce_prompt,
                # Specify document variable names to match the prompts
                map_prompt_document_variable_name="docs",
                combine_prompt_document_variable_name="docs"
            )

            logfire.info("Attempting to run load_summarize_chain (map_reduce).")
            summary = chain.invoke(chunked_docs) # Use invoke as run is deprecated

            logfire.info("Langchain summarization test completed successfully.")
            logfire.info("Generated Summary: {summary}", summary=summary)

        except Exception as e:
            logfire.error("An error occurred during Langchain summarization chain execution: {error}", error=e, exc_info=True)
    else:
        logfire.warn("Skipping summarization chain execution due to import errors.")


if __name__ == "__main__":
    # Use the specified file for testing
    test_file = "winter-fragrances.txt" # Corrected to use raw article text
    test_langchain_summarization(test_file)
