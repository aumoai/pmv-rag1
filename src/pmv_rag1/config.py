from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Configuration
    API_TITLE: str = "RAG Chatbot API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Gemini API Configuration
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    # GEMINI_MODEL = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")

    # Vector Store Configuration
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "chroma")  # chroma, lancedb or faiss
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
    LANCEDB_URI: str = os.getenv("LANCEDB_URI", "./data/lancedb")
    LANCEDB_TABLE_NAME: str = os.getenv("LANCEDB_TABLE_NAME", "rag_documents")
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")

    # File Upload Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10")) * 1024 * 1024  # 10MB default
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx", ".txt", ".wav", ".mp3", ".m4a"}

    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_CONTEXT_LENGTH: int = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))

    # Speech Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    TEMP_AUDIO_DIR: str = os.getenv("TEMP_AUDIO_DIR", "./data/temp")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# Validate required environment variables
def validate_config():
    required_vars = ["GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not getattr(Config, var)]

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# Create directories if they don't exist
def create_directories():
    directories = [
        Config.UPLOAD_DIR,
        Config.TEMP_AUDIO_DIR,
        Config.CHROMA_PERSIST_DIRECTORY,
        Config.LANCEDB_URI,
        os.path.dirname(Config.FAISS_INDEX_PATH),
    ]

    for directory in directories:
        if "://" in directory:
            continue
        os.makedirs(directory, exist_ok=True)
