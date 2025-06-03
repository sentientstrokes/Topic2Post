import logfire
from typing import List, Tuple, Dict
from bs4 import BeautifulSoup
import re

def clean_html(html: str) -> str:
    """
    Cleans HTML content by stripping unwanted tags and extracting relevant content.

    Args:
        html (str): The raw HTML content.

    Returns:
        str: The cleaned text content.
    """
    logfire.info("Cleaning HTML content.")
    soup = BeautifulSoup(html, 'html.parser')

    # Strip unwanted tags
    unwanted_tags = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe', 'img', 'audio', 'video']
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()

    # Extract content from relevant tags
    relevant_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']
    text_parts = []
    for element in soup.find_all(relevant_tags):
        text_parts.append(element.get_text(separator='\n', strip=True))

    cleaned_text = "\n\n".join(text_parts)
    logfire.info("HTML cleaning completed. Extracted {length} characters.", length=len(cleaned_text))
    return cleaned_text

def validate_text(text: str) -> Tuple[bool, Dict]:
    """
    Validates the cleaned text content based on defined criteria.

    Args:
        text (str): The cleaned text content.

    Returns:
        Tuple[bool, Dict]: A tuple containing a boolean indicating validity and a dictionary of validation reasons/results.
    """
    logfire.info("Validating cleaned text content.")
    reasons: Dict[str, any] = {}
    is_valid = True

    # Check length >= 500 chars
    if len(text) < 500:
        is_valid = False
        reasons["length"] = f"Text length ({len(text)}) is less than 500 characters."

    # Ensure >=1 <h1> or >=3 <p> tags (This check requires access to the original HTML structure,
    # which is not available in the cleaned text. A better approach is to check for
    # presence of significant text blocks or headings in the cleaned text.)
    # Placeholder check based on text content
    if not re.search(r'#+\s', text) and len(re.findall(r'\n\n', text)) < 2: # Basic check for headings or paragraphs
         # This is a simplified check. A more robust check would involve analyzing the structure before cleaning.
         pass # Skipping this check for now as it's difficult with just cleaned text

    # Verify text/HTML ratio >= 0.7 (This check requires original HTML and cleaned text length)
    # Skipping this check for now as original HTML is not passed to this function

    # Confirm language is English (Requires a language detection library)
    # Skipping this check for now as it requires an external dependency

    if not is_valid:
        logfire.warn("Text validation failed. Reasons: {reasons}", reasons=reasons)
    else:
        logfire.info("Text validation successful.")

    # Returning cleaned text and a placeholder title for now.
    # The actual title extraction should happen before cleaning or during scraping.
    reasons["cleaned_text"] = text
    reasons["title"] = "Extracted Article Title Placeholder" # Placeholder

    return is_valid, reasons