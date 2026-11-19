
import os

# --------------------------------------------------
# LLM PROVIDER CONFIGURATION
# --------------------------------------------------

LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "http://localhost:11434/v1"
)

LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "qwen3.5:4b-q4_K_M"
)


# --------------------------------------------------
# EMBEDDING CONFIGURATION
# --------------------------------------------------

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"
)

EMBEDDING_BASE_URL = os.getenv(
    "EMBEDDING_BASE_URL",
    "http://localhost:11434/v1"
)


# --------------------------------------------------
# DOCUMENT INGESTION CONFIGURATION
# --------------------------------------------------

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
BATCH_SIZE = 32


# --------------------------------------------------
# RETRIEVAL CONFIGURATION
# --------------------------------------------------

TOP_K = 5
MAX_DISTANCE = 0.37
COLLECTION_NAME = "novatech_documents"


# --------------------------------------------------
# GENERATION CONFIGURATION
# --------------------------------------------------

TEMPERATURE = 0.1

REASONING_EFFORT = os.getenv(
    "REASONING_EFFORT",
    "none"
)

MAX_TOKENS = 1024

TOKEN_LIMIT_PARAM = os.getenv(
    "TOKEN_LIMIT_PARAM",
    "max_tokens"
)
