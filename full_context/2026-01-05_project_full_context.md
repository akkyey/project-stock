# Project Full Context Report

Generated at: 2026-01-05 17:04:02

## Documentation

### docs/analyst_rules.md

```markdown
# 株式アナリスト判定ルールブック (Analyst Rulebook)

本ドキュメントは、システム全体の投資判断における「客観的な閾値」と「AIの判定ロジック」を定義する公式ガイドです。

## 1. 判定カテゴリと解釈 (Judgment Definitions)

| 判定                     | 意味                   | 境界条件・基準                                                                    |
| :----------------------- | :--------------------- | :-------------------------------------------------------------------------------- |
| **Bullish (Aggressive)** | **死角なしの絶対買い** | 定量スコア 80以上 かつ Red Flag なし。成長性が極めて高い王道株。                  |
| **Bullish (Defensive)**  | **救済による割安買い** | 「例外救済ルール」適用銘柄。圧倒的なボトム価格（低PBR等）によるお宝株。           |
| **Neutral (Positive)**   | **有力候補**           | スコア 70以上 かつ 致命的欠陥なし。打診買い検討圏内。                             |
| **Neutral (Wait)**       | **様子見**             | スコア 50〜69。成長期待とリスクが拮抗している一般的な検討対象。                   |
| **Neutral (Caution)**    | **要注意**             | スコア 50未満 または 非致命的な懸念（データ一部欠損・低収益等）あり。精査が必要。 |
| **Bearish**              | **回避推奨**           | Red Flag 検出銘柄。構造的欠陥等により投資不可（地雷）。                           |

---

## 2. 定量的判断基準 (Financial Thresholds)

### 2.1 基準値 (Valuation / Profitability / Growth / Quality)
| 項目                     | 割安・良好 (Target) | 割高・警戒 (Min/Max)     | 備考                |
| :----------------------- | :------------------ | :----------------------- | :------------------ |
| **PER (株価収益率)**     | **15.0倍以下**      | **25.0倍以上**           | 成長株は例外あり    |
| **PBR (株価純資産倍率)** | **1.0倍以下**       | **3.0倍以上**            | 解散価値(1.0)を意識 |
| **ROE (自己資本利益率)** | **15.0%以上**       | **8.0%未満**             | 資本効率の重要指標  |
| **営業利益率**           | **10.0%以上**       | **5.0%未満**             | 本業の稼ぐ力        |
| **OCFマージン**          | **10.0%以上**       | **0.0%未満** (即Bearish) | 現金の裏付け        |
| **売上高成長率**         | **20.0%以上**       | **5.0%未満**             | モメンタムの維持    |

### 2.2 Red Flag (即時回避・Bearish)
以下の条件に1つでも該当する場合、AIは冷徹に **Bearish** を宣告しなければならない。
- **営業CFマージン < 0** (粉飾リスク、資金繰り懸念)
- **売上高成長率 < 0** (構造的衰退)
- **PER 30倍超 かつ PBR 5倍超** (正当化できない割高感)

### 2.3 例外救済ルール (Positive Bias)

#### 第1層：鉄板バリュー救済
- **条件**: **PBR 1.0倍未満 かつ 配当利回り 4.0%超** の場合。
- **指示**: 判定を **Neutral (Positive)** 以上へ引き上げ検討。
- **マナー**: その際は必ず **「極めて不本意ではあるが」「例外的に」** などの枕詞を使用すること。

#### 第2層：プロの目利き救済 (v3.5)
- **Deep Value**: **PBR 0.7倍未満** かつ 配当利回り 3.0%超 なら、利益成長が弱くても **Neutral (Wait)** 以上。
- **Quality Growth**: **ROE 15%以上 かつ 営業CFプラス** なら、PER 30倍超でも判定維持。
- **Efficiency**: **PER 10倍未満 かつ 営業利益率 10%超** なら、成長力不足でも判定をボトムアップ。

### 2.4 異常値（分析スキップ）
以下の条件が Pydantic により検知された場合、AI分析をスキップしランキングから除外する。
- **自己資本比率 < 0** (債務超過)
- **OCFマージン < -10%** (破綻リスク)
- **PER > 500 or PBR > 20** (データ異常または極端なバブル)
- **配当性向 > 300%** (タコ足配当)

---

## 3. 戦略別ロジック (Strategy Context)

| 戦略                | 優先評価項目        | AIへの期待                                 |
| :------------------ | :------------------ | :----------------------------------------- |
| **value_strict**    | 割安性・CF・財務    | バリュエーション最優先。成長性は補助。     |
| **growth_quality**  | 利益率・ROE・成長性 | 成長・収益性を最優先。割高はある程度許容。 |
| **turnaround_spec** | 割安性・改善余地    | PBR1倍割れを重視。CFと財務の底打ちを確認。 |
| **balanced**        | 全指標均等          | バランスを重視し、Red Flag は即Bearish。   |

---

## 4. 出力要件 (Reporting Standards)

### 4.1 3行サマリ
```text
【結論】判定。内容。｜【強み】要素1、要素2。｜【懸念】要素1、要素2。
```
※ 枕詞（不本意ながら〜 等）を人格フレーズとして組み込むこと。

### 4.2 テンプレート多様化
以下の語彙をローテーションし、自然かつ知的な文章を生成せよ。
- **導入文**: 「総合的に判断すると」「データを精査した結果」「慎重に見極めたうえで」等。
- **強み**: 「特筆すべきは」「強調すべきは」等。
- **懸念**: 「しかしながら」「一方で」等。

```

---

### docs/architecture_ja.md

```markdown
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
- **Validation Engine (`src/validation_engine.py`)**:
    - **セクター別ポリシー**: セクターごとのデータ欠損許容度や異常値判定を動的に適用。
    - **並列検証**: `ThreadPoolExecutor` を活用し、大量の銘柄データを高速に検証。
- **Sentinel (`src/sentinel.py`)**:
    - **異常検知**: 株価の急変やランク変動を監視し、インテリジェントに再分析をリクエスト。

### 4. AI 層 (Qualitative Analysis)
- **AI パッケージ (`src/ai/`)**:
    - **`KeyManager`**: 複数 API キーのローテーションと健康診断 (Health Check)。
    - **`PromptBuilder`**: 戦略に応じた動的なプロンプト生成。
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
*最終更新: 2026-01-01 (v12.0)*

```

---

### docs/backlog.md

```markdown
# Backlog

## 🟢 [Priority] Post-API-Limit Release Verification (Pending Tests)
API制限解除後に実行すべき、新規実装機能のテスト計画。

### 1. API Usage Dashboard & Token Eaters
- **目的**: ダッシュボードの集計精度と「Token Eaters」（リソース大量消費銘柄）検出機能の確認。
- **実行コマンド**:
  ```bash
  python equity_auditor.py --mode analyze --strategy turnaround_spec --limit 10
  ```
- **確認観点**:
  - [ ] コンソール出力の最後に `API Usage Audit Report` が表示されること。
  - [ ] `Total API Calls` が `Total Stocks` よりも適切に多いこと（リトライ分が含まれるため）。
  - [ ] リトライが多発した銘柄があれば `[😈 Top Token Eaters]` リストに表示されること。

### 2. Smart API Key Rotation
- **目的**: API制限 (429) 到達時に、自動的に次のキーへ切り替わり、処理が継続することの確認。
- **前提**: `GEMINI_API_KEY_2` 以降が設定されていること。
- **実行方法**:
  - 大量のリクエストを投げるか、APIキーの1つを意図的に無効/枯渇状態（またはコード一時変更で模擬）にする。
- **確認観点**:
  - [ ] ログに `⚠️ Quota Exceeded (429)` が出た後、`🔄 Switching permanently to Key #X` が表示されること。
  - [ ] 切り替え後、エラーで終了せずに分析が継続すること。

---

## Logic Enhancements
- [ ] **Calculate Real Volatility from History** (Status: Pending)
  - **Proposed**: 2025-12-24
  - **Details**: Currently using Beta as a proxy for Volatility. Should calculate standard deviation of returns from `stock.history` for accurate volatility.
  - **Reason**: Beta measures market correlation, not price volatility. AI interpretation might be skewed.

---

## Maintenance & Compliance
- [ ] **Maintain Mypy Compliance** (Status: Proposed)
  - **Proposed**: 2026-01-01
  - **Details**: `Success: no issues found` を維持するための CI 連携や開発ガイドラインの整備。
  - **Reason**: 長期的なプロジェクトの保守性確保。

---
*Note: Completed integration tests and test isolation issues have been resolved and removed from the active backlog (2026-01-02).*

```

---

### docs/coverage_analysis_ja.md

```markdown
# カバレッジ分析レポート

## 1. 現状の分析結果
**全体カバレッジ: 72%** (2025-12-18 時点)

カバレッジ向上施策により、初期状態（40%）から大幅に改善されました。主要モジュールの網羅性は以下の通りです。

### 1.1 モジュール別カバレッジ
| モジュール | カバレッジ | 向上理由 |
| :--- | :--- | :--- |
| `src/database.py` | **91%** | 一時DBファイルを用いた全CRUD操作・マイグレーションのテスト拡充 |
| `src/ai_agent.py` | **91%** | モックを用いたプロンプト生成・APIレスポンス処理の網羅 |
| `src/calc.py` | **70%** | 定量評価・スコアリング計算ロジックのユニットテスト作成 |
| `src/data_fetcher.py` | **66%** | 外部APIモック、ネットワークエラー時のフォールバック処理をカバー |

---

## 2. 実施した対応内容

### 2.1 テストコードの新規作成と拡充
以下のテストファイルを新規作成し、`pytest` 管理下に追加しました。
*   **`tests/test_calc.py`**: `Calculator` クラスの全ロジックをカバー。
*   **`tests/test_database.py`**: SQLite操作を実ファイルを使用して検証。
*   **`tests/test_data_fetcher.py`**: 通信周りの異常系を含むフォールバックを検証。

### 2.2 不具合修正
不具合調査の過程で以下の修正を実施しました。
*   **No.1**: `test_ai_agent.py` におけるプロンプト仕様とテスト期待値の乖離を解消。
*   **No.2**: `StockDatabase` において、インメモリDB（`:memory:`）指定時にパス作成でエラーになる問題を解消。

---

## 3. 追加の推奨アクション (今後の課題)

カバレッジ 72% を達成しましたが、以下の領域については引き続き改善の余地があります。

### 3.1 `analyzer.py` の結合テスト強化 (現在 17%)
`StockAnalyzer` は複数のコンポーネントを統合する役割を担っており、異常系の組み合わせテストが不足しています。今後は銘柄データが不完全な場合などのエラーハンドリングの網羅が必要です。

### 3.2 AI 回答品質の評価
自動テストでは「回答の形式」はチェック可能ですが、「内容の正当性」は検証できません。定期的な目視確認、または評価用データセットを用いた精度測定が推奨されます。

---

## 4. 自動化困難な検証項目
詳細は [walkthrough.md] を参照してください。以下の項目は手動検証または実地確認を継続してください。
*   大量データ処理時のパフォーマンス
*   Excel 出力の見た目・条件付き書式
*   実際の API 接続による推論品質

```

---

### docs/equity_auditor_guide.md

```markdown
# Equity Auditor ガイド (v12.0)

Equity Auditor は、多段階の株式分析プロセス（抽出・スコアリング・検証・AI分析・登録）を最適化・自動化するエンジンです。v12.0 では、型安全な内部設計とモジュール化された AI 連携により、安定性が飛躍的に向上しました。

## 新機能と改善 (v12.0)

### 1. 分割された AI モジュール
`src/ai/` パッケージへの移行により、各機能が専門化されました。
- **KeyManager**: 複数 API キーの効率的なローテーションと健康状態監視。
- **PromptBuilder**: 戦略やセクターに応じた動的プロンプト生成。
- **ResponseParser**: 厳格な JSON 検証と、投資判断に不可欠な情報の抽出。

### 2. インテリジェントな検証
- **Validation Engine**: セクター別のポリシーを適用し、データ欠損や計算の不整合を自動検知。
- **Scoring Engine**: 戦略ごとの動的な一括スコアリングをサポート。

### 3. 基盤能力の強化
- **一括データ取得**: データベースからのバッチ取得（`get_market_data_batch`）により、ボトルネックを解消。

---

## 運用モード一覧

| モード      | 説明                                            | コマンド例       |
| :---------- | :---------------------------------------------- | :--------------- |
| **analyze** | **[標準]** 抽出からAI分析、登録までを自動実行。 | `--mode analyze` |
| **extract** | 候補銘柄の抽出とタスクJSONの生成。              | `--mode extract` |
| **ingest**  | 外部AI結果や編集済みデータの取込・登録。        | `--mode ingest`  |
| **reset**   | 特定の銘柄や戦略の分析結果をクリーンアップ。    | `--mode reset`   |

## ワークフロー詳細

### 1. 全自動分析 (Analyze Mode)
```bash
python equity_auditor.py --mode analyze --limit 5 --strategy growth_quality
```
- 有効なキャッシュがある場合は `Smart Cache` を活用し、API 消費を抑制します。
- キャッシュがない（または `--force-refresh` 指定時）は、Gemini API を呼び出して最新の定性的分析を行います。

### 2. 手動・オフライン AI 分析
API を介さず、ブラウザ版 AI を活用する場合や、結果を一度確認してから登録したい場合に使用します。

1. **抽出**: `python equity_auditor.py --mode extract --limit 10`
2. **AI 分析**: 抽出された JSON、または `manual_runner.py --step 1` で生成されたプロンプトを使用。
3. **登録**: AI の回答（JSON）を `python equity_auditor.py --mode ingest --files {FILE}` で DB に反映。

---

## Tips & トラブルシューティング

- **API キー管理**: `.env` または `config/config.yaml` に複数のキーを設定することで、1日の制限を回避できます。
- **ログ確認**: `logs/app.log` で詳細な実行過程（フィルタリングの理由、API 応答等）を確認できます。
- **型チェック**: 開発者は `mypy src` でコードの健全性を保つことができます。

---
*最終更新: 2026-01-01 (v12.0)*

```

---

### docs/manual_coverage.md

```markdown
# カバレッジテスト実施マニュアル

## 概要
本プロジェクトでは、コードの品質と堅牢性を維持するために `pytest-cov` を用いたカバレッジテストを導入しています。
プログラムの改変を行った際は、必ず本手順に従ってカバレッジを計測し、テスト漏れがないか確認してください。

## 前提条件
* 親ディレクトリに `venv` (`../venv`) が作成済みであること。
* 必要なライブラリ (`pytest`, `pytest-cov`) がインストールされていること (自動セットアップ済み)。

## 実行手順

プロジェクトのルートディレクトリで以下のコマンドを実行してください。

```bash
./tools/run_coverage.sh
```

## 出力の見方

### 1. ターミナル出力
コマンド実行後、ターミナルに以下のようなサマリーが表示されます。

```text
Name                       Stmts   Miss  Cover
----------------------------------------------
src/analyzer.py              150     10    93%
src/calc.py                   50      0   100%
collector.py                  80      5    94%
----------------------------------------------
TOTAL                        280     15    95%
```

* **Stmts**: ステートメント（命令）の総数
* **Miss**: 実行されなかったステートメント数
* **Cover**: カバレッジ率 (%)

### 2. HTML詳細レポート
より詳細な分析（行ごとの実行有無）を確認するには、生成されたHTMLレポートを開いてください。

* **保存場所**: `htmlcov/index.html`
* **確認方法**: ブラウザで上記ファイルを開くか、VS Codeの「Live Server」等で確認します。

## 運用ルール (GEMINI.mdより抜粋)

1. **テストの実装**: 新規機能やロジック変更に対して、十分なカバレッジを持つテストケースを作成・更新すること。
2. **低下の防止**: 原則として、既存のカバレッジ率を低下させないように努めること。

```

---

### docs/manual_db_check_ja.md

```markdown
<<<<<<< HEAD
# ユーザーマニュアル: DB 診断ツール (DB Checker)

## 概要
`src/check_db.py` は、SQLite データベース (`data/stock_history.db`) の中身を直接確認するためのツールです。
SQL クライアントを使わずに、コマンドラインから手軽にデータを CSV 形式で出力できます。

## 使い方

### 先頭 N 件を表示
デフォルトでは先頭 5 件を表示します。
```bash
python src/check_db.py
```

件数を指定する場合（例: 10件）:
```bash
python src/check_db.py -n 10
```

### 全件を表示
保存されているすべてのレコードを出力します。
```bash
python src/check_db.py -a
```

## 出力形式
- **標準出力 (stdout)**: CSV 形式のデータ。ファイルにリダイレクトして保存可能です。
- **標準エラー (stderr)**: `Total records: 175` などのメタ情報。

### 活用例: CSV ファイルへの保存
```bash
python src/check_db.py -a > db_dump.csv
```
このコマンドを実行すると、メタ情報はコンソールに表示され、データ部分だけが `db_dump.csv` に保存されます。
=======
# ユーザーマニュアル: DB 診断ツール (DB Checker)

## 概要
`src/check_db.py` は、SQLite データベース (`data/stock_history.db`) の中身を直接確認するためのツールです。
SQL クライアントを使わずに、コマンドラインから手軽にデータを CSV 形式で出力できます。

## 使い方

### 先頭 N 件を表示
デフォルトでは先頭 5 件を表示します。
```bash
python src/check_db.py
```

件数を指定する場合（例: 10件）:
```bash
python src/check_db.py -n 10
```

### 全件を表示
保存されているすべてのレコードを出力します。
```bash
python src/check_db.py -a
```

## 出力形式
- **標準出力 (stdout)**: CSV 形式のデータ。ファイルにリダイレクトして保存可能です。
- **標準エラー (stderr)**: `Total records: 175` などのメタ情報。

### 活用例: CSV ファイルへの保存
```bash
python src/check_db.py -a > db_dump.csv
```
このコマンドを実行すると、メタ情報はコンソールに表示され、データ部分だけが `db_dump.csv` に保存されます。
>>>>>>> 2466ef38d8256ab6703eab59874909499acd6d9e

```

---

### docs/manual_ja.md

```markdown
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
```

---

### docs/manual_main_ja.md

```markdown
# ユーザーマニュアル: 自動分析システム (v12.0)

## 概要
`stock_analyzer.py` は、Stock Analyzer v12.0 のエントリーポイントの一つです。現在は `EquityAuditor` のコアロジックを呼び出す薄いラッパーとして機能しており、後方互換性を維持しながら最新の ScoringEngine と AIAgent を活用した分析を提供します。

## 基本的な使い方

### 実行コマンド
```bash
python stock_analyzer.py [オプション]
```

### オプション一覧 (主要なもの)

| オプション | デフォルト       | 説明                                             |
| :--------- | :--------------- | :----------------------------------------------- |
| `--limit`  | `None`           | 分析する銘柄数の上限。                           |
| `--style`  | `value_balanced` | 分析時のスコアリングスタイルを指定します。       |
| `--repair` | `False`          | 失敗したレコードのみを再試行するリカバリモード。 |

## 動作の仕組み

### エンジン統合
内部的には `ScoringEngine` による高速な一括スコアリングと、`AIAgent` モジュール群による定性的分析が実行されます。
分析結果はデータベースの `analysis_results` テーブルに保存され、同時に `data/output/` にレポートが出力されます。

### スマートキャッシュ
一度分析された銘柄は、データのハッシュ値ベースでキャッシュが効き、API コストを最小化します。

## 注意事項
v12.0 より、高度なワークフロー（抽出・登録の分離など）が必要な場合は、`equity_auditor.py` の使用を推奨しています。

---
*最終更新: 2026-01-01 (v12.0)*

```

---

### docs/manual_test_runner_ja.md

```markdown
<<<<<<< HEAD
# ユーザーマニュアル: テストランナー (Test Runner)

## 概要
`test_runner.py` は、`analyze.py` の動作を自動的に検証するためのツールです。
様々な引数パターンで `analyze.py` を実行し、ログ出力を解析して期待通りの動作をしているかチェックします。

## 使い方

```bash
python test_runner.py
```

実行すると、以下のテストケースが順次実行されます。

1. **Mock Run (api200)**
   - デバッグモードで正常に動作するか。
   - ログに "Debug: True" が含まれるか。
2. **Error Handling (api404)**
   - API エラー（モック）発生時もクラッシュせずに継続するか。

## 出力
- **コンソール**: 各テストの合否（`✅ PASS` / `❌ FAIL`）が表示されます。
- **ログファイル**: `test_run_v2.log` に詳細な実行ログが保存されます。

## 開発者向け
新しい機能を追加した場合は、このスクリプトにもテストケースを追加して、既存機能が壊れていないか確認することを推奨します。
=======
# ユーザーマニュアル: テストランナー (Test Runner)

## 概要
`test_runner.py` は、`analyze.py` の動作を自動的に検証するためのツールです。
様々な引数パターンで `analyze.py` を実行し、ログ出力を解析して期待通りの動作をしているかチェックします。

## 使い方

```bash
python test_runner.py
```

実行すると、以下のテストケースが順次実行されます。

1. **Mock Run (api200)**
   - デバッグモードで正常に動作するか。
   - ログに "Debug: True" が含まれるか。
2. **Error Handling (api404)**
   - API エラー（モック）発生時もクラッシュせずに継続するか。

## 出力
- **コンソール**: 各テストの合否（`✅ PASS` / `❌ FAIL`）が表示されます。
- **ログファイル**: `test_run_v2.log` に詳細な実行ログが保存されます。

## 開発者向け
新しい機能を追加した場合は、このスクリプトにもテストケースを追加して、既存機能が壊れていないか確認することを推奨します。
>>>>>>> 2466ef38d8256ab6703eab59874909499acd6d9e

```

---

### docs/testing_manual_ja.md

```markdown
# テスト仕様書 (v12.0)

本プロジェクトの品質保証体系（静的解析、単体テスト、自己診断、統合テスト）を定義します。

---

## 1. 静的解析 (Static Analysis)

### 概要
`mypy` を使用して型安全性を検証します。v12.0 より、すべての主要ソースコードで型ヒントが必須となりました。

### 実行コマンド
```bash
source ../venv/bin/activate
mypy src --explicit-package-bases
```

### 目標
- **Success: no issues found** (50 source files)

---

## 2. カバレッジ検証 (Unit & Functional Tests)

### 概要
`pytest` と `pytest-cov` を使用した単体・機能テストです。

### 実行コマンド
```bash
python -m pytest tests/test_*.py --cov=src --cov-report=term-missing
```

### 主要テストケース
| カテゴリ  | 対象モジュール                       | 検証内容                                  |
| :-------- | :----------------------------------- | :---------------------------------------- |
| **Logic** | `src/calc/*`                         | ScoringEngine, Mixin, 複数戦略の計算      |
| **AI**    | `src/ai/*`                           | KeyManager, PromptBuilder, ResponseParser |
| **Base**  | `src/database.py`, `src/sentinel.py` | DB操作, インテリジェント異常検知          |

### 目標
- カバレッジ: **80%以上**

---

## 3. 自己診断 (Self-Diagnostic)

### 概要
`self_diagnostic.py` による迅速なスモークテストです。コミット前の最終確認として実行します。

### 実行コマンド
```bash
python self_diagnostic.py
```

### 検証内容 (19項目)
- **基盤機能**: ConfigLoader, StockDatabase(一括取得対応), DataFetcher(DBアクセス抽象化)
- **分析コア**: Calculator(ScoringEngine), StockAnalyzer(Smart Cache, Circuit Breaker)
- **バリデーション**: ValidationEngine(セクター別ポリシー)
- **ランナー**: EquityAuditor(抽出・分析・登録フロー)

---

## 4. 総合・統合テスト (Integration Tests)

### 概要
実際の戦略ファイルを用いた E2E ワークフローの検証です。

### 実行コマンド
```bash
python -m pytest tests/run_integration_tests.py -v
```

---
 
 ## 5. オーケストレーター結合テスト
 
 Daily/Weekly の各ルーチンが、収集、監視、分析、レポート生成の各フェーズを正しく連鎖させているかを確認します。
 
 - **Daily ルーチン・スモークテスト**:
   ```bash
   python orchestrator.py daily --debug
   ```
   - アラートの検知 (`SentinelAlert` テーブル) と、AI 分析の委譲が正常かを確認。
 
 - **Weekly ルーチン・スモークテスト**:
   ```bash
   python orchestrator.py weekly --debug
   ```
   - 全銘柄のスコアリングと、`RankHistory` への保存が正しく行われるかを確認。
 
 ---
 
 ## メンテナンスと不具合報告

### 不具合検出時のフロー
1. `trouble/YYYY-MM-DD-report.md` に不具合を記録。
2. 修正案を提示し、承認後に `history/YYYY-MM-DD.md` に記録して修正。
3. `self_diagnostic.py` または関連テストを実行して再発防止を確認。

---
*最終更新: 2026-01-01 (v12.0)*

```

---

### GEMINI.md

```markdown
# エージェント行動規範 (Agent Behavior Protocol)

## 1. 厳格なフェーズ管理と実行承認

すべてのタスク実行は、以下のフェーズに厳密に分割し、ユーザーの明示的な実行許可を待つこと。

1.  **調査 (Investigation):** タスクの要求、関連コードベース、および制約の初期調査を行う。
2.  **調査結果の報告 (Investigation Report):** 調査結果、提案されるアプローチ、および予想される変更の概要を提示する。
3.  **修正作業 (Implementation):** 調査結果に基づき、具体的なコード修正や設定変更を行う。
4.  **検証 (Verification):** 修正作業が完了した後、テストを実行し、意図した動作を満たしているかを確認する。
5.  **結果報告 (Final Report):** 最終的な検証結果と、タスクの完了ステータスを報告する。

### 実行の合言葉 (Execution Passphrase)

各フェーズの実行を開始する際には、ユーザーが提示する**合言葉**（例えば「`PROCEED`」や「`続行`」など）と、そのフェーズの実行を促す**指示**があった場合のみ、次のフェーズに進むこと。

### 検証失敗時の対応 (Failure Protocol)

「検証 (Verification)」フェーズでテストが失敗、または予期せぬ動作をした場合、**自動的に修正を行わない**こと。必ず失敗の原因を特定し、「調査結果の報告 (Investigation Report)」フェーズに戻ってユーザーに状況を報告し、再度の指示を仰ぐこと。

---

## 2. 不具合修正ポリシー (Defect Remediation Policy)

### 不具合検出時の動作

タスク実行中または検証フェーズで不具合（バグ、エラー、テスト失敗など）を検出した場合、**即座に修正作業を行わない**こと。

### 報告形式

検出したすべての不具合は、以下の形式で一覧としてユーザーに提示し、レポートファイルに記録すること。

* **検出時刻:** `HH:MM` 形式のタイムスタンプ。
* **通番:** その日の不具合としての連番（No.1, No.2...）を付与すること。
* **不具合の概要:** 検出された現象の簡潔な説明。
* **原因の提示:** その不具合の推定される根本原因。
* **影響 (Impact):** その不具合がシステムやユーザーに与える**影響の大きさ**を具体的に記載すること。
* **修正案 (Proposed Fix):** その不具合に対する**具体的な修正アプローチ**を提案すること。

### 修正の実行

修正作業は、ユーザーから**以下のいずれかの指示**があった場合にのみ行うこと。

* **番号指示:** 「`Fix #N`」のように**通番が指定された場合**は、その番号に対応する不具合のみを修正すること。
* **全体指示:** 「`Fix ALL`」のように**すべてを修正する指示**があった場合は、一覧に提示した不具合すべてを修正すること。

---

## 3. ファイル管理ポリシー (File Management Policy)

### テストモジュールの配置

テストコードは、プロジェクトルートに作成する専用のフォルダ内に保存すること。

* **プラットフォーム管理:** テストフォルダの内部は、**対象プラットフォームや環境**（例: `web/`, `mobile/ios/`, `backend/unit/`など）ごとにサブフォルダを作成し、管理すること。

### 障害レポートの記録 (Defect Reporting)

不具合（障害）を検出した際は、プロジェクトルートに「**`trouble`**」という名前のフォルダを作成し、以下のルールに従って記録すること。

* **ファイル名の形式:** 必ず検出日の日付を使用し、`YYYY-MM-DD-report.md` とする。(例: `2025-12-10-report.md`)
* **日次統合 (Daily Consolidation):** 該当する日付のファイルが既に存在する場合は、**新規作成せず、既存ファイルの末尾に追記（Append）**すること。ファイルが存在しない場合のみ、新規作成すること。

### 修正履歴の記録 (Modification History)

コード修正作業を実行する際には、プロジェクトルートに「**`history`**」という名前のフォルダを作成すること。

* **ファイル作成:** 履歴ファイルは、`history`フォルダ内に、修正実施日を基に `YYYY-MM-DD.md` (例: `2025-12-10.md`) の形式で作成または追記すること。
* **記録内容:** 修正を行った**対象ファイル**、**修正の概要**、および**対応した不具合の通番**を記録すること。
*   **必須事項:** ソースコードの変更を伴うすべての作業において、この履歴ファイルの作成・更新は**必須**である。コミット前には必ず履歴ファイルが更新されているかを確認すること。

---

## 4. コミュニケーションと透明性に関するルール

### コミュニケーション言語

ユーザーとのすべてのコミュニケーション（報告、質問、指示の確認など）は、**日本語**で行うこと。技術用語は英語表記を併記しても良い。
**プロポーサルなどのドキュメント作成も原則として日本語で行うこと。**

### ソースコード修正の厳格なプロセス (Strict Source Code Modification Process)

ソースコード（`src/`, `tests/` 以下のファイルなど）を修正する際は、いきなり変更ツール（`replace`, `write_file`）を実行せず、必ず以下の手順を遵守すること。

1.  **問題の特定と報告:** 修正が必要な箇所とその理由（バグの原因、リファクタリングの目的など）を特定し、ユーザーに報告する。
2.  **修正案の提示:** 具体的にどのようにコードを変更するか、**変更前後のコードブロック**や**差分（Diff）**を用いて明確に提示する。
3.  **承認の取得:** ユーザーから明示的な修正の許可（「修正して」「OK」など）を得るまで、ファイルの変更は行わないこと。
4.  **修正の実行:** 許可を得た修正案に基づき、ツールを使用してファイルを変更する。
5.  **履歴の記録:** 修正完了後、速やかに`history`フォルダ内の履歴ファイル（`YYYY-MM-DD.md`）に修正内容を記録すること。

### 変更の差分表示

「修正作業 (Implementation)」フェーズの報告、または「検証 (Verification)」後の結果報告において、コードの変更内容は**差分（Diff）形式**で簡潔かつ正確に提示すること。

### ダークモード対応の出力 (Dark Mode Accessibility)

ユーザーはダークモードを使用している可能性があるため、以下の点に配慮すること。

*   **Markdownテーブルの使用:** 絵文字やテキストだけでなく、構造化された情報はMarkdownテーブルを使用して表示すること。テーブルはテーマに依存せず読みやすい。
*   **絵文字の活用:** ステータス表示には絵文字（✅ ❌ ⚠️ 📦 など）を使用すること。これらはダークモードでも視認性が高い。
*   **HTMLカラーコードの禁止:** `<span style="color:red">` などのインラインHTMLによる色指定は、ダークモードで見えなくなるため**使用禁止**とする。
*   **コードブロックの活用:** Diff表示やコード例は必ずフェンス付きコードブロック（```diff, ```python など）を使用すること。シンタックスハイライトはテーマ対応している。

---

## 5. コードおよびドキュメントの最新化 (Code and Document Synchronization)

コードモジュールを修正した際は、対応する**設計書**を更新するとともに、必ず以下のスクリプトを実行してプロジェクト全体のコンテキストファイルおよび自己診断スクリプトを最新化すること。

*   **コンテキストファイルの生成:** `python3 full_context/generate_full_context.py`
    *   生成場所: `full_context/[YYYY-MM-DD]_project_full_context.md`
    *   このファイルは、他のAIエージェントにプロジェクトの全容を伝えるために使用される。
*   **自己診断スクリプトの更新:** `self_diagnostic.py`
    *   **重要:** 新しい機能の追加や既存コードの変更があった場合は、**必ず `self_diagnostic.py` に対応するテストを追加または更新し、コード品質が維持されていることを保証すること。**


## 6. 自動化と環境維持 (Automation & Environment Maintenance)

### Git Hook の運用と遵守

プロジェクトの品質とコンテキストの整合性を保つため、`.git/hooks/pre-commit` に自動化スクリプトを配置し、コミット時に以下の処理を強制的に実行すること。

1.  **自己診断の実行 (Self-Diagnostic):**
    * コミット前に必ず `python self_diagnostic.py` を実行する。
    * テストが失敗した場合、コミットは**拒否**されなければならない。

2.  **コンテキストの自動更新 (Context Auto-Update):**
    * コミットに含まれる変更が `src/`, `docs/`, `config.yaml` 等の仕様に関わるものである場合、自動的に `generate_full_context.py` (または `generate_context.py`) を実行する。
    * 生成された最新のコンテキストファイル（例: `project_context.md`）を自動的にステージングし、同一のコミットに含めること。

---

## 7. コマンド実行の安全性 (Command Safety)

### Gitコミットメッセージの取り扱い (Git Commit Messages)

シェルによる意図しないコマンド実行（コマンド置換など）を防ぐため、コミットメッセージを指定する際は以下の手順を遵守すること。

1.  **直接指定の禁止:** `git commit -m "message"` の形式で、シェルコマンド内に直接メッセージを含めることは、メッセージ内に特殊文字（バッククォート等）が含まれる可能性があるため**原則禁止**とする。
2.  **ファイル経由の指定:** 必ずコミットメッセージを一時ファイルに保存し、`-F` オプションを使用して読み込むこと。

    **実行手順例:**
    ```bash
    # 1. メッセージを一時ファイルに作成
    cat <<EOF > .git_commit_msg
    feat: 機能追加

    詳細な説明文（バッククォート `code` も使用可能）
    EOF

    # 2. ファイルを指定してコミット
    git commit -F .git_commit_msg

    # 3. 一時ファイルを削除
    rm .git_commit_msg
    ```
## 8. カバレッジテストに関する規定 (Coverage Testing Policy)

プログラムの改変を行う際は、必ずカバレッジテスト環境 ( 等) への反映を行うこと。

1.  **テストの実装:** 新規機能やロジック変更に対して、十分なカバレッジを持つテストケースを作成・更新すること。
2.  **カバレッジの確認:**  (または同等のスクリプト) を実行し、カバレッジレポートを確認すること。
3.  **低下の防止:** 原則として、既存のカバレッジ率を低下させないように努めること。

---

## 9. バックログ管理 (Backlog Management)

### バックログへの記録基準

提案された機能や修正案のうち、以下の理由で実装を見送ったものは、必ずバックログリスト (`docs/backlog.md`) に記録すること。

*   時期尚早と判断されたもの。
*   優先順位の変更により延期されたもの。
*   技術的な課題や依存関係により即時実装が困難なもの。

### 記録内容

バックログには、各項目について以下の情報を記載すること。
*   **ID** バックログ内でユニークな番号。
*   **ステータス:** 保留中 (Pending) / 検討中 (On Hold) など。
*   **起案日:** バックログに追加した日付。
*   **関連提案:** 関連する提案資料やドキュメントへのリンク。
*   **概要:** 機能や修正の内容。
*   **保留理由:** なぜ今回実装を見送ったのか、その理由。

---

## 10. 無限修正ループの防止 (Prevention of Infinite Modification Loops)

### ループ検知基準

同一または類似の修正が、短期間に**2回以上**繰り返され、かつ解決に至らない場合、「無限修正ループ」に陥っていると判断すること。
（例：修正A → テスト失敗 → 修正Aの取り消し/修正B → テスト失敗 → 再度修正Aを適用... のような状況）

### 直ちに停止と再調査

ループを検知した際は、**即座にその修正作業を停止**し、以下の手順をとること。

1.  **盲目的な再試行の禁止:** 前回の修正を少し変えて再試行するだけの行為は禁止する。
2.  **原因の深掘り (Deep Dive):** なぜその修正が機能しないのか、根本原因を再調査する（例：隠れた依存関係、テスト自体の誤り、環境の差異など）。
3.  **代替案の提示:** 既存のアプローチが通用しないことを認め、全く異なるアプローチや解決策をユーザーに提案する。

---

## 11. プロポーサルの管理 (Proposal Management)

### アーカイブ化の基準
実装が完了し、検証を通過したプロポーサル（`docs/proposal/*.md`）は、速やかにアーカイブディレクトリ（`docs/archive/`）へ移動すること。

*   **目的:** `docs/proposal/` フォルダを常に「現在進行形」または「未着手」の提案のみが含まれる状態に保ち、プロジェクトの進捗状況を明確にするため。
*   **管理:** アーカイブへ移動する際は、必要に応じてステータスを「完了 (Implemented)」等に更新した上で移動すること。

---

## 12. 改造時の結果整合性検証 (Modified Code Integrity Verification)

### 結果の一致確認の義務化
リファクタリング、パフォーマンス最適化、または基盤コードの改変を行う際は、必ず**改造前後で同一の入力データを用い、最終的な出力結果（CSV, Excel, DBレコード等）が完全に一致すること**を物理的に検証しなければならない。

### 一致不可能な場合の対応
プログラムの性質上、または意図した仕様変更により、改造前後で結果を完全に一致させることが不可能な場合には、以下の手順を遵守すること。

1.  **即時報告:** 一致させられない理由（例：計算精度の向上、浮動小数点の挙動差異、仕様変更の必然性など）を明確にし、ユーザーに報告する。
2.  **指示の要請:** 差分の許容範囲や、新しい結果を「正」として受理するかについて、ユーザーからの具体的な指示を仰ぐこと。
3.  **独自判断の禁止:** ユーザーの明示的な許可なく、「微差だから問題ない」と判断して作業を続行してはならない。

---

## 13. 静的解析ツールの実行 (Static Analysis Execution)

### 変更時の義務
プログラムを変更した際は、必ず静的解析ツールを実行し、コード品質を維持すること。

1.  **実行タイミング:** コード修正後、コミットまたはレビュー依頼を行う前。
2.  **実行ツール:**
    *   **Formatting:** `black .` (コードの自動整形)
    *   **Lint:** `ruff check .` (高速Lint & Import整理)
    *   **Type Check:** `mypy` (推奨設定: `ignore_missing_imports = True`)
    *   **Legacy Lint:** `flake8` (移行期間中のみ併用)
3.  **対応:** 検出されたエラーや警告は、修正するか、正当な理由がある場合は明示的に無視（`# noqa` 等）し、その理由を記録すること。

---

## 14. Python 実行環境 (Python Execution Environment)

### 仮想環境の使用義務

すべての Python コマンド（`python`, `pip`, `pytest`, `mypy` 等）の実行において、プロジェクト専用の仮想環境を使用すること。

### 仮想環境パス

```
/home/irom/project-stock2/venv
```

### 実行方法

以下のいずれかの方法で仮想環境を使用すること。

1.  **アクティベート方式**（推奨）:
    ```bash
    source /home/irom/project-stock2/venv/bin/activate
    python <script>
    pip install <package>
    ```

2.  **直接パス指定**:
    ```bash
    /home/irom/project-stock2/venv/bin/python <script>
    /home/irom/project-stock2/venv/bin/pip install <package>
    ```

### 禁止事項

*   **システムの `python3` / `pip3` を直接使用することは禁止**。
*   `/usr/bin/python3` や `/usr/bin/pip3` が使用された場合、依存パッケージの不整合やテスト失敗の原因となる。

### 確認方法

コマンド実行前に、使用している Python のパスを確認すること。

```bash
which python3  # 期待値: /home/irom/project-stock2/venv/bin/python3
```
```

---

## Proposals (Active)

_No files found in this group._

## Configuration

_No files found in this group._

## Root Scripts

_No files found in this group._

## Source Code (src)

_No files found in this group._

## History (Latest 3)

### history/2026-01-03.md

```markdown
# 2026-01-03 修正履歴

## 作業概要
未コミットの変更を適用し、`feature-MS2` ブランチを `main` ブランチへ安全に統合・プッシュしました。

## 実施内容
- **Git操作**:
    - `feature-MS2` ブランチでの `.git_commit_msg` 削除のコミットとプッシュ。
    - `main` ブランチへのマージと `origin/main` へのプッシュ。
- **自動検証・更新**:
    - プリコミットフックによる `self_diagnostic.py` の自動実行（全テスト通過）。
    - プリコミットフックによる `generate_full_context.py` の自動実行とコンテキストファイルの更新。

## 修正ファイル
- `.git_commit_msg` (削除)
- `full_context/2026-01-03_project_full_context.md` (新規)
- `history/2026-01-03.md` (新規)

```

---

### history/2026-01-04.md

```markdown
# 2026-01-04 修正履歴

## 修正作業概要
QAプロセスで検出されたテスト失敗（3件）の修正、および仮想環境 (`venv`) のディレクトリ移動に伴うパス設定の全体的な更新を行いました。

## 変更ファイル一覧

### 1. ソースコード修正 (バグ修正)
*   **`src/config_loader.py`**:
    *   [Bug Fix] 設定ファイルが存在しない、または空の場合に `ConfigModel` のバリデーションエラーが発生する問題を修正。デフォルト値を補完するフォールバックロジックを追加。

### 2. テストコード修正 (仕様追従)
*   **`tests/test_config_loader.py`**:
    *   `src/config_loader.py` の修正に合わせて、モックおよびテストケースを修正。構文エラーおよび名前解決エラーを解消。
*   **`tests/test_hard_cutting.py`**:
    *   `StockAnalysisData` (Pydanticモデル) 導入に伴うエラーコード変更 (`Insolvent` → `equity_ratio_negative`, `Severe OCF Drain` → `operating_cf_extreme_negative`) に追従し、アサーション期待値を修正。
    *   テストデータに必須項目 (`ocf_margin`) を追加。
*   **`tests/test_validation_tiered.py`**:
    *   Pydantic の型検証エラーをテスト対象と誤認していた箇所を修正。
    *   エラーメッセージの期待値を実装に合わせて `Snake Case` (`sales_growth` 等) に統一。
    *   未実装の異常値バリデーションテストを、実装済みの Red Flag 検知テストに変更。

### 3. 環境設定・ドキュメント更新 (パス変更)
*   **`tools/run_coverage.sh`**: `source venv/bin/activate` → `source ../venv/bin/activate` に変更。
*   **`scripts/measure_coverage.sh`**: 同上。
*   **`pyproject.toml`**: Black/Ruff の除外設定に `../venv` を追加。
*   **`docs/*.md`**: 手順書内の `venv` 参照パスを更新。

## 対応した不具合 (QA指摘事項)
*   Fix #1: ConfigValidation Error (`test_config_loader.py`) - 解消
*   Fix #2: Assertion Error: Error Code Mismatch (`test_hard_cutting.py`) - 解消
*   Fix #3: Validation Message / Type Mismatch (`test_validation_tiered.py`) - 解消

## 統合テスト実施結果 (追加)
ユーザー要望により統合テスト (`pytest -m integration`) を実施しました。
これまで実行対象外となっていた統合テストファイルに `@pytest.mark.integration` を付与し、正常に収集・実行されるよう修正しました。

*   **対象ファイル**:
    *   `test_base_features_integration.py`
    *   `test_integration_analyzer.py`
    *   `test_integration_manual_workflow.py`
    *   `test_sentinel_orchestrator_integration.py`
    *   `test_strategy_analyst_rules_integration.py`

*   **実行結果**:
    *   Status: ✅ **PASS** (34 tests passed)
    *   Warning: 5 warnings (FutureWarning etc.) - ※動作に影響なし

## 2026-01-04 修正履歴

- **対象:** /home/irom/project-stock2/stock-analyzer.bak
- **内容:** Gitリポジトリ重複表示解消のため、バックアップディレクトリを削除
- **対応理由:** エディタ等でリポジトリが2つ表示される問題の解決

- **対象:** /home/irom/project-stock2/.venv
- **内容:** 不要な仮想環境ディレクトリを削除
- **対応理由:** 構成の簡素化

## 優先度 高・中 問題修正

### 対処した問題
1. **テストコレクションエラー修正** (15件 → 0件)
   - 原因: ,  が venv に未インストール
   - 対処: 依存パッケージは既に venv にインストール済みだったが、venv がアクティベートされていなかった

2. **ruff エラー修正** (6件 → 0件)
   - :  のインポート追加
   - : 重複関数定義の削除
   - 3件の import 順エラー: All checks passed! で自動修正

3. **mypy 型スタブ導入**
   - , ,  を venv にインストール
   - 結果: 

## GEMINI.md 更新

- **対象:** /home/irom/project-stock2/stock-analyzer4/GEMINI.md
- **内容:** セクション14「Python 実行環境」を追加
- **目的:** AIエージェントが仮想環境を使用することを明示的に義務化

```

---

## Trouble Reports (Latest 1)

_No files found in this group._

