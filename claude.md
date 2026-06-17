\# CLAUDE.md



\# AI Resume Builder - Claude Code Instructions



This file contains project-specific instructions for Claude Code.



Always read and follow these instructions before implementing or modifying any code.



\---



\# Primary Objective



Your goal is to help build a production-quality AI Resume Builder.



Do not generate code quickly just to satisfy the prompt.



Instead:



\* understand the existing architecture

\* preserve modularity

\* write maintainable code

\* minimize unnecessary changes

\* avoid introducing technical debt



Always think like a senior software engineer.



\---



\# Before Every Task



Before modifying code:



1\. Read all relevant files.

2\. Understand how the current implementation works.

3\. Search for reusable components.

4\. Reuse existing services whenever possible.

5\. Never assume missing functionality without checking the repository.



If additional context is required, read more files before writing code.



\---



\# Project Architecture



The project follows a modular architecture.



Frontend



↓



API Layer



↓



Backend Routers



↓



Business Services



↓



AI Provider Layer



↓



Database



Do not bypass layers.



Business logic belongs in backend services.



Frontend should remain presentation-focused.



\---



\# Frontend Guidelines



Use existing components whenever possible.



Avoid duplicate components.



Keep components small and reusable.



Avoid placing business logic inside UI components.



Separate:



\* UI

\* API calls

\* state management



Do not create unnecessary global state.



Maintain consistent styling throughout the application.



\---



\# Backend Guidelines



Keep routers lightweight.



Business logic belongs inside services.



Database logic belongs inside the data layer.



Avoid putting AI logic directly inside routers.



Write reusable service methods.



Maintain separation of concerns.



\---



\# AI Provider Design



The project should remain provider-agnostic.



Do NOT tightly couple the application to:



\* Anthropic

\* Gemini

\* NVIDIA NIM

\* OpenAI

\* OpenRouter



AI providers should always be replaceable.



Design abstractions instead of provider-specific implementations.



\---



\# Implementation Strategy



Never attempt to implement the entire application in one step.



Always implement one feature at a time.



Preferred workflow:



1\. Understand current implementation.

2\. Identify missing functionality.

3\. Design the solution.

4\. Implement.

5\. Verify.

6\. Explain what changed.



\---



\# Code Quality



Always prefer:



Readable code over clever code.



Reusable code over duplicated code.



Simple architecture over unnecessary complexity.



Consistency over personal preference.



Write production-quality code.



\---



\# Existing Code



Treat existing code as the source of truth.



Do not rewrite working code unless necessary.



Avoid large refactors.



Preserve existing architecture.



Do not rename files or folders without a strong reason.



\---



\# Feature Development



Before implementing any feature:



\* inspect related components

\* inspect related services

\* inspect related API endpoints

\* inspect related models



Only then begin implementation.



\---



\# Bug Fixes



When fixing bugs:



1\. Identify root cause.

2\. Explain the cause.

3\. Fix only the necessary code.

4\. Avoid introducing unrelated changes.



Never patch symptoms without understanding the underlying issue.



\---



\# Repository Analysis



Avoid performing repository-wide refactors.



Avoid changing multiple modules unnecessarily.



When analyzing the repository:



\* work module by module

\* avoid unnecessary file reads

\* avoid Explore Agent style planning



Incremental analysis is preferred.



\---



\# Documentation



When implementing significant features:



Update documentation if necessary.



Keep comments concise.



Avoid redundant comments.



Code should be self-explanatory whenever possible.



\---



\# Performance



Avoid unnecessary re-renders.



Avoid unnecessary API calls.



Reuse existing objects.



Prefer efficient algorithms when appropriate.



\---



\# File Organization



Do not create new files unless necessary.



Prefer extending existing modules.



If a new file is required:



\* place it in the appropriate folder

\* follow existing naming conventions



\---



\# Design Philosophy



Every implementation should satisfy:



\* Modular

\* Maintainable

\* Scalable

\* Reusable

\* Readable

\* Production-ready



Never sacrifice architecture for short-term convenience.



\---



\# Response Style



Before writing code:



Explain your understanding of the task.



Describe your implementation plan.



Identify affected files.



After implementation:



Explain:



\* what changed

\* why it changed

\* any assumptions made

\* possible future improvements



\---



\# If Information Is Missing



Never guess.



Instead:



\* inspect additional files

\* ask for clarification if necessary



Do not invent APIs or project structure.



\---



\# Long-Term Vision



The project is intended to become a complete AI career platform.



Future features include:



\* AI Resume Builder

\* Resume Editor

\* ATS Analyzer

\* Cover Letter Generator

\* Job Description Analyzer

\* Resume Scoring

\* Portfolio Generator

\* Resume Versioning

\* AI Career Assistant



Current implementations should support future expansion.



\---



\# Final Rule



Quality is more important than speed.



Understand first.



Plan second.



Implement third.



Verify fourth.



Maintain the architecture at all times.



