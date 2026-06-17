# AI Resume Builder

## Project Overview

AI Resume Builder is a full-stack web application that helps users create professional, ATS-friendly resumes using AI. Instead of manually filling out templates, users can describe their experience in natural language, and the application generates structured resume content that can be edited, optimized, and exported.

The long-term vision is to provide an intelligent resume platform capable of:

* AI-powered resume generation
* ATS score analysis
* Resume optimization
* Cover letter generation
* Multiple professional templates
* PDF export
* Real-time editing experience

---

# Current Project Status

The project foundation has been established.

## Backend

* FastAPI backend
* Authentication system
* Database models
* API routing
* AI service layer
* Resume service architecture
* Template management
* SQLite database

## Frontend

* React + Vite
* Component-based architecture
* API integration layer
* Resume editor foundation
* Landing page
* Authentication pages
* Dashboard pages
* Global styling

The project is currently transitioning from infrastructure development into feature implementation.

---

# Technology Stack

## Frontend

* React
* Vite
* JavaScript
* CSS

## Backend

* FastAPI
* Python
* SQLAlchemy
* SQLite

## AI

Current development uses Claude Code for implementation.

The project is designed so AI providers can be swapped without affecting the application architecture.

Possible providers include:

* Gemini
* OpenRouter
* OpenCode Zen
* Anthropic
* OpenAI

---

# Repository Structure

```
Resume-main/

├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   │
│   ├── requirements.txt
│   ├── run.py
│   └── resume_builder.db
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   └── ...
│   │
│   ├── implementation_plan.md
│   └── package.json
│
└── README.md
```

---

# Planned User Flow

```
Landing Page
        │
        ▼
Prompt Entry
        │
        ▼
AI Resume Generation
        │
        ▼
Resume Preview
        │
        ▼
Resume Editor
        │
        ▼
ATS Analysis
        │
        ▼
Template Selection
        │
        ▼
PDF Export
```

---

# Major Features

## Resume Generation

Generate complete resumes from natural language prompts.

Example:

> "I am a software engineer with three years of Python experience."

---

## Resume Editing

Users can edit every generated section.

* Summary
* Skills
* Experience
* Education
* Projects
* Certifications

---

## ATS Optimization

The application will evaluate resumes against ATS standards.

Future metrics include:

* Keyword matching
* Formatting quality
* Readability
* Missing sections
* Overall ATS score

---

## Cover Letter Generation

Generate personalized cover letters based on:

* Resume
* Job description
* Company information

---

## Resume Templates

Planned templates:

* Meridian
* Ashford
* Luma
* Pulse

Users will be able to switch templates without losing resume data.

---

## PDF Export

Generate professional PDFs while preserving formatting.

---

# Current Development Progress

## Completed

* Project architecture
* Backend initialization
* Database setup
* API structure
* Frontend initialization
* Component organization
* Authentication foundation
* Resume service foundation
* AI service abstraction

---

## In Progress

* AI resume generation workflow
* Resume editor
* Prompt-driven generation
* Template rendering
* ATS analysis
* Export functionality

---

## Planned

* Cover letter generator
* Job description analyzer
* Resume comparison
* Resume version history
* AI suggestions
* Interview preparation
* Portfolio generation

---

# Development Philosophy

This project follows a modular architecture.

Each major responsibility is isolated into its own layer.

```
Frontend

↓

API Layer

↓

Backend Routers

↓

Business Services

↓

AI Providers

↓

Database
```

This makes the project easier to maintain and allows future AI providers to be integrated with minimal changes.

---

# AI Development Workflow

Development is performed using Claude Code.

Current capabilities:

* Read repository
* Modify code
* Refactor components
* Implement features
* Generate documentation
* Debug issues

Current limitations:

* Repository-wide planning using Anthropic Explore Agents is not supported by third-party proxy providers.
* Large repository analysis should be performed module-by-module.

---

# Development Guidelines

When implementing new features:

1. Reuse existing components whenever possible.
2. Keep business logic inside backend services.
3. Keep UI components focused on presentation.
4. Maintain separation between frontend and backend.
5. Avoid hardcoding AI provider logic.
6. Build reusable, maintainable components.
7. Preserve modular architecture.

---

# Long-Term Vision

The goal is to build a production-ready AI career platform rather than a simple resume builder.

Future capabilities include:

* AI Resume Builder
* AI Cover Letter Generator
* ATS Scanner
* Job Matching
* Interview Preparation
* Career Assistant
* Portfolio Generator
* Resume Analytics
* Multiple Export Formats
* User Dashboard
* Resume Version Management

---

# Notes for AI Coding Assistants

Before implementing any feature:

* Read the existing architecture.
* Reuse existing services whenever possible.
* Avoid duplicate components.
* Preserve the project structure.
* Follow modular design principles.
* Keep frontend and backend responsibilities separate.
* Prefer incremental implementation over large-scale refactoring.

The goal is to extend the existing architecture rather than replace it.
