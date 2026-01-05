# Stock Analyzer v12.0 - ユーザーマニュアル

Stock Analyzer v12.0 の操作マニュアルです。本バージョンでは **Equity Auditor** が中核となり、型安全な ScoringEngine と AI パッケージにより、より高度で信頼性の高い分析を実現します。

## 全体ワークフロー

### 1. データ収集 (Daily Update)
最新の株価・財務データを取得してデータベースを更新します。
```bash
python collector.py
```

### 2. 定型ルーチン (Orchestration)
運用のメインとなる定型処理（スキャン、異常検知、AI分析、レポート生成）を一括実行します。
```bash
# 日次：Top50銘柄の監視とAI分析
python orchestrator.py daily

# 週次：全銘柄のフルスキャンとAI分析、履歴更新
python orchestrator.py weekly --debug # 最初はデバッグ推奨
```

### 3. 個別分析 (Analyze Mode)
特定の戦略や銘柄に絞って、スクリーニングとAI分析を詳細に行います。
```bash
# 例: バリュー厳選戦略で上位5件を分析
python equity_auditor.py --mode analyze --limit 5 --strategy value_strict --format csv
```
- **特徴**:
    - **Scoring Engine**: 戦略ごとの動的なスコアリング。
    - **Validation Engine**: セクター別の厳格なデータ品質チェック。
    - **AIAgent (v12.0)**: 分割されたモジュールによる、より正確な定性的パース。
    - **Smart Cache / Hybrid Retry**: API リソースの効率化とエラー時の自動復旧。

### 3. テストと品質確認
開発者やテスターは、以下のコマンドでシステムの健全性を確認できます。
```bash
# 自己診断 (19項目)
python self_diagnostic.py

# 静的解析
../venv/bin/mypy src --explicit-package-bases
```

---

## 主要オプション (equity_auditor.py)

| オプション        | 説明                                                                    |
| :---------------- | :---------------------------------------------------------------------- |
| `--mode`          | 動作モードを指定 (`extract`, `analyze`, `ingest`, `reset`)              |
| `--strategy`      | 投資戦略を指定 (`value_strict`, `growth_quality`, `turnaround_spec` 等) |
| `--limit`         | 処理する銘柄数の上限                                                    |
| `--format`        | 出力形式 (`json` or `csv`)                                              |
| `--debug`         | デバッグモード（AI呼び出しをシミュレート）                              |
| `--force-refresh` | キャッシュを無視して強制的に再分析                                      |
| `--all`           | 全件対象 (resetモード等)                                                |

## 監視・運用コア (orchestrator.py / sentinel.py)

オーケストレーターは `sentinel` (監視) と `equity_auditor` (分析) を統括し、定型ワークフローを提供します。

- **Daily ルーチン**:
  - 各戦略の上位 50 銘柄を選定。
  - `sentinel` による価格異常・ランキング変動の検知。
  - 必要に応じた再分析とレポート生成。
- **Weekly ルーチン**:
  - 全市場の全銘柄を対象としたフルスキャン。
  - 最新スコアに基づく上位銘柄の AI 分析。
  - 公式ランキング履歴 (`RankHistory`) の更新。

## メンテナンス

### リセット (Reset)
特定戦略のデータをクリアし、再分析可能にします。
```bash
python equity_auditor.py --mode reset --strategy value_strict
```

## 設計・仕様関連
- **[アーキテクチャ設計](architecture_ja.md)**: v12.0 内部構造
- **[テスト仕様書](testing_manual_ja.md)**: テスト・静的解析手順
- **[開発バックログ](backlog.md)**: 今後の計画

---
*最終更新: 2026-01-01 (v12.0)*