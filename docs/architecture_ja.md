# アーキテクチャ設計 (v12.0) - 自動分析システム

## 概要
本書は、**自動分析システム (`stock_analyzer.py`)** の最新アーキテクチャについて記述します。
Stock Analyzer v12.0 は、定量的戦略（フィルタリング）と定性的分析（AI）を明確に分離した **2段階分析 (Two-Stage Analysis)** を継承しつつ、各コンポーネントを独立したエンジンとして再構成し、型安全と拡張性能を最大化しています。

## システムコンポーネント

### 1. 実行層 (Runner / CLI / Commands)
- **コマンド層 (`src/commands/`)**:
    - **機能分離**: `analyze`, `extract`, `ingest`, `reset` などの機能を独立したコマンドクラスとして実装。
    - **Orchestrator (`src/orchestrator.py`)**: 複雑なスケジュール（日次・週次・月次）と Sentinel アラートによる再分析トリザーを管理。

### 2. データ層 (Data Persistence)
- **データベース (SQLite + Peewee ORM)**:
    - **`stocks` / `market_data` / `analysis_results`**: 構造化されたデータ保存と高速なクエリ（複数銘柄一括取得等）をサポート。
    - **`src/database.py`**: ORM 操作をカプセル化し、一括処理（`upsert_market_data`, `get_market_data_batch`）を提供。

### 3. ロジック層 (Analysis Engines)
- **Scoring Engine (`src/calc/engine.py`)**:
    - **戦略登録制**: `STRATEGY_REGISTRY` により、動的な戦略の追加が可能。
    - **Explainable Scoring**: スコアを要素分解し、`v1` (Legacy) および `v2` (Vectorized Generic) 戦略をサポート。
    - **リスク調整 (v14.0)**: `real_volatility` (実ボラティリティ) に基づく自動ペナルティ (-10pt) ロジックを統合。
- **Validation Engine (`src/validation_engine.py`)**:
    - **セクター別ポリシー**: セクターごとのデータ欠損許容度や異常値判定を動的に適用。
    - **並列検証**: `ThreadPoolExecutor` を活用し、大量の銘柄データを高速に検証。
- **Sentinel (`src/sentinel.py`)**:
    - **異常検知**: 株価の急変やランク変動を監視し、インテリジェントに再分析をリクエスト。

### 4. AI 層 (Qualitative Analysis)
- **AI パッケージ (`src/ai/`)**:
    - **`KeyManager`**: 複数 API キーのローテーションと健康診断 (Health Check)。
    - **`PromptBuilder`**: 戦略に応じた動的なプロンプト生成。`real_volatility` や `beta` などのリスク指標を変数として注入。
    - **`ResponseParser`**: AI 出力の厳格なパースと構造化。
    - **`AIAgent`**: 上記を統合し、Gemini API を用いた定性的評価を実行。

### 5. 出力・ユーティリティ層
- **Reporting (`src/reporter.py`, `src/result_writer.py`)**: 多彩なフォーマットでの分析結果出力。
- **Utils (`src/utils.py`)**: `safe_float` などの共通関数の集約。

## 品質保証
- **静的解析 (`mypy`)**: プロジェクト全体で型安全を確保。
- **自己診断 (`self_diagnostic.py`)**: システム健全性のスモークテスト。
- **テスト網羅率**: `pytest` によるユニットテストおよび統合テスト。

---
*最終更新: 2026-01-07 (v14.0)*
