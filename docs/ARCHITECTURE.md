# System Architecture Overview

This document summarizes how the PMV RAG API is assembled so that an autonomous
coding agent can reason about the codebase and implement new features safely.

## Runtime Topology

The FastAPI application in `pmv_rag1.main` is the single runtime entry point. It
validates environment variables, creates data directories, attaches permissive
CORS middleware, and wires the text, file, and speech routers under the
`/api/v1` prefix while exposing health probes and a catch-all exception handler.
All configuration values flow from `pmv_rag1.config.Config`, which reads
`.env`/environment variables and centralizes limits (chunk sizes, vector store
backend, upload quotas, API keys).

The API is designed for synchronous HTTP clients; long-running work (e.g.,
Gemini calls, Whisper transcription, audio conversion) is offloaded to thread
pools via `asyncio.to_thread` to keep the event loop responsive.

## Layered Responsibilities

```
FastAPI Routers → Orchestrator Service → RAG Pipeline & Gemini Client → Vector Store & External APIs
```

### Presentation Layer (Routers)
- **Text (`api/text_route.py`)** – Delegates plain queries to the orchestrator,
and optionally accepts an ad-hoc document upload for single-request context. The
`/text-with-file` variant stores the upload in a temp directory, parses it via
`FileParser`, and skips persistent indexing.
- **File (`api/file_route.py`)** – Validates extensions/size, persists uploads to
`Config.UPLOAD_DIR`, extracts text, and forwards content to the orchestrator for
chunking and indexing. A placeholder `/files` listing and `/file/{file_id}`
delete endpoint are stubbed for future work.
- **Speech (`api/speech_route.py`)** – Accepts audio uploads, validates/limits
size, converts to WAV with `audio_utils`, transcribes with `SpeechToText`, and
feeds the recognized text back into the text workflow.

Routers instantiate shared singletons (`Orchestrator`, `FileParser`,
`SpeechToText`) at import time so future handlers should reuse them rather than
creating new instances per request.

### Service Layer
- **Orchestrator** – Coordinates query cleaning, context retrieval, Gemini
response generation, file ingestion, and document deletion. It is the main
integration point if you need to add chat history, alternative retrieval
strategies, or non-text modalities.
- **RAGPipeline** – Splits documents with LangChain’s
`RecursiveCharacterTextSplitter`, enforces context length limits, and queries
the vector store with or without metadata filters. It is intentionally thin so
new retrieval modes (reranking, hybrid search) should extend here.
- **GeminiClient** – Wraps the Google Gemini SDK, exposes `generate_response`
and `get_embeddings`, and centralizes prompt templates for vanilla, document,
and file-specific interactions. Prompt localization is currently hard-coded to
Burmese.

### Data Access Layer
- **VectorStore** – Initializes the configured backend (Chroma today, FAISS
placeholders for future use), manages embeddings via `GeminiClient`, and exposes
`add_documents`, similarity search (optionally filtered by metadata), deletion
by metadata, and collection stats. All methods are async to match the service
layer.

## Supporting Components

- **FileParser** – Handles PDF (PyPDF2), DOCX (`python-docx`), TXT, and image
files (returned as raw bytes; no OCR). Future pipelines must guard against bytes
payloads before assuming textual context.
- **SpeechToText** – Lazily loads one of multiple Whisper implementations
(`faster-whisper`, `openai-whisper`, or `whisperx`) with automatic detection.
Transcription results feed the text handler, and optional timestamp / TTS helpers
are available for extension.
- **Utilities** – `audio_utils` covers validation, format conversion (via
pydub), normalization, trimming, and temp cleanup; `mime_utils` encapsulates
extension/MIME logic, safe filenames, and supported type registries.

## Data & Deployment Considerations

- **Persistence** – The repo expects `./data/uploads` for raw files,
`./data/chroma_db` for vector persistence, and `./data/temp` for scratch space.
All directories are auto-created during startup.
- **Asynchronous Safety** – Long CPU/IO calls are dispatched to worker threads;
when adding heavy logic, follow this pattern or use background tasks to avoid
blocking the event loop.
- **Environment** – A valid `GEMINI_API_KEY` is mandatory. Chunk sizing and
retrieval fan-out are configurable for experimentation without code changes.

## Extensibility Notes

- To integrate new retrieval algorithms, extend `RAGPipeline` (e.g., rerankers)
and keep the orchestrator surface area stable.
- To support additional storage engines, flesh out the FAISS stubs or add new
branches in `VectorStore.__init__` and its helper methods.
- To persist chat history, implement the TODOs inside `Orchestrator` and align
router handlers to store metadata per session/user.
- For multimodal support (e.g., OCR), augment `FileParser.extract_text` to
return structured payloads and update the orchestrator to branch on response
types.

