# Stock Analyzer v12.0 - User Manual

Stock Analyzer v12.0 is an automated investment analysis platform. It features **Equity Auditor** as the core engine, utilizing decoupled Scoring and AI modules for high-speed, type-safe analysis.

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Fetch Data**:
   ```bash
   python collector.py
   ```
   Downloads latest stock prices and financials to the database.

3. **Analyze**:
   ```bash
   python equity_auditor.py --mode analyze --limit 5 --strategy value_strict
   ```
   Performs screening, scoring, and AI analysis in one go.

## Core Features

### 1. Advanced Engines (v12.0)
- **Scoring Engine**: High-speed, dynamic scoring for multiple investment strategies.
- **Validation Engine**: Automated data quality checks using sector-specific policies.
- **AIAgent**: Sophisticated qualitative analysis using Gemini API with multi-key rotation.

### 2. Smart Cache & Hybrid Retry
- **Smart Cache**: Skips AI analysis if stock data hasn't changed, saving API quota.
- **Hybrid Retry**: Automatically handles API limits (429) and network errors.

## CLI Options (equity_auditor.py)

| Option       | Description                                                   |
| :----------- | :------------------------------------------------------------ |
| `--mode`     | Operation mode (`extract`, `analyze`, `ingest`, `reset`).     |
| `--strategy` | Investment strategy (`value_strict`, `growth_quality`, etc.). |
| `--limit`    | Limit the number of stocks to process.                        |
| `--format`   | Output format (`json` or `csv`).                              |
| `--debug`    | Mock AI calls for testing.                                    |

---
*Last Updated: 2026-01-01 (v12.0)*
