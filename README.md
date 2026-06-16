# Prompt Resume

## Project Overview

Prompt Resume is an AI-powered Career Document Platform currently under active development.

The goal is to build a production-grade SaaS application that generates professional, ATS-optimized resumes and cover letters using AI while following Harvard, Stanford, MIT, and other university career-writing guidance.

This repository already contains a significant amount of frontend and backend implementation.

Before making any changes, understand the existing architecture and continue building on top of it instead of replacing it.

---

# Current Project Status

This project is **NOT** starting from scratch.

Approximate completion:

Frontend: **70%**

Backend: **45%**

AI Layer: **25%**

Overall Product: **60-65%**

The foundation has already been built.

The remaining work should extend the existing architecture instead of rebuilding it.

---

# Existing Frontend

The frontend already contains the following modules:

* Landing Page
* Authentication
* Login
* Register
* Dashboard
* Resume Builder Flow
* Resume Editor
* Resume Preview
* ATS Review Components
* AI Generation Screens
* Resume Export
* Template Selection
* Modern UI Components
* Responsive Layout
* Animations

Most frontend pages already exist.

Do not recreate them unless absolutely necessary.

Focus on integrating real backend functionality.

---

# Existing Backend

The backend is built using FastAPI.

Existing components include:

* JWT Authentication
* SQLAlchemy ORM
* Database Models
* API Routers
* Service Layer
* Template APIs
* Resume APIs
* ATS APIs
* PDF Services
* Storage Services
* LLM Service
* Authentication System

The backend architecture is already modular.

Continue following the existing structure.

Do not collapse everything into a single file.

---

# Current AI Implementation

The project already contains an LLM service.

Current implementation includes:

* LLM abstraction
* Gemini integration
* Mock fallback generation

However, most AI generation is still placeholder or fallback based.

The existing architecture should be improved rather than replaced.

---

# Existing Architecture

Current architecture already follows a service-oriented approach.

Frontend

↓

FastAPI Backend

↓

Services

↓

Database

↓

LLM Service

↓

Generated Output

Continue using this architecture.

---

# Current Goal

The current objective is **NOT** to redesign the application.

The objective is to replace mocked AI functionality with a production-ready AI pipeline.

---

# What Already Exists

The following systems already exist in some form:

Authentication

Database

Resume CRUD

Template Selection

Resume Preview

Dashboard

Backend APIs

LLM Service

PDF Services

Storage Services

JWT Authentication

Do not rebuild these modules.

Improve and extend them.

---

# What Still Needs To Be Built

The following features are incomplete or missing:

## AI Provider

Replace mocked generation with production-ready OpenAI integration.

The architecture should remain provider-independent so Gemini and Claude can be added later.

---

## Prompt Builder

Create a dedicated Prompt Builder Service.

Responsibilities:

* Build prompts
* Inject writing rules
* Inject ATS rules
* Inject knowledge
* Build structured prompts

Never send raw user input directly to the LLM.

---

## Knowledge Engine

Create a knowledge ingestion system.

The application will contain a folder similar to:

backend/

knowledge/

pdfs/

Harvard Resume Guide.pdf

Harvard Cover Letter Guide.pdf

Stanford Career Guide.pdf

MIT Career Guide.pdf

Yale Career Guide.pdf

...

The application should automatically read these PDFs.

Extract useful information.

Store the extracted knowledge inside the database.

Do not hardcode knowledge inside prompts.

---

## Knowledge Retrieval

During generation:

Retrieve relevant knowledge from the database.

Inject it into prompts.

The LLM should use retrieved university guidance while generating resumes and cover letters.

---

## Resume Examples

Create a database containing professional resume transformations.

Example:

Raw:

Worked with Oracle.

Professional:

Developed Oracle SQL reporting solutions supporting enterprise business operations.

These examples should improve prompt quality.

---

## ATS Engine

Implement a deterministic ATS scoring engine.

Do not rely on AI for ATS scores.

Scoring should include:

Resume completeness

Action verbs

Skills

Formatting

Keywords

Section coverage

Length

Generate:

Score

Suggestions

Recommendations

---

## Job Description Analyzer

Implement:

Keyword extraction

Technology extraction

Skill extraction

Resume matching

Gap analysis

Match score

---

## Cover Letter Engine

Generate professional cover letters using:

Resume

Job Description

Company

Role

University guidance

ATS best practices

---

## Knowledge Base

The application will use career guidance from:

Harvard University

Stanford University

MIT

Yale

Princeton

Columbia

Carnegie Mellon

Georgia Tech

University of Pennsylvania

Other trusted universities.

These PDFs are knowledge sources.

They should become part of the application's knowledge base.

The LLM should reference this knowledge during generation.

---

## Future RAG Support

Design the architecture so it can later support:

Vector embeddings

Semantic search

pgvector

Retrieval-Augmented Generation (RAG)

Do not tightly couple the system to today's implementation.

---

# Development Principles

Continue using the existing architecture.

Avoid unnecessary rewrites.

Write modular services.

Avoid hardcoding business logic.

Avoid hardcoding prompts.

Avoid hardcoding templates.

Keep frontend and backend loosely coupled.

Write production-quality code.

Follow clean architecture.

Follow SOLID principles.

---

# AI Development Philosophy

The competitive advantage is **NOT** the LLM.

The competitive advantage is:

Knowledge Engine

Prompt Builder

Resume Rules

University Career Guidance

ATS Engine

Resume Examples

Job Matching

The LLM is only responsible for writing.

The application is responsible for intelligence.

---

# Immediate Development Priority

The next implementation phase should focus on:

1. Production-ready OpenAI integration

2. Prompt Builder Service

3. Knowledge Ingestion Pipeline

4. Knowledge Retrieval Layer

5. Resume Generation Pipeline

6. Cover Letter Generation

7. ATS Scoring Engine

8. Job Description Analyzer

The existing frontend should begin consuming these services rather than mocked responses.

---

# Mission

Continue building Prompt Resume into a production-ready AI Career Document Platform by extending the existing architecture, replacing mocked AI with real intelligence, and using university career guidance as the foundation for high-quality resume and cover letter generation.

Do not rebuild what already exists.

Build on top of it.
