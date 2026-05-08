# SYSTEM_CONTEXT.md

Version: 0.1.1
Date: 2026-05-08
Project: JobIntel

---

# Project Identity

JobIntel is a local-first autonomous AI-powered job intelligence platform.

Primary goals:
- discover relevant jobs
- rank opportunities semantically
- generate ATS-aware application documents
- minimize repetitive manual work
- preserve user privacy
- remain locally executable

This project is intended for:
- personal use
- local execution
- AI-assisted development

The project is NOT intended initially for:
- enterprise deployment
- SaaS hosting
- multi-user architecture
- cloud-native scaling
- automated job application submission

---

# Current Development Philosophy

This repository is optimized for:

## AI Maintainability

Code should be:
- explicit
- modular
- readable
- minimally abstracted
- heavily documented
- easy for AI systems to extend safely

Avoid:
- clever patterns
- excessive indirection
- premature optimization
- unnecessary architecture complexity

Future AI coding sessions should be able to:
- understand module purpose quickly
- modify isolated components safely
- repair broken functionality incrementally

---

# Primary Technical Stack

## Backend
Python 3.12+

## API
FastAPI

## Database
SQLite

## ORM
SQLAlchemy

## Embeddings
sentence-transformers

## Local LLM Runtime
Ollama

## Document Generation
python-docx

## Spreadsheet Export
pandas
openpyxl

## Future Frontend
React + Tailwind

---

# Current MVP Scope

The current milestone is NOT full autonomy.

The current milestone is:

## MVP Vertical Slice

Inputs:
- master_resume.docx
- career_reference.md
- one manually provided job description

Processing:
- embedding generation
- similarity scoring
- database persistence

Outputs:
- stored job record
- SMI score
- generated tailored resume

---

# Current Repository Structure

```txt
/jobintel
    /backend
        /ai
        /documents
        /jobs
        /pipeline
        /storage

    /config

    /data
        /input
        /generated

    SYSTEM_CONTEXT.md
    README.md
    requirements.txt
    main.py
```

---

# Backend Module Responsibilities

## /backend/ai

Contains:
- embedding generation
- semantic similarity
- future prompt orchestration
- local LLM integrations

Rules:
- isolate AI logic from business logic
- avoid UI dependencies
- keep functions composable

---

## /backend/jobs

Contains:
- job models
- job normalization
- job source handling
- source adapters

Rules:
- normalize external job data immediately
- maintain source independence

---

## /backend/pipeline

Contains:
- orchestration logic
- job processing flow
- scoring sequence
- document generation flow

Rules:
- pipeline stages should remain independently testable
- avoid hidden side effects

---

## /backend/storage

Contains:
- database configuration
- ORM models
- persistence utilities

Rules:
- SQLite first
- no distributed database assumptions
- maintain portability

---

## /backend/documents

Contains:
- resume generation
- cover letter generation
- DOCX export
- ODT export

Rules:
- preserve factual integrity
- never hallucinate experience
- preserve original resume structure where possible

---

# Database Design Principles

Current database:

```txt
SQLite
```

Current primary table:

```txt
jobs
```

Initial fields:
- id
- company
- title
- location
- description
- source_url
- smi_score
- status

Future tables may include:
- applications
- generated_documents
- embeddings
- pipeline_events

Avoid premature schema complexity.

---

# Similarity Match Index (SMI)

Purpose:
- prioritize semantically relevant jobs
- reduce irrelevant search noise
- support autonomous ranking

Current method:
- embedding comparison
- cosine similarity

Comparison:

```txt
career_reference_embedding
VS
job_description_embedding
```

Score range:

```txt
0.0 → 1.0
```

Interpretation:
- higher score = stronger semantic fit

---

# Resume Generation Rules

Generated resumes MUST:
- remain truthful
- preserve factual work history
- avoid fabricated achievements
- inject ATS keywords naturally
- maintain readability
- minimize unnecessary rewrites

The system should optimize for:
- ATS compatibility
- semantic relevance
- minimal distortion of source resume

---

# Cover Letter Rules

Cover letters should be:
- concise
- modern
- role-aware
- company-aware where possible
- generated automatically after score threshold

Avoid:
- generic fluff
- exaggerated enthusiasm
- fabricated claims

---

# AI Usage Rules

AI systems are collaborators, not authoritative decision makers.

Rules:
- verify generated code incrementally
- test every pipeline stage independently
- avoid accepting large untested refactors blindly
- maintain human-readable architecture

Prompts should reference:

```txt
SYSTEM_CONTEXT.md
```

for consistency.

---

# Current Development Sequence

## Completed

- initial project structure
- FastAPI application bootstrap
- SQLite configuration
- SQLAlchemy model creation
- automatic database initialization

---

## Immediate Next Steps

### Step 1
Create:

```txt
backend/ai/similarity_engine.py
```

Responsibilities:
- cosine similarity
- embedding comparison

---

### Step 2
Create:

```txt
career_reference.md loader
```

Responsibilities:
- load markdown
- prepare semantic profile

---

### Step 3
Create:

```txt
manual job ingestion
```

Responsibilities:
- load one test job
- normalize structure
- compute SMI
- save to database

---

### Step 4
Generate:
- first tailored resume
- first spreadsheet export

---

# Explicit Non-Goals (Current Phase)

Do NOT implement yet:
- LinkedIn scraping
- browser fingerprint evasion
- cloud deployment
- Kubernetes
- plugin systems
- microservices
- multi-user auth
- autonomous auto-apply systems
- distributed orchestration
- complex agent frameworks

Keep the system:
- local
- inspectable
- debuggable
- incremental

---

# Coding Standards

## General Rules

Prefer:
- small files
- single responsibility
- descriptive names
- explicit imports
- predictable flow

Avoid:
- magic behavior
- hidden state
- overly dynamic architecture
- deep inheritance trees

---

## Function Design

Functions should:
- do one thing
- return predictable outputs
- remain independently testable
- avoid unnecessary side effects

---

## Logging

Use clear logging.

Example:

```python
print("Generating embedding...")
```

Prefer understandable diagnostics over elegant abstraction.

---

# Long-Term Vision

Future versions may include:
- autonomous source discovery
- adaptive career weighting
- interview preparation
- recruiter response analysis
- salary intelligence
- local vector memory evolution
- email parsing
- calendar integration
- local fine-tuned models

These are future expansion areas, not current implementation targets.

---

# Core Principle

JobIntel is fundamentally:

```txt
A local autonomous semantic career intelligence system.
```

The project prioritizes:
- relevance
- transparency
- privacy
- maintainability
- AI-assisted extensibility

Above:
- scale
- complexity
- premature sophistication

