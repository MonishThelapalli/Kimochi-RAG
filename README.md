# Kimochi RAG System

A production-ready RAG backend using FastAPI, Weaviate, PostgreSQL, and Groq LLM.

## Features
-   **PDF & Text Ingestion**: Auto-chunking and embedding generation.
-   **Semantic Search**: Cosine similarity search via Weaviate.
-   **QA w/ Citations**: Answers questions using strict context retrieval from citations.
-   **Dockerized**: One-command deployment.

## Prerequisites
-   Docker & Docker Compose
-   Groq API Key (for LLM inference)

## Quick Start

1.  **Set Environment Variables**
    Copy `.env.example` to `.env` and add your API Key.
    ```bash
    cp .env.example .env
    # Edit .env and set GROQ_API_KEY=...
    ```

2.  **Run with Docker Compose**
    ```bash
    docker-compose up --build
    ```
    The API will be available at `http://localhost:8000`.

## API Usage

### 1. Ingest a Document
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/file" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_docs/example_policy.txt"
```

### 2. Semantic Search
```bash
curl -X GET "http://localhost:8000/api/v1/search/?q=sick%20leave&k=3"
```

### 3. Ask a Question (RAG)
```bash
curl -X POST "http://localhost:8000/api/v1/qa/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many days of sick leave do I get?",
    "k": 3
  }'
```

## Folder Structure
-   `/app`: Main application code
    -   `/api`: Route handlers
    -   `/core`: Business logic (LLM, Embeddings, Config)
    -   `/db`: Database connections
    -   `/schemas`: Pydantic models
-   `/sample_docs`: Test data

## Architecture
See [design_doc.md](./design_doc.md) for details.
