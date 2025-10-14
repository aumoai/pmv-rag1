# 🐳 Docker FastAPI Service

This guide explains how to build and run the `pmv-rag1` FastAPI service with Docker.

## 📦 Dockerfile Overview

The `Dockerfile` packages the FastAPI application with the following features:

- **Multi-stage build** for optimized image size
- **Python 3.13** runtime managed with UV
- **Non-root user** for enhanced security
- **Uvicorn** application server bound to port **8000**

### Build Architecture

```dockerfile
Stage 1 (builder): ghcr.io/astral-sh/uv:python3.13-bookworm-slim
├── Install dependencies with UV
├── Copy source code
└── Build application

Stage 2 (runtime): python:3.13-slim-bookworm
├── Create non-root user (app:app)
├── Copy the virtual environment and source code
├── Set environment variables
└── Start the FastAPI service with Uvicorn
```

## 🚀 Quick Start

### 1. Build the Docker Image

```bash
docker build -t pmv-rag1:latest .
```

### 2. Run the FastAPI Service

```bash
# With environment file
docker run -p 8000:8000 --env-file .env pmv-rag1:latest

# With individual environment variables
docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your_gemini_api_key" \
  -e SECRET_KEY="your_secret" \
  pmv-rag1:latest
```

## ⚙️ Configuration

Copy `env.example` to `.env` before building or running the container so the image loads the expected configuration.

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Required Gemini API key used for both chat and embedding requests. |

### Optional API Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug logging for the API. | `False` |
| `SECRET_KEY` | Secret used for signing access tokens. | `your-secret-key-change-in-production` |

### Optional Gemini Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_MODEL` | Model used for chat completions. | `gemini-2.5-flash` |
| `GEMINI_EMBEDDING_MODEL` | Model used to generate embeddings. | `models/embedding-001` |

### Optional Vector Store Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `VECTOR_STORE_TYPE` | Backend for storing embeddings (`chroma`, `lancedb`, or `faiss`). | `chroma` |
| `CHROMA_PERSIST_DIRECTORY` | Directory for Chroma collections. | `./data/chroma_db` |
| `LANCEDB_URI` | Directory or URI for LanceDB storage. | `./data/lancedb` |
| `LANCEDB_TABLE_NAME` | Table name to use when LanceDB is selected. | `rag_documents` |
| `FAISS_INDEX_PATH` | Path to the FAISS index directory. | `./data/faiss_index` |

### Optional Upload Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `UPLOAD_DIR` | Directory used to persist uploaded documents. | `./data/uploads` |
| `MAX_FILE_SIZE` | Maximum upload size in megabytes. | `10` |

### Optional RAG Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `CHUNK_SIZE` | Token count per document chunk. | `1000` |
| `CHUNK_OVERLAP` | Overlap between sequential chunks. | `200` |
| `MAX_CONTEXT_LENGTH` | Maximum tokens supplied to the model. | `4000` |
| `TOP_K_RETRIEVAL` | Number of documents retrieved during RAG. | `5` |
| `SECRET_KEY` | Secret key used for session security | `change-me-in-prod` |


### Optional Speech Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `WHISPER_MODEL` | Whisper model variant used for transcription. | `base` |
| `TEMP_AUDIO_DIR` | Directory for temporary audio processing. | `./data/temp` |
| `DEBUG` | Enable debug logging | `False` |
| `VECTOR_STORE_TYPE` | Vector database backend (`chroma`, `lancedb`, `faiss`) | `chroma` |
| `CHROMA_PERSIST_DIRECTORY` | Directory for Chroma persistence | `./data/chroma_db` |
| `UPLOAD_DIR` | Directory for uploaded files | `./data/uploads` |
| `MAX_FILE_SIZE` | Maximum upload size in MB | `10` |

Refer to `.env.example` for the full list of configurable options.

## 🔧 Advanced Usage

### Custom Port Mapping
```bash
docker run -p 9000:8000 --env-file .env pmv-rag1:latest
```

### Volume Mounting for Persistent Data
```bash
# Mount local data directories for uploads and vector stores
docker run -p 8000:8000 --env-file .env \
  -v $(pwd)/data:/app/data \
  pmv-rag1:latest
```

### Debug Mode
```bash
docker run -p 8000:8000 --env-file .env \
  -e DEBUG=true \
  pmv-rag1:latest
```

## 🏥 Monitoring

Monitor the container and FastAPI service status:

```bash
# Check container status
docker ps

# Check if the Uvicorn process is running
docker exec <container_id> pgrep -f "uvicorn"

# View container logs
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>
```

## 🔍 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs <container_id>

# Run interactively for debugging
docker run -it --env-file .env pmv-rag1:latest bash
```

### Port Already in Use
```bash
# Use a different host port
docker run -p 9000:8000 --env-file .env pmv-rag1:latest
```

### API Key Issues
```bash
# Verify environment variables
docker run --env-file .env pmv-rag1:latest env | grep GEMINI_API_KEY

# Test Gemini connectivity
docker run -it --env-file .env pmv-rag1:latest \
  uv run python -c "print('Environment OK')"
```

## 📝 Development

### Building Different Versions
```bash
# Build with specific tag
docker build -t pmv-rag1:v1.0.0 .

# Build a development version with cache busting
docker build --no-cache -t pmv-rag1:dev .
```

### Testing the Container
```bash
# Run tests inside the container
docker run --env-file .env pmv-rag1:latest \
  uv run pytest

# Interactive development
docker run -it -v $(pwd):/app --env-file .env \
  pmv-rag1:latest bash
```

## 🚢 Deployment

### Docker Compose (Recommended)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  fastapi-server:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./data:/app/data  # Optional: for persistent storage
    # Optional: Uncomment for health checks
    # healthcheck:
    #   test: ["CMD", "pgrep", "-f", "uvicorn"]
    #   interval: 30s
    #   timeout: 10s
    #   retries: 3
    #   start_period: 40s
```

Run with:
```bash
docker-compose -f docker-compose.yml up -d
```

### Production Considerations

1. **Security**: Use secrets management for API keys.
2. **Monitoring**: Integrate container logs with your monitoring stack.
3. **Logging**: Configure log aggregation (e.g., Fluent Bit, Loki, or CloudWatch).
4. **Backup**: Persist important data volumes (uploads, vector stores).
5. **Updates**: Automate image rebuilds and deployments.

## 📊 Container Specifications

| Aspect | Details |
|--------|---------|
| Base Image | `python:3.13-slim-bookworm` |
| Package Manager | UV (ultra-fast Python package manager) |
| User | Non-root (`app:app`, UID/GID 1000) |
| Working Directory | `/app` |
| Default Port | `8000` |
| Health Check | Manual monitoring only |
| Entry Point | `uv` |
| Default Command | `uvicorn pmv_rag1.main:app --host 0.0.0.0 --port 8000` |

This Docker setup provides a robust, secure, and efficient way to deploy the `pmv-rag1` FastAPI service.
