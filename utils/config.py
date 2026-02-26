"""Configuration for Azure OpenAI integration and caching."""

import os
from dotenv import load_dotenv

load_dotenv()

AZURE_MODEL_ID = os.getenv("AZURE_DEPLOYMENT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION", "2024-12-01-preview")

CACHE_DIR = os.path.join(os.getcwd(), ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)
