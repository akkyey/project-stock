# Refactoring Plan

## 1. Objective
Enhance code maintainability, testability, and robustness by refactoring complex logic accumulated through iterative development.

## 2. Targeted Areas

### A. Core Architecture (High Impact)
1. **Type Hinting & Modern Python**:
    - **Issue**: Lack of type hints reduces code clarity and IDE support.
    - **Proposal**: Add type hints (Python 3.12+) to all function signatures in `src/`.
2. **Configuration Management**:
    - **Issue**: `stock_analyzer.py` manually loads `.env` and merges args.
    - **Proposal**: Centralize environment and arg management in `ConfigLoader` or a new `AppConfig` class.

### B. Business Logic Components
1. **Analysis Engine (`src/engine.py`)**:
    - **Issue**: Conflict between V3 Strategy filters and V3.3 Styling logic.
    - **Proposal**: Decouple "Hard Filters" from "Scoring Styles". Ensure distinct processing layers.
2. **Calculator (`src/calc.py`)**:
    - **Issue**: Monolithic `calc_quant_score` (Coverage 70%).
    - **Proposal**: Extract metric-specific logic into helper methods or Strategy classes.
3. **Data Provider (`src/provider.py`)**:
    - **Issue**: Hardcoded SQL queries.
    - **Proposal**: Use dynamic query construction based on Model fields using Peewee introspection.

### C. Data Ingestion & Orchestration
1. **Loader (`src/loader.py`)**:
    - **Issue**: Hardcoded column mapping and manual encoding loops.
    - **Proposal**: Move column mappings to `config.yaml` or a constant definition file. Simplify encoding logic.
2. **Analyzer (`src/analyzer.py`)**:
    - **Issue**: Mixes orchestration, logging, and circuit breaker logic.
    - **Proposal**: Extract `CircuitBreaker` logic into a separate class/module. Simplify `run_analysis`.

## 3. Execution Phase Plan
1. **Phase 1: Foundation**: Add Type Hints and Fix Engine Logic (Fixes known defect).
2. **Phase 2: Decomposition**: Refactor Calculator and Provider (Improves Testability).
3. **Phase 3: Modernization**: Refactor Loader and Config (Cleanup).

## 4. Verification
- Use `tests/run_integration_tests.py` as the safety net.
- Enforce strict mypy checks (optional but recommended).


## 4. Verification
- Use the newly created **System Test Suite** (`tests/run_integration_tests.py`) to ensure no regression in logic behavior.
- Use **Coverage Tests** to verify that refactored modules have improved testability.
