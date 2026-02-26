"""Extraction agents for lease document processing."""

from typing import List

from agno.agent import Agent
from agno.models.azure.openai_chat import AzureOpenAI

from utils.config import (
    AZURE_MODEL_ID,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
)
from models.schemas import LeaseKVPairs, PageOCR, QAResponse
from prompts.prompts import qa_agent_prompt, extract_kv_pairs_prompt


def extract_kv_pairs(ocr_results: List[PageOCR]) -> LeaseKVPairs:
    """Extract structured KV pairs from OCR text.

    Args:
        ocr_results: List of PageOCR objects from OCR processing

    Returns:
        LeaseKVPairs object with extracted key-value pairs
    """
    # Filter out None values from ocr_results
    valid_results = [r for r in ocr_results if r is not None]

    if not valid_results:
        return LeaseKVPairs()

    full_text = "\n\n".join(
        [f"--- PAGE {r.page_number} ---\n{r.text}" for r in valid_results]
    )

    extraction_agent = Agent(
        model=AzureOpenAI(
            id=AZURE_MODEL_ID,
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        ),
        output_schema=LeaseKVPairs,
        instructions=extract_kv_pairs_prompt,
    )

    try:
        response = extraction_agent.run(
            f"Extract all lease details from this document:\n\n{full_text}"
        )

        # Handle response safely
        if response and hasattr(response, "content"):
            content = response.content
            if isinstance(content, LeaseKVPairs):
                return content
            elif isinstance(content, dict):
                return LeaseKVPairs(**content)

        # Fallback
        return LeaseKVPairs()
    except Exception as e:
        # Return safe default on error
        return LeaseKVPairs()


def answer_question(question: str, ocr_results: List[PageOCR]) -> QAResponse:
    """Answer questions about the lease document with page references and confidence.

    Args:
        question: The question to answer
        ocr_results: List of PageOCR objects from OCR processing

    Returns:
        QAResponse object with answer and metadata
    """
    # Filter out None values from ocr_results
    valid_results = [r for r in ocr_results if r is not None]

    if not valid_results:
        return QAResponse(
            answer="No document content available.",
            reference_pages=[],
            section_reference=None,
            confidence_sapp=0.0,
            relevant_excerpt="",
        )

    full_text = "\n\n".join(
        [f"--- PAGE {r.page_number} ---\n{r.text}" for r in valid_results]
    )

    qa_agent = Agent(
        model=AzureOpenAI(
            id=AZURE_MODEL_ID,
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        ),
        output_schema=QAResponse,
        instructions=qa_agent_prompt,
    )

    try:
        response = qa_agent.run(f"Document:\n{full_text}\n\nQuestion: {question}")

        # Handle response safely
        if response and hasattr(response, "content"):
            content = response.content
            if isinstance(content, QAResponse):
                return content
            elif isinstance(content, dict):
                return QAResponse(**content)

        # Fallback
        return QAResponse(
            answer="Unable to generate response",
            reference_pages=[],
            section_reference=None,
            confidence_sapp=0.0,
            relevant_excerpt="",
        )
    except Exception as e:
        # Return safe default on error
        return QAResponse(
            answer=f"Error processing question: {str(e)}",
            reference_pages=[],
            section_reference=None,
            confidence_sapp=0.0,
            relevant_excerpt="",
        )
