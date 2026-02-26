"""OCR functionality for PDF documents using Azure OpenAI Vision."""

import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import List

import fitz

from agno.agent import Agent
from agno.media import Image
from agno.models.azure.openai_chat import AzureOpenAI

from utils.config import (
    AZURE_MODEL_ID,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
)
from models.schemas import PageOCR


def ocr_single_page_from_path(img_path: str, page_num: int) -> PageOCR:
    """OCR a single page from image file using Azure OpenAI vision."""
    ocr_agent = Agent(
        model=AzureOpenAI(
            id=AZURE_MODEL_ID,
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        ),
        output_schema=PageOCR,
        instructions=[
            f"You are an expert OCR agent. This is page {page_num}.",
            "Extract ALL text: printed, handwritten, signatures, stamps.",
            "Reproduce tables in markdown format.",
            "Identify handwritten notes separately.",
            "Describe any signatures found.",
            "Rate your confidence from 0 to 1.",
        ],
    )

    try:
        response = ocr_agent.run(
            f"Extract everything from page {page_num} of this document. "
            "Include all printed text, handwritten text, tables, and signatures.",
            images=[Image(filepath=img_path)],
        )

        # Handle response safely
        if response and hasattr(response, "content"):
            content = response.content
            if isinstance(content, PageOCR):
                return content
            elif isinstance(content, dict):
                # Ensure page_number is set
                if "page_number" not in content:
                    content["page_number"] = page_num
                return PageOCR(**content)

        # Fallback
        return PageOCR(
            page_number=page_num, text="No content extracted", confidence=0.0
        )
    except Exception as e:
        # Return safe default on error
        return PageOCR(page_number=page_num, text=f"Error: {str(e)}", confidence=0.0)


def pdf_to_images(pdf_path: str, dpi: int = 600) -> List[str]:
    """Convert PDF pages to images using PyMuPDF (no Poppler needed).

    Optimized for OCR with grayscale conversion.

    Args:
        pdf_path: Path to PDF file
        dpi: Dots per inch for image quality (default 600, use 400 for speed)

    Returns:
        List of paths to generated image files
    """
    temp_dir = tempfile.mkdtemp()
    doc = fitz.open(pdf_path)
    images = []

    for page_num, page in enumerate(doc):
        # Direct DPI approach with grayscale - better for OCR
        # colorspace=fitz.csGRAY ensures 8-bit grayscale for better text recognition
        pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
        img_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
        pix.save(img_path)
        images.append(img_path)

    doc.close()
    return images


def parallel_ocr(pdf_path: str, max_workers: int = 5, dpi: int = 600) -> List[PageOCR]:
    """Process all PDF pages in parallel.

    Args:
        pdf_path: Path to PDF file
        max_workers: Number of concurrent workers
        dpi: Image DPI for text extraction (600 default, 400 for speed)

    Returns:
        List of PageOCR objects for each page
    """
    img_paths = pdf_to_images(pdf_path, dpi=dpi)

    results = [None] * len(img_paths)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(ocr_single_page_from_path, path, i + 1): i
            for i, path in enumerate(img_paths)
        }
        for future in futures:
            idx = futures[future]
            results[idx] = future.result()

    return results
