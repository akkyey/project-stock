# Manual Browser Analysis Tool (`manual_runner.py`) - v12.0

## Overview
This tool is designed to bypass API quotas or leverage advanced features of browser-based AI models (such as Gemini Advanced or ChatGPT with Web Search). It splits the analysis process into two stages: "Prepare" and "Ingest".

## Workflow
1. **Step 1: Prepare**
    - Reads the database and applies `ScoringEngine` filters.
    - Generates a prompt file (`manual_prompt.txt`) and a context file (`data/temp/manual_context.csv`).
2. **Human Interaction (Browser)**
    - User copies the prompt to the browser AI.
    - User saves the AI's JSON response as `manual_response.json`.
3. **Step 2: Ingest**
    - Reads `manual_response.json` and `manual_context.csv`.
    - Merges data and saves results to the **Database**.

## Usage

### Step 1: Preparation
Run the following to filter stocks and generate the prompt.
```bash
python manual_runner.py --step 1
```

### Step 2: Ingestion
After getting the AI response:
1. Copy the JSON part of the response.
2. Save it as `manual_response.json` in the project root.
3. Run the ingestion command:
```bash
python manual_runner.py --step 2
```

## Tips
- **JSON Format**: Ensure the AI returns a valid JSON array.
- **Backend Sync**: v12.0 uses the same `ScoringEngine` as the automated tools, ensuring consistency between manual and automatic analysis.

## Legacy Support
- **Japanese Headers**: The tool automatically handles Japanese column headers for backward compatibility with legacy spreadsheets.

---
*Last Updated: 2026-01-01 (v12.0)*
