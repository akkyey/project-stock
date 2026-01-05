# Architecture Design (v12.1) - Automated Analysis System

## Overview
This document describes the latest architecture of the **Automated Analysis System (`stock_analyzer.py`)**. 
Stock Analyzer v12.0 inherits the **Two-Stage Analysis** (Screening & AI) while re-architecting each component into independent engines to maximize type safety and scalability.

## System Components

### 1. Execution Layer (Runner / CLI / Commands)
- **Command Layer (`src/commands/`)**:
    - **Functional Separation**: `analyze`, `extract`, `ingest`, `reset` are implemented as independent command classes.
    - **Orchestrator (`src/orchestrator.py`)**: Manages complex schedules (Daily/Weekly/Monthly) and re-analysis triggers via Sentinel alerts.
    - **Notebooks (`notebook/`)**: Interactive environments (`run_analysis.ipynb`, `run_diagnostic.ipynb`) used for ad-hoc analysis, debugging, and cloud (Colab) execution.

### 2. Data Layer (Data Persistence)
- **Database (SQLite + Peewee ORM)**:
    - **`stocks` / `market_data` / `analysis_results`**: Supports structured storage and high-speed queries.
    - **`src/database.py`**: Encapsulates ORM operations and provides batch processing (`get_market_data_batch`).

### 3. Logic Layer (Analysis Engines)
- **Scoring Engine (`src/calc/engine.py`)**:
    - **Plugin-based Strategies**: Supports dynamic strategy registration via `STRATEGY_REGISTRY`.
    - **Explainable Scoring**: Decomposes scores into elements, supporting `v1` (Legacy) and `v2` (Vectorized) engines.
- **Validation Engine (`src/validation_engine.py`)**:
    - **Sector-specific Policies**: Dynamically applies data quality checks based on sector.
    - **Parallel Validation**: Utilizes `ThreadPoolExecutor` for high-speed batch verification.
- **Sentinel (`src/sentinel.py`)**:
    - **Anomaly Detection**: Monitors price changes and rank fluctuations to trigger intelligent re-analysis.

### 4. AI Layer (Qualitative Analysis)
- **AI Package (`src/ai/`)**:
    - **`KeyManager`**: Multi-key rotation and health monitoring.
    - **`PromptBuilder`**: Dynamic prompt generation based on strategy/sector.
    - **`ResponseParser`**: Strict parsing and validation of AI output.
    - **`AIAgent`**: Integrates the above to perform qualitative analysis using Gemini API.

### 5. Output & Utility Layer
- **Reporting (`src/reporter.py`, `src/result_writer.py`)**: Generates reports in various formats.
- **Utils (`src/utils.py`, `src/env_loader.py`)**: Centralized utility functions (e.g., `safe_float`) and environment variable management (recursive .env loader).

## Quality Assurance
- **Static Analysis (`mypy`)**: Ensures project-wide type safety.
- **Self-Diagnostic (`self_diagnostic.py`)**: Automated health checks for the entire system.

---
*Last Updated: 2026-01-04 (v12.1)*
