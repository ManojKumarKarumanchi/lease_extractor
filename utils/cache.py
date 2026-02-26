"""Cache management for OCR and extraction results."""

import hashlib
import json
import os
from typing import List, Optional, Tuple

import streamlit as st

from utils.config import CACHE_DIR
from models.schemas import LeaseKVPairs, PageOCR


def get_file_hash(file_bytes: bytes) -> str:
    """Generate SHA256 hash of file content."""
    return hashlib.sha256(file_bytes).hexdigest()


def get_cache_path(file_hash: str) -> dict:
    """Get cache file paths for OCR and KV extraction."""
    return {
        "ocr": os.path.join(CACHE_DIR, f"{file_hash}_ocr.json"),
        "kv": os.path.join(CACHE_DIR, f"{file_hash}_kv.json"),
        "metadata": os.path.join(CACHE_DIR, f"{file_hash}_metadata.json"),
    }


def load_from_cache(file_hash: str) -> Optional[Tuple[List[PageOCR], LeaseKVPairs]]:
    """Load cached OCR and KV results.

    Returns:
        Tuple of (ocr_results, kv_pairs) or None if cache doesn't exist.
    """
    cache_paths = get_cache_path(file_hash)

    if not os.path.exists(cache_paths["ocr"]) or not os.path.exists(cache_paths["kv"]):
        return None

    try:
        # Load OCR results
        with open(cache_paths["ocr"], "r") as f:
            ocr_data = json.load(f)
        ocr_results = [PageOCR(**item) for item in ocr_data]

        # Load KV pairs
        with open(cache_paths["kv"], "r") as f:
            kv_data = json.load(f)
        kv_pairs = LeaseKVPairs(**kv_data)

        return (ocr_results, kv_pairs)
    except Exception as e:
        st.warning(f"Failed to load cache: {str(e)}")
        return None


def save_to_cache(
    file_hash: str,
    ocr_results: List[PageOCR],
    kv_pairs: LeaseKVPairs,
    filename: str = "",
) -> None:
    """Save OCR and KV results to cache."""
    cache_paths = get_cache_path(file_hash)

    try:
        # Save OCR results
        ocr_data = [r.model_dump() for r in ocr_results]
        with open(cache_paths["ocr"], "w") as f:
            json.dump(ocr_data, f, indent=2)

        # Save KV pairs
        kv_data = kv_pairs.model_dump()
        with open(cache_paths["kv"], "w") as f:
            json.dump(kv_data, f, indent=2)

        # Save metadata
        metadata = {
            "filename": filename,
            "file_hash": file_hash,
            "timestamp": str(os.path.getctime(cache_paths["ocr"])),
        }
        with open(cache_paths["metadata"], "w") as f:
            json.dump(metadata, f, indent=2)

        st.success("✅ Results cached for faster access later!")
    except Exception as e:
        st.warning(f"Failed to cache results: {str(e)}")


def clear_cache() -> None:
    """Clear all cached files."""
    try:
        import shutil

        for file in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        st.success("✅ Cache cleared!")
    except Exception as e:
        st.error(f"Failed to clear cache: {str(e)}")


def get_cache_count() -> int:
    """Get the number of cached documents."""
    try:
        cache_files = [
            f for f in os.listdir(CACHE_DIR) if f.endswith(".json")
        ]
        return len(cache_files) // 3 if cache_files else 0
    except Exception:
        return 0
