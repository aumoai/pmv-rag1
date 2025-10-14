# 🐳 Docker MCP Server

This document explains how to build and run the Snapture SQL Agent MCP server using Docker.

## 📦 Dockerfile.mcp Overview

The `Dockerfile` creates a containerized version of the MCP server with the following features:

- **Multi-stage build** for optimized image size
- **Python 3.13** runtime with UV package manager
- **Non-root user** for enhanced security
- **Manual monitoring** capabilities
- **Port 3000** exposed for HTTP transport
- **FastMCP 2.0** for MCP server functionality

### Build Architecture

```dockerfile
Stage 1 (builder): ghcr.io/astral-sh/uv:python3.13-bookworm-slim
├── Install dependencies with UV
├── Copy source code
└── Build application

Stage 2 (runtime): python:3.13-slim-bookworm
├── Create non-root user (app:app)
├── Copy built application from builder
├── Set environment variables
└── Configure MCP server
```

## 🚀 Quick Start

### 1. Build the Docker Image

```bash
# Using the build script (recommended)
./devtools/build-mcp-docker.sh

# Or manually
docker build -f Dockerfile -t pmv-rag1:latest .
```

### 2. Run the MCP Server

#### HTTP Mode (Default)
```bash
# With environment file
docker run -p 3000:3000 --env-file .env pmv-rag1:latest

# With individual environment variables
docker run -p 3000:3000 \
  -e GEMINI_API_KEY="your_database_url" \
  -e ANTHROPIC_API_KEY="your_api_key" \
  pmv-rag1:latest
```

#### STDIO Mode (for MCP Client Integration)
```bash
docker run -i --env-file .env snapture-sql-agent-mcp:latest \
  fastmcp run mcp_server.py:mcp --transport stdio
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

### Optional Speech Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `WHISPER_MODEL` | Whisper model variant used for transcription. | `base` |
| `TEMP_AUDIO_DIR` | Directory for temporary audio processing. | `./data/temp` |

## 🔧 Advanced Usage

### Custom Port
```bash
docker run -p 8080:8080 --env-file .env snapture-sql-agent-mcp:latest \
  fastmcp run mcp_server.py:mcp --transport http --port 8080 --host 0.0.0.0
```

### Volume Mounting for Database
```bash
# Mount local database directory
docker run -p 3000:3000 --env-file .env \
  -v /path/to/local/db:/app/data \
  snapture-sql-agent-mcp:latest
```

### Debug Mode
```bash
docker run -p 3000:3000 --env-file .env \
  -e MCP_DEBUG=true \
  -e LOG_LEVEL=DEBUG \
  snapture-sql-agent-mcp:latest
```

## 🏥 Monitoring

Monitor the container and MCP server status:

```bash
# Check container status
docker ps

# Check if MCP server process is running
docker exec <container_id> pgrep -f \"fastmcp run\"

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
docker run -it --env-file .env snapture-sql-agent-mcp:latest bash
```

### Port Already in Use
```bash
# Use a different port
docker run -p 3001:3000 --env-file .env snapture-sql-agent-mcp:latest
```

### Database Connection Issues
```bash
# Verify environment variables
docker run --env-file .env snapture-sql-agent-mcp:latest env | grep DATABASE_URL

# Test database connectivity
docker run -it --env-file .env snapture-sql-agent-mcp:latest \
  python -c "import duckdb; print('DuckDB OK')"
```

## 📝 Development

### Building Different Versions
```bash
# Build with specific tag
./build-mcp-docker.sh v1.0.0

# Build development version
docker build -f Dockerfile.mcp -t snapture-sql-agent-mcp:dev .
```

### Testing the Container
```bash
# Run tests inside container
docker run --env-file .env snapture-sql-agent-mcp:latest \
  uv run pytest

# Interactive development
docker run -it -v $(pwd):/app --env-file .env \
  snapture-sql-agent-mcp:latest bash
```

## 🚢 Deployment

### Docker Compose (Recommended)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    env_file:
      - .env
    restart: unless-stopped
    # Optional: Uncomment for health checks
    # healthcheck:
    #   test: ["CMD", "pgrep", "-f", "fastmcp run"]
    #   interval: 30s
    #   timeout: 10s
    #   retries: 3
    #   start_period: 40s
    volumes:
      - ./data:/app/data  # Optional: for persistent database storage
```

Run with:
```bash
docker-compose -f docker-compose.yml up -d
```

### Production Considerations

1. **Security**: Use secrets management for API keys
2. **Monitoring**: Integrate with your monitoring stack
3. **Logging**: Configure log aggregation
4. **Backup**: Ensure database data is backed up
5. **Updates**: Set up automated image updates

## 📊 Container Specifications

| Aspect | Details |
|--------|---------|
| Base Image | `python:3.13-slim-bookworm` |
| Package Manager | UV (ultra-fast Python package manager) |
| User | Non-root (`app:app`, UID/GID 1000) |
| Working Directory | `/app` |
| Default Port | `3000` |
| Health Check | Manual monitoring only |
| Entry Point | `uv run` |
| Default Command | FastMCP server on HTTP transport |

This Docker setup provides a robust, secure, and efficient way to deploy the Snapture SQL Agent MCP server in any containerized environment.