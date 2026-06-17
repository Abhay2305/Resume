# TASKS.md

# AI Resume Builder Development Roadmap

This document tracks the development progress of the AI Resume Builder.

Claude Code should always consult this file before beginning implementation.

---

# Project Status

Current Phase:

🟡 Infrastructure Complete

The project architecture has been established.

Development is now focused on feature implementation.

---

# Completed

## Project Setup

* [x] Frontend initialized
* [x] Backend initialized
* [x] FastAPI configured
* [x] React + Vite configured
* [x] SQLite database created
* [x] Authentication foundation
* [x] API routing structure
* [x] Business service layer
* [x] AI abstraction layer
* [x] Component architecture
* [x] Initial project documentation

---

# Current Goal

Build a production-quality AI Resume Builder following the existing architecture.

Implement features incrementally.

Do not perform large-scale refactoring unless explicitly requested.

---

# Phase 1 — Core User Experience

## Landing Page

Status: Pending

Tasks

* [ ] Hero section
* [ ] Feature overview
* [ ] Resume templates preview
* [ ] Call-to-action buttons
* [ ] Navigation
* [ ] Footer

---

## Authentication

Status: Review Existing Implementation

Tasks

* [ ] Verify login flow
* [ ] Verify registration flow
* [ ] Verify session handling
* [ ] Improve UI if necessary

---

## Dashboard

Status: Review Existing Implementation

Tasks

* [ ] Dashboard layout
* [ ] Resume list
* [ ] Create Resume button
* [ ] Recent resumes
* [ ] User profile

---

# Phase 2 — Resume Generation

## Prompt Input

Status: Pending

Tasks

* [ ] Prompt textarea
* [ ] Resume type selection
* [ ] Experience level
* [ ] Industry selection
* [ ] Additional instructions

---

## AI Resume Generation

Status: Pending

Tasks

* [ ] Connect frontend to backend
* [ ] Generate structured resume
* [ ] Loading animation
* [ ] Error handling
* [ ] Retry support

---

## Resume Preview

Status: Pending

Tasks

* [ ] Live preview
* [ ] Section rendering
* [ ] Template rendering
* [ ] Responsive layout

---

# Phase 3 — Resume Editor

Status: Pending

Tasks

* [ ] Personal information
* [ ] Summary editor
* [ ] Experience editor
* [ ] Education editor
* [ ] Skills editor
* [ ] Projects editor
* [ ] Certifications
* [ ] Drag-and-drop ordering
* [ ] Undo support

---

# Phase 4 — Templates

Status: Pending

Templates

* [ ] Meridian
* [ ] Ashford
* [ ] Luma
* [ ] Pulse

Requirements

* Switching templates must not lose resume data.

---

# Phase 5 — ATS Optimization

Status: Pending

Tasks

* [ ] Resume scoring
* [ ] Keyword analysis
* [ ] Missing skills detection
* [ ] Formatting analysis
* [ ] Improvement suggestions

---

# Phase 6 — Cover Letter Generator

Status: Pending

Tasks

* [ ] Job description input
* [ ] Company information
* [ ] AI cover letter generation
* [ ] Editing
* [ ] Export

---

# Phase 7 — Export

Status: Pending

Tasks

* [ ] PDF export
* [ ] Print support
* [ ] Download
* [ ] Sharing

---

# Phase 8 — User Features

Status: Pending

Tasks

* [ ] Resume history
* [ ] Resume duplication
* [ ] Delete resume
* [ ] Auto-save
* [ ] Version history

---

# Future Features

These should NOT be implemented unless requested.

* AI Interview Preparation
* Portfolio Generator
* LinkedIn Profile Generator
* Job Matching
* Resume Analytics
* AI Career Assistant
* Resume Comparison
* Multi-language Support

---

# Development Workflow

For every feature:

1. Read the existing implementation.
2. Understand the architecture.
3. Search for reusable components.
4. Implement one feature only.
5. Test the implementation.
6. Explain the changes.

---

# Rules

Do NOT

* Rewrite the project
* Refactor unrelated modules
* Duplicate components
* Hardcode AI providers
* Break existing APIs
* Introduce unnecessary dependencies

Always

* Preserve architecture
* Write reusable code
* Keep components modular
* Keep backend logic inside services
* Keep routers lightweight
* Follow existing naming conventions

---

# Definition of Done

A task is complete only when:

* Functionality works
* Existing features remain intact
* Code follows project architecture
* No duplicate logic exists
* Error handling is implemented
* Code is production-ready

---

# Next Task

Before implementing anything:

1. Inspect the repository.
2. Compare the current implementation with this roadmap.
3. Determine what has already been completed.
4. Update this document if necessary.
5. Continue with the next unfinished task.

Never assume a feature is missing without verifying the existing code first.
