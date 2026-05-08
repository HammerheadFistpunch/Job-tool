```md
# JobIntel — Autonomous AI Job Intelligence System
Version: 0.1
Date: 2026-05-08

---

# Project Summary

JobIntel is a local-first autonomous AI-powered job intelligence platform for Windows.

The system continuously:
- analyzes candidate fit
- discovers jobs
- scores job relevance
- generates tailored application documents
- tracks application pipeline state

The system is designed for personal use and prioritizes:
- local data ownership
- free/open tooling
- low manual intervention
- portable architecture
- ATS-aware resume adaptation

---

# Core Functional Goals

## Outputs

### 1. Tailored Resume Generation
Generate a minimally modified ATS-optimized resume for each job.

Requirements:
- preserve original structure
- preserve factual integrity
- inject relevant ATS keywords naturally
- avoid hallucinated experience
- generate versioned outputs per job

Output formats:
- DOCX
- ODT

---

### 2. Tailored Cover Letter Generation
Generate a short modern cover letter for each job.

Requirements:
- concise
- modern tone
- role-aware
- company-aware where possible
- generated automatically after scoring threshold met

Output formats:
- DOCX
- ODT

---

### 3. Curated Job Spreadsheet
Generate a continuously updated structured job list.

Columns:
- Company
- Title
- Location
- Remote/Hybrid/Local
- Salary (if available)
- SMI score
- Source URL
- Date discovered
- Pipeline status

Export formats:
- XLSX
- CSV

---

### 4. Autonomous Job Discovery
The system autonomously determines:
- best-fit roles
- adjacent opportunities
- evolving search targets

The user does not manually curate most searches.

---

# Intelligence Model

## Career Reference Markdown

The primary intelligence source is a markdown document.

Example:
career_reference.md

This file contains:
- goals
- preferences
- strengths
- role interests
- weighted skills
- exclusions
- AI-derived observations

The markdown file acts as:
- semantic intent source
- vector embedding source
- autonomous search guidance layer

---

# Similarity Match Index (SMI)

Jobs are ranked using semantic similarity.

Method:
- embedding comparison
- vector similarity scoring

Comparison:
career_reference_embedding
VS
job_description_embedding

Range:
0.00 → 1.00

Purpose:
- prioritize best-fit jobs
- suppress low-relevance noise
- continuously refine targeting

---

# User Constraints

## User Preferences

### Resume Source
- master_resume.docx

### Job Scope
- remote
- local

### Authentication
- avoid authenticated scraping

### Application Submission
- no auto-apply

### Storage
- local only

### Product Scope
- personal use

### AI Control Model
- fully autonomous AI guidance

---

# Recommended Technical Stack

## Backend
Python

Reason:
- AI ecosystem
- document tooling
- automation tooling
- local model compatibility

---

## Frontend
Local web application

Recommended stack:
- FastAPI
- React

Reason:
- fast iteration
- clean UI
- easy desktop packaging later

---

## Desktop Packaging
Future:
- Tauri
OR
- PyInstaller

Potential output:
JobIntel.exe

---

# Recommended AI Stack

## Local AI
Ollama

Recommended models:
- llama3
- mistral
- qwen

---

## Embeddings
nomic-embed-text

---

## Semantic Matching
sentence-transformers

---

## Vector Storage
ChromaDB

---

## Database
SQLite

Tables:
- jobs
- applications
- similarity_scores
- generated_documents
- pipeline_status

---

# Recommended Job Discovery Strategy

## Preferred Sources
- Greenhouse
- Lever
- Wellfound
- RemoteOK
- WeWorkRemotely
- company career pages

---

## Avoid Initial Dependence On
- LinkedIn scraping
- authenticated-only sources

Reason:
- instability
- anti-bot systems
- maintenance overhead

---

# Automation Strategy

## Browser Automation
Recommended:
Playwright

Reason:
- resilient
- cross-site capable
- less fragile than raw scraping

---

# Recommended Directory Structure

/jobintel
    /backend
        /ai
        /jobs
        /pipeline
        /documents
        /scheduler

    /frontend
        /dashboard
        /settings
        /jobviewer

    /storage
        /jobs
        /generated
        /vectors
        /profiles

    /config

---

# Proposed Workflow

## Step 1
Load:
- master resume
- career_reference.md

---

## Step 2
Generate embeddings.

---

## Step 3
Autonomous job discovery begins.

---

## Step 4
Scrape and normalize job descriptions.

---

## Step 5
Calculate SMI score.

---

## Step 6
Rank and store jobs.

---

## Step 7
Generate:
- ATS-aware resume
- short cover letter

---

## Step 8
Track lifecycle states:
- discovered
- reviewed
- applied
- interviewing
- rejected
- offer

---

# UI Design Goals

Style:
- clean
- minimal
- low-friction

---

## Dashboard Components

### Left Panel
- scheduler
- AI provider
- system status
- search controls

### Main Table
| SMI | Role | Company | Salary | Remote | Status |

---

## Job Detail View
Displays:
- job description
- generated resume preview
- generated cover letter preview
- pipeline controls

---

# Long-Term Expansion Possibilities

Potential future additions:
- local LLM fine-tuning
- adaptive weighting evolution
- interview preparation
- salary intelligence
- recruiter response scoring
- company culture analysis
- local vector memory evolution
- email parsing
- calendar integration

---

# Design Philosophy

The system should:
- minimize user effort
- maximize semantic relevance
- preserve privacy
- remain portable
- avoid vendor lock-in
- operate locally where possible
- maintain transparent outputs
- avoid fabricated resume content

---

# Current Strategic Direction

Architecture Direction:
Autonomous Local AI Job Intelligence Platform

Primary Differentiator:
Semantic career intent modeling via markdown-driven AI guidance.
```
That materially changes the implementation strategy — and honestly, in a good way.

You should NOT be building this as:

* a traditional hand-coded software project
* a deeply engineered enterprise application
* or a manually maintained scraper platform

You should build it as:

# An AI-Orchestrated Software System

Meaning:

* architecture is human-defined
* implementation is AI-generated
* components are modular
* prompts become part of the development system

That is now a viable development methodology.

# What This Means Practically

You should optimize for:

## 1. AI-Friendly Codebase

The project should be:

* modular
* explicit
* heavily documented
* low abstraction
* predictable naming

NOT:

* clever
* compressed
* over-engineered

Because future AI sessions will maintain it.

---

# 2. Prompt-Driven Development

You will likely use:

* ChatGPT
* local models
* Claude
* Cursor
* Copilot

to iteratively generate:

* modules
* fixes
* integrations
* UI components

So the repository itself should contain:

* architecture markdown
* implementation plans
* interface definitions
* behavioral specifications

The markdown becomes part of the software.

---

# 3. Strong Separation Boundaries

AI performs MUCH better when components are isolated.

Good:

```txt id="ogfbfk"
job_scraper.py
similarity_engine.py
resume_generator.py
```

Bad:

```txt id="xqfk9n"
mega_system.py
```

---

# 4. Self-Describing Structure

Every folder should explain itself.

Example:

```txt id="jlwmro"
/ai
    README.md

/jobs
    README.md

/pipeline
    README.md
```

This dramatically improves AI-generated maintenance quality.

---

# 5. Avoid Premature Complexity

Do NOT start with:

* microservices
* Kubernetes
* cloud infra
* distributed systems
* complex auth
* plugin ecosystems

You are building:

```txt id="3v0bsz"
single-user local intelligence software
```

That is GOOD.

Keep it that way initially.

---

# Revised Recommended Stack (For AI-Assisted Development)

## Backend

Python

Reason:

* easiest AI generation quality
* best documentation ecosystem
* easiest debugging
* best automation tooling

---

## Frontend

React + Tailwind

Reason:

* AI generates excellent React now
* UI iteration is fast
* local web UX is clean

---

## Database

SQLite

Reason:

* zero maintenance
* easy inspection
* AI-friendly

---

## Local AI

Ollama

Reason:

* free
* local
* predictable

---

# Most Important Recommendation

You should structure the repository around:

# “AI maintainability”

That is now an actual engineering concern.

---

# You Also Need a “System Brain” File

I strongly recommend a root-level file:

```txt id="4sjvwf"
SYSTEM_CONTEXT.md
```

This file should contain:

* architecture overview
* coding standards
* module contracts
* AI behavioral rules
* assumptions
* design philosophy

Every future AI coding session references it.

This massively improves consistency.

---

# Example AI Development Workflow

## Step 1

You say:

```txt id="gprrry"
Build the similarity engine using sentence-transformers.
Reference SYSTEM_CONTEXT.md.
```

## Step 2

AI generates module.

## Step 3

You test locally.

## Step 4

AI fixes issues.

This becomes iterative orchestration rather than traditional coding.

---

# Critical Recommendation

Because you are not primarily a coder:

## DO NOT begin with:

* full-stack complexity
* polished UX
* production packaging
* all job sources

Instead:

# Build vertical slices.

Example:

## Slice 1

* ingest resume
* ingest markdown
* scrape ONE job
* generate ONE score

Then:

* generate ONE tailored resume

THEN:

* scale outward

This prevents overwhelming debugging complexity.

---

# Your Actual Role

You are effectively:

# the systems architect/operator

not the line-by-line programmer.

That is completely workable in 2026 if the repository is structured correctly.

---

# Strong Recommendation for Your First Milestone

## MVP v0.1

Build ONLY:

### Inputs

* master_resume.docx
* career_reference.md

### Processing

* scrape one source
* compute SMI
* generate one tailored resume

### Outputs

* spreadsheet
* generated docx

### UI

* simple dashboard
* job table

No more than that initially.

---

# Final Recommendation

You should treat:

* markdown
* prompts
* architecture docs
* schemas
* behavioral contracts

as first-class software assets.

Not “notes.”

They are part of the executable intelligence layer of this system.
