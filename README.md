# ArXivist 🔬

> An experimental research ingestion and retrieval engine built from the ground up.

ArXivist is a personal project where I am trying to build a practical research system around arXiv papers.

The basic idea is:

```text
Research Paper
     ↓
  Ingestion
     ↓
 Text Extraction
     ↓
   Chunking
     ↓
  Embeddings
     ↓
   Storage
     ↓
   Retrieval
     ↓
  Reasoning
     ↓
 Research Workflows
````

The project is being built one layer at a time.

I don't want to just make an AI application that works. I want to understand the engineering decisions underneath it — databases, transactions, retrieval, embeddings, system boundaries, failure modes, scaling and eventually the more complicated AI system parts.

So things will probably change a lot as I build it.

---

## 🚧 Current Status

**Early development — ingestion → embeddings → vector retrieval**

Currently ArXivist can:

* Fetch paper metadata from arXiv
* Download paper PDFs
* Extract text using PyMuPDF
* Split extracted text into overlapping chunks
* Persist papers and chunks
* Prevent duplicate paper ingestion
* Enforce database-level integrity constraints
* Use async SQLAlchemy sessions
* Use repository-based database access
* Keep transaction boundaries intentional
* Manage schema changes with Alembic
* Generate embeddings for chunks
* Store embedding metadata and vectors
* Avoid unnecessary duplicate embedding generation
* Perform cosine similarity search using pgvector
* Return Top-K relevant chunks

### Current milestone

```text
Chunk
  ↓
Embedding
  ↓
pgvector
  ↓
Cosine Similarity Search
  ↓
Top-K Chunks
```

The next step is **not RAG yet**.

First I want to understand and evaluate retrieval quality, inspect the generated SQL, understand how pgvector performs the search, and then add the appropriate vector index.

---

# 🧱 Technology Stack

### Core

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.x-009688?style=flat-square\&logo=fastapi\&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?style=flat-square\&logo=pydantic\&logoColor=white)

### Database

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?style=flat-square\&logo=postgresql\&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00?style=flat-square\&logo=sqlalchemy\&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-5A5A5A?style=flat-square)
![pgvector](https://img.shields.io/badge/pgvector-Vector_Search-336791?style=flat-square)

### Infrastructure

![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=flat-square\&logo=docker\&logoColor=white)
![Git](https://img.shields.io/badge/Git-Version_Control-F05032?style=flat-square\&logo=git\&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square\&logo=github\&logoColor=white)

### AI / Retrieval

![Hugging Face](https://img.shields.io/badge/Hugging_Face-Embeddings-FFD21E?style=flat-square\&logo=huggingface\&logoColor=black)

Current / planned AI and retrieval technologies include:

* Sentence Transformers
* Embeddings
* pgvector
* Vector similarity search
* Reranking
* Hybrid retrieval
* LLM-based research workflows
* Knowledge retrieval
* Sandboxed code execution

---

# 🏗️ Architecture

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
              ┌────────────┴────────────┐
              ▼                         ▼
         Repository              External Services
              │                         │
              ▼                         ├── arXiv
          Database                      ├── PDF
              │                         └── Embedding Model
              ▼
         PostgreSQL
```

The separation is intentional.

I'm trying to keep each layer responsible for one type of problem instead of putting everything into one large service or router.

### Router

Responsible for the HTTP boundary:

* Requests
* Responses
* Path/query/body parameters
* Dependency injection
* HTTP-level errors

Routers should stay thin.

### Service

Responsible for the application workflow:

* Business/application logic
* Coordinating operations
* Calling repositories
* Calling external services
* Deciding transaction boundaries
* Deciding what should happen when something fails

### Repository

Responsible for database interaction:

* Queries
* Inserts
* Updates
* Deletes
* Persistence-related operations

Repositories should not decide application/business policy.

### Models

SQLAlchemy ORM models representing database entities.

### Schemas

Pydantic models used for validation, serialization and application boundaries.

### Config

Infrastructure configuration such as:

* Database engine
* Async session factory
* Environment configuration

---

# 📥 Current Ingestion Pipeline

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
                           │
                           ▼
                 Vector Similarity Search
                           │
                           ▼
                     Top-K Chunks
```

The ingestion workflow is intentionally separated into stages because each stage has a different responsibility and different failure characteristics.

---

# 📁 Project Structure

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
│   ├── embedding.py
│   └── retrieval.py
│
├── routers/
│   └── api/
│       └── v1/
│           ├── ingestion.py
│           ├── metadata.py
│           └── retrieval.py
│
├── schema/
│   ├── paper.py
│   ├── chunk.py
│   ├── ingestion.py
│   └── retrieval.py
│
├── services/
│   ├── ingestion.py
│   ├── metadata.py
│   ├── pdf_downloader.py
│   ├── extraction.py
│   ├── chunker.py
│   ├── embedding.py
│   └── retrieval.py
│
└── main.py
```

The exact structure will probably evolve as ArXivist becomes more complex.

---

# 🗄️ Database Design

The current conceptual model is:

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

Embeddings are deliberately stored separately from chunks.

The reason is that I don't want to assume that one chunk can only ever have one representation.

For example, eventually:

```text
Chunk
 ├── Embedding (model A)
 ├── Embedding (model B)
 └── Embedding (model C)
```

The current implementation can still use one embedding per chunk.

---

# ✂️ Chunking

The current chunker uses fixed-size chunks with overlap.

Example:

```text
chunk_size = 1000
overlap    = 100

Chunk 0: [0 -------------------- 1000]
Chunk 1:                [900 -------------------- 1900]
Chunk 2:                               [1800 --------]
```

Each chunk stores:

* `chunk_index`
* `start_char`
* `end_char`
* `text`

The current approach is intentionally simple.

Later I want to evaluate whether retrieval improves with:

* Semantic chunking
* Section-aware chunking
* Sentence-aware chunking
* Heading-aware chunking
* Token-based chunking

I don't want to add complexity before measuring whether it actually helps.

---

# 🧠 Embeddings

Each chunk is converted into a numerical vector representation.

```text
Chunk text
    │
    ▼
Embedding Model
    │
    ▼
Vector
```

Current experimentation uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

which produces:

```text
384-dimensional vectors
```

Conceptually:

```text
text
  ↓
Embedding Model
  ↓
[0.012, -0.034, 0.081, ...]
  ↓
384 dimensions
```

Different embedding models can produce different dimensions and different semantic representations.

Because of that, embedding model information is treated as part of the embedding's identity.

---

# 🔌 Embedding Provider

Embedding generation is separated behind a provider abstraction.

```text
             EmbeddingProvider
                    ▲
                    │
        ┌───────────┴───────────┐
        │                       │
LocalEmbeddingProvider    Future Provider
```

The idea is to avoid coupling the whole application to one specific embedding implementation.

For now the implementation is local and uses Sentence Transformers.

A future implementation could use a hosted model or another local model without rewriting the entire retrieval/ingestion workflow.

---

# ⚡ Embedding Workflow

Current workflow:

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

Batch generation is preferred over generating one chunk at a time because embedding models can process multiple texts more efficiently.

An important invariant is:

```text
number of input chunks
        ==
number of generated vectors
```

If this doesn't hold, the system should fail instead of silently storing incorrect relationships.

---

# 🔎 Vector Retrieval

The current retrieval flow is:

```text
User Query
    │
    ▼
Query Embedding
    │
    ▼
384-dimensional Vector
    │
    ▼
pgvector
    │
    ▼
Cosine Distance
    │
    ▼
Top-K Embeddings
    │
    ▼
Corresponding Chunks
```

The current SQL generated by SQLAlchemy is conceptually:

```sql
SELECT
    chunks.id,
    chunks.paper_id,
    chunks.text,
    embeddings.vector <=> $1 AS distance
FROM embeddings
JOIN chunks
    ON embeddings.chunk_id = chunks.id
WHERE embeddings.model = $2
ORDER BY embeddings.vector <=> $1
LIMIT $3;
```

The important part is:

```text
vector <=> query_vector
```

which is pgvector's cosine-distance operation.

Lower distance means closer vectors.

For the current normalized embeddings, the service converts that distance into:

```text
score = 1 - distance
```

---

# 🧪 Retrieval Evaluation

The retrieval system is currently being evaluated before moving into RAG.

The plan is simple:

```text
Query
  ↓
Retrieve Top-K
  ↓
Inspect results
  ↓
Is the relevant chunk present?
  ↓
Top-1 / Top-3 / Top-5
```

The goal isn't to pretend that a similarity score automatically means "good retrieval".

I want to test actual retrieval quality and inspect failure cases.

Possible causes of bad retrieval include:

```text
Bad PDF extraction
        ↓
Bad chunking
        ↓
Bad embeddings
        ↓
Bad query representation
        ↓
Bad retrieval configuration
```

This is why retrieval quality comes before building a full RAG pipeline.

---

# 🗃️ Persistence

Database access follows a repository pattern.

Conceptually:

```text
Service
   │
   ├── create_paper()
   ├── create_chunks()
   ├── create_embeddings()
   ├── get_paper_by_arxiv_id()
   └── search_similar_chunks()
            │
            ▼
       Repository
            │
            ▼
         Database
```

Repositories handle database operations.

The service layer decides:

* When to call them
* In what order
* Whether the operation should happen
* What should happen when something fails

---

# 🔄 Transactions

Expensive processing is kept outside database transactions whenever possible.

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

This keeps the database transaction relatively short.

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

The database should return to its previous consistent state.

---

# ♻️ Duplicate Ingestion & Idempotency

Repeated ingestion of the same paper should not unnecessarily repeat expensive work.

Conceptually:

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

However, application checks alone cannot guarantee uniqueness under concurrent requests.

Therefore database constraints are still required.

```text
Application check
       +
Database constraint
       ↓
Better protection
```

---

# 🛡️ Database Integrity

The database is treated as the final source of truth for data integrity.

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

# 🌐 API

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

---

## Semantic Retrieval

```http
GET /api/v1/retrieval/search?query=...
```

The query is embedded by the service layer and similarity search is performed through the repository.

---

# 🐳 Running Locally

## 1. Clone

```bash
git clone <https://github.com/Hasnain-tech295/arxivist.git>
cd arxivist
```

## 2. Create virtual environment

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

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🗄️ Database Setup

ArXivist uses PostgreSQL for the intended development architecture.

Configure:

```text
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
```

Example:

```text
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/arxivist
```

Do not commit real credentials.
Although, I did it by mistake. Fix the issue and rotate the credentials.

Use environment variables or a local `.env` file.

---

# 🐳 Docker

Docker is used to make infrastructure such as PostgreSQL easier to reproduce.

If Docker Compose is configured:

```bash
docker compose up -d
```

Check containers:

```bash
docker compose ps
```

Stop services:

```bash
docker compose down
```

To remove database volumes as well:

```bash
docker compose down -v
```

> ⚠️ `down -v` deletes database volumes. Use it only when you intentionally want to reset the development database.

---

# 🗃️ Database Migrations

ArXivist uses Alembic for database schema migrations.

Create a migration:

```bash
alembic revision --autogenerate -m "describe the change"
```

Always inspect the generated migration before applying it.

Apply migrations:

```bash
alembic upgrade head
```

Check current revision:

```bash
alembic current
```

View history:

```bash
alembic history
```

Rollback one migration:

```bash
alembic downgrade -1
```

Autogenerated migrations are not treated as blindly correct. They should be reviewed before being committed.

---

# 🚀 Start the API

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://localhost:8000
```

FastAPI docs:

```text
http://localhost:8000/docs
```

---

# 🔁 Development Workflow

ArXivist is deliberately developed feature-by-feature.

The loop I'm following is:

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
                │ Entities            │
                │ Relationships       │
                │ Constraints         │
                │ Failure Modes       │
                │ Transactions        │
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

The purpose is not just to finish features.

I want to build the habit of asking **why** a system behaves the way it does.

---

# 🧠 Engineering Questions

For every significant feature, I try to ask:

```text
What are the entities?

What are their relationships?

Who owns what?

What should be unique?

What can fail?

What happens if it runs twice?

What happens if two requests run concurrently?

What belongs inside a transaction?

What belongs outside?

Which layer owns the decision?

What happens when the system grows?

What are the alternatives?

Why are we choosing this design?
```

These questions are becoming part of the project itself.

---

# 🎯 Why ArXivist?

There are already many excellent tools for searching, summarizing and interacting with research papers.

The point of ArXivist is different.

I want to understand and build the machinery myself.

The long-term direction is:

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

Eventually I want ArXivist to move beyond simply retrieving pieces of papers.

The bigger idea is a system that can:

```text
Find relevant research
        ↓
Understand the evidence
        ↓
Connect information
        ↓
Identify gaps / questions
        ↓
Plan research
        ↓
Run experiments
        ↓
Evaluate results
        ↓
Remember what happened
        ↓
Continue the research loop
```

That's a much bigger problem, so I'm building toward it one layer at a time.

---

# 📚 Learning Philosophy

ArXivist is both a software project and an engineering laboratory.

The goal is not:

> "How quickly can I finish this application?"

The goal is:

> "Can I understand why the system works, why it fails, and why we chose this design over the alternatives?"

Sometimes the implementation will be simple.

Sometimes I'll probably design something badly, break it, fix it and then understand why the original design was wrong.

That's intentional.

I want the project to teach me things that I won't get from simply following tutorials.

---

# 🚧 Status

**Early development.**

The architecture, database schema, APIs and retrieval strategy will change as I discover new problems.

For now the immediate milestone is:

```text
Chunk
  ↓
Embedding
  ↓
pgvector
  ↓
Similarity Search
  ↓
Evaluate Retrieval
  ↓
Vector Index
  ↓
Benchmark
```

Only after retrieval is understood and working well will I move into the next layer.