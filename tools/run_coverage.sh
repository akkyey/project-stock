#!/bin/bash

# Validate environment
if [[ ! -f "../venv/bin/activate" ]]; then
    echo "⚠️  venv not found in parent directory. Please ensure ../venv exists."
    exit 1
fi

source ../venv/bin/activate
export PYTHONPATH=$(pwd)

echo "🚀 Running Tests with Coverage..."

# オプション: --all で統合テスト含む全テストを実行
if [[ "$1" == "--all" ]]; then
    echo "📊 Mode: ALL tests (including integration)"
    pytest --cov=src --cov=collector --cov=equity_auditor --cov-report=term --cov-report=html -m "" --ignore=tests/archive self_diagnostic.py tests/
else
    echo "⚡ Mode: Unit tests only (excluding integration)"
    pytest --cov=src --cov=collector --cov=equity_auditor --cov-report=term --cov-report=html --ignore=tests/archive self_diagnostic.py tests/
fi

echo ""
echo "✅ Coverage run complete."
echo "📄 Report: file://$(pwd)/htmlcov/index.html"
