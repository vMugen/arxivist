# ArXivist

> An experimental research ingestion and retrieval engine built from the ground up.

ArXivist is a personal project for building a practical research system around arXiv papers.

The idea is simple:

> Take a research paper → ingest it → extract its content → chunk it → generate embeddings → store everything in a structured way → retrieve relevant knowledge → eventually reason and execute research workflows.

This project is being built incrementally rather than as a collection of disconnected tutorials.

The goal is not only to make the system work, but to understand the engineering decisions behind it.

---

## Current Status

🚧 **Early development — ingestion + embedding pipeline**

ArXivist currently supports:

- Fetching paper metadata from arXiv
- Downloading paper PDFs
- Extracting text using PyMuPDF
- Splitting extracted text into overlapping chunks
- Persisting papers and chunks in the database
- Preventing duplicate paper ingestion
- Database-level integrity constraints
- SQLAlchemy async sessions
- Repository-based database access
- Explicit transaction boundaries
- Alembic database migrations
- Generating embeddings for chunks
- Storing embedding metadata and vectors
- Avoiding unnecessary duplicate embedding generation
- Preparing the system for vector similarity search

The semantic retrieval layer is the next major milestone.

---

## Technology

### Core

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.x-009688?style=flat-square&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?style=flat-square&logo=pydantic&logoColor=white)

### Database

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-5A5A5A?style=flat-square)

### Infrastructure

![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=flat-square&logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-Version_Control-F05032?style=flat-square&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white)

### AI / Retrieval

![Hugging Face](https://img.shields.io/badge/Hugging_Face-Embeddings-FFD21E?style=flat-square&logo=huggingface&logoColor=black)

Current and planned AI/retrieval technologies include:

- Sentence Transformers
- pgvector
- Vector similarity search
- Hybrid retrieval
- LLM-based research workflows
- Sandboxed code execution

---

# Architecture

The current architecture follows a simple layered structure:

```text
                    Client
                      │
                      ▼
                  FastAPI
                    Router
                      │
                      ▼
                   Service
              Business Workflow
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     Repository            External Services
          │                       │
          ▼                       ├── arXiv
      Database                    ├── PDF
          │                       └── Embedding Model
          ▼
     PostgreSQL
````

The separation is intentional.

### Router

Responsible for:

* HTTP requests
* HTTP responses
* Path/query/body parameters
* Dependency injection
* HTTP-level error handling

Routers should remain thin.

### Service

Responsible for:

* Application/business workflow
* Deciding what operations happen
* Transactional boundaries
* Coordinating repositories and external services
* Deciding how failures affect the workflow

### Repository

Responsible for:

* Database interaction
* Queries
* Inserts
* Updates
* Deletes
* Persistence-related operations

Repositories should not decide application/business policy.

### Models

SQLAlchemy ORM models representing database entities.

### Schemas

Pydantic models used for data validation, serialization, and application boundaries.

### Config

Infrastructure configuration such as:

* Database engine
* Async session factory
* Environment configuration

---

# Current Pipeline

The current ingestion and embedding pipeline looks like:

```text
                        arXiv
                          │
                          ▼
                  Fetch Metadata
                          │
                          ▼
                   Download PDF
                          │
                          ▼
                    Extract Text
                          │
                          ▼
                     Chunk Text
                          │
                          ▼
                    Persist Paper
                          │
                          ▼
                    Persist Chunks
                          │
                          ▼
                 Generate Embeddings
                          │
                          ▼
                 Persist Embeddings
```

The next major step is:

```text
Embedding
    │
    ▼
pgvector
    │
    ▼
Similarity Search
    │
    ▼
Top-K Chunks
```

---

# Project Structure

Current structure:

```text
app/
├── config/
│   └── db.py
│
├── models/
│   ├── paper.py
│   ├── chunk.py
│   └── embedding.py
│
├── repositories/
│   ├── paper.py
│   ├── chunk.py
│   └── embedding.py
│
├── routers/
│   └── api/
│       └── v1/
│           ├── ingestion.py
│           └── metadata.py
│
├── schema/
│   ├── paper.py
│   ├── chunk.py
│   └── ingestion.py
│
├── services/
│   ├── ingestion.py
│   ├── metadata.py
│   ├── pdf_downloader.py
│   ├── extraction.py
│   ├── chunker.py
│   └── embedding.py
│
└── main.py
```

The exact structure may evolve as the system becomes more complex.

---

# Database Design

The current conceptual data model is:

```text
Paper
  │
  │ 1:N
  ▼
Chunk
  │
  │ 1:N
  ▼
Embedding
```

## `papers`

```text
papers
────────────────────────────
id
arxiv_id
title
authors
summary
pdf_url
published
```

Important constraints:

* `id` → Primary Key
* `arxiv_id` → Unique
* `pdf_url` → Unique
* `arxiv_id` → Indexed

---

## `chunks`

```text
chunks
────────────────────────────
id
paper_id
chunk_index
start_char
end_char
text
```

Relationship:

```text
Paper
  │
  └───< Chunk
```

A paper can contain many chunks.

The following combination is unique:

```text
(paper_id, chunk_index)
```

This prevents two chunks from occupying the same position within the same paper.

---

## `embeddings`

Conceptually:

```text
embeddings
────────────────────────────
id
chunk_id
model
dimensions
vector
```

Relationship:

```text
Chunk
  │
  └───< Embedding
```

The current design deliberately keeps embeddings in a separate table rather than placing a vector directly inside `chunks`.

This gives ArXivist room to support multiple embedding representations for the same chunk in the future.

For example:

```text
Chunk
 ├── Embedding (model A)
 ├── Embedding (model B)
 └── Embedding (model C)
```

The current implementation may still generate only one embedding per chunk.

---

# Chunking

The current chunker uses fixed-size chunks with overlap.

Example:

```text
chunk_size = 1000
overlap    = 100

Chunk 0: [0 -------------------- 1000]
Chunk 1:                [900 -------------------- 1900]
Chunk 2:                               [1800 --------]
```

Every chunk stores:

* `chunk_index`
* `start_char`
* `end_char`
* `text`

The current strategy is intentionally simple.

More advanced strategies such as:

* Semantic chunking
* Section-aware chunking
* Sentence-aware chunking
* Heading-aware chunking
* Token-based chunking

can be evaluated later based on retrieval performance.

---

# Embeddings

Each chunk can be converted into a numerical vector representation.

Conceptually:

```text
Chunk text
    │
    ▼
Embedding Model
    │
    ▼
Vector
```

Current experimentation uses a Sentence Transformer model producing:

```text
384-dimensional vectors
```

Example:

```text
text
  ↓
Embedding Model
  ↓
[0.012, -0.034, 0.081, ...]
  ↓
384 dimensions
```

The embedding model determines the dimensionality of the resulting vector.

The system therefore treats embedding model information as part of the embedding's identity rather than assuming that every future model will produce the same vector representation.

---

# Embedding Provider

Embedding generation is separated behind a provider abstraction.

Conceptually:

```text
             EmbeddingProvider
                    ▲
                    │
        ┌───────────┴───────────┐
        │                       │
LocalEmbeddingProvider    Future Provider
```

This allows the application to change the underlying embedding implementation without coupling the entire ingestion workflow to one specific model or provider.

---

# Embedding Workflow

The current workflow is approximately:

```text
Chunks
   │
   ▼
Collect chunk texts
   │
   ▼
Generate embeddings in batch
   │
   ▼
Validate vector count
   │
   ▼
Create embedding records
   │
   ▼
Persist embeddings
```

Batching is preferred over generating embeddings one chunk at a time because embedding models can process batches more efficiently.

An important invariant is:

```text
number of input chunks
        ==
number of generated vectors
```

If this invariant fails, the embedding operation should not continue blindly.

---

# Persistence

Database access follows a repository pattern.

Example:

```text
Service
   │
   ├── create_paper()
   ├── create_chunks()
   ├── create_embeddings()
   └── get_paper_by_arxiv_id()
            │
            ▼
       Repository
            │
            ▼
         Database
```

Repositories perform database operations.

The service layer decides:

* When to call them
* In what order
* Whether the operation should happen
* What should happen when an operation fails

---

# Transactions

The expensive processing stages are kept outside the database transaction whenever possible.

Conceptually:

```text
Fetch metadata
      ↓
Download PDF
      ↓
Extract text
      ↓
Chunk text
      ↓
Generate embeddings
      ↓
BEGIN TRANSACTION
      ↓
Persist Paper
      ↓
Persist Chunks
      ↓
Persist Embeddings
      ↓
COMMIT
```

This keeps the transaction relatively short and avoids holding a database transaction open while performing expensive external or CPU-heavy operations.

If persistence fails:

```text
BEGIN
  ↓
Paper
  ↓
Chunks
  ↓
Embeddings
  ↓
ERROR
  ↓
ROLLBACK
```

The database can return to its previous consistent state.

---

# Duplicate Ingestion & Idempotency

Repeated ingestion of the same paper should not unnecessarily repeat expensive work.

The conceptual flow is:

```text
Request
   │
   ▼
Does paper already exist?
   │
   ├── YES ──► Reuse existing paper
   │
   └── NO
        │
        ▼
     Process paper
        │
        ▼
     Persist data
```

The application-level existence check improves efficiency.

However, database constraints remain necessary because two concurrent requests can both pass an application-level check before either one commits.

Therefore:

```text
Application check
       +
Database constraint
       ↓
Better protection
```

---

# Database Integrity

The database is treated as the final authority for data integrity.

Important constraints include:

```text
Primary Key
Foreign Key
Unique Constraint
Composite Unique Constraint
```

For example:

```text
(paper_id, chunk_index)
```

is unique.

This guarantees that the same paper cannot contain two chunks with the same chunk position.

---

# API

## Get Paper Metadata

```http
GET /api/v1/papers/{arxiv_id}
```

Example:

```text
GET /api/v1/papers/2608.13547
```

---

## Ingest Paper

```http
POST /api/v1/papers/{arxiv_id}/ingest
```

Example:

```text
POST /api/v1/papers/2608.13547/ingest
```

The endpoint coordinates the ingestion workflow through the service layer.

---

# Running Locally

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd arxivist
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If the project uses a different dependency manager, use the corresponding project configuration.

---

# Database Setup

ArXivist uses PostgreSQL for the intended development architecture.

If PostgreSQL is running locally, configure:

```text
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
```

Example:

```text
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/arxivist
```

Do not commit real credentials to Git.

Use environment variables or a local `.env` file instead.

---

# Docker

Docker is used to make infrastructure such as PostgreSQL reproducible across environments.

If a Docker Compose configuration is provided in the repository:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

Stop the services:

```bash
docker compose down
```

To stop containers and remove their volumes:

```bash
docker compose down -v
```

> `down -v` deletes database volumes. Use it only when you intentionally want to reset the development database.

---

# Database Migrations

ArXivist uses Alembic for schema migrations.

Create a migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe the change"
```

Always inspect the generated migration before applying it.

Apply migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

Rollback one migration:

```bash
alembic downgrade -1
```

Autogenerated migrations should be reviewed manually rather than blindly trusted.

---

# Start the API

Run the development server with:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://localhost:8000
```

FastAPI's interactive documentation:

```text
http://localhost:8000/docs
```

---

# Development Workflow

ArXivist is deliberately developed feature-by-feature.

The development loop is:

```text
                  ┌─────────────────────┐
                  │    Choose Feature   │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │    Think / Design   │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Entities             │
                  │ Relationships        │
                  │ Constraints          │
                  │ Failure Modes        │
                  │ Transactions         │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │      Implement      │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │        Test         │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Intentionally Break │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Diagnose + Fix      │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Record What Learned │
                  └──────────┬──────────┘
                             │
                             └──────────► Next Feature
```

The purpose of this workflow is to develop engineering judgment rather than simply reproduce code.

---

# Engineering Principles

Several principles guide the project.

### 1. Database is the final source of truth

Application validation improves user experience and efficiency, but database constraints protect the actual data.

### 2. Keep transactions intentional

Do not keep transactions open while performing expensive external or CPU-heavy work unless there is a specific reason.

### 3. Keep routers thin

HTTP concerns belong at the API boundary.

### 4. Keep repositories focused

Repositories should know how to interact with the database, not why the application wants the data.

### 5. Put workflow decisions in services

The service layer coordinates application behavior and transactional boundaries.

### 6. Design for failure

Every new feature should answer:

```text
What happens if this step fails?
What happens if it runs twice?
What happens if two requests run concurrently?
What data must remain consistent?
```

### 7. Prefer explicit trade-offs

A simple design that is understood is often more valuable at this stage than premature complexity.


# Why ArXivist?

There are already excellent tools for searching, summarizing, and interacting with research papers.

The purpose of ArXivist is different.

It is an attempt to understand and build the underlying machinery myself.

```text
Ingestion
    ↓
Storage
    ↓
Retrieval
    ↓
Reasoning
    ↓
Research
    ↓
Execution
```

The project is intentionally built one layer at a time.

Each layer is an opportunity to understand the engineering problems underneath modern AI systems.

---

# Learning Philosophy

ArXivist is both a software project and an engineering laboratory.

The goal is not:

> "How quickly can I finish this application?"

The goal is:

> "Can I understand why the system works, why it fails, and why we chose this design over alternatives?"

For every significant feature, the project asks:

```text
What are the entities?
What are their relationships?
What owns what?
What must be unique?
What can fail?
What happens if it runs twice?
What happens concurrently?
What belongs inside a transaction?
What belongs outside?
Which layer owns the decision?
What happens when the system grows?
```

The answers become part of the architecture rather than remaining implicit assumptions.

---

# Status

🚧 **Early development**

ArXivist is actively evolving.

The architecture, database schema, APIs, and retrieval strategy will change as new engineering problems are discovered.

The current immediate goal is:

```text
Chunk
  ↓
Embedding
  ↓
pgvector
  ↓
Similarity Search
  ↓
Top-K Relevant Chunks
```

After that, the system will move toward increasingly sophisticated retrieval, research reasoning, and eventually research execution.

```