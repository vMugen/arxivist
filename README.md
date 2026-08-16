# ArXivist

> An experimental research ingestion and retrieval engine built from the ground up.

ArXivist is a personal project for building a practical research system around arXiv papers.

The idea is simple: take a research paper, ingest it, extract its content, break it into useful chunks, and store everything in a structured way so that it can later become the foundation for semantic search, retrieval, research analysis, and eventually automated research workflows.

This project is being built incrementally rather than as a collection of disconnected tutorials.

---

## Current Status

**Early development — ingestion pipeline is working.**

At the moment, ArXivist can:

- Fetch paper metadata from arXiv
- Download the paper PDF
- Extract text from the PDF
- Split the extracted text into overlapping chunks
- Persist papers and chunks in the database
- Avoid re-processing an already ingested paper
- Use database constraints to protect data integrity
- Manage database operations through a repository layer
- Use SQLAlchemy async sessions and explicit transaction boundaries
- Manage database schema changes with Alembic

The retrieval and AI layers have not been implemented yet.

---

## Current Pipeline

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
              PostgreSQL/DB
                 │        │
                 ▼        ▼
               Paper     Chunks
````

The goal is to eventually extend this into:

```text
Papers
   │
   ▼
Chunks
   │
   ▼
Embeddings
   │
   ▼
Semantic Retrieval
   │
   ▼
Research Analysis
   │
   ▼
Research Workflows
   │
   ▼
Experiments & Execution
```

---

## Project Structure

The project is currently organized around a few clear responsibilities:

```text
app/
├── config/
│   └── db.py
│
├── models/
│   ├── paper.py
│   └── chunk.py
│
├── repositories/
│   ├── paper.py
│   └── chunk.py
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
│   └── chunker.py
│
└── main.py
```

The separation is intentional:

* **Routers** handle HTTP requests and responses.
* **Services** contain application/business workflow.
* **Repositories** handle database operations.
* **Models** describe database tables.
* **Schemas** describe data entering/leaving different parts of the application.
* **Config** contains infrastructure such as the database session.

---

## Database Design

### `papers`

A paper is identified internally by its database `id` and externally by its `arxiv_id`.

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

Important constraints currently include:

* `id` → primary key
* `arxiv_id` → unique
* `pdf_url` → unique
* `arxiv_id` → indexed

### `chunks`

Each paper can contain many chunks.

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

A `(paper_id, chunk_index)` combination is unique, which prevents duplicate chunk positions within the same paper.

---

## Chunking

The current chunker uses a simple fixed-size strategy with overlap.

For example:

```text
chunk_size = 1000
overlap    = 100

Chunk 0: [0 -------------------- 1000]
Chunk 1:                [900 -------------------- 1900]
Chunk 2:                               [1800 --------]
```

Each chunk records:

* its position within the paper
* starting character
* ending character
* extracted text

This is intentionally simple for now. More sophisticated chunking strategies can be evaluated later when retrieval becomes the focus.

---

## Persistence

Database access follows a repository pattern.

For example:

```text
Service
   │
   ├── create_paper()
   ├── create_chunks()
   └── get_paper_by_arxiv_id()
          │
          ▼
      Repository
          │
          ▼
       Database
```

Repositories do not decide application behavior. They perform database operations and leave workflow decisions to the service layer.

---

## Transactions

The ingestion workflow separates expensive processing from database persistence.

```text
Fetch metadata
      ↓
Download PDF
      ↓
Extract text
      ↓
Chunk text
      ↓
BEGIN TRANSACTION
      ↓
Create Paper
      ↓
Create Chunks
      ↓
COMMIT
```

The database transaction is deliberately kept short.

If persistence fails partway through, the transaction can roll back instead of leaving a partially-created paper in the database.

---

## Duplicate Ingestion

Trying to ingest a paper that already exists should not cause the system to download and process the PDF again.

The current flow first checks whether the paper already exists:

```text
Request
   │
   ▼
Does paper exist?
   │
   ├── Yes → return existing state
   │
   └── No
        ↓
     Process paper
        ↓
     Persist
```

The database uniqueness constraint remains important even with this check because application-level checks alone cannot protect against concurrent requests.

---

## Technology

Current stack:

* **Python**
* **FastAPI**
* **Pydantic**
* **SQLAlchemy 2.x**
* **PostgreSQL / SQLite during development**
* **Alembic**
* **PyMuPDF**
* **arxiv**
* **httpx**
* **AnyIO**

Planned technologies include:

* `pgvector`
* Embedding models
* Semantic search
* Hybrid retrieval
* LLM-based research workflows
* Sandboxed code execution

Those are not part of the current implementation yet.

---

## API

Current endpoints include:

### Get paper metadata

```http
GET /api/v1/papers/{arxiv_id}
```

### Ingest paper

```http
POST /api/v1/papers/{arxiv_id}/ingest
```

The ingestion endpoint currently handles:

```text
arXiv ID
   ↓
metadata
   ↓
PDF
   ↓
text
   ↓
chunks
   ↓
database
```

---

## Development Philosophy

ArXivist is being built as a learning project as much as a software project.

The goal isn't just to make the application work.

For each feature, the development loop is:

```text
Choose next feature
       ↓
Think through the design
       ↓
Identify entities & relationships
       ↓
Consider constraints & failure modes
       ↓
Implement
       ↓
Test
       ↓
Break it intentionally
       ↓
Diagnose the failure
       ↓
Fix it
       ↓
Record what was learned
```

The intention is to gradually develop the engineering judgment required to design larger AI and backend systems rather than simply following implementation recipes.

---

## What's Next

The immediate focus is making the ingestion pipeline more robust:

* Better failure handling
* Transaction and rollback tests
* Duplicate/race-condition handling
* Automated tests
* More deliberate validation around ingestion

After that, the next major milestone is retrieval:

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

That will become the foundation for the research side of ArXivist.

---

## Why ArXivist?

There are plenty of tools that can search papers or summarize them.

The purpose of ArXivist is different.

It's an attempt to understand and build the underlying machinery myself:

**ingestion → storage → retrieval → reasoning → execution**

One layer at a time.

---

## Status

🚧 **Early development**

This project is actively evolving. The architecture, database schema, and APIs will change as the system grows and as new engineering problems are discovered.