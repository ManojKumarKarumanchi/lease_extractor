"""Streamlit UI for the lease extraction application."""

import json
import os
import tempfile

import streamlit as st

from utils.cache import (
    clear_cache,
    get_cache_count,
    get_file_hash,
    load_from_cache,
    save_to_cache,
)
from app.extraction import answer_question, extract_kv_pairs
from utils.ocr import parallel_ocr
from models.schemas import LeaseKVPairs, PageOCR, QAResponse, KV_FIELD_CATEGORIES


def render_ocr_results(ocr_results: list[PageOCR]) -> None:
    """Render OCR results for each page."""
    for page in ocr_results:
        with st.expander(
            f"Page {page.page_number} (confidence: {page.confidence:.0%})"
        ):
            st.markdown("**Full Text:**")
            st.text(page.text)
            if page.tables:
                st.markdown("**Tables:**")
                for table in page.tables:
                    st.markdown(table)
            if page.handwritten_notes:
                st.markdown("**Handwritten Notes:**")
                for note in page.handwritten_notes:
                    st.info(note)
            if page.signatures:
                st.markdown("**Signatures:**")
                for sig in page.signatures:
                    st.warning(sig)


def render_kv_pairs(kv_pairs: LeaseKVPairs) -> None:
    """Render extracted key-value pairs organized by category."""
    if not kv_pairs:
        return

    kv = kv_pairs
    data = {k: v for k, v in kv.model_dump().items() if v is not None}

    # Display by category
    for category, fields in KV_FIELD_CATEGORIES.items():
        category_data = {k: data[k] for k in fields if k in data}
        if category_data:
            with st.expander(
                f"📋 {category} ({len(category_data)} fields)",
                expanded=True,
            ):
                for k, v in category_data.items():
                    label = k.replace("_", " ").title()
                    st.markdown(f"**{label}:** {v}")

    # Download as JSON
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download as JSON",
            json.dumps(data, indent=2),
            "extracted_lease_summary.json",
            "application/json",
        )
    with col2:
        # Also show summary stats
        st.metric("Fields Extracted", len(data))


def render_qa_section(
    conversation_history: list,
    ocr_results: list[PageOCR],
) -> None:
    """Render the Q&A section with conversation history."""
    st.markdown(
        "❓ **Ask questions about the lease document.** Multi-turn conversation with source citations."
    )

    # Conversation history display
    if conversation_history:
        st.markdown("### 💬 Conversation History")
        for i, exchange in enumerate(conversation_history):
            # User question
            st.markdown(f"**Q{i+1}: {exchange['question']}**")

            # Assistant answer
            qa: QAResponse = exchange["answer"]
            st.write(qa.answer)

            # Source information in columns
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if qa.section_reference:
                    st.caption(f"📍 {qa.section_reference}")
                if qa.reference_pages:
                    page_refs = ", ".join([f"Page {p}" for p in qa.reference_pages])
                    st.caption(f"📄 {page_refs}")

            with col2:
                st.caption(f"Confidence: {qa.confidence_sapp:.0%}")

            with col3:
                relevance = (
                    "High"
                    if qa.confidence_sapp > 0.7
                    else "Medium" if qa.confidence_sapp > 0.4 else "Low"
                )
                st.caption(f"Relevance: {relevance}")

            # Supporting excerpt
            if qa.relevant_excerpt:
                with st.expander(f"📋 See excerpt for Q{i+1}"):
                    st.text_area(
                        f"Excerpt{i}",
                        value=qa.relevant_excerpt,
                        height=80,
                        disabled=True,
                        label_visibility="collapsed",
                    )

            st.divider()

    # New question input
    st.markdown("### Ask a New Question")
    question = st.text_input("Your question:")

    col_ask, col_clear = st.columns([4, 1])
    with col_ask:
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    with col_clear:
        clear_button = st.button("🗑️ Clear History", use_container_width=True)

    if ask_button and question:
        with st.spinner("Searching document..."):
            qa = answer_question(question, ocr_results)

        # Add to conversation history
        st.session_state.conversation_history.append(
            {"question": question, "answer": qa}
        )

        st.rerun()

    if clear_button:
        st.session_state.conversation_history = []
        st.rerun()


def render_sidebar() -> tuple:
    """Render the sidebar with upload and settings.

    Returns:
        Tuple of (uploaded_file, max_workers, dpi) or (None, None, None) if no file
    """
    with st.sidebar:
        st.header("📄 Document Management")

        # Show current document
        if st.session_state.current_filename:
            st.info(f"📌 Current: {st.session_state.current_filename}")

        st.subheader("Upload PDF")
        uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

        # OCR Settings
        st.markdown("⚙️ **OCR Settings**")
        max_workers = st.slider(
            "Parallel Workers", 1, 10, 5, help="More workers = faster processing"
        )
        dpi = st.select_slider(
            "Image Quality (DPI)",
            options=[150, 200, 300, 400, 600],
            value=400,
            help="Higher DPI = better text clarity (useful for small text/indices). 400 DPI recommended.",
        )

        if uploaded_file:
            # Read file and compute hash
            file_bytes = uploaded_file.read()
            file_hash = get_file_hash(file_bytes)

            # Check if file is already loaded
            if st.session_state.file_hash == file_hash:
                st.info("This document is already loaded!")
                if st.button("🔄 Reload from Disk", use_container_width=True):
                    cache_result = load_from_cache(file_hash)
                    if cache_result:
                        st.session_state.ocr_results, st.session_state.kv_pairs = (
                            cache_result
                        )
                        st.success("Loaded from cache!")
                        st.rerun()
            else:
                if st.button(
                    "🚀 Process PDF", type="primary", use_container_width=True
                ):
                    # Check cache first
                    cache_result = load_from_cache(file_hash)

                    if cache_result:
                        st.session_state.ocr_results, st.session_state.kv_pairs = (
                            cache_result
                        )
                        st.session_state.file_hash = file_hash
                        st.session_state.current_filename = uploaded_file.name
                        st.success("⚡ Loaded from cache (no processing needed)!")
                        st.rerun()
                    else:
                        # Save uploaded file
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".pdf"
                        ) as f:
                            f.write(file_bytes)
                            pdf_path = f.name

                        # Step 1: Parallel OCR
                        with st.spinner("⚡ Running parallel OCR on all pages..."):
                            st.session_state.ocr_results = parallel_ocr(
                                pdf_path, max_workers, dpi
                            )
                        st.success(
                            f"OCR complete: {len(st.session_state.ocr_results)} pages"
                        )

                        # Step 2: Extract KV pairs
                        with st.spinner("🔍 Extracting key-value pairs..."):
                            st.session_state.kv_pairs = extract_kv_pairs(
                                st.session_state.ocr_results
                            )
                        st.success("Extraction complete!")

                        # Save to cache
                        with st.spinner("💾 Saving to cache..."):
                            save_to_cache(
                                file_hash,
                                st.session_state.ocr_results,
                                st.session_state.kv_pairs,
                                uploaded_file.name,
                            )

                        # Update session state
                        st.session_state.file_hash = file_hash
                        st.session_state.current_filename = uploaded_file.name
                        st.session_state.conversation_history = (
                            []
                        )  # Reset chat for new document
                        st.rerun()

        # Cache Management
        st.divider()
        st.subheader("💾 Cache Management")
        cache_count = get_cache_count()
        st.caption(f"Cached documents: {cache_count}")

        if st.button("🗑️ Clear All Cache", use_container_width=True):
            clear_cache()
            st.session_state.file_hash = None
            st.session_state.current_filename = None
            st.rerun()

    return uploaded_file, max_workers, dpi


def init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "ocr_results" not in st.session_state:
        st.session_state.ocr_results = None
    if "kv_pairs" not in st.session_state:
        st.session_state.kv_pairs = None
    if "file_hash" not in st.session_state:
        st.session_state.file_hash = None
    if "current_filename" not in st.session_state:
        st.session_state.current_filename = None
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []


def main() -> None:
    """Main application entry point."""
    st.set_page_config(page_title="PDF OCR + Extraction", layout="wide")
    st.title("PDF OCR & Lease Extraction")

    # Initialize session state
    init_session_state()

    # Render sidebar
    render_sidebar()

    # Main content area
    if st.session_state.ocr_results:
        tab1, tab2, tab3 = st.tabs(["📝 OCR Results", "🔑 Extracted Fields", "❓ Q&A"])

        # Tab 1: OCR Results per page
        with tab1:
            render_ocr_results(st.session_state.ocr_results)

        # Tab 2: KV Pairs
        with tab2:
            if st.session_state.kv_pairs:
                render_kv_pairs(st.session_state.kv_pairs)

        # Tab 3: Q&A
        with tab3:
            render_qa_section(
                st.session_state.conversation_history,
                st.session_state.ocr_results,
            )


# if __name__ == "__main__":
#     main()
