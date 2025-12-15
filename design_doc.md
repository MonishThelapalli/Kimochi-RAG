# System Design Document: Kimochi RAG

## 1. Architecture Overview
The system follows a microservices-style architecture composed of:
1.  **API Service (FastAPI)**: Handles ingestion, search, and QA logic. Stateless and scalable.
2.  **Vector Database (Weaviate)**: Stores high-dimensional vector embeddings of document chunks for semantic retrieval.
3.  **Relational Database (PostgreSQL)**: Stores document metadata (ID, title, source, tags) for structured filtering and persistence.
4.  **LLM Layer (Groq)**: Abstracted generation layer calling Groq API (Mixtral/Llama3).

```ascii
[Client] -> [FastAPI (Boxer)]
               |
               +--> [PostgreSQL] (Metadata)
               +--> [Weaviate] (Vectors)
               +--> [Groq API] (LLM Generation)
```

## 2. Key Technology Decisions

### Weaviate
We limited usage to Weaviate as a pure vector store ("Bring Your Own Vectors"). This decouples the embedding generation (which happens in our app using SentenceTransformers) from the storage, allowing us to swap models without re-indexing infrastructure changes. Weaviate was chosen for its performance, ease of Docker deployment, and hybrid search capabilities.

### Sentence-Transformers
Used `all-MiniLM-L6-v2` for embeddings.
-   **Pros**: Fast, runs effectively on CPU/low-resource containers, small memory footprint.
-   **Cons**: Lower semantic capacity than large commercial models (e.g. OpenAI ada-002), but sufficient for this demo.

### LLM Strategy: Groq (Llama3)
We use Groq for ultra-fast inference speed suitable for real-time RAG.
**Critical Design Choice - Abstraction**:
Although a hosted LLM (Groq) is used for reliability and speed, the system is designed with a strict abstraction layer (`app/core/llm.py`), allowing seamless replacement with other providers without API changes. The application logic interacts with `LLMClient.generate(prompt)`, unaware of the underlying provider.

Although Groq is used in this implementation, the system is fully abstracted and can be switched to other LLM providers (e.g., Gemini, OpenAI, self-hosted models) without application-level changes.

### Hallucination Prevention
1.  **Strict Prompting**: The System Prompt explicitly instructs the model to say "I don't know" if the context is insufficient.
2.  **Context-Only**: We provide retrieved chunks as the *only* source of truth.

## 3. Trade-offs
-   **Sync vs Async**: We heavily used `async` for I/O bound operations (DB, networked APIs), but embedding generation is CPU bound. In a high-load production scenario, embedding should be offloaded to a worker queue (Celery/Celery) to avoid blocking the event loop.
-   **Chunking**: Simple sliding window text splitting. A more robust solution would use language-specific parsing (e.g. via LangChain/LlamaIndex) to respect sentence boundaries.
