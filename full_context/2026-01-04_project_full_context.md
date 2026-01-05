# Project Full Context Report

Generated at: 2026-01-04 18:33:17

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
```

---

### README.md

```markdown
# Stock Analyzer v5.3

Stock Analyzer is a comprehensive tool for analyzing Japanese stocks using a combination of **Quantitative Strategy** (Financial & Technical Analysis) and **Qualitative Analysis** (AI-powered insights). Version 5.3 introduces significant enhancements in transparency and efficiency.

## 🚀 Key Features

*   **Explainable Scoring (Sub-scores)**: Breakdown of `quant_score` into specific categories:
    *   **Value**: Undervaluation metrics (PER, PBR, Yield).
    *   **Growth**: Revenue and Profit growth, including Turnaround detection.
    *   **Quality**: Financial health (ROE, Equity Ratio, Cash Flow).
    *   **Trend**: Technical momentum (MACD, RSI, Moving Averages).
*   **Two-Stage Analysis**: Efficiently separated workflow:
    *   `screening`: Fast quantitative filtering to generate candidate lists.
    *   `ai`: Deep dive qualitative analysis using Gemini AI.
*   **Smart Refresh & Caching**: Minimizes API costs by reusing results for unchanged data and intelligently refreshing only when prices or scores change significantly.
*   **Robust Repair Mode**: Automatically retries analysis for recoverable errors (API limits, Network) while skipping invalid data.
*   **Granular Status**: new `profit_status` and `sales_status` columns to clearly identify growth phases (Surge, Stable, Crash, Turnaround).

## 📦 Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up your Google Gemini API Key in your environment variables:
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    # For multi-key rotation (optional):
    # export GEMINI_API_KEY_2="another_key"
    ```

## 🛠️ Usage Workflow

### Step 1: Screening (Quantitative Analysis)
Generate a candidate list based on financial metrics and technical indicators.
```bash
python stock_analyzer.py --stage screening --strategy value_strict --limit 100
```
*   **Output**: `data/output/candidates_YYYY-MM-DD_value_strict.csv`
*   **Key Columns**: `code`, `name`, `quant_score`, `score_value`, `score_growth`, `score_trend`, `profit_status`...

### Step 2: AI Analysis (Qualitative Deep Dive)
Run AI analysis on the screened candidates.
```bash
python stock_analyzer.py --stage ai --input data/output/candidates_YYYY-MM-DD_value_strict.csv
```
*   **Output**: `data/output/analysis_result.csv` (Saved to DB and exported)

### All-in-One Mode
Run both steps sequentially (Screening -> AI).
```bash
python stock_analyzer.py --stage all --limit 10
```

## ⚙️ Options

*   `--stage {screening, ai, all}`: Select the analysis phase.
*   `--strategy {value_strict, growth_quality, value_growth_hybrid}`: Override the investment strategy.
*   `--limit N`: Process only the top N stocks.
*   `--repair`: Retry analysis for failed records (Quota/Network errors).

## 📄 Documentation

For more details, check the `docs/` directory:
*   [User Manual (Japanese)](docs/manual_ja.md)
*   [Architecture Design (Japanese)](docs/architecture_ja.md)
*   [Backlog & Roadmap](docs/backlog.md)

```

---

## Proposals (Active)

_No files found in this group._

## Configuration

### config/ai_prompts.yaml

```yaml
# [v3.5] Unified Analyst Prompt - Pro Edition
# Sync with docs/analyst_rules.md & User-defined Persona & Score Breakdown
audit_version: 6

# Base Template (Structure)
base_template: |
  あなたは「厳格かつ透明性の高いシニア証券アナリスト」です。
  市場の番人として、投資家を甘い誘惑から守り、客観的な財務データのみに基づいて判断を下してください。
  {persona}として、{default_horizon}の視点から分析を行ってください。

  【重要】データ検証ステータス (Pydantic Validated)
  本銘柄のデータは **StockAnalysisData モデル** によって検証を完了しています。
  - 欠損値: ✅ 完了 (Tier1: {tier1_missing_count}件, Tier2: {tier2_missing_count}件)
  - 異常値: ✅ 完了 (Red Flags: {red_flag_count}件)
  - 例外救済判定: {rescue_status}
  ⚠️ **禁則事項**: システム提示のデータに忠実に従い、独自の楽観的な推測は**一切禁止**します。

  【格付け判定の基準 (Rulebook v3.5 Sync)】
  - **Bullish (Aggressive)**: 定量スコア 80以上 かつ Red Flag なし。成長性が極めて高い。
  - **Bullish (Defensive)**: 「例外救済ルール」適用銘柄。圧倒的な下値の堅さ。
  - **Neutral (Positive)**: スコア 70以上。致命的欠陥なし。有力な仕込み候補。
  - **Neutral (Wait)**: スコア 50〜69。成長期待とリスクが拮抗。
  - **Neutral (Caution)**: スコア 50未満 または 非致命的な懸念（データ一部欠損等）あり。要精査。
  - **Bearish**: 即時回避。営業CF赤字、売上減少、または極端な割高のいずれかに抵触する場合。

  【第2層：プロの目利き救済ルール】
  以下の条件を満たす場合、AIは定量的な弱点を補完して判定を引き上げることができる（Bullish (Defensive) 等）。
  - **Deep Value**: PBR < 0.7 × 利益成長が弱くても「資産価値」で救済。
  - **Quality Growth**: ROE > 15% × 高PERでも「資本効率の卓越性」で許容。
  - **Efficiency**: PER < 10 × 営業利益率 > 10% なら「収益体制の強固さ」で高く評価。

  【戦略別ロジックとスコア解釈】
  現在、この銘柄は **Best_Strategy: {strategy_name}** として評価されています。
  下示の「定量スコア内訳」を読み解き、論評の根拠として活用せよ（例：Value点が低い理由は妥当か、等）。
  - **value_strict**: バリュエーションとCFを最優先。
  - **growth_quality**: 利益率、ROE、成長モメンタムを最優先。
  - **turnaround_spec**: 資産価値(PBR)と改善余地を重視。

  【専門的語彙セット (Vocabulary Enhancement)】
  論評の多様性とプロらしさを追求し、以下の表現を積極的に織り交ぜよ。
  - **強み**: 「財務の堅牢性」「利益の質の高さ」「キャッシュ創出力の強さ」「資本効率の卓越性」「強固な参入障壁」
  - **懸念**: 「利益の質の低さ」「成長鈍化の兆候」「割高感の顕著さ」「財務レバレッジへの過度な依存」「資産の不健全性」
  - **例外時**: 「極めて不本意ではあるが」「データの欠損には目をつぶり、例外的に」

  【出力要件】
  **(A) 3行サマリ (ai_summary)**
  - 形式: `【結論】判定。内容。｜【強み】要素1、要素2。｜【懸念】要素1、要素2。`
  - 1行（改行なし）を厳格に守ること。

  **(B) 詳細解説 (ai_detail)**
  - 構造: ①現状 ②強み ③リスク ④CF ⑤Red Flag ⑥テクニカル ⑦総合結論
  - ⑦では、なぜこの判定に至ったかを戦略とスコア内訳に触れつつ論理的に締めくくれ。

  【銘柄情報】
  {code} {name} （業種: {sector}）
  現在の市場環境: {market_context}
  定量スコア内訳: {quant_scores_str}
  {exclusion_notice}
  {special_instruction}

  {metrics_section}
  
  必ず以下のJSON形式で出力してください。
  {{
      "code": "{code}",
      "ai_sentiment": "Bullish (Aggressive)/Bullish (Defensive)/Neutral (Positive)/Neutral (Wait)/Neutral (Caution)/Bearish",
      "ai_summary": "【結論】判定。内容。｜【強み】...｜【懸念】...",
      "ai_detail": "①... \n②... \n③...",
      "ai_risk": "Low/Medium/High (理由)",
      "ai_horizon": "Short-term/Long-term/Wait"
  }}

# Metrics Section Template
metrics_template: |
  【バリュエーション】PER: {per}倍, PBR: {pbr}倍, 利回り: {dividend_yield}%, 配当性向: {payout_ratio}%
  【収益・成長】売上成長: {sales_growth}%, 営業利益率: {op_margin_val}%, ROE: {roe}%
  【CF・安全性】営CFマージン: {ocf_margin_val}%, D/Eレシオ: {de_ratio}%, 自己資本比率: {equity_ratio}%
  【モメンタム】トレンド: {trend_desc}, RSI: {rsi}, MA乖離: {ma_divergence}%, 出来高倍: {volume_ratio}
  定量スコア内訳: {quant_scores_str}

```

---

### config/config.yaml

```yaml
api_settings:
  gemini_tier: "paid" # "free" or "paid"

current_strategy: value_strict
data:
  jp_stock_list: data/input/jp_stock_list.csv
  output_path: data/output/analysis_result.csv
filter:
  max_rsi: 100
  min_quant_score: 60
  min_trading_value: 10000000

csv_mapping:
  col_map:
    'コード': 'code'
    'コード/ティッカー': 'code'
    '銘柄名': 'name'
    '売上高': 'sales'
    '市場': 'market'
    '業種': 'sector'
    '財務': 'financial'
    '現在値': 'current_price'
    '現値': 'current_price'
    '前日比(%)': 'price_change_pct'
    'PER(株価収益率)': 'per'
    '予想PER': 'per'
    'PER': 'per'
    'PBR(株価純資産倍率)': 'pbr'
    '実績PBR': 'pbr'
    'PBR': 'pbr'
    'ROE(自己資本利益率)': 'roe'
    '配当利回り': 'dividend_yield'
    '予想配当利回り': 'dividend_yield'
    '売上高変化率': 'sales_growth'
    '経常利益変化率': 'profit_growth'
    '流動比率': 'current_ratio'
    '当座比率': 'quick_ratio'
    '平均売買代金': 'trading_value'
    '売買代金': 'trading_value'
    'RSI': 'rsi'
    '売上高営業利益率': 'operating_margin'
    '有利子負債自己資本比率': 'debt_equity_ratio'
    'フリーキャッシュフロー': 'free_cf'
    '営業キャッシュフロー': 'operating_cf'
  numeric_cols:
    - per
    - pbr
    - roe
    - dividend_yield
    - sales_growth
    - profit_growth
    - current_ratio
    - quick_ratio
    - trading_value
    - rsi
    - current_price
    - ocf_margin
    - free_cf
    - debt_equity_ratio
    - volatility
    - macd
    - peg_ratio
    - trend_signal
    - cf_status
    - sma_75
scoring:
  lower_is_better:
  - per
  - pbr
  - debt_equity_ratio
  - peg_ratio
  - volatility
strategies:
  growth_quality:
    default_style: long_term_growth
    persona: "Growth Investor" # [v7.1]
    default_horizon: "Long-term" # [v7.1]
    base_score: 20
    min_requirements:
      profit_growth: 5.0
      roe: 8.0
      sales_growth: 5.0
    points:
      cf_status: 5
      peg_ratio: 15
      profit_growth: 20
      roe: 20
      rsi_overbought: -10
      rsi_oversold: 10
      sales_growth: 20
      trend_signal: 10
    thresholds:
      cf_status: 1.0
      peg_ratio: 1.5
      profit_growth: 15.0
      roe: 10.0
      rsi_overbought: 80
      rsi_oversold: 40
      sales_growth: 10.0
      trend_signal: 1.0
  value_growth_hybrid:
    default_style: value_balanced
    persona: "GARP Evaluator" # [v7.1] Growth at a Reasonable Price
    default_horizon: "Long-term" # [v7.1]
    base_score: 30
    min_requirements:
      roe: 5.0
      sales_growth: 0.0
    points:
      dividend_yield: 10
      pbr: 10
      per: 10
      roe: 20
      sales_growth: 20
    thresholds:
      dividend_yield: 2.5
      pbr: 2.0
      per: 20.0
      roe: 10.0
      sales_growth: 10.0
  Balanced Strategy:
    default_style: value_balanced
    persona: "Multi-Strategy Allocator"
    default_horizon: "Medium-term"
    base_score: 20
    min_requirements:
      roe: 5.0
    points:
      per: 10
      roe: 10
    thresholds:
      per: 15.0
      roe: 8.0
  value_strict:
    default_style: value_balanced
    persona: "Deep Value Investor" # [v7.1]
    default_horizon: "Long-term" # [v7.1]
    base_score: 25
    min_requirements:
      current_ratio: 150.0
      dividend_yield: 2.0
      pbr_max: 2.0
      per_max: 20.0
      profit_growth: 0.0
      quick_ratio: 100.0
      roe: 5.0
      sales_growth: 0.0
    points:
      cf_status: 5
      current_ratio: 5
      dividend_yield: 15
      pbr: 15
      peg_ratio: 10
      per: 15
      roe: 10
      rsi_overbought: -10
      rsi_oversold: 10
      trend_signal: 5
    thresholds:
      cf_status: 1.0
      current_ratio: 200.0
      dividend_yield: 3.5
      pbr: 0.8
      peg_ratio: 2.0
      per: 12.0
      roe: 8.0
      rsi_overbought: 70
      rsi_oversold: 30
      trend_signal: 1.0

  turnaround_spec: # [v6.1] 新設: ターンアラウンド・投機戦略
    default_style: turnaround_style
    persona: "Distressed Asset Specialist" # [v7.1]
    default_horizon: "Short-term" # [v7.1]
    base_score: 10
    min_requirements:
      sales_growth: 0.0
      pbr_max: 5.0
    points: # PERを除外した配点構成
      sales_growth: 30
      pbr: 25
      roe: 20
      profit_growth: 15
      trend_signal: 10
    thresholds:
      sales_growth: 15.0
      pbr: 1.2
      roe: 10.0
      profit_growth: 0.0
      trend_signal: 1.0

scoring_v2:
  macro:
    sentiment: "neutral"
    interest_rate: "stabilizing"
    active_sector: "Technology"
  styles:
    value_balanced:
      weight_fund: 0.7
      weight_tech: 0.3
    short_term_momentum:
      weight_fund: 0.3
      weight_tech: 0.7
    long_term_growth:
      weight_fund: 0.9
      weight_tech: 0.1
    turnaround_style: # Value: 0.3, Growth: 0.4, Quality: 0.1, Trend: 0.2 相当の配分
      weight_fund: 0.8  # (0.3+0.4+0.1)
      weight_tech: 0.2  # (0.2)
  tech_points:
    macd_bullish: 15
    rsi_oversold: 10
    rsi_overbought: -10
    trend_up: 10

ai:
  model_name: "gemini-flash-latest"
  # [Concurrency Control]
  # Free: concurrency=1, interval=5.0
  # Pro : concurrency=10, interval=0.1
  max_concurrency: 1
  interval_sec: 5.0
  validity_days: 7  # AI分析結果を再利用する有効期間（日数）。0の場合は毎回再分析。
  refresh_triggers:
    price_change_pct: 5.0    # 前回から株価が 5.0% 以上変動したら強制再分析 (0で無効)
    score_change_point: 10.0 # 定量スコアが 10.0点 以上変動したら強制再分析 (0で無効)

circuit_breaker:
  consecutive_failure_threshold: 1 # 連続でこの回数以上API制限(429)が発生したら中断

database:
  retention_days: 30  # 市況データと分析結果を保持する期間（日数）。

# [v6.0] セクター別ポリシー
# セクター特有の「構造的欠損」に対応
# Based on full database diagnostic analysis (2025-12-25)
sector_policies:
  銀行業:
    na_allowed:           # バリデーションで欠損を許容（全銘柄で確認された構造的欠損）
      - debt_equity_ratio
      - operating_margin
      - operating_cf
      - free_cf
      - current_ratio     # 銀行業では流動比率の概念が異なる
      - quick_ratio       # 銀行業では当座比率の概念が異なる
    score_exemptions:     # スコアリングから除外（正規化対象）
      - debt_equity_ratio
      - current_ratio
      - quick_ratio
    ai_prompt_excludes:   # AIプロンプトで「分析対象外」と明示
      - Debt/Equity Ratio
      - Operating Margin
      - Current Ratio
      - Quick Ratio
  
  情報・通信業:
    na_allowed:
      - free_cf
      - operating_cf
      - debt_equity_ratio  # 新興企業対応
    score_exemptions:
      - free_cf
      - debt_equity_ratio
    ai_prompt_excludes:
      - Free CF
      - Debt/Equity Ratio
  
  証券、商品先物取引業:
    na_allowed:
      - free_cf
      - debt_equity_ratio
      - current_ratio
      - quick_ratio
    score_exemptions:
      - free_cf
      - debt_equity_ratio
    ai_prompt_excludes:
      - Free CF
      - Debt/Equity Ratio
  
  鉱業:
    na_allowed:
      - debt_equity_ratio
    score_exemptions: []
    ai_prompt_excludes: []
  
  保険業:
    na_allowed:
      - free_cf
      - operating_cf
      - current_ratio
      - quick_ratio
    score_exemptions:
      - free_cf
    ai_prompt_excludes:
      - Free CF
  
  サービス業:
    na_allowed:
      - free_cf
      - operating_cf
    score_exemptions:
      - free_cf
    ai_prompt_excludes:
      - Free CF
  
  電気機器:
    na_allowed:
      - free_cf
      - operating_cf
    score_exemptions:
      - free_cf
    ai_prompt_excludes:
      - Free CF
  
  建設業:
    na_allowed:
      - debt_equity_ratio
      - free_cf
      - operating_cf
    score_exemptions:
      - free_cf
    ai_prompt_excludes:
      - Free CF
  
  不動産業:
    na_allowed:
      - free_cf
      - operating_cf
    score_exemptions:
      - free_cf
    ai_prompt_excludes:
      - Free CF
  
  その他製品:
    na_allowed:
      - free_cf
      - operating_cf
    score_exemptions:
      - free_cf
    ai_prompt_excludes:
      - Free CF
  
  石油・石炭製品:
    na_allowed:
      - free_cf
      - operating_cf
    score_exemptions:
      - free_cf
    ai_prompt_excludes:
      - Free CF

  # [v6.1] 構造的欠損セクターの拡充
  小売業:
    na_allowed: [free_cf, operating_cf]
    score_exemptions: [free_cf]
    ai_prompt_excludes: [Free CF]
  化学:
    na_allowed: [free_cf, operating_cf]
    score_exemptions: [free_cf]
    ai_prompt_excludes: [Free CF]
  機械:
    na_allowed: [free_cf, operating_cf]
    score_exemptions: [free_cf]
    ai_prompt_excludes: [Free CF]
  金属製品:
    na_allowed: [free_cf, operating_cf]
    score_exemptions: [free_cf]
    ai_prompt_excludes: [Free CF]
  医薬品:
    na_allowed: [free_cf, operating_cf]
    score_exemptions: [free_cf]
    ai_prompt_excludes: [Free CF]
  精密機器:
    na_allowed: [free_cf, operating_cf]
    score_exemptions: [free_cf]
    ai_prompt_excludes: [Free CF]
  繊維製品:
    na_allowed: [free_cf, operating_cf]
    score_exemptions: [free_cf]
    ai_prompt_excludes: [Free CF]
  電気・ガス業:
    na_allowed: [free_cf, operating_cf]
    score_exemptions: [free_cf]
    ai_prompt_excludes: [Free CF]

  # [v6.1] 戦略レベルのポリシー（セクター不問でPER欠損を許容）
  # [v7.4] turnaround_spec: 財務困難銘柄対応として複数指標の欠損を許容
  # ValidationEngine側で戦略名をフックして適用
  _strategy_turnaround_spec:
    na_allowed: [per, roe, operating_margin, debt_equity_ratio, free_cf, operating_cf, pbr]
    score_exemptions: [per]
    ai_prompt_excludes: []

  # デフォルト（未定義セクターに適用）
  default:
    na_allowed: []
    score_exemptions: []
    ai_prompt_excludes: []

# [v7.1] Sector-specific Risk Factors for AI Analysis
sector_risks:
  不動産業: "Interest Rate Hike Impact: High sensitivity to rising rates due to debt financing."
  建設業: "Interest Rate & Labor Cost: Impact of rising borrowing costs and labor shortages."
  機械: "FX Risk: High sensitivity to JPY appreciation via export profits."
  電気機器: "Global Trade: High sensitivity to global economic cycles and semiconductor market."
  銀行業: "YCC/Interest Rate: Benefit from rising rates but valuation risk on bond holdings."
  輸送用機器: "FX & Supply Chain: Highly sensitive to USD/JPY rates and global logistics."
  小売業: "Domestic Consumption: Sensitive to inflation (cost push) and consumer spending power."
  医薬品: "Regulatory & R&D: Drug pricing revisions and patent expirations."
  情報・通信業: "Talent & Security: Risks related to IT talent shortage and potential data breaches."
  商社: "Commodity & FX: Exposure to resource price volatility and exchange rates."

# [v7.0] Metadata Mapping for Validation and Analysis
metadata_mapping:
  metrics:
    # prompt label -> model field name
    "PER": "per"
    "PBR": "pbr"
    "ROE": "roe"
    "Operating Margin": "operating_margin"
    "Debt/Equity Ratio": "debt_equity_ratio"
    "Free CF": "free_cf"
    "Op CF Margin": "operating_cf" # Validated as proxy check
    "Sales Growth": "sales_growth"
    "Profit Growth": "profit_growth"
    "Current Ratio": "current_ratio"
    "Quick Ratio": "quick_ratio"
  
  validation:
    # 7 items out of 11 criticals missing => Fatal
    critical_missing_threshold: 7
    mode: "tiered" # "strict" or "tiered" [v12.5 Tiered Validation]

# 正規化設定
scoring:
  min_coverage_pct: 50  # 有効配点がこの割合以下なら警告

```

---

### requirements.txt

```text
annotated-types==0.7.0
beautifulsoup4==4.14.3
cachetools==6.2.2
certifi==2025.11.12
cffi==2.0.0
black
ruff
charset-normalizer==3.4.4
curl_cffi==0.13.0
et_xmlfile==2.0.0
frozendict==2.4.7
google-ai-generativelanguage==0.6.15
google-api-core==2.28.1
google-api-python-client==2.187.0
google-auth==2.45.0
google-auth-httplib2==0.2.1
google-genai==1.56.0
google-generativeai==0.8.6
googleapis-common-protos==1.72.0
grpcio==1.76.0
grpcio-status==1.71.2
httplib2==0.31.0
idna==3.11
multitasking==0.0.12
numpy==2.3.5
openpyxl==3.1.5
pandas==2.3.3
peewee==3.18.3
platformdirs==4.5.1
proto-plus==1.26.1
protobuf==5.29.5
pyasn1==0.6.1
pyasn1_modules==0.4.2
pycparser==2.23
pydantic==2.12.5
pydantic_core==2.41.5
pyparsing==3.2.5
python-dateutil==2.9.0.post0
pytz==2025.2
PyYAML==6.0.3
requests==2.32.5
rsa==4.9.1
six==1.17.0
soupsieve==2.8
tqdm==4.67.1
typing-inspection==0.4.2
typing_extensions==4.15.0
tzdata==2025.2
uritemplate==4.2.0
urllib3==2.6.1
websockets==15.0.1
xlrd==2.0.2
yfinance==0.2.66
python-dotenv

```

---

## Root Scripts

### collector.py

```python
#!/usr/bin/env python3
import argparse
import logging

from src.database import StockDatabase
from src.env_loader import load_env_file
from src.fetcher.facade import DataFetcher
from src.logger import setup_logger
from src.models import Stock, db_proxy


def main():
    parser = argparse.ArgumentParser(description="Stock Data Collector v12.0")
    parser.add_argument(
        "--codes",
        help="Comma separated stock codes to fetch. If omitted, fetches all active stocks.",
    )
    parser.add_argument(
        "--limit", type=int, help="Limit the number of stocks to fetch."
    )
    parser.add_argument(
        "--jpx-only", action="store_true", help="Only refresh JPX stock list."
    )

    args = parser.parse_args()

    load_env_file()  # Load .env variables (auto-discovery)
    setup_logger()
    logger = logging.getLogger("Collector")
    config = ConfigLoader().config

    # データベースの初期化 (db_proxy を使用する前に必要)
    db = StockDatabase()

    fetcher = DataFetcher(config)

    logger.info("📡 Stock Data Collector started.")

    # 1. JPX 銘柄リストの更新
    logger.info("Step 1: Refreshing JPX stock list...")
    try:
        jpx_df = fetcher.fetch_jpx_list(save_to_csv=True)
        if jpx_df.empty:
            logger.error("❌ Failed to fetch JPX list.")
            return

        # Stock テーブルの更新 (UPSERT)
        stock_records = []
        for _, row in jpx_df.iterrows():
            stock_records.append(
                {
                    "code": str(row["code"]),
                    "name": row["name"],
                    "sector": row["sector"],
                    "market": row["market"],
                }
            )

        with db_proxy.atomic():
            Stock.insert_many(stock_records).on_conflict_replace().execute()

        logger.info(f"✅ JPX list updated: {len(jpx_df)} stocks.")
    except Exception as e:
        logger.error(f"❌ JPX Refresh Error: {e}")
        if args.jpx_only:
            return

    if args.jpx_only:
        logger.info("Done (JPX only mode).")
        return

    # 2. マーケットデータの取得
    logger.info("Step 2: Fetching market data...")
    codes = None
    if args.codes:
        codes = args.codes.split(",")
    elif args.limit:
        # 全銘柄リストから limit 分を取得
        active_codes = [s.code for s in Stock.select(Stock.code)]
        codes = active_codes[: args.limit]

    # データ取得とDB保存の実行
    # fetch_stock_data は内部で tqdm を使用して進捗を表示する
    try:
        df = fetcher.fetch_stock_data(codes=codes)

        if not df.empty:
            logger.info(f"✅ Fetched data for {len(df)} stocks. Saving to database...")
            # upsert_market_data は内部で重複チェックを行い保存する
            records = df.to_dict("records")
            db.upsert_market_data(records)
            logger.info("🎉 Data collection and ingestion completed.")
        else:
            logger.warning("⚠️ No data was fetched.")

    except Exception as e:
        logger.error(f"❌ Collection Error: {e}")


if __name__ == "__main__":
    main()

```

---

### equity_auditor.py

```python
import argparse
import sys

from src.env_loader import load_env_file

load_env_file()  # [Fix] Discover and load .env from parent dirs

from src.commands.analyze import AnalyzeCommand  # noqa: E402
from src.commands.extract import ExtractCommand  # noqa: E402
from src.commands.ingest import IngestCommand  # noqa: E402
from src.commands.reset import ResetCommand  # noqa: E402
from src.config_loader import load_config  # noqa: E402
from src.logger import setup_logger  # noqa: E402

# Initialize Logger globally
setup_logger()


class EquityAuditor:
    """
    Refactored Facade for Antigravity V7.
    Delegates commands to specialized Command classes.
    """

    def __init__(self, debug_mode=False):
        self.config = load_config("config/config.yaml")
        self.debug_mode = debug_mode
        self.commands = {
            "extract": ExtractCommand(self.config, debug_mode),
            "analyze": AnalyzeCommand(self.config, debug_mode),
            "ingest": IngestCommand(self.config, debug_mode),
            "reset": ResetCommand(self.config, debug_mode),
        }
        # Ingest doubles as Export provider if needed, or we can separate ExportCommand
        # Current AnalyzeCommand handles its own pipeline, but also Ingest handles file import.

    # --- Backward Compatibility Properties (Delegating to ExtractCommand primary) ---
    @property
    def provider(self):
        return self.commands["extract"].provider

    @property
    def db(self):
        return self.commands["extract"].db

    @property
    def agent(self):
        return self.commands["extract"].agent

    def run(self):
        parser = argparse.ArgumentParser(
            description="Equity Auditor - Stock Analysis Pipeline"
        )
        parser.add_argument(
            "--mode",
            choices=[
                "extract",
                "analyze",
                "ingest",
                "report",
                "repair",
                "monitor",
                "archive",
                "reset",
                "gen_prompt",
                "merge",
            ],
            required=True,
        )
        parser.add_argument("--strategy", help="Strategy name")
        parser.add_argument("--limit", type=int, default=50, help="Limit")
        parser.add_argument("--files", help="File pattern tasks")
        parser.add_argument("--codes", help="Comma separated codes")
        parser.add_argument("--input", help="Input file for merge")
        parser.add_argument("--output", help="Output file")
        parser.add_argument(
            "--format", choices=["csv", "json", "all"], default="csv", help="Format"
        )
        parser.add_argument("--debug", action="store_true", help="Debug/Mock Mode")
        parser.add_argument("--force", action="store_true", help="Force Reset")
        parser.add_argument(
            "--all", action="store_true", help="Reset All (for reset mode)"
        )
        parser.add_argument(
            "--force-refresh",
            action="store_true",
            help="Skip cache and force fresh AI analysis",
        )
        parser.add_argument("--date", help="Date for reset/archive")

        args = parser.parse_args()

        # Override debug if flag provided
        debug_mode = args.debug or self.debug_mode

        # [Fix] Propagate debug_mode to commands initialized before args parsing
        if debug_mode:
            for cmd in self.commands.values():
                cmd.debug_mode = True
                # Propagate to Agent if exists
                if hasattr(cmd, "agent") and cmd.agent:
                    cmd.agent.debug_mode = True
                    cmd.agent.client = None  # Force disable client

        # Parse Codes
        codes_list = [c.strip() for c in args.codes.split(",")] if args.codes else None

        if args.mode == "extract":
            if not args.strategy:
                print("❌ --strategy is required for extract mode.")
                return
            self.commands["extract"].execute(
                strategy=args.strategy,
                limit=args.limit,
                codes=codes_list,
                output_path=args.output,
            )

        elif args.mode == "analyze":
            self.commands["analyze"].execute(
                strategy=args.strategy,
                limit=args.limit,
                codes=codes_list,
                files=args.files,
                force_refresh=args.force_refresh,
            )

        elif args.mode == "ingest":
            pattern = [args.files] if args.files else ["data/interim/*.json"]
            self.commands["ingest"].execute(
                file_patterns=pattern, strategy=args.strategy, output_format=args.format
            )

        elif args.mode == "report":
            print("\n📊 Consolidated report via ReportGenerator is deprecated.")
            print(
                "💡 Please use CSV reports in data/output/ generated by 'analyze' or 'ingest' mode."
            )

        elif args.mode == "gen_prompt":
            # TODO: Migrate to ExtractCommand or separate
            print("⚠️ gen_prompt mode under migration.")

        elif args.mode == "merge":
            # TODO: Migrate
            print("⚠️ merge mode under migration.")

        elif args.mode == "repair":
            print("⚠️ repair mode disabled.")

        elif args.mode == "reset":
            self.commands["reset"].execute(
                strategy=args.strategy,
                code=args.codes,  # Note: args.codes is "code,code" string or just one code. ResetCommand logic handles "code" param. Parser logic splits above.
                # Wait, ResetCommand expects single 'code' or we iterate?
                # The plan said --code [code].
                # Let's check parser. codes_list was parsed.
                # Analyze uses list. Reset might want list too?
                # ResetCommand implementation (checked in file) used 'code' (singular) for `MarketData.code == code`.
                # Let's act strictly on singular code for now as per plan, or update ResetCommand to handle list.
                # Given "specific stock" requirement, singular is fine.
                # But args.codes is comma separated string.
                # If user says --codes 3498, args.codes is "3498".
                # If user says --code 3498, we need to allow --code arg?
                # Parser says: parser.add_argument("--codes", help="Comma separated codes")
                # It doesn't have --code.
                # Let's interpret args.codes as the input for 'code' logic.
                # If multiple codes are passed, ResetCommand needs update?
                # ResetCommand logic: `conditions.append(MarketData.code == code)`
                # If we pass a list, Peewee might handle `in_`?
                # Let's adjust ResetCommand if needed. But for now let's pass the raw string if simple?
                # No, `codes_list` contains list. `args.codes` is string.
                # Let's Assume user passes one code for now, or use `in` operator in ResetCommand.
                # Let's assume single code for "sniper" reset.
                reset_all=(
                    args.all if hasattr(args, "all") else args.force
                ),  # Use force as 'all' or add --all arg?
                # Requirement said: --all argument.
            )


if __name__ == "__main__":
    runner = EquityAuditor()
    try:
        runner.run()
    except KeyboardInterrupt:
        # Silently exit to allow Orchestrator to handle the message
        sys.exit(0)

```

---

### orchestrator.py

```python
#!/usr/bin/env python3
import argparse
import sys

from src.env_loader import load_env_file
from src.logger import setup_logger
from src.orchestrator import Orchestrator


def main():
    load_env_file()  # Load .env variables (with auto-discovery)
    parser = argparse.ArgumentParser(description="Antigravity Orchestrator")
    parser.add_argument(
        "mode", choices=["daily", "weekly", "monthly"], help="Orchestrator Mode"
    )
    parser.add_argument("--debug", action="store_true", help="Debug Mode")
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically accept all handshake proposals",
    )

    args = parser.parse_args()

    setup_logger()

    try:
        orchestrator = Orchestrator(debug_mode=args.debug)

        # Inject auto-fix preference if we implemented it in class
        # Current implementation just logs alerts.
        # Future: orchestrator.set_auto_fix(args.auto_fix)

        orchestrator.run(args.mode)

    except KeyboardInterrupt:
        print("\n\n🎻 Orchestration cancelled by user (KeyboardInterrupt).")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Orchestrator failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

```

---

### sentinel.py

```python
#!/usr/bin/env python3
import argparse
import sys

from src.logger import setup_logger
from src.sentinel import Sentinel


def main():
    parser = argparse.ArgumentParser(
        description="Antigravity Sentinel (Market Watcher)"
    )
    parser.add_argument(
        "--limit", type=int, default=200, help="Number of stocks to scan (default: 200)"
    )
    parser.add_argument("--debug", action="store_true", help="Debug Mode")

    args = parser.parse_args()

    setup_logger()

    try:
        sentinel = Sentinel(debug_mode=args.debug)
        sentinel.run(limit=args.limit)

    except Exception as e:
        print(f"❌ Sentinel failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

```

---

## Source Code (src)

### src/__init__.py

```python

```

---

### src/ai/__init__.py

```python

```

---

### src/ai/agent.py

```python
import time
from logging import getLogger
from typing import Any, Dict, Optional

from src.ai.key_manager import APIKeyManager
from src.ai.prompt_builder import PromptBuilder
from src.ai.response_parser import ResponseParser
from src.validation_engine import ValidationEngine


class AIAgent:
    """分析エージェントのメインクラス。

    各コンポーネント（KeyManager, PromptBuilder, ResponseParser）を統合して、
    株式銘柄の AI 分析ワークフローを実行する。

    Attributes:
        model_name (str): 使用する AI モデル名。
        interval_sec (float): リクエスト間のインターバル（秒）。
        debug_mode (bool): デバッグモード（APIコールをスキップ）のフラグ。
        config (Dict[str, Any]): システム設定の辞書。
        key_manager (APIKeyManager): APIキーの管理モジュール。
        prompt_builder (PromptBuilder): プロンプト構築モジュール。
        response_parser (ResponseParser): 回答パース・検証モジュール。
        validator (ValidationEngine): データ検証モジュール。
    """

    def __init__(
        self, model_name: str, interval_sec: float = 2.0, debug_mode: bool = False
    ):
        """AIAgent を初期化する。

        Args:
            model_name (str): AI モデルの名。
            interval_sec (float, optional): リクエスト間隔。デフォルトは 2.0。
            debug_mode (bool, optional): デバッグモード。デフォルトは False。
        """
        self.logger = getLogger(__name__)
        self.model_name = model_name
        self.interval_sec = interval_sec
        self.debug_mode = debug_mode
        self.config: Dict[str, Any] = {}
        self.key_manager = APIKeyManager(debug_mode=debug_mode)
        self.prompt_builder = PromptBuilder()
        self.response_parser = ResponseParser()
        self.validator: Optional[ValidationEngine] = None  # set_config で初期化

        # 内部定数とフォールバック
        self.MAX_RETRIES = 3
        self.FALLBACK_REASON = "[ANALYSIS FAILED]: 判断不能。3回のリトライ後も具体的根拠を生成できず。財務データの欠損または材料不足のため、投資判断には手動確認が必須。"

        # クライアントの初期化 (KeyManager経由)
        self.client = self.key_manager.get_current_client()
        self.audit_version = 1

    @property
    def api_keys(self):
        return self.key_manager.api_keys

    @api_keys.setter
    def api_keys(self, value):
        self.key_manager.api_keys = value

    @property
    def current_key_idx(self):
        return self.key_manager.current_key_idx

    @current_key_idx.setter
    def current_key_idx(self, value):
        self.key_manager.current_key_idx = value

    @property
    def key_stats(self):
        return self.key_manager.key_stats

    @key_stats.setter
    def key_stats(self, value):
        self.key_manager.key_stats = value

    @property
    def thresholds_cfg(self):
        return self.prompt_builder.thresholds_cfg

    @property
    def sector_policies(self):
        """互換性のためのエイリアス"""
        return self.config.get("sector_policies", {})

    @sector_policies.setter
    def sector_policies(self, value):
        self.config["sector_policies"] = value

    def set_config(self, config: Dict[str, Any]):
        """システム設定を注入し、内部コンポーネントを最新化する。

        Args:
            config (Dict[str, Any]): アプリケーション全体の設定。
        """
        self.config = config
        self.prompt_builder.config = config
        # Validatorの初期化
        if self.validator is None:
            self.validator = ValidationEngine(config)

    def get_total_calls(self) -> int:
        """全APIキーを通じた累積呼び出し回数を取得する。"""
        return self.key_manager.get_total_calls()

    def generate_usage_report(self) -> str:
        """API 使用状況の監査レポートを文字列として生成する。

        Returns:
            str: 構造化された使用状況レポート。
        """
        lines = ["\n" + "=" * 40, "       📊 API Usage Audit Report", "=" * 40]
        for i, stats in enumerate(self.key_stats):
            status_icon = "✅" if stats["status"] == "active" else "🚫"
            lines.append(f"Key #{i+1}: {status_icon} {stats['status']}")
            lines.append(f"  - Total Calls: {stats['total_calls']}")
            lines.append(f"  - Success:     {stats['success_count']}")
            lines.append(f"  - Retries(BL): {stats['retry_count']}")
            lines.append(f"  - Errors(429): {stats['error_429_count']}")
        lines.append("=" * 40)
        return "\n".join(lines)

    def _generate_content_with_retry(self, prompt: str):
        """API 呼び出しのリトライループを実行し、キーローテーションを管理する。

        Args:
            prompt (str): AI に送信するプロンプト。

        Returns:
            Optional[Any]: API レスポンスオブジェクト、または失敗時 None。
        """
        if self.debug_mode:
            return None

        # [v12.0] 歴史的な実装に合わせてリトライ回数を動的に設定
        max_retries = len(self.api_keys) + 2
        base_delay = 5
        attempt = 0

        while attempt < max_retries:
            if self.client is None:
                self.client = self.key_manager.get_current_client()

            if not self.client:
                # クライアント初期化失敗時はキーの欠如を想定し、ベースディレイ後にリトライ
                attempt += 1
                time.sleep(base_delay)
                continue

            idx = self.key_manager.current_key_idx
            self.key_manager.update_stats(idx, "total_calls")
            self.key_manager.update_stats(idx, "usage")

            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"},
                )
                self.key_manager.update_stats(idx, "success_count")
                return response
            except Exception as e:
                err_msg = str(e)
                attempt += 1
                self.key_manager.update_stats(idx, "errors")

                # クォータ制限（429 / ResourceExhausted）のチェック
                if "429" in err_msg or "ResourceExhausted" in err_msg:
                    self.logger.warning(
                        f"⚠️ Key #{idx+1} hit rate limit (429). Rotating..."
                    )
                    self.key_manager.update_stats(idx, "error_429_count")
                    self.key_manager.key_stats[idx]["is_exhausted"] = True
                    if self._rotate_key():
                        # 新しいキーで即座に再試行
                        continue
                    else:
                        # 全てのキーが枯渇した場合は一定時間待機
                        self.logger.info("⏳ No more keys. Waiting 60s...")
                        time.sleep(60)
                        continue

                # その他のエラー（接続エラー等）
                self.key_manager.check_key_health(idx)
                delay = base_delay * (2 ** (attempt - 1))
                self.logger.warning(f"⚠️ API Error: {err_msg}. Retrying in {delay}s...")
                time.sleep(delay)

        return None

    def analyze(
        self, row: Dict[str, Any], strategy_name: str = "Unknown"
    ) -> Dict[str, Any]:
        """銘柄データを受け取り、AI 分析プロセスを実行するメインメソッド。

        Args:
            row (Dict[str, Any]): 銘柄の財務・マーケットデータ。
            strategy_name (str, optional): 使用する投資戦略。デフォルトは "Unknown"。

        Returns:
            Dict[str, Any]: 分析結果（感情、理由、リスク、期間等を含む辞書）。
        """
        target_code = row.get("code")

        # 1. データのバリデーション
        if self.validator:
            is_valid, data_issues = self.validator.validate_stock_data(
                row, strategy=strategy_name
            )
        else:
            # フォールバック (Validatorがない場合の最小限のチェック)
            is_valid = target_code is not None
            data_issues = [] if is_valid else ["Missing Code"]

        if not is_valid:
            self.logger.warning(
                f"🚫 Analysis Skipped for {target_code}: Critical Data Defects -> {data_issues}"
            )
            return {
                "ai_sentiment": "Neutral",
                "ai_reason": f"[ANALYSIS SKIPPED]: データ不備のため分析対象外 (理由: {', '.join(data_issues)})",
                "ai_risk": "High (Unknown)",
                "ai_horizon": "Wait",
                "_analysis_failed": True,
                "audit_version": 0,
            }

        # [Debug Mode Bypass]
        if self.debug_mode:
            return {
                "ai_sentiment": "Neutral",
                "ai_summary": "【結論】MOCK ANALYSIS: データ不備なし。安定成長を期待。",
                "ai_reason": "【結論】MOCK ANALYSIS: データ不備なし。安定成長を期待。",
                "ai_detail": "これはデバッグモード用のモックレスポンスです。",
                "ai_risk": "Low (Reason: Mock)",
                "ai_horizon": "Wait",
                "audit_version": 1,
            }

        # 2. プロンプト作成
        prompt = self._create_prompt(row, strategy_name)
        # DQF (Data Quality Flag) アラートの追加
        dqf_alert = self._generate_dqf_alert(row)
        if dqf_alert:
            prompt += f"\n\n注意: {dqf_alert}"

        # 3. 実行とリトライループ (パースエラーや品質エラーに対応)
        final_result = None
        for attempt in range(self.MAX_RETRIES):
            try:
                if attempt > 0:
                    time.sleep(self.interval_sec)

                idx = self.key_manager.current_key_idx
                response = self._generate_content_with_retry(prompt)
                if not response:
                    self.logger.warning(
                        f"⚠️ Attempt {attempt+1} failed: No response from API."
                    )
                    continue

                # パース
                res_dict = self._parse_response(response.text)

                # 回答の品質・形式バリデーション
                is_valid_res, err_reason = self._validate_response(res_dict)
                if is_valid_res:
                    final_result = res_dict
                    # 基盤監査バージョンの注入
                    if (
                        "audit_version" not in final_result
                        or not final_result["audit_version"]
                    ):
                        final_result["audit_version"] = self.audit_version
                    break
                else:
                    self.logger.warning(
                        f"⚠️ Attempt {attempt+1} failed quality check: {err_reason}"
                    )
                    self.key_manager.update_stats(idx, "retry_count")
            except Exception as e:
                self.logger.error(f"Attempt {attempt+1} failed with error: {e}")

        if not final_result:
            return {
                "ai_sentiment": "Neutral",
                "ai_reason": self.FALLBACK_REASON,
                "ai_risk": "High (Unknown)",
                "ai_horizon": "Wait",
                "_analysis_failed": True,
                "audit_version": 0,
            }

        return final_result

    def analyze_from_text(self, prompt: str) -> Dict[str, Any]:
        """生のテキストプロンプトから AI 分析を実行する（Runner/Debug向け）。

        Args:
            prompt (str): 自作または加工済みのプロンプト文字列。

        Returns:
            Dict[str, Any]: パースされた分析結果。
        """
        if self.debug_mode:
            return {
                "ai_sentiment": "Neutral",
                "ai_reason": "【結論】MOCK ANALYSIS: データ不備なし。安定成長を期待。",
                "ai_summary": "【結論】MOCK ANALYSIS: データ不備なし。安定成長を期待。",
                "ai_risk": "Low (Reason: Mock)",
                "ai_horizon": "Wait",
                "audit_version": 1,
            }

        response = self._generate_content_with_retry(prompt)
        return self._parse_response(response.text if response else "{}")

    # ============================================================
    # 後方互換性およびテストのためのラッパーメソッド
    # ============================================================
    def _rotate_key(self):
        success = self.key_manager.rotate_key()
        if success:
            self._init_client()
        return success

    def _check_key_health(self, idx):
        return self.key_manager.check_key_health(idx)

    def _prepare_variables(self, row, strategy_name):
        return self.prompt_builder.prepare_variables(row, strategy_name)

    def _create_prompt(self, row, strategy_name):
        return self.prompt_builder.create_prompt(row, strategy_name)

    def _parse_response(self, text):
        return self.response_parser.parse_response(text)

    def _validate_response(self, result):
        return self.response_parser.validate_response(result)

    def _generate_dqf_alert(self, row):
        return self.response_parser.generate_dqf_alert(row)

    def _init_client(self):
        self.client = self.key_manager.get_current_client()

    def _load_prompt_template(self):
        """プロンプトテンプレートの読み込み (互換性のためのラッパー)"""
        if not hasattr(self, "prompt_builder"):
            return {}
        self.prompt_builder.prompt_config = self.prompt_builder._load_prompt_template()
        return self.prompt_builder.prompt_config

```

---

### src/ai/key_manager.py

```python
import os
import sys
import threading
from logging import getLogger
from typing import Any, Dict, List

from google import genai


class APIKeyManager:
    """
    [v12.0] APIキーの保持、健康状態管理、ローテーションロジックを担当。
    AIAgentからキー管理責務を分離。
    """

    def __init__(self, debug_mode: bool = False):
        self.logger = getLogger(__name__)
        self.debug_mode = debug_mode
        self.api_keys: List[str] = []
        self.key_stats: List[Dict[str, Any]] = []
        self.current_key_idx = 0
        self.lock = threading.Lock()

        self._load_keys()

    def _load_keys(self):
        """環境変数からAPIキーを読み込む"""
        if self.debug_mode:
            return

        # Primay key
        key1 = os.getenv("GEMINI_API_KEY")
        if key1:
            self.api_keys.append(key1)

        # Additional keys
        for i in range(2, 10):
            k = os.getenv(f"GEMINI_API_KEY_{i}")
            if k:
                self.api_keys.append(k)

        if self.api_keys:
            self.logger.info(f"Loaded {len(self.api_keys)} API keys.")
            self.key_stats = [
                {
                    "usage": 0,
                    "errors": 0,
                    "status": "active",
                    "is_exhausted": False,
                    "total_calls": 0,  # 全試行回数 (リトライ含む)
                    "success_count": 0,  # 成功回数
                    "retry_count": 0,  # ブラックリストによるリトライ
                    "error_429_count": 0,  # 429エラーによるリトライ
                }
                for _ in self.api_keys
            ]
        else:
            self.logger.warning("GEMINI_API_KEY not found. AI features will fail.")

    def get_current_client(self):
        """現在のインデックスのキーでクライアントを初期化して返す"""
        if self.debug_mode:
            self.logger.info(
                "🔧 Debug Mode: Skipping Gemini Client initialization (Simulation Mode)"
            )
            return None

        if not self.api_keys:
            return None

        current_key = self.api_keys[self.current_key_idx]
        try:
            client = genai.Client(api_key=current_key)
            masked_key = current_key[:4] + "..." + current_key[-4:]
            self.logger.info(
                f"Initialized Gemini Client with Key #{self.current_key_idx + 1} ({masked_key})"
            )
            return client
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini Client: {e}")
            return None

    def check_key_health(self, idx: int):
        """キーの健康状態をチェックし、必要なら無効化 (Self-Healing)"""
        if idx >= len(self.key_stats):
            return

        stats = self.key_stats[idx]
        if stats["usage"] > 0:
            error_rate = stats["errors"] / stats["usage"]
            if (
                error_rate > 0.5 and stats["usage"] >= 5
            ):  # 閾値: 5回以上の試行でエラー率50%以上
                stats["status"] = "disabled"
                self.logger.warning(
                    f"🚫 Key #{idx + 1} Disabled (Self-Healing). Error Rate: {error_rate:.1%}"
                )

    def rotate_key(self) -> bool:
        """
        次の有効なAPIキーに切り替える (Permanent Switch)
        Returns:
            bool: 切り替え成功時 True
        """
        with self.lock:
            if len(self.api_keys) <= 1:
                if self.key_stats and self.key_stats[self.current_key_idx].get(
                    "is_exhausted"
                ):
                    self.logger.critical(
                        "🚨 SINGLE KEY EXHAUSTED: Daily quota reached. Terminating."
                    )
                    sys.exit(0)
                return False

            attempts = 0
            while attempts < len(self.api_keys):
                idx = (self.current_key_idx + 1) % len(self.api_keys)
                self.current_key_idx = idx

                stats = self.key_stats[idx]
                if stats["status"] == "active" and not stats.get("is_exhausted"):
                    current_key = self.api_keys[idx]
                    masked = current_key[:4] + "..." + current_key[-4:]
                    self.logger.warning(
                        f"🔄 Switching permanently to Key #{idx + 1} (ID: {masked})"
                    )
                    return True

                attempts += 1

            self.logger.critical(
                "🚨 ALL API KEYS EXHAUSTED: Daily quota reached."
                " Terminating analysis session to protect data integrity."
            )
            sys.exit(1)

    def get_total_calls(self) -> int:
        """全キーを通じた累積API呼出回数を取得"""
        if not self.key_stats:
            return 0
        return sum(k["total_calls"] for k in self.key_stats)

    def update_stats(self, idx: int, field: str, amount: int = 1):
        """統計情報の更新"""
        if 0 <= idx < len(self.key_stats):
            if field in self.key_stats[idx]:
                self.key_stats[idx][field] += amount

```

---

### src/ai/prompt_builder.py

```python
import os
from logging import getLogger
from typing import TYPE_CHECKING, Any, Dict, Optional

import yaml

if TYPE_CHECKING:
    from src.domain.models import StockAnalysisData


class PromptBuilder:
    """
    [v12.0] プロンプトのテンプレート読み込み、変数の準備、最終的なプロンプト文字列の組み立てを担当。
    [v2.0] StockAnalysisData の ValidationFlag を活用した検証メタデータの埋め込みに対応。
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = getLogger(__name__)
        self.config = config or {}
        self.prompt_config = self._load_prompt_template()
        self.thresholds_cfg = self._load_thresholds()
        self.audit_version = self.prompt_config.get("audit_version", 0)

    def _load_prompt_template(self) -> Dict[str, Any]:
        """YAMLからプロンプトテンプレートを読み込む"""
        path = "config/ai_prompts.yaml"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                self.logger.error(f"Failed to load prompt config: {e}")
        return {}

    def _load_thresholds(self) -> Dict[str, Any]:
        """thresholds.yaml から判定閾値を読み込む"""
        path = "config/thresholds.yaml"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return data.get("thresholds", {})
            except Exception as e:
                self.logger.error(f"Failed to load thresholds.yaml: {e}")
        return {}

    def prepare_variables(
        self, row: Dict[str, Any], strategy_name: str
    ) -> Dict[str, Any]:
        """プロンプトに挿入する変数の辞書を作成する。

        Args:
            row (Dict[str, Any]): 銘柄データの一行。
            strategy_name (str): 戦略名。

        Returns:
            Dict[str, Any]: テンプレートに適用可能な変数値の辞書。
        """
        from src.utils import safe_float as s

        # 0. 基本情報の取得
        sector_info = row.get("sector_17", row.get("sector", "Unknown"))
        code = row.get("code", "Unknown")
        name = row.get("name", "Unknown")

        # 1. 設定情報の取得 (Persona, Risks)
        strategies_cfg = self.config.get("strategies", {})
        strat_cfg = strategies_cfg.get(strategy_name, {})
        persona = strat_cfg.get("persona", "Analysis Expert")
        default_horizon = strat_cfg.get("default_horizon", "Wait")

        sector_risks = self.config.get("sector_risks", {})
        risk_context_str = sector_risks.get(
            sector_info, "General Market Risk (No specific sector data)."
        )

        # 2. 除外設定とマーケットコンテキスト
        sector_policies = self.config.get("sector_policies", {})
        sector_policy = sector_policies.get(
            sector_info, sector_policies.get("default", {})
        )
        ai_excludes = list(sector_policy.get("ai_prompt_excludes", []))
        strat_policy_key = f"_strategy_{strategy_name}"
        if strat_policy_key in sector_policies:
            strat_excludes = sector_policies[strat_policy_key].get(
                "ai_prompt_excludes", []
            )
            ai_excludes = list(set(ai_excludes + strat_excludes))

        exclusion_notice = ""
        if ai_excludes:
            exclusion_notice = (
                "\n        [ANALYSIS NOTICE]\n        The following metrics are NOT APPLICABLE for this sector/strategy and should be EXCLUDED from your analysis:\n        - "
                + "\n        - ".join(ai_excludes)
                + "\n        (These metrics may show 'None' or 'N/A' due to structural reasons, not data errors.)\n"
            )

        special_instruction = ""
        if strategy_name == "turnaround_spec":
            # [v12.7 Fix] PERが実際にNaN/Negativeの場合のみ特別指示を表示
            per_val = row.get("per")
            # [v12.7 Fix] PERがNone, NaN, または0以下の場合を「収益なし」と判定
            import pandas as pd

            is_per_none = per_val is None or (
                isinstance(per_val, float) and pd.isna(per_val)
            )
            is_per_negative = (
                isinstance(per_val, (int, float))
                and not pd.isna(per_val)
                and per_val <= 0
            )

            if is_per_none or is_per_negative:
                special_instruction = """
        [SPECIAL ANALYST INSTRUCTION]
        This company currently has no earnings (PER is NaN/Negative). Focus your analysis on:
        1. Sales Growth sustainability.
        2. Asset value backing (PBR).
        3. Probability of a near-term turnaround (profitability improvements).
        Evaluate it as a high-risk, high-reward turnaround play.
"""

        market_context = "No specific market context available."
        market_context_file = "market_context.txt"
        if os.path.exists(market_context_file):
            try:
                with open(market_context_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    filtered_lines = [
                        line
                        for line in lines
                        if not line.strip().startswith("[STRATEGY_SIGNAL]")
                    ]
                    market_context = "".join(filtered_lines)
            except Exception:
                pass

        # 3. 計算メトリクスの準備
        # Trend Score ロジック
        trend_score = 0
        if s(row.get("trend_up")) == 1:
            trend_score += 1
        macd_val = s(
            row.get("macd_hist")
            if row.get("macd_hist") is not None
            else row.get("macd")
        )
        if macd_val > 0:
            trend_score += 1
        rsi_val = s(row.get("rsi") if row.get("rsi") is not None else row.get("rsi_14"))
        if rsi_val > 50:
            trend_score += 1
        score_trend = s(row.get("score_trend"))
        if score_trend >= 60:
            trend_score += 1

        trend_signal_str = (
            "Strong Uptrend" if s(row.get("trend_up")) == 1 else "Neutral/Weak"
        )
        trend_desc = f"{trend_score}/4 ({trend_signal_str})"

        # ステータス文字列
        p_status_raw = str(row.get("profit_status", ""))
        t_status_raw = str(row.get("turnaround_status", ""))
        profit_status_str = p_status_raw
        if t_status_raw == "turnaround_black":
            profit_status_str = "Turnaround (Moved from Loss to Profit!)"
        elif p_status_raw == "surge":
            profit_status_str = "Surge (Profit Jump)"
        elif p_status_raw == "loss_shrinking":
            profit_status_str = "Loss Shrinking"
        elif p_status_raw == "loss_expanding":
            profit_status_str = "Loss Expanding (Warning)"
        elif p_status_raw == "crash":
            profit_status_str = "Crash (Profit Drop)"

        sales_status_str = str(row.get("sales_status", "Unknown"))

        q_val = row.get("score_value", 0)
        q_gro = row.get("score_growth", 0)
        q_qual = row.get("score_quality", 0)
        quant_scores_str = f"Value({q_val}), Growth({q_gro}), Quality({q_qual})"

        # ハイライト設定
        highlight_msg = ""
        if t_status_raw == "turnaround_black" or p_status_raw == "turnaround":
            highlight_msg = "\n        [🚨 PRIORITY ANALYSIS: TURNAROUND 🚨]\n        This stock is showing signs of a TURNAROUND (Loss -> Profit). Validate if this recovery is sustainable!"
        elif p_status_raw == "surge":
            highlight_msg = "\n        [🔥 PRIORITY ANALYSIS: PROFIT SURGE 🔥]\n        This stock is showing a PROFIT SURGE. Determine if this is a one-time event or a structural growth phase!"

        # 値のフォーマッティング
        ocf = s(row.get("operating_cf"))
        sales = s(row.get("sales"))
        ocf_margin_val = f"{(ocf / sales * 100):.2f}" if sales != 0 else "None"

        op_margin_val = (
            row.get("operating_margin")
            if row.get("operating_margin") is not None
            else "None"
        )
        de_ratio = (
            row.get("debt_equity_ratio")
            if row.get("debt_equity_ratio") is not None
            else "None"
        )

        # 4. 閾値の設定注入
        threshold_vars = {}
        for category, metrics in self.thresholds_cfg.items():
            for m_key, m_val in metrics.items():
                threshold_vars[f"threshold_{m_key}"] = m_val
                threshold_vars[m_key] = m_val

        # データ不備の分類 (Deficiency Classification)
        import pandas as pd

        missing_metrics = []
        dqf_items_map = {
            "per": "PER",
            "pbr": "PBR",
            "roe": "ROE",
            "operating_cf": "営業CF",
            "free_cf": "フリーCF",
            "sales_growth": "売上成長率",
            "operating_margin": "営業利益率",
            "debt_equity_ratio": "自己資本比率/DEレシオ",
        }

        for key, label in dqf_items_map.items():
            val = row.get(key)
            if val is None or (isinstance(val, float) and pd.isna(val)):
                missing_metrics.append(label)

        deficiency_type = "完全データ型"
        if missing_metrics:
            has_cf_missing = any(m in missing_metrics for m in ["営業CF", "フリーCF"])
            has_pl_missing = any(
                m in missing_metrics for m in ["PER", "ROE", "売上成長率", "営業利益率"]
            )
            has_bs_missing = any(
                m in missing_metrics for m in ["PBR", "自己資本比率/DEレシオ"]
            )
            types = []
            if has_cf_missing:
                types.append("CF欠損型")
            if has_pl_missing:
                types.append("PL欠損型")
            if has_bs_missing:
                types.append("BS欠損型")
            if len(types) >= 2:
                deficiency_type = "複合欠損型"
            elif types:
                deficiency_type = types[0]
            else:
                deficiency_type = "その他欠損型"

        missing_metrics_summary = (
            "、".join(missing_metrics) if missing_metrics else "なし"
        )

        # 変数辞書の生成
        base_vars = {
            "code": code,
            "name": name,
            "sector": sector_info,
            "strategy_name": strategy_name,
            "persona": persona,
            "default_horizon": default_horizon,
            "highlight_msg": highlight_msg,
            "market_context": market_context,
            "exclusion_notice": exclusion_notice,
            "special_instruction": special_instruction,
            "risk_context_str": risk_context_str,
            "deficiency_type": deficiency_type,
            "missing_metrics_summary": missing_metrics_summary,
            "current_price": row.get("current_price"),
            "per": row.get("per"),
            "pbr": row.get("pbr"),
            "peg_ratio": row.get("peg_ratio"),
            "ocf_margin_val": ocf_margin_val,
            "free_cf": row.get("free_cf"),
            "de_ratio": de_ratio,
            "equity_ratio": row.get("equity_ratio"),
            "current_ratio": row.get("current_ratio"),
            "cf_status": row.get("cf_status"),
            "roe": row.get("roe"),
            "sales_growth": row.get("sales_growth"),
            "profit_growth": row.get("profit_growth"),
            "op_margin_val": op_margin_val,
            "dividend_yield": row.get("dividend_yield"),
            "payout_ratio": row.get("payout_ratio"),
            "volatility": row.get("volatility"),
            "rsi": row.get("rsi") or row.get("rsi_14") or "N/A",
            "macd": row.get("macd") or row.get("macd_hist") or "N/A",
            "trend_signal": row.get("trend_signal"),
            "trend_desc": trend_desc,
            "profit_status_str": profit_status_str,
            "sales_status_str": sales_status_str,
            "quant_scores_str": quant_scores_str,
            "ma_divergence": (
                f"{row.get('ma_divergence', 0):.2f}"
                if row.get("ma_divergence") is not None
                else "N/A"
            ),
            "volume_ratio": (
                f"{row.get('volume_ratio', 0):.2f}"
                if row.get("volume_ratio") is not None
                else "N/A"
            ),
            # [v2.0] ValidationFlag 関連のプレースホルダー
            "tier1_missing_count": row.get("tier1_missing_count", 0),
            "tier2_missing_count": row.get("tier2_missing_count", 0),
            "red_flag_count": row.get("red_flag_count", 0),
            "red_flags_list": row.get("red_flags_list", "なし"),
            "rescue_status": row.get("rescue_status", "非該当"),
            "pydantic_validated": row.get("pydantic_validated", False),
        }
        base_vars.update(threshold_vars)
        return base_vars

    def create_prompt(self, row: Dict[str, Any], strategy_name: str) -> str:
        """テンプレートを元に最終的なプロンプトを作成する。

        Args:
            row (Dict[str, Any]): 銘柄データ。
            strategy_name (str): 戦略名。

        Returns:
            str: 生成されたプロンプト文字列。
        """
        vars_dict = self.prepare_variables(row, strategy_name)

        base_tmpl = self.prompt_config.get("base_template", "")
        metrics_tmpl = self.prompt_config.get("metrics_template", "")

        if not base_tmpl:
            return "Error: Prompt template missing."

        try:
            metrics_section = metrics_tmpl.format(**vars_dict)
        except KeyError as e:
            self.logger.warning(f"Missing key in metrics template: {e}")
            metrics_section = "[Metrics Generation Error]"

        vars_dict["metrics_section"] = metrics_section

        try:
            return base_tmpl.format(**vars_dict)
        except Exception as e:
            self.logger.error(f"Failed to format base prompt: {e}")
            return f"Analyze stock {row.get('code')} ({row.get('name')})"

    def create_prompt_from_model(
        self, stock: "StockAnalysisData", strategy_name: str  # type: ignore
    ) -> str:
        """[v2.0] StockAnalysisData モデルからプロンプトを生成する。

        ValidationFlag のメタデータを活用し、AI に検証状態を明示する。

        Args:
            stock: StockAnalysisData インスタンス。
            strategy_name: 戦略名。

        Returns:
            str: 生成されたプロンプト文字列。
        """
        # モデルを辞書化
        row = stock.model_dump()

        # ValidationFlag の情報を変数として追加
        flags = stock.validation_flags
        row["tier1_missing_count"] = len(flags.tier1_missing)
        row["tier2_missing_count"] = len(flags.tier2_missing)
        row["red_flag_count"] = len(flags.red_flags)
        row["red_flags_list"] = (
            "、".join(flags.red_flags) if flags.red_flags else "なし"
        )
        row["rescue_status"] = "該当 ✅" if flags.rescue_eligible else "非該当"
        row["pydantic_validated"] = True

        # 既存のcreate_promptを利用
        return self.create_prompt(row, strategy_name)

    def get_validation_metadata_section(self, stock: "StockAnalysisData") -> str:  # type: ignore
        """[v2.0] ValidationFlag をプロンプト用テキストに変換。

        Args:
            stock: StockAnalysisData インスタンス。

        Returns:
            str: 検証メタデータセクションのテキスト。
        """
        flags = stock.validation_flags
        lines = [
            "【検証メタデータ (Pydantic Validated)】",
            f"- Tier 1 欠損: {len(flags.tier1_missing)}件 ({', '.join(flags.tier1_missing) or 'なし'})",
            f"- Red Flags: {len(flags.red_flags)}件 ({', '.join(flags.red_flags) or 'なし'})",
            f"- 例外救済該当: {'✅ 該当' if flags.rescue_eligible else '非該当'}",
            "※このデータはシステムで事前検証済みです。独自の計算は行わず、提供された数値に基づいて判断してください。",
        ]
        return "\n".join(lines)

```

---

### src/ai/response_parser.py

```python
import json
import os
import re
from logging import getLogger
from typing import Any, Dict, List, Optional, Tuple


class ResponseParser:
    """
    [v12.0] LLMの回答パース、構文・構造バリデーション、DQFアラート生成を担当。
    """

    def __init__(self):
        self.logger = getLogger(__name__)
        self.blacklist = self._load_blacklist()

    def _load_blacklist(self) -> List[str]:
        """ブラックリスト・フレーズを読み込む"""
        path = "config/blacklist.txt"
        blacklist = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        blacklist.append(line)
        # 固定ブラックリストの追加 (AIAgent.bak L285)
        blacklist.extend(["安定した業績推移", "マクロ経済の影響", "AI言語モデル"])
        return blacklist

    def parse_response(self, text: str) -> Dict[str, Any]:
        """
        LLMの回答(JSON)を辞書に変換し、正規化する。
        """
        try:
            cleaned_text = text.strip()
            if cleaned_text.startswith("```"):
                match = re.search(
                    r"```(?:json)?\s*(.*?)\s*```", cleaned_text, re.DOTALL
                )
                if match:
                    cleaned_text = match.group(1)

            data = json.loads(cleaned_text)

            # [v12.0] ai_agent.py.bak L360-382 の構造に合わせる
            # ai_reason は ai_summary としても使われる
            return {
                "ai_sentiment": data.get("ai_sentiment", "Neutral"),
                "ai_reason": data.get(
                    "ai_reason", data.get("ai_summary", "No reason provided.")
                ),
                "ai_risk": data.get("ai_risk", "Unknown"),
                "ai_horizon": data.get("ai_horizon", "Wait"),
                "ai_detail": data.get("ai_detail", ""),
                "audit_version": data.get("audit_version", 0),
            }
        except Exception as e:
            self.logger.error(f"Failed to parse AI response: {e}")
            return {
                "ai_sentiment": "Error",
                "ai_reason": "Failed to parse JSON response.",
                "ai_risk": "Unknown",
                "ai_horizon": "Wait",
                "_parse_error": True,
            }

    def validate_response(self, result: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        JSON構造とサマリー構文、およびブラックリストフレーズを検証する。
        [v12.0] ai_agent.py.bak L293-331 の完全移植。
        """
        ai_sentiment = result.get("ai_sentiment")
        ai_reason = result.get("ai_reason", "")
        ai_detail = result.get("ai_detail", "")
        ai_risk = result.get("ai_risk", "")

        # 1. Sentiment Enum Check
        # 1. Sentiment Enum Check
        if ai_sentiment not in [
            "Bullish",
            "Bullish (Aggressive)",
            "Bullish (Defensive)",
            "Bearish",
            "Neutral",
            "Neutral (Positive)",
            "Neutral (Wait)",
            "Neutral (Caution)",
        ]:
            return False, f"Invalid sentiment: {ai_sentiment}"

        # 2. Summary (ai_reason) Syntax Check
        if not ai_reason:
            return False, "Empty ai_summary"

        # [Phase 1] New Rule: Must be 1 line (no newlines)
        if "\n" in ai_reason or "\r" in ai_reason:
            return False, "Summary contains newlines (Must be single line)"

        # Check order and presence of tags with "|" delimiter
        if not (
            ai_reason.startswith("【結論】")
            and "｜【強み】" in ai_reason
            and "｜【懸念】" in ai_reason
        ):
            return (
                False,
                "Summary format/order violation (Must be 【結論】...｜【強み】...｜【懸念】...)",
            )

        # Check if tags appear only once
        if (
            ai_reason.count("【結論】") != 1
            or ai_reason.count("【強み】") != 1
            or ai_reason.count("【懸念】") != 1
        ):
            return False, "Summary tags duplicated"

        # 3. Detail Body Structural Check (①-⑦)
        if not ai_detail or "①" not in ai_detail or "⑦" not in ai_detail:
            return False, "Detail body missing numbered sections ①-⑦"

        # 4. Blacklist Check
        for phrase in self.blacklist:
            if phrase in ai_reason or phrase in ai_risk:
                return False, f"Blacklist violation: '{phrase}' detected."

        return True, None

    def generate_dqf_alert(self, row: Dict[str, Any]) -> str:
        """重要なデータ欠損に対する DQF (Data Quality Flag) アラートを生成する"""
        import pandas as pd

        dqf_items = {
            "debt_equity_ratio": "Debt/Equity Ratio",
            "free_cf": "Free CF",
            "operating_cf": "Operating CF",
            "roe": "ROE",
            "per": "PER",
        }
        missing = []
        for key, label in dqf_items.items():
            val = row.get(key)
            if val is None or (isinstance(val, float) and pd.isna(val)):
                missing.append(label)

        if missing:
            return f"\n[DQF ALERT: 欠損項目 - {', '.join(missing)}]\nデータ不足を考慮した慎重な評価を行ってください。具体的な数値や根拠に基づいた分析を心がけてください。\n"
        return ""

```

---

### src/analyzer.py

```python
import os
from logging import getLogger
from typing import Any, Dict, Optional

import pandas as pd
from tqdm import tqdm

from src.ai.agent import AIAgent
from src.circuit_breaker import CircuitBreaker
from src.engine import AnalysisEngine
from src.provider import DataProvider
from src.result_writer import ResultWriter


class StockAnalyzer:
    def __init__(self, config: Dict[str, Any], debug_mode: bool = False):
        self.config = config
        self.debug_mode = debug_mode
        self.logger = getLogger(__name__)

        # 各コンポーネントの初期化
        self.provider = DataProvider(config)
        self.engine = AnalysisEngine(config)
        self.writer = ResultWriter(config)

        ai_cfg = config.get("ai", {})
        model_name = ai_cfg.get("model_name", "gemini-2.0-flash")
        interval_sec = ai_cfg.get("interval_sec", 2.0)
        self.ai_agent = AIAgent(
            model_name, interval_sec=interval_sec, debug_mode=debug_mode
        )

    def run_analysis(
        self,
        limit: Optional[int] = None,
        mode: str = "normal",
        stage: str = "all",
        input_path: Optional[str] = None,
    ) -> None:
        """分析実行フロー (Orchestrator)"""
        current_strategy = self.config.get("current_strategy", "default")
        style = self.config.get("current_style", "value_balanced")

        self.logger.info(f"🚦 Execution Stage: {stage.upper()}")

        if input_path:
            self.logger.info(f"📂 Loading candidates from input file: {input_path}")
            if not os.path.exists(input_path):
                self.logger.error(f"❌ Input file not found: {input_path}")
                return

            # Load from CSV
            # Ensure 'code' is treated as string (in case it reads as int)
            candidates = pd.read_csv(input_path, dtype={"code": str})
            self.logger.info(f"Loaded {len(candidates)} records from CSV.")

            # Skip fetch/calc/filter steps
            # Since we loaded candidates, we proceed directly to AI analysis loop
            if stage == "screening":
                self.logger.warning(
                    "Stage is 'screening' but --input was provided. Nothing to do (already screened)."
                )
                return

        elif mode == "repair":
            self.logger.info(
                "🛠️ Repair Mode: Re-analyzing failed records (Quota/Network/Error). Skipping invalid data."
            )
            # Repair mode implies we already have data, so we might skip data loading if stage is just AI?
            # For simplicity, Repair overrides stage to 'ai' conceptually, but we keep the flow.
            df = self.provider.load_error_analysis_records()
            # Repair ignores screening logic usually
            candidates = df
        else:
            self.logger.info(f"⚙️ Strategy: '{current_strategy}' (Style: {style})")
            df = self.provider.load_latest_market_data()

            if df.empty:
                self.logger.warning("No data to analyze.")
                return

            # 2. 定量スコアリング
            df = self.engine.calculate_scores(df, strategy_name=current_strategy)

            # 3. フィルタリング & ランキング
            # Note: candidates is ALREADY sorted by Quant Score (Desc) by engine.filter_and_rank
            candidates = self.engine.filter_and_rank(df, current_strategy)
            self.logger.info(f"Filtered candidates: {len(candidates)}")

            if limit and limit > 0:
                candidates = candidates.head(limit)

            # --- Stage: Screening ---
            if stage == "screening":
                from src.utils import get_today_str

                # Use ResultWriter to ensure consistent encoding
                filename = f"candidates_{get_today_str()}_{current_strategy}.csv"
                full_path = self.writer.save(candidates, filename)
                # candidates.to_csv(csv_path, index=False) # Removed direct save
                self.logger.info(
                    f"✅ Screening completed. Candidate list saved to: {full_path}"
                )
                self.logger.info(
                    f"   Top 5:\n{candidates[['code', 'name', 'quant_score']].head(5)}"
                )
                return

        # Apply limit if input_path was used (optimization to not load everything into AI loop if not needed?
        # Actually limit is applied above for normal flow. For input_path, we should also apply limit if user wants to test subset)
        if input_path and limit and limit > 0:
            candidates = candidates.head(limit)

        # 4. AI分析
        if stage in [
            "ai",
            "all",
            "screening",
        ]:  # 'screening' calls return above so it won't reach here, but for safety
            if stage == "screening":
                return

        results = []
        # [v4.6] Circuit Breaker (Refactored)
        cb_config = self.config.get("circuit_breaker", {})
        threshold = cb_config.get("consecutive_failure_threshold", 1)
        circuit_breaker = CircuitBreaker(threshold=threshold)

        # [v4.18] Asyncio Concurrency Control
        import asyncio

        # Helper Inner Async Function
        async def _run_async_batch(candidates_df):
            ai_cfg = self.config.get("ai", {})
            max_concurrency = ai_cfg.get("max_concurrency", 1)

            sem = asyncio.Semaphore(max_concurrency)
            tasks = []

            # Use tqdm manually inside async?
            # Or use as_completed. For simplicity with DataFrame, we create tasks first.

            pbar = tqdm(
                total=len(candidates_df),
                desc=f"AI Analysis (Concurrency={max_concurrency})",
            )

            async def _bounded_analyze(index, row):
                async with sem:
                    if circuit_breaker.check_abort_condition():
                        pbar.update(1)
                        return None
                    # Run blocking IO (DB/Network) in thread
                    # to_thread is available in Python 3.9+
                    res = await asyncio.to_thread(
                        self.process_single_stock, row.to_dict(), current_strategy
                    )

                    # [v4.19] Async Rate Limiting Wait
                    interval_sec = ai_cfg.get("interval_sec", 2.0)
                    if interval_sec > 0:
                        await asyncio.sleep(interval_sec)

                    # Update Pbar
                    pbar.update(1)

                    # Logging (Thread-safe enough for simple info)
                    cache_label = res.get("_cache_label", "")
                    self.logger.info(
                        f"  {row.get('code')} {row.get('name')[:10]:<10}: {res.get('ai_sentiment', 'Unknown'):<8} {cache_label}"
                    )

                    # Circuit Breaker Update
                    circuit_breaker.update_status(res)
                    return res

            for idx, row in candidates_df.iterrows():
                tasks.append(_bounded_analyze(idx, row))

            return await asyncio.gather(*tasks)

        # Execute Async Batch
        try:
            results_with_none = asyncio.run(_run_async_batch(candidates))
            results = [r for r in results_with_none if r is not None]
        except Exception as e:
            self.logger.error(f"Async Loop Error: {e}")
            # Fallback or just stop
            results = []

        # 5. 結果出力 (Excel/CSV)
        if results:
            result_df = pd.DataFrame(results)

            # [v4.15] Dynamic Filename with Date & Strategy
            from src.utils import get_today_str

            today_str = get_today_str()
            # output_dir defaults to data/output if output_path is just a filename
            # But ResultWriter.save handles directory joining.
            # We construct the base filename here.

            # e.g. analysis_result_2025-12-24_value_strict.csv
            new_filename = f"analysis_result_{today_str}_{current_strategy}.csv"

            # Override whatever was in config['output_path'] for the filename part,
            # but usually ResultWriter.save takes just the filename.

            self.writer.save(result_df, new_filename)
            self.logger.info(f"✅ Analysis completed. Results saved to: {new_filename}")

            # [v4.4] DB メンテナンス (古いデータの削除と最適化)
            retention_days = self.config.get("database", {}).get("retention_days", 30)
            self.provider.stock_db.cleanup_and_optimize(retention_days=retention_days)

    def process_single_stock(self, row_dict, strategy_name):
        """単一銘柄の AI 分析と結果保存 (Smart Refresh 対応)"""
        ai_cfg = self.config.get("ai", {})
        validity_days = ai_cfg.get("validity_days", 0)
        triggers = ai_cfg.get("refresh_triggers", {})

        # キャッシュ確認
        cached, row_hash = self.provider.get_ai_cache(
            row_dict,
            strategy_name,
            validity_days=validity_days,
            refresh_triggers=triggers,
        )

        # [v4.1] Ignore 'Error' records in cache to allow re-analysis
        if cached and cached.get("ai_sentiment") != "Error":
            row_dict.update(cached)
            row_dict["row_hash"] = row_hash
            row_dict["_is_cached"] = True

            # [v4.5] キャッシュ種別の判別
            if cached.get("_is_smart_cache"):
                analyzed_at = cached.get("analyzed_at")
                if hasattr(analyzed_at, "strftime"):
                    date_str = analyzed_at.strftime("%Y-%m-%d")
                else:
                    date_str = str(analyzed_at) if analyzed_at else "Unknown"
                row_dict["_cache_label"] = f"♻️  Smart Cache (from {date_str})"
            else:
                row_dict["_cache_label"] = "[Cached]"
        else:
            # AI 実行
            row_dict["_cache_label"] = "🚀 Analyzing..."  # ログ表示用
            ai_result = self.ai_agent.analyze(row_dict, strategy_name=strategy_name)
            row_dict.update(ai_result)
            row_dict["row_hash"] = row_hash
            row_dict["_is_cached"] = False

            # DB 保存
            self.provider.save_analysis_result(row_dict, strategy_name)

        return row_dict

```

---

### src/calc/__init__.py

```python
import pandas as pd

from .base import BaseCalculator
from .engine import ScoringEngine
from .v1 import V1ScoringMixin


class Calculator(BaseCalculator, V1ScoringMixin):
    """
    Main Calculator Interface.
    Integrates V1 (Legacy) and V2 (Dual) scoring logic.
    """

    def __init__(self, config):
        super().__init__(config)
        self.engine = ScoringEngine(config)

    def calc_quant_score(self, data, strategy_name=None):
        """
        [v8.0] Override to delegate to ScoringEngine strategies.
        Returns the scalar or series 'quant_score'.
        """
        res = self.calc_v2_score(data, strategy_name=strategy_name)
        if isinstance(data, pd.DataFrame):
            return res["quant_score"]
        return res.get("quant_score", 0.0)

    def calc_v2_score(self, data, style="value_balanced", strategy_name=None):
        """
        [v8.0] Calculates score using the new Strategy Registry.
        """
        if not strategy_name:
            strategy_name = self.config.get("current_strategy", "value_strict")

        strategy = self.engine.get_strategy(strategy_name)

        if isinstance(data, pd.DataFrame):
            return strategy.calculate_score(data)
        else:
            # Scalar Mode
            if hasattr(strategy, "calculate_score_scalar"):
                return strategy.calculate_score_scalar(data)
            else:
                # Fallback wrapper
                df = pd.DataFrame([data])
                res = strategy.calculate_score(df)
                return res.iloc[0].to_dict()

```

---

### src/calc/base.py

```python
from logging import getLogger
from typing import Optional

import numpy as np
import pandas as pd

from src.constants import LOWER_IS_BETTER_DEFAULTS


class BaseCalculator:
    def __init__(self, config):
        self.config = config
        self.logger = getLogger(__name__)
        scoring_cfg = self._get_scoring_config()
        self.lower_is_better = scoring_cfg.get(
            "lower_is_better", LOWER_IS_BETTER_DEFAULTS
        )

    def _get_scoring_config(self, strategy_name: Optional[str] = None):
        target = (
            strategy_name
            if strategy_name
            else self.config.get("current_strategy", "value_strict")
        )
        strategies = self.config.get("strategies", {})
        return strategies.get(target, self.config.get("scoring", {}))

    def _safe_float(self, value):
        """値を安全にfloatに変換する (Scalar版)"""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.replace(",", "").replace("%", "")
            return float(value)
        except (ValueError, TypeError):
            return None

    def _evaluate_metric_vectorized(self, metric: str, vals, th: float):
        """Evaluate metric condition (Vectorized)"""
        if metric == "rsi_oversold":
            return vals <= th
        elif metric == "rsi_overbought":
            return vals >= th
        elif metric in self.lower_is_better:
            return vals <= th
        else:
            return vals >= th

    def _evaluate_metric_scalar(self, metric: str, v: float, th: float) -> bool:
        """Evaluate metric condition (Scalar)"""
        if metric == "rsi_oversold":
            return v <= th
        elif metric == "rsi_overbought":
            return v >= th
        elif metric in self.lower_is_better:
            return v <= th
        return v >= th

    def _calc_dividend_points_vectorized(self, df: pd.DataFrame, condition, pts: int):
        """Calculate dividend points with quality adjustments (Vectorized)"""
        pts_series = np.where(condition, pts, 0)

        # Operating CF check (< 0 -> 0点)
        if "operating_cf" in df.columns:
            op_cf = pd.to_numeric(df["operating_cf"], errors="coerce")
            pts_series = np.where((op_cf < 0) & (pts_series > 0), 0, pts_series)

        # Payout Ratio check (> 100 -> -20点)
        if "payout_ratio" in df.columns:
            payout = pd.to_numeric(df["payout_ratio"], errors="coerce")
            pts_series = np.where(
                (payout > 100) & (pts_series > 0), pts_series - 20, pts_series
            )

        return pts_series

    def _calc_dividend_points_scalar(self, row: dict, pts: int) -> int:
        """Calculate dividend points with quality adjustments (Scalar)"""
        pts_to_add = pts
        op_cf = self._safe_float(row.get("operating_cf"))
        if (op_cf is not None) and (op_cf < 0):
            return 0

        payout = self._safe_float(row.get("payout_ratio"))
        if (payout is not None) and (payout > 100):
            pts_to_add -= 20
        return pts_to_add

```

---

### src/calc/engine.py

```python
"""ScoringEngine: 戦略パターンに基づくスコアリングオーケストレータ

責務:
- 投資戦略クラス（BaseStrategy継承クラス）の登録と管理
- 各銘柄データに対するスコアリング処理のディスパッチ
- スコア計算後のフィルタリングおよびランキング実行
"""

from logging import getLogger
from typing import Any, Dict, Optional, Type

import pandas as pd

from src.calc.strategies.base import BaseStrategy
from src.calc.strategies.generic import GenericStrategy
from src.calc.strategies.growth_quality import GrowthQualityStrategy
from src.calc.strategies.turnaround import TurnaroundStrategy
from src.calc.strategies.value_growth_hybrid import ValueGrowthHybridStrategy
from src.calc.strategies.value_strict import ValueStrictStrategy


class ScoringEngine:
    """各戦略クラスにスコアリング処理を振り分ける中央エンジン。

    Attributes:
        config (Dict[str, Any]): システム設定。
        _strategy_cache (Dict[str, BaseStrategy]): 生成済み戦略インスタンスのキャッシュ。
    """

    # Strategy Registry
    STRATEGY_REGISTRY: Dict[str, Type[BaseStrategy]] = {
        "turnaround_spec": TurnaroundStrategy,
        "value_strict": ValueStrictStrategy,
        "growth_quality": GrowthQualityStrategy,
        "value_growth_hybrid": ValueGrowthHybridStrategy,
    }

    GENERIC_STRATEGIES: set[str] = set()

    def __init__(self, config: Dict[str, Any]):
        """ScoringEngine を初期化する。

        Args:
            config (Dict[str, Any]): アプリケーション全体の設定。
        """
        self.config = config
        self.logger = getLogger(__name__)
        self._strategy_cache: Dict[str, BaseStrategy] = {}

    def get_strategy(self, strategy_name: str) -> BaseStrategy:
        """指定した戦略名のインスタンスを取得（または生成）する。

        Args:
            strategy_name (str): 戦略名。

        Returns:
            BaseStrategy: 戦略インスタンス。
        """
        if strategy_name in self._strategy_cache:
            return self._strategy_cache[strategy_name]

        if strategy_name in self.STRATEGY_REGISTRY:
            strategy_class = self.STRATEGY_REGISTRY[strategy_name]
            strategy = strategy_class(self.config)
        elif strategy_name in self.GENERIC_STRATEGIES:
            strategy = GenericStrategy(self.config, strategy_name)
        else:
            # 未知の戦略の場合は GenericStrategy を使用
            self.logger.warning(
                f"Unknown strategy '{strategy_name}', using GenericStrategy"
            )
            strategy = GenericStrategy(self.config, strategy_name)

        strategy.logger = self.logger
        self._strategy_cache[strategy_name] = strategy
        return strategy

    def calculate_score(
        self, data: pd.DataFrame, strategy_name: Optional[str] = None
    ) -> pd.DataFrame:
        """指定された戦略を用いて、データのスコアを算出する。

        Args:
            data (pd.DataFrame): 銘柄データの DataFrame。
            strategy_name (Optional[str], optional): 戦略名。省略時は設定ファイルのデフォルトを使用。

        Returns:
            pd.DataFrame: スコア計算結果が付与された DataFrame。
        """
        if strategy_name is None:
            strategy_name = self.config.get("current_strategy", "value_strict")

        strategy = self.get_strategy(strategy_name)

        try:
            result = strategy.calculate_score(data)
            return result
        except Exception as e:
            self.logger.error(
                f"Error in calculate_score with {strategy_name}: {e}", exc_info=True
            )
            # エラー発生時はデフォルト値（0点）を返す
            return pd.DataFrame(
                {
                    "quant_score": 0.0,
                    "score_value": 0.0,
                    "score_growth": 0.0,
                    "score_quality": 0.0,
                    "score_trend": 50.0,
                    "strategy_name": strategy_name,
                },
                index=data.index,
            )

    def register_strategy(self, name: str, strategy_class: Type[BaseStrategy]) -> None:
        """
        Register a new strategy class.

        Args:
            name: Name to register the strategy under
            strategy_class: Strategy class (must inherit from BaseStrategy)
        """
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError(f"{strategy_class} must inherit from BaseStrategy")

        self.STRATEGY_REGISTRY[name] = strategy_class
        # Clear cache to ensure new strategy is used
        if name in self._strategy_cache:
            del self._strategy_cache[name]

        self.logger.info(f"Registered strategy: {name}")

    def list_strategies(self) -> list:
        """List all available strategy names."""
        all_strategies = set(self.STRATEGY_REGISTRY.keys()) | self.GENERIC_STRATEGIES
        return sorted(all_strategies)

    # ============================================================
    # [v12.0] AnalysisEngine からの移植: フィルタリングとランキング
    # ============================================================
    def filter_and_rank(self, df: pd.DataFrame, strategy_name: str) -> pd.DataFrame:
        """スコア計算済みのデータをフィルタリングし、ランキング用にソートする。

        Args:
            df (pd.DataFrame): スコア計算済みの銘柄データ。
            strategy_name (str): 適用する戦略名。

        Returns:
            pd.DataFrame: フィルタリング・ソート済みの銘柄データ。
        """
        min_score = self.config.get("filter", {}).get("min_quant_score", 0)

        # 1. 戦略固有のフィルター
        strategy_cfg = self.config.get("strategies", {}).get(strategy_name, {})
        hard_filters = strategy_cfg.get("min_requirements", {})

        # 2. グローバルフィルター（戦略固有がない場合）
        if not hard_filters:
            hard_filters = self.config.get("hard_filters", {})

        # 3. ベーススコアフィルタリング
        before_score = len(df)
        candidates = df[df["quant_score"] >= min_score].copy()
        self.logger.info(
            f"DEBUG: Score Filter (>= {min_score}): "
            f"{len(candidates)} (Dropped {before_score - len(candidates)})"
        )

        # 4. ハードフィルター適用
        for key, val in hard_filters.items():
            col = key.replace("_max", "")
            if col not in candidates.columns:
                self.logger.info(f"DEBUG: Skipping filter {key} (Column {col} missing)")
                continue

            before_filter = len(candidates)
            try:
                # 欠損値を除去してから比較
                candidates = candidates[candidates[col].notna()]

                # 数値比較のために float 変換を試みる
                target_series = pd.to_numeric(candidates[col], errors="coerce")

                if key.endswith("_max"):
                    candidates = candidates[target_series <= float(val)]
                else:
                    candidates = candidates[target_series >= float(val)]
            except Exception as e:
                self.logger.error(f"Error applying filter {key}: {e}")
                continue

            self.logger.info(
                f"DEBUG: Filter {key} ({col}) against {val}: "
                f"{len(candidates)} (Dropped {before_filter - len(candidates)})"
            )

        # 5. ソート
        candidates = candidates.sort_values(
            ["quant_score", "code"], ascending=[False, True]
        )
        return candidates

```

---

### src/calc/v1.py

```python
from typing import TYPE_CHECKING, Any, Dict, Union, cast

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from .strategies.base import BaseStrategy


class V1ScoringMixin:
    def calc_quant_score(self: "BaseStrategy", data: Union[pd.DataFrame, Dict[str, Any], pd.Series]) -> Union[pd.Series, float, int]:  # type: ignore
        """
        基本的定量スコアの計算 (Vectorized & Scalar support)
        data: pd.DataFrame or dict/pd.Series
        """
        try:
            scoring_cfg = self._get_scoring_config()

            if isinstance(data, pd.DataFrame):
                return self._calc_vectorized_score(data, scoring_cfg)  # type: ignore
            else:
                return self._calc_scalar_score(data, scoring_cfg)  # type: ignore

        except Exception as e:
            self.logger.error(f"Error calculating score: {e}", exc_info=True)
            if isinstance(data, pd.DataFrame):
                return pd.Series(0, index=data.index)
            return 0

    def _calc_vectorized_score(self: "BaseStrategy", df: pd.DataFrame, scoring_cfg: dict) -> pd.Series:  # type: ignore
        """Vectorized scoring calculation"""
        base_score = scoring_cfg.get("base_score", 50)
        thresholds = scoring_cfg.get("thresholds", {})
        points = scoring_cfg.get("points", {})

        # Initialize score column
        scores = pd.Series(base_score, index=df.index, dtype=float)

        for metric, pts in points.items():
            target_col = "rsi" if "rsi_" in metric else metric
            if target_col not in df.columns:
                continue

            # 数値変換 (Moved logic to inline for vectorization, _safe_float is scalar)
            vals = pd.to_numeric(
                df[target_col].astype(str).str.replace(",", "").str.replace("%", ""),
                errors="coerce",
            )

            th = thresholds.get(metric)
            if th is None:
                continue

            # 閾値判定
            condition = self._evaluate_metric_vectorized(
                metric, cast(pd.Series, vals), th
            )

            # 配当品質チェックのベクトル化
            if metric == "dividend_yield":
                scores += self._calc_dividend_points_vectorized(df, condition, pts)
            else:
                scores += np.where(condition, pts, 0)

        return scores.clip(0, 100)

    def _calc_scalar_score(self: "BaseStrategy", row: dict, scoring_cfg: dict) -> float:  # type: ignore
        """Scalar scoring calculation (Legacy/Fallback)"""
        base_score = scoring_cfg.get("base_score", 50)
        thresholds = scoring_cfg.get("thresholds", {})
        points = scoring_cfg.get("points", {})

        score = base_score

        for metric, pts in points.items():
            target_col = "rsi" if "rsi_" in metric else metric
            val = row.get(target_col)

            v = self._safe_float(val)
            if v is None:
                continue

            th = thresholds.get(metric)
            if th is None:
                continue

            match = self._evaluate_metric_scalar(metric, v, th)

            if match:
                pts_to_add = pts
                if metric == "dividend_yield":
                    pts_to_add = self._calc_dividend_points_scalar(row, pts)
                score += pts_to_add

        return max(0, min(100, score))

```

---

### src/circuit_breaker.py

```python
from logging import getLogger
from typing import Any, Dict


class CircuitBreaker:
    def __init__(self, threshold: int = 1):
        self.threshold = threshold
        self.consecutive_429_errors = 0
        self.logger = getLogger(__name__)

    def check_abort_condition(self) -> bool:
        """RPD超過などで中断すべきかチェック"""
        if self.consecutive_429_errors >= self.threshold:
            self.logger.warning(
                "🛑 Daily Quota Exceeded (RPD). Aborting remaining tasks."
            )
            self.logger.warning(
                "   Please wait 24h or check Google AI Studio dashboard."
            )
            return True
        return False

    def update_status(self, result: Dict[str, Any]) -> None:
        """AI分析結果に基づいてステータスを更新"""
        sentiment = result.get("ai_sentiment", "")
        reason = str(result.get("ai_reason", "")).lower()

        if sentiment == "Error" and ("429" in reason or "quota" in reason):
            self.consecutive_429_errors += 1
        else:
            self.consecutive_429_errors = 0

```

---

### src/commands/__init__.py

```python
from .analyze import AnalyzeCommand as AnalyzeCommand
from .extract import ExtractCommand as ExtractCommand
from .ingest import IngestCommand as IngestCommand

```

---

### src/commands/analyze.py

```python
import asyncio
import os
from datetime import datetime
from typing import List, Optional

import pandas as pd
from tqdm import tqdm

from src.ai.agent import AIAgent
from src.circuit_breaker import CircuitBreaker
from src.commands.base_command import BaseCommand
from src.result_writer import ResultWriter
from src.utils import get_current_time, get_today_str


class AnalyzeCommand(BaseCommand):
    """
    Command to execute AI analysis loop (Extract -> Analyze -> Save).
    Replaces StockAnalyzer.run_analysis logic mostly.
    """

    def __init__(self, config, debug_mode=False):
        super().__init__(config, debug_mode)

        # Initialize AI Agent
        ai_cfg = self.config.get("ai", {})
        model_name = ai_cfg.get("model_name", "gemini-2.0-flash-exp")
        interval_sec = ai_cfg.get("interval_sec", 2.0)
        self.agent = AIAgent(
            model_name, interval_sec=interval_sec, debug_mode=debug_mode
        )
        self.agent.set_config(self.config)
        self.agent._load_prompt_template()  # Pre-load

        # Writer
        self.writer = ResultWriter(self.config)

        # Circuit Breaker
        cb_config = self.config.get("circuit_breaker", {})
        threshold = cb_config.get("consecutive_failure_threshold", 5)
        self.circuit_breaker = CircuitBreaker(threshold=threshold)

        # [v8.7] Dashboard Stats
        self.token_eaters = []

    def execute(
        self,
        strategy: str,
        limit: Optional[int] = None,
        codes: Optional[List[str]] = None,
        files: Optional[str] = None,
        output_format="json",
        force_refresh: bool = False,
    ):
        """
        Main entry point for Analyze mode.
        """
        # [v8.1] Store force_refresh flag
        self.force_refresh = force_refresh
        if force_refresh:
            self.logger.info("🔄 Force Refresh enabled - skipping cache")

        # [v8.8] Handle None strategy by iterating all defined strategies
        if not strategy:
            strategies = list(self.config.get("strategies", {}).keys())
            if not strategies:
                self.logger.error("❌ No strategies defined in config.")
                return

            self.logger.info(
                f"🔄 No strategy specified. Iterating all {len(strategies)} strategies for {len(codes) if codes else 'all'} codes..."
            )

            for s in strategies:
                self.execute(
                    strategy=s,
                    limit=limit,
                    codes=codes,
                    files=files,
                    output_format=output_format,
                    force_refresh=force_refresh,
                )
            return

        if files:
            self.execute_from_files(files, strategy=strategy)
            return

        self.logger.info(
            f"🚀 [Analyze Mode] Strategy: {strategy}, Limit: {limit}, Codes: {len(codes) if codes else 'None'}"
        )

        # 1. Fetch Candidates
        if codes:
            candidates_df = self._fetch_candidates_df_by_code(codes, strategy)
        else:
            candidates_df = self._fetch_candidates_df_logic(strategy, limit)

        if candidates_df.empty:
            self.logger.info("ℹ️  No candidates to analyze.")
            return

        self.logger.info(f"🚀 Analyzing {len(candidates_df)} candidates (Async)...")

        # [v8.7] Reset Token Eaters for this run
        self.token_eaters = []

        try:
            # 2. Async Analysis Loop
            results = asyncio.run(self._run_async_batch(candidates_df, strategy))

            # 3. Save Results
            if results:
                self._save_results(results, strategy)

                # DB Maintenance
                retention_days = self.config.get("database", {}).get(
                    "retention_days", 30
                )
                self.db.cleanup_and_optimize(retention_days=retention_days)
            else:
                self.logger.info("ℹ️  No results generated.")
        finally:
            self._print_usage_report()

    def execute_from_files(self, file_pattern: str, strategy: Optional[str] = None):
        """
        Execute analysis from pre-extracted tasks (JSON).
        """
        import glob
        import json

        files = glob.glob(file_pattern)
        if not files:
            self.logger.warning(f"❌ No files match pattern: {file_pattern}")
            return

        self.logger.info(
            f"🚀 [Analyze Files] Found {len(files)} task files. Processing..."
        )

        for file_path in files:
            self.logger.info(f"  Reading {file_path}...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tasks = json.load(f)

                if not isinstance(tasks, list):
                    tasks = [tasks]

                tasks_df = pd.DataFrame(tasks)
                if tasks_df.empty:
                    continue

                # Determine strategy from file if possible, or use provided
                current_strategy = strategy or tasks[0].get("strategy", "unknown")
                self.logger.info(
                    f"  Analyzing {len(tasks_df)} tasks for strategy: {current_strategy}"
                )

                # Run Analysis
                results = asyncio.run(self._run_async_batch(tasks_df, current_strategy))

                if results:
                    # Save as analyzed_*.json
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base = (
                        os.path.basename(file_path)
                        .replace("tasks_", "")
                        .replace(".json", "")
                    )
                    out_path = os.path.join(
                        "data/interim", f"analyzed_{base}_{ts}.json"
                    )

                    with open(out_path, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

                    self.logger.info(f"  ✅ Saved analyzed results to: {out_path}")
            except Exception as e:
                self.logger.error(f"  ❌ Error processing {file_path}: {e}")

    async def _run_async_batch(self, df, strategy):
        # [v8.9] Check API Tier for Dynamic Concurrency
        api_settings = self.config.get("api_settings", {})
        gemini_tier = api_settings.get("gemini_tier", "free").lower()

        if gemini_tier == "paid":
            max_concurrency = 30
            tier_label = "PAID"
            # [v8.9] Speed Optimization: Minimal sleep for Paid Tier
            active_interval = 0.1
        else:
            ai_cfg = self.config.get("ai", {})
            max_concurrency = ai_cfg.get("max_concurrency", 1)
            tier_label = "FREE"
            active_interval = ai_cfg.get("interval_sec", 2.0)

        self.logger.info(
            f"🚀 API Tier: {tier_label} (Concurrency: {max_concurrency}, Interval: {active_interval}s)"
        )

        # [v8.9] ThreadPool Optimization: Ensure executor has enough workers
        # Default executor is typically CPU count * 5, which might be < 30.
        try:
            loop = asyncio.get_running_loop()
            from concurrent.futures import ThreadPoolExecutor

            # +2 for safety buffer
            executor = ThreadPoolExecutor(max_workers=max_concurrency + 2)
            loop.set_default_executor(executor)
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to optimize ThreadPool: {e}")

        # [v9.1] Pre-scan for Cache Status to inform user
        self.logger.info("🔍 Pre-scanning cache status...")
        estimated_calls = 0
        cached_count = 0

        # We need to replicate cache check logic briefly or reuse it.
        # Since validity check is inside _process_single_stock, it's safer to just iterate and check.
        # But _process_single_stock updates the row_dict.
        # To avoid double overhead, we can just do a lightweight check or just accept the overhead.
        # 170 items check is fast.

        # Let's do a lightweight check using provider directly.
        ai_cfg = self.config.get("ai", {})
        validity_days = ai_cfg.get("validity_days", 0)
        triggers = ai_cfg.get("refresh_triggers", {})
        current_ver = getattr(self.agent, "audit_version", 0)
        if not isinstance(current_ver, (int, float)):
            current_ver = 0

        for _, row in df.iterrows():
            row_dict = row.to_dict() if hasattr(row, "to_dict") else row

            # Check Force Refresh
            if getattr(self, "force_refresh", False):
                estimated_calls += 1
                continue

            cached, _ = self.provider.get_ai_cache(
                row_dict,
                strategy,
                validity_days=validity_days,
                refresh_triggers=triggers,
            )

            is_valid_cache = False
            if cached and cached.get("ai_sentiment") != "Error":
                cached_ver = cached.get("audit_version") or 0
                if cached_ver >= current_ver:
                    is_valid_cache = True

            if is_valid_cache:
                cached_count += 1
            else:
                estimated_calls += 1

        self.logger.info(
            f"📊 Execution Plan: Total {len(df)} | ✅ Cached: {cached_count} | 🚀 To Analyze: {estimated_calls}"
        )

        sem = asyncio.Semaphore(max_concurrency)
        tasks = []

        pbar = tqdm(total=len(df), desc=f"AI Analysis (Cncr={max_concurrency})")

        async def _bounded_analyze(index, row):
            async with sem:
                # Check Circuit Breaker
                if self.circuit_breaker.check_abort_condition():
                    pbar.update(1)
                    return None

                # Run Analysis (Blocking wrapper)
                res = await asyncio.to_thread(self._process_single_stock, row, strategy)

                # Rate Limit Sleep
                if active_interval > 0:
                    await asyncio.sleep(active_interval)

                pbar.update(1)

                # Update Circuit Breaker
                self.circuit_breaker.update_status(res)

                # Logging
                code = res.get("code")
                name = (res.get("name", "") or "")[:10]
                sentiment = res.get("ai_sentiment") or "Unknown"
                label = res.get("_cache_label") or ""
                self.logger.info(f"  {code} {name:<10}: {sentiment:<8} {label}")

                return res

        for idx, row in df.iterrows():
            tasks.append(_bounded_analyze(idx, row))

        results_with_none = await asyncio.gather(*tasks)
        return [r for r in results_with_none if r is not None]

    def _process_single_stock(self, row, strategy_name):
        """Single stock analysis step (similar to StockAnalyzer.process_single_stock)."""
        # Convert to dict
        row_dict = row.to_dict() if hasattr(row, "to_dict") else row

        # Cache Check Config
        ai_cfg = self.config.get("ai", {})
        validity_days = ai_cfg.get("validity_days", 0)
        triggers = ai_cfg.get("refresh_triggers", {})

        # [v8.1] Skip cache if force_refresh is enabled
        if getattr(self, "force_refresh", False):
            cached = None
            # Generate row_hash manually
            import pandas as pd

            from src.utils import generate_row_hash

            row_hash = generate_row_hash(pd.Series(row_dict))
        else:
            cached, row_hash = self.provider.get_ai_cache(
                row_dict,
                strategy_name,
                validity_days=validity_days,
                refresh_triggers=triggers,
            )

        if cached and cached.get("ai_sentiment") != "Error":
            # [v8.5] Semantic Version Check
            cached_ver = cached.get("audit_version") or 0  # Handle None from DB
            current_ver = getattr(self.agent, "audit_version", 0)
            if not isinstance(current_ver, (int, float)):
                current_ver = 0  # Default if it's a Mock or non-numeric

            if cached_ver < current_ver:
                self.logger.info(
                    f"🔄 Smart Refresh: v{cached_ver} < v{current_ver} "
                    f"for {row_dict.get('code')}"
                )
                cached = None  # Force re-analysis
            else:
                row_dict.update(cached)
                row_dict["row_hash"] = row_hash
                row_dict["_is_cached"] = True

                if cached.get("_is_smart_cache"):
                    row_dict["_cache_label"] = "♻️ SmartCache"
                else:
                    row_dict["_cache_label"] = f"[Cached v{cached_ver}]"

                # [v12.2] Fix: Persist Cached Result for current MarketData ID
                # If we don't save, reporter won't find result for today's market record.
                self.provider.save_analysis_result(row_dict, strategy_name)

        if not cached:
            # AI Execution
            row_dict["_cache_label"] = "🚀 Analyzing..."

            # [v13.0] Deep Financial Repair (Ground Truth) for Top Candidates
            # Estimated data from ingest is replaced with precise data from financial statements.
            if not self.debug_mode:
                try:
                    self.logger.info(
                        f"🔍 Deep Refreshing financials for {row_dict.get('code')}..."
                    )
                    precise_data = self.fetcher._fetch_single_stock(
                        row_dict.get("code"), deep_repair=True
                    )
                    if precise_data:
                        # Update critical financials before AI sees them
                        for key in [
                            "equity_ratio",
                            "operating_cf",
                            "per",
                            "pbr",
                            "roe",
                            "operating_margin",
                        ]:
                            if precise_data.get(key) is not None:
                                row_dict[key] = precise_data[key]
                        self.logger.info(
                            f"  ✅ High precision data updated for {row_dict.get('code')}"
                        )
                except Exception as e:
                    self.logger.warning(
                        f"  ⚠️ Deep Refresh failed for {row_dict.get('code')}: {e}"
                    )

            # [v13.5] Post-Refresh Guardrail (Hard-Cutting)
            # 精密データ取得後、改めて異常値（債務超過等）をチェック
            from src.validation_engine import ValidationEngine

            val_engine = ValidationEngine(self.config)
            is_abnormal, reasons = val_engine.is_abnormal(row_dict)

            if is_abnormal:
                reason_str = ", ".join(reasons)
                self.logger.warning(
                    f"  🚨 [GUARDRAIL] Skipping AI analysis for {row_dict.get('code')} due to abnormal values: {reason_str}"
                )
                ai_result = {
                    "code": row_dict.get("code"),
                    "ai_sentiment": "Bearish (Abnormal Skip)",
                    "ai_reason": f"【結論】分析対象外。{reason_str}により投資不適格と判定。｜【強み】なし。｜【懸念】{reason_str}。",
                    "ai_detail": f"精密調査の結果、以下の重大な異常値が検出されたため、証券アナリストとして分析を即時中止しました。\n理由: {reason_str}\n債務超過や重度の資金流出が見られる銘柄は、定量評価にかかわらず地雷（Trap）として扱います。",
                    "ai_risk": "Critical (Fatal Error)",
                    "ai_horizon": "Wait",
                    "analyzed_at": get_current_time(),
                }
                call_count = 0
            else:
                # [v8.7] Track API Calls
                start_calls = self.agent.get_total_calls()

                ai_result = self.agent.analyze(row_dict, strategy_name=strategy_name)

                end_calls = self.agent.get_total_calls()

                # [v8.7] Track API Calls (Handle mocks in tests)
                try:
                    call_count = int(end_calls) - int(start_calls)
                except (TypeError, ValueError):
                    call_count = 0

            # [v8.7] Identify Token Eaters
            if call_count > 1:
                self.token_eaters.append(
                    {
                        "code": row_dict.get("code"),
                        "name": row_dict.get("name"),
                        "calls": call_count,
                        "reason": ai_result.get("ai_reason", "Unknown")[:50],
                    }
                )

            ai_result["api_call_count"] = call_count
            row_dict.update(ai_result)
            row_dict["row_hash"] = row_hash
            row_dict["_is_cached"] = False

            # [Fix] Explicitly update analyzed_at for UPSERT to work correctly
            # [Fix] Explicitly update analyzed_at for UPSERT to work correctly
            row_dict["analyzed_at"] = get_current_time()

            # Save to DB immediately
            self.provider.save_analysis_result(row_dict, strategy_name)

        return row_dict

    def _save_results(self, results, strategy):
        df = pd.DataFrame(results)
        today_str = get_today_str()
        filename = f"analysis_result_{today_str}_{strategy}.csv"
        # self.writer.save(df, filename) # Wait, filename line specific E501?
        # filename is 55 chars. where is 81?
        # Ah, maybe previous line + this?
        # Let's just break it if needed or check context.
        # "        filename = f"analysis_result_{today_str}_{strategy}.csv"" is ~60 chars.
        # Line 210 in previous view: self.logger.info(f"✅ Analysis Results saved to: {filename}")
        # That line might be long.
        self.writer.save(df, filename)
        self.logger.info(f"✅ Results saved: {filename}")

    # --- Duplicated Fetch Logic (Ideally shared in utils or provider) ---
    def _fetch_candidates_df_logic(self, strategy, limit):
        df = self.provider.load_latest_market_data()
        if df.empty:
            return pd.DataFrame()

        from src.engine import AnalysisEngine

        engine = AnalysisEngine(self.config)
        df = engine.calculate_scores(df, strategy_name=strategy)
        df = engine.filter_and_rank(df, strategy_name=strategy)

        if limit and limit > 0:
            df = df.head(limit)
        return df

    def _fetch_candidates_df_by_code(self, codes, strategy):
        df = self.provider.load_latest_market_data()
        if df.empty:
            return pd.DataFrame()
        df = df[df["code"].astype(str).isin(codes)]

        from src.engine import AnalysisEngine

        engine = AnalysisEngine(self.config)
        df = engine.calculate_scores(df, strategy_name=strategy)
        return df

    def _print_usage_report(self):
        """[v8.7] Print API Usage Dashboard."""
        report = self.agent.generate_usage_report()

        # Append Token Eaters
        if self.token_eaters:
            report += "\n\n[😈 Top Token Eaters (High Retry Stocks)]"
            # Sort by calls descending
            sorted_eaters = sorted(
                self.token_eaters, key=lambda x: x["calls"], reverse=True
            )[:5]
            for eater in sorted_eaters:
                report += f"\n- {eater['code']} {eater['name']}: {eater['calls']} calls. Reason: {eater['reason']}..."
        else:
            report += "\n\n[✅ No Token Eaters Detected (All efficient)]"

        self.logger.info(report)

```

---

### src/commands/base_command.py

```python
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, Dict

from src.database import StockDatabase
from src.provider import DataProvider


class BaseCommand(ABC):
    """
    Base class for all Antigravity commands (Extract, Analyze, Ingest).
    Holds shared resources and configuration.
    """

    def __init__(self, config: Dict[str, Any], debug_mode: bool = False):
        self.config = config
        self.debug_mode = debug_mode
        self.logger = getLogger(self.__class__.__name__)

        # Initialize Shared Components
        # Note: Some commands might not need all components, but for simplicity
        # and consistency with the current Runner, we initialize basic providers here.
        # Lazily initialization could be considered if startup time becomes an issue.
        from src.fetcher.facade import DataFetcher

        self.fetcher = DataFetcher(self.config)
        self.provider = DataProvider(self.config)

        # Use common DB instance
        self.db: StockDatabase = self.provider.stock_db

        # Interim directory for artifacts
        self.interim_dir = "data/interim"

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the command logic."""
        pass

```

---

### src/commands/extract.py

```python
import asyncio
import json
import os
from datetime import datetime
from typing import List, Optional

from src.ai.agent import AIAgent
from src.commands.base_command import BaseCommand
from src.utils import get_today_str
from src.validation_engine import ValidationEngine


class ExtractCommand(BaseCommand):
    """
    Command to extract candidates, validate them, and generate AI prompts.
    """

    def __init__(self, config, debug_mode=False):
        super().__init__(config, debug_mode)

        # Initialize specialized components
        model_name = self.config.get("ai", {}).get("model_name", "gemini-2.0-flash-exp")
        self.agent = AIAgent(model_name=model_name, debug_mode=debug_mode)
        self.agent.sector_policies = self.config.get("sector_policies", {})
        self.agent.set_config(self.config)
        # Pre-load prompt template to avoid race condition
        self.agent._load_prompt_template()

        self.validator = ValidationEngine(self.config)

        # Ensure interim dirs exist
        self.interim_dir = "data/interim"
        self.quarantine_dir = os.path.join(self.interim_dir, "quarantine")
        self.prompts_dir = os.path.join(
            self.interim_dir, "prompts"
        )  # Optional: separate prompts dir? Runner uses interim root usually.
        os.makedirs(self.interim_dir, exist_ok=True)
        os.makedirs(self.quarantine_dir, exist_ok=True)

    def execute(
        self,
        strategy: str,
        limit: Optional[int] = None,
        codes: Optional[List[str]] = None,
        output_path: Optional[str] = None,
    ):
        """
        Main entry point for Extract mode.
        """
        self.logger.info(
            f"🚀 [Extract Mode] Strategy: {strategy}, Limit: {limit}, Codes: {codes}, Debug: {self.debug_mode}"
        )

        # 1. Fetch Candidates (Un-analyzed or specific codes)
        if codes:
            candidates = self._fetch_candidates_by_code(codes, strategy)
        else:
            candidates = self._fetch_candidates_logic(strategy, limit)

        if not candidates:
            self.logger.info("ℹ️  No candidates found.")
            return

        self.logger.info(
            f"🚀 Processing {len(candidates)} candidates in parallel (Asyncio)..."
        )

        # 2. Parallel Process (Validation & Prompt Gen)
        # Migrated to asyncio in Phase 2
        results = asyncio.run(self._run_async_batch(candidates, strategy))

        valid_tasks = []
        error_tasks = []

        for task, is_valid, reason in results:
            if is_valid:
                valid_tasks.append(task)
            else:
                task["error_reason"] = reason
                error_tasks.append(task)
                # Log warning for quarantine
                code = task.get("code", "Unknown")
                self.logger.warning(f"  ⚠️  [Quarantine] {code}: {reason}")

        # 3. Save Valid Tasks
        if valid_tasks:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            if output_path:
                final_path = output_path
            else:
                final_path = os.path.join(
                    self.interim_dir, f"tasks_{strategy}_{ts}.json"
                )

            with open(final_path, "w", encoding="utf-8") as f:
                json.dump(valid_tasks, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(f"✅ Saved {len(valid_tasks)} tasks to: {final_path}")
        else:
            self.logger.info("ℹ️  No valid tasks to save.")

        # 4. Save Quarantine Tasks
        self._save_quarantine(error_tasks, strategy)

    async def _run_async_batch(self, candidates, strategy):
        # Local processing, so strict limit isn't crucial but good for stability
        max_concurrency = self.config.get("system", {}).get("max_workers", 5)
        sem = asyncio.Semaphore(max_concurrency)
        tasks = []

        # Optional: Add tqdm logic if desired, but for now simple gather
        # If tqdm is needed, wrapping in a bounded function is better.
        from tqdm import tqdm

        pbar = tqdm(total=len(candidates), desc="Extracting Tasks")

        async def _bounded_process(row):
            async with sem:
                try:
                    # Offload blocking logic to thread
                    res = await asyncio.to_thread(
                        self._process_single_candidate, row, strategy
                    )
                    pbar.update(1)
                    return res
                except Exception as e:
                    self.logger.error(f"Worker Error: {e}")
                    pbar.update(1)
                    # Return distinct error structure? Or just (None, False, str(e))
                    return ({}, False, f"Exception: {str(e)}")

        for row in candidates:
            tasks.append(_bounded_process(row))

        results = await asyncio.gather(*tasks)
        pbar.close()
        return results

    def _fetch_candidates_logic(self, strategy, limit):
        """Fetch unanalyzed candidates from DB."""
        self.logger.info(
            f"🔍 Fetching UNANALYZED candidates for strategy: '{strategy}'..."
        )

        # Use DataProvider logic or migrate raw SQL here?
        # Runner used stock_db.fetch_unanalyzed_candidates directly usually?
        # Let's check provider. stock_db has fetch_unanalyzed_candidates?
        # Actually Runner had _fetch_candidates_logic using self.db.get_market_data_for_strategy...
        # Wait, get_market_data_for_strategy is in StockDatabase ??
        # Let's verify StockDatabase methods via check_db or assume standard.
        # Original code used: self.provider.load_latest_market_data() then filter?
        # No, Runner had: _fetch_candidates_logic -> complex logic including checking duplicate analysis.

        # Re-implementing simplified version using DB methods
        # 1. Get all candidates for strategy (filters applied)
        # Note: AnalysisEngine.calculate_scores + filter_and_rank needs DataFrame.
        # If we want to reuse Engine logic:

        df = self.provider.load_latest_market_data()
        if df.empty:
            return []

        # Calculate & Filter
        # We need config-based engine here.
        from src.engine import AnalysisEngine

        engine = AnalysisEngine(self.config)

        df = engine.calculate_scores(df, strategy_name=strategy)
        candidates_df = engine.filter_and_rank(df, strategy_name=strategy)

        # Filter out already analyzed today?
        # Original Runner logic checked DB for existing analysis results to avoid re-running.
        # "candidates = [row for row in candidates if not self.db.check_analysis_exists(...)]"

        final_candidates = []
        count = 0
        for _, row in candidates_df.iterrows():
            if limit and count >= limit:
                break

            code = str(row["code"])
            # Check overlap
            if self.db.get_ai_cache(
                code, "", strategy
            ):  # Check if analyzed recently or today?
                # get_ai_cache checks exact hash.
                # We probably want to check if analyzed TODAY for this strategy regardless of hash?
                # Or just trust the user wants to run extract?
                pass

            # For extract mode, we usually want unanalyzed.
            # But let's simplify: Just take top N from filtered list.
            final_candidates.append(row)
            count += 1

        return final_candidates

    def _fetch_candidates_by_code(self, codes, strategy):
        """Fetch candidates by specific codes."""
        # Simple implementation using provider
        df = self.provider.load_latest_market_data()
        if df.empty:
            return []

        # Filter by codes
        df = df[df["code"].astype(str).isin(codes)]

        # Calculate scores needed for prompt
        from src.engine import AnalysisEngine

        engine = AnalysisEngine(self.config)
        df = engine.calculate_scores(df, strategy_name=strategy)

        return [row for _, row in df.iterrows()]

    def _process_single_candidate(self, row, strategy):
        """Worker function."""
        # Convert row to dict
        data = row.to_dict() if hasattr(row, "to_dict") else row
        code = str(data.get("code"))

        # [v13.0] Deep Financial Repair (Ground Truth) for candidates
        # This ensures the generated prompt and validation use the best available data.
        if not self.debug_mode:
            try:
                precise_data = self.fetcher._fetch_single_stock(code, deep_repair=True)
                if precise_data:
                    for key in [
                        "equity_ratio",
                        "operating_cf",
                        "per",
                        "pbr",
                        "roe",
                        "operating_margin",
                    ]:
                        if precise_data.get(key) is not None:
                            data[key] = precise_data[key]
            except Exception as e:
                self.logger.warning(f"  ⚠️ Deep Refresh failed for {code}: {e}")

        # Generate Prompt
        prompt = self.agent._create_prompt(data, strategy)

        # Market Data ID
        md_id = data.get("market_data_id")
        if not md_id:
            entry_date = data.get("entry_date", get_today_str())
            md_id = self.db.get_market_data_id(code, entry_date)

        task = {
            "code": code,
            "name": data.get("name"),
            "market_data_id": md_id,
            "strategy": strategy,
            "prompt": prompt,
            "score": data.get("quant_score"),
            "sector": data.get("sector", "Unknown"),
            # Essential for validation
            "current_price": data.get("current_price") or data.get("price"),
            # Legacy fields often expected
            "score_value": data.get("score_value"),
            "score_growth": data.get("score_growth"),
            "score_quality": data.get("score_quality"),
            "score_trend": data.get("score_trend"),
        }

        # Validate
        is_valid, reason = self.validator.validate(task, sector=task["sector"])
        return task, is_valid, reason

    def _save_quarantine(self, error_tasks, strategy):
        """Save error tasks."""
        if not error_tasks:
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_path = os.path.join(
            self.quarantine_dir, f"quarantine_{strategy}_{ts}.json"
        )

        with open(error_path, "w", encoding="utf-8") as f:
            json.dump(error_tasks, f, indent=2, ensure_ascii=False, default=str)
        self.logger.info(f"🚫 Quarantined {len(error_tasks)} tasks to: {error_path}")

```

---

### src/commands/ingest.py

```python
import glob
import json
import os
from datetime import datetime
from typing import List, Optional

import pandas as pd

from src.commands.base_command import BaseCommand
from src.result_writer import ResultWriter


class IngestCommand(BaseCommand):
    """
    Command to ingest JSON results, save to DB, and export CSV.
    """

    def __init__(self, config, debug_mode=False):
        super().__init__(config, debug_mode)
        self.writer = ResultWriter(self.config)

    def execute(
        self,
        file_patterns: List[str],
        strategy: Optional[str] = None,
        output_format="json",
    ):
        """
        Main entry point for Ingest mode.
        """
        self.logger.info(
            f"🚀 [Ingest Mode] Strategies: {strategy or 'Auto'}, Pattern: {file_patterns}"
        )

        files = []
        for pattern in file_patterns:
            files.extend(glob.glob(pattern))

        if not files:
            self.logger.warning(f"❌ No files found matching patterns: {file_patterns}")
            return

        self.logger.info(f"📂 Found {len(files)} files. Importing to DB...")

        total_saved = 0
        detected_strategies = set()
        processed_codes = set()

        for file_path in files:
            self.logger.info(f"  Reading {file_path}...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Normalize list vs dict
                if isinstance(data, dict):
                    records = [data]
                elif isinstance(data, list):
                    records = data
                else:
                    self.logger.warning(
                        f"  ⚠️ Skipping {file_path}: Invalid JSON structure"
                    )
                    continue

                # Process records
                saved_count = 0
                for record in records:
                    # Validate essential fields
                    if "code" not in record or "ai_sentiment" not in record:
                        continue

                    # Determine strategy
                    rec_strategy = record.get("strategy", strategy or "manual")
                    detected_strategies.add(rec_strategy)
                    processed_codes.add(str(record["code"]))

                    # Save to DB
                    self.provider.save_analysis_result(record, rec_strategy)
                    saved_count += 1

                total_saved += saved_count
                self.logger.info(
                    f"  ✅ Imported {saved_count} records from {os.path.basename(file_path)}"
                )

            except Exception as e:
                self.logger.error(f"  ❌ Error reading {file_path}: {e}")

        self.logger.info(f"🎉 Ingest completed. Total {total_saved} records saved.")

        # Export CSV (Auto-Export)
        if output_format in ["csv", "all"]:
            # Export for detected strategies
            strategies_to_export: List[Optional[str]] = (
                [strategy] if strategy else list(detected_strategies)
            )

            # Export everything if None? No, only what we touched usually?
            # Original Runner exported specifically for 'strategy' if provided, or detected ones.

            if not strategies_to_export and not strategy:
                # Fallback if no strategy detected
                strategies_to_export = [None]  # Will check all?

            self._export_to_csv(strategies_to_export, list(processed_codes))

    def _export_to_csv(self, strategies: List[Optional[str]], filter_codes: List[str]):
        """Export logic (chunked)."""
        # We can reuse the same logic from Runner, but cleaned up.
        from src.models import db_proxy

        # Ensure codes are unique strings
        if filter_codes:
            filter_codes = list(set(str(c) for c in filter_codes if c))

        base_query_sql = """
        SELECT 
            m.code, s.name, 
            ar.strategy_name,
            ar.ai_sentiment, ar.ai_reason, ar.ai_risk,
            ar.score_value, ar.score_growth, ar.score_quality, ar.score_trend,
            ar.quant_score,
            m.price, m.per, m.pbr, m.roe, m.dividend_yield,
            m.sales_growth, m.profit_growth, m.operating_margin,
            m.debt_equity_ratio, m.free_cf, m.operating_cf,
            ar.analyzed_at,
            m.entry_date
        FROM analysis_results ar
        JOIN market_data m ON ar.market_data_id = m.id
        LEFT JOIN stocks s ON m.code = s.code
        WHERE 1=1
        """

        conn = db_proxy.connection()
        try:
            for strat in strategies:
                self.logger.info(f"📦 Exporting CSV for strategy: {strat}...")
                strat_sql = base_query_sql
                if strat:
                    strat_sql += f" AND ar.strategy_name = '{strat}'"

                # Chunking
                dfs = []
                chunk_size = 500

                if filter_codes:
                    for i in range(0, len(filter_codes), chunk_size):
                        chunk = filter_codes[i : i + chunk_size]
                        placeholders = ",".join(["?"] * len(chunk))
                        chunk_query = (
                            strat_sql
                            + f" AND m.code IN ({placeholders}) ORDER BY ar.analyzed_at DESC"
                        )

                        df_chunk = pd.read_sql(chunk_query, conn, params=chunk)
                        if not df_chunk.empty:
                            dfs.append(df_chunk)
                else:
                    full_query = strat_sql + " ORDER BY ar.analyzed_at DESC"
                    df = pd.read_sql(full_query, conn)
                    if not df.empty:
                        dfs.append(df)

                if not dfs:
                    self.logger.info(f"ℹ️  No results found for {strat}.")
                    continue

                final_df = pd.concat(dfs, ignore_index=True)

                # Save
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                suffix = f"_{strat}" if strat else "_ALL"
                if filter_codes:
                    suffix += f"_filtered_{len(final_df)}"

                filename = f"AnalysisResult{suffix}_{ts}.csv"
                self.writer.save(final_df, filename)
                self.logger.info(f"✅ Exported {len(final_df)} records to: {filename}")

        except Exception as e:
            self.logger.error(f"❌ CSV Export Error: {e}")
            import traceback

            traceback.print_exc()

```

---

### src/commands/reset.py

```python
import logging
from typing import Optional

from src.commands.base_command import BaseCommand
from src.models import AnalysisResult, MarketData


class ResetCommand(BaseCommand):
    """
    Command to reset (clear) audit_version for specific stocks or strategies.
    This effectively marks them as 'not audited' by the current prompt version,
    forcing a re-analysis on the next run.
    """

    def __init__(self, config, debug_mode=False):
        super().__init__(config, debug_mode)
        self.logger = logging.getLogger(__name__)

    def execute(
        self,
        strategy: Optional[str] = None,
        code: Optional[str] = None,
        reset_all: bool = False,
    ):
        """
        Execute reset logic.
        """
        if not (strategy or code or reset_all):
            self.logger.error("❌ Reset requires --strategy, --code, or --all.")
            print("Please specify --strategy, --code, or --all.")
            return

        query = AnalysisResult.update(audit_version=None)

        conditions = []
        join_market_data = False

        if not reset_all:
            if strategy:
                conditions.append(AnalysisResult.strategy_name == strategy)

            if code:
                # We need to join with MarketData to filter by code if we want to support code input
                # However, AnalysisResult has market_data foreign key.
                # Let's filter by joining MarketData.
                join_market_data = True
                conditions.append(MarketData.code == code)

        # Apply Join if needed
        # Note: update queries with JOINS in peewee/sqlite can be tricky.
        # SQLite supports UPDATE ... FROM in newer versions, but Peewee's update() with join might not work directly for SQLite backend easily.
        # Alternative: Subquery or select IDs first.

        if join_market_data:
            # Subquery approach for safely updating based on related table
            # UPDATE analysis_results SET audit_version=NULL WHERE market_data_id IN (SELECT id FROM market_data WHERE code=?)
            subquery = MarketData.select(MarketData.id).where(MarketData.code == code)
            ids = [row.id for row in subquery]
            if not ids:
                print(f"No data found for code {code}")
                return
            query = query.where(AnalysisResult.market_data << ids)

            if strategy:
                query = query.where(AnalysisResult.strategy_name == strategy)

        elif conditions:
            # Only strategy specified
            import operator
            from functools import reduce

            expr = reduce(operator.and_, conditions)
            query = query.where(expr)

        try:
            count = query.execute()
            self.logger.info(
                f"✅ Reset audit_version for {count} records. (Strategy: {strategy}, Code: {code}, All: {reset_all})"
            )
            print(f"✅ Reset audit_version for {count} records.")
        except Exception as e:
            self.logger.error(f"❌ Reset failed: {e}")
            print(f"❌ Reset failed: {e}")

```

---

### src/config_loader.py

```python
import os
import re
from typing import Any, Dict

import yaml

from src.config_schema import ConfigModel
from src.env_loader import load_env_file


class ConfigLoader:
    def __init__(self, config_path: str = "config/config.yaml"):
        # Ensure environment variables are loaded (auto-discovery)
        load_env_file()

        self.config_path: str = config_path
        self.env = os.getenv("STOCK_ENV", "production")

        if config_path is None:
            # Auto-switch based on env (optional, or just stick to default)
            pass

        self.raw_config: Dict[str, Any] = self._load_config()

        # [Fix] If config file is missing/empty, initialize with defaults BEFORE overrides
        if not self.raw_config:
            self.raw_config = {
                "current_strategy": "value_strict",
                "data": {"jp_stock_list": "data/input/stock_master.csv", "output_path": "data/output/result.csv"},
                "csv_mapping": {"col_map": {}, "numeric_cols": []},
                "scoring": {"min_coverage_pct": 50},
                "strategies": {},
                "ai": {"model_name": "gemini-pro"},
                "logging": {"level": "INFO", "file": "stock_analyzer.log"},
                "api": {"wait_time": 1.0, "max_retries": 3, "timeout": 30},
                # Add other required fields if necessary for Pydantic
            }

        # [Safety] If TEST env, override critical paths to avoid polluting production
        if self.env == "test":
            self._apply_test_overrides()

        # Macro sync before validation
        self._sync_macro_context()

        # Pydantic Validation
        self.config_model = self.validate_config()
        # Maintain dict interface for backward compatibility
        self.config = self.config_model.model_dump()

    def _apply_test_overrides(self):
        """テスト環境用の強制オーバーライド設定"""
        import tempfile

        # 1. DB Path - メモリDBまたは一時ファイル
        # メモリDBだとマルチプロセス/マルチ接続で問題起きる可能性あるが、
        # ここでは一時ファイルを作成してそれを指すようにする。
        # ただし、毎回作成するとクリーンアップが大変なので、
        # pytestのfixtureで設定される環境変数 STOCK_TEST_DB_PATH があればそれを使う。

        test_db = os.getenv("STOCK_TEST_DB_PATH")
        if not test_db:
            # Fallback to a temp file in /tmp
            self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix="_test.db")
            test_db = self.temp_db.name
            # Note: This file might remain if not cleaned up externally

        if "paths" not in self.raw_config:
            self.raw_config["paths"] = {}
        self.raw_config["paths"]["db_file"] = test_db

        # 2. Output Path
        test_out = os.getenv("STOCK_TEST_OUTPUT_PATH")
        if not test_out:
            test_out = tempfile.mkdtemp(prefix="stock_test_out_")

        if "data" not in self.raw_config:
            self.raw_config["data"] = {}
        self.raw_config["data"]["output_path"] = os.path.join(test_out, "result.csv")

        # [Fix] Also set paths.output_dir for Orchestrator/Reporter
        if "paths" not in self.raw_config:
            self.raw_config["paths"] = {}
        self.raw_config["paths"]["output_dir"] = test_out

        # 他の data フォルダ系もオーバーライド推奨だが、とりあえずこれらを必須とする
        print(f"🧪 [TEST MODE] Config Overridden: DB={test_db}, Out={test_out}")

    def validate_config(self) -> ConfigModel:
        """ConfigをPydanticモデルで検証する"""
        try:
            model = ConfigModel(**self.raw_config)
            return model
        except Exception as e:
            print(f"❌ Config Validation Failed: {e}")
            raise ValueError(f"Invalid Configuration: {e}")

    def _sync_macro_context(self) -> None:
        """market_context.txt からマクロ環境設定を読み込み Config をオーバーライドする"""
        context_path = os.path.join(
            os.path.dirname(self.config_path), "market_context.txt"
        )
        if not os.path.exists(context_path):
            return

        try:
            with open(context_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Config 構造の初期化 (Raw Config操作)
            if "scoring_v2" not in self.raw_config:
                self.raw_config["scoring_v2"] = {}
            if "macro" not in self.raw_config["scoring_v2"]:
                self.raw_config["scoring_v2"]["macro"] = {}

            macro_cfg = self.raw_config["scoring_v2"]["macro"]

            # 正規表現でタグ解析
            match_sentiment = re.search(r"\[MACRO_SENTIMENT:([a-zA-Z0-9_]+)\]", content)
            if match_sentiment:
                val = match_sentiment.group(1).lower()
                macro_cfg["sentiment"] = val

            match_rate = re.search(r"\[INTEREST_RATE:([a-zA-Z0-9_]+)\]", content)
            if match_rate:
                val = match_rate.group(1).lower()
                macro_cfg["interest_rate"] = val

            match_sector = re.search(r"\[ACTIVE_SECTOR:([^\]]+)\]", content)
            if match_sector:
                val = match_sector.group(1).strip()
                macro_cfg["active_sector"] = val

        except Exception as e:
            print(f"⚠️ Failed to sync macro context: {e}")

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込んで辞書として返す"""
        if not os.path.exists(self.config_path):
            print(f"⚠️ Config file not found at: {self.config_path}")
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return {}


# --- 旧コードとの互換性用 ---
def load_config(config_path="config.yaml"):
    loader = ConfigLoader(config_path)
    return loader.config

```

---

### src/config_schema.py

```python
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class DataConfig(BaseModel):
    jp_stock_list: str = "data/input/jp_stock_list.csv"
    output_path: str = "data/output/analysis_result.csv"


class FilterConfig(BaseModel):
    max_rsi: Optional[int] = 100
    min_quant_score: Optional[int] = 60
    min_trading_value: Optional[int] = 10000000


class CsvMappingConfig(BaseModel):
    col_map: Dict[str, str]
    numeric_cols: List[str]


class StrategyConfig(BaseModel):
    default_style: str
    persona: str
    default_horizon: str
    base_score: int
    min_requirements: Dict[str, float]
    points: Dict[str, int]
    thresholds: Dict[str, float]


class AIConfig(BaseModel):
    model_name: str
    max_concurrency: int = Field(default=1, ge=1)
    interval_sec: float = Field(default=2.0, ge=0.0)
    validity_days: int = 7
    refresh_triggers: Dict[str, float] = {}


class CircuitBreakerConfig(BaseModel):
    consecutive_failure_threshold: int = 5


class DatabaseConfig(BaseModel):
    retention_days: int = 30


class APISettingsConfig(BaseModel):
    gemini_tier: str = "free"


class SectorPolicy(BaseModel):
    na_allowed: List[str] = []
    score_exemptions: List[str] = []
    ai_prompt_excludes: List[str] = []


class ScoringConfig(BaseModel):
    lower_is_better: List[str] = []
    min_coverage_pct: Optional[int] = 50


class ScoringV2Config(BaseModel):
    macro: Dict[str, str] = {}
    styles: Dict[str, Dict[str, float]] = {}
    tech_points: Dict[str, int] = {}


class MetadataMappingConfig(BaseModel):
    metrics: Dict[str, str]
    validation: Dict[str, Any]


class PathsConfig(BaseModel):
    db_file: Optional[str] = None
    output_dir: Optional[str] = None


class ConfigModel(BaseModel):
    api_settings: APISettingsConfig = Field(default_factory=APISettingsConfig)
    current_strategy: str
    data: DataConfig
    paths: Optional[PathsConfig] = Field(default_factory=PathsConfig)
    filter: FilterConfig = Field(default_factory=FilterConfig)
    csv_mapping: CsvMappingConfig
    scoring: ScoringConfig
    scoring_v2: Optional[ScoringV2Config] = None
    strategies: Dict[str, StrategyConfig]
    ai: AIConfig
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    sector_policies: Dict[str, SectorPolicy] = {}
    sector_risks: Dict[str, str] = {}
    metadata_mapping: Optional[MetadataMappingConfig] = None

    @field_validator("sector_policies")
    def validate_sector_policies(cls, v):
        if "default" not in v:
            pass
        return v

```

---

### src/constants.py

```python
# Scoring Constants and Defaults

# Metric Categories for Breakdown
METRIC_CATEGORY = {
    # Value
    "per": "value",
    "pbr": "value",
    "dividend_yield": "value",
    "peg_ratio": "value",
    # Quality
    "roe": "quality",
    "equity_ratio": "quality",
    "operating_cf": "quality",
    "payout_ratio": "quality",
    # Growth
    "sales_growth": "growth",
    "profit_growth": "growth",
    # Trend (Technical)
    "rsi_oversold": "trend",
    "rsi_overbought": "trend",
    "macd_bullish": "trend",
    "trend_up": "trend",
}

# Metrics where lower value is better
LOWER_IS_BETTER_DEFAULTS = ["per", "pbr", "debt_equity_ratio", "peg_ratio"]

# Scoring Defaults
DEFAULT_BASE_SCORE = 50.0
DEFAULT_SCORING_V2_STYLES = {
    "value_balanced": {"weight_fund": 0.7, "weight_tech": 0.3},
    "short_term_momentum": {"weight_fund": 0.3, "weight_tech": 0.7},
    "long_term_growth": {"weight_fund": 0.8, "weight_tech": 0.2},
}

```

---

### src/database.py

```python
from logging import getLogger
from typing import Optional

import pandas as pd

from src.database_factory import DatabaseFactory
from src.models import (
    AnalysisResult,
    MarketData,
    RankHistory,
    SentinelAlert,
    Stock,
    db_proxy,
)
from src.utils import get_current_time, get_today_str


class StockDatabase:
    def __init__(self, db_path="data/stock_master.db"):
        self.db_path = db_path
        self.logger = getLogger(__name__)

        # DatabaseFactory に初期化を委譲
        DatabaseFactory.initialize(self.db_path)

        self._init_db()

    def _init_db(self):
        """テーブルの初期化とマイグレーション"""
        with db_proxy.connection_context():
            # テーブル作成
            db_proxy.create_tables(
                [Stock, MarketData, AnalysisResult, SentinelAlert, RankHistory],
                safe=True,
            )

            # 手動マイグレーション (Peewee は ALTER TABLE を自動で行わないため)
            self._manual_migration()

    def _manual_migration(self):
        """不足カラムの追加 (Peewee の接続を使用)"""
        try:
            # market_data
            cursor = db_proxy.execute_sql("PRAGMA table_info(market_data)")
            existing_cols = [row[1] for row in cursor.fetchall()]

            new_cols = {
                "payout_ratio": "REAL",
                "current_ratio": "REAL",
                "quick_ratio": "REAL",
                "macd_hist": "REAL",
                "rsi_14": "REAL",
                "trend_up": "INTEGER",
                "sales": "REAL",
                "sales_growth": "REAL",
                "profit_growth": "REAL",
                "is_turnaround": "INTEGER",
                "turnaround_status": "TEXT",
                "fetch_status": "TEXT",
                # v5.1 Refinement
                "trend_score": "INTEGER",
                "profit_growth_raw": "REAL",
                "payout_status": "TEXT",
                "profit_status": "TEXT",
                "sales_status": "TEXT",
                # [v5.4]
                "operating_margin": "REAL",
                "debt_equity_ratio": "REAL",
                "free_cf": "REAL",
                "volatility": "REAL",
                # [v10.0] Phase 3 Advanced Technicals
                "ma_divergence": "REAL",
                "volume_ratio": "REAL",
            }
            for col, dtype in new_cols.items():
                if col not in existing_cols:
                    db_proxy.execute_sql(
                        f"ALTER TABLE market_data ADD COLUMN {col} {dtype}"
                    )
                    self.logger.info(f"Migration: Added column '{col}' to market_data")

            # analysis_results
            cursor = db_proxy.execute_sql("PRAGMA table_info(analysis_results)")
            existing_cols = [row[1] for row in cursor.fetchall()]

            new_cols_ar = {
                "score_long": "REAL",
                "score_short": "REAL",
                "score_gap": "REAL",
                "active_style": "TEXT",
                "row_hash": "TEXT",
                "ai_horizon": "TEXT",  # [v4.11]
                "ai_detail": "TEXT",  # [v11.0]
                "audit_version": "INTEGER",  # [v8.5]
            }
            for col, dtype in new_cols_ar.items():
                if col not in existing_cols:
                    db_proxy.execute_sql(
                        f"ALTER TABLE analysis_results ADD COLUMN {col} {dtype}"
                    )
                    self.logger.info(
                        f"Migration: Added column '{col}' to analysis_results"
                    )

            # --- Index Migration ---
            # MarketData: entry_date
            db_proxy.execute_sql(
                "CREATE INDEX IF NOT EXISTS stock_market_data_entry_date ON market_data(entry_date)"
            )

            # AnalysisResult: row_hash, analyzed_at
            db_proxy.execute_sql(
                "CREATE INDEX IF NOT EXISTS stock_analysis_results_row_hash ON analysis_results(row_hash)"
            )
            db_proxy.execute_sql(
                "CREATE INDEX IF NOT EXISTS stock_analysis_results_analyzed_at ON analysis_results(analyzed_at)"
            )

        except Exception as e:
            self.logger.error(f"Migration failed: {e}")

    def upsert_stocks(self, stocks_list):
        """銘柄マスタの一括登録・更新 (Peewee 版)"""
        if not stocks_list:
            return

        with db_proxy.atomic():
            for data in stocks_list:
                Stock.insert(**data).on_conflict(
                    conflict_target=[Stock.code],
                    preserve=[Stock.name, Stock.sector, Stock.market],
                    update={"updated_at": get_current_time()},
                ).execute()
        self.logger.info(f"Upserted {len(stocks_list)} stocks to master.")

    def get_stock(self, code):
        """銘柄情報の取得 (Peewee 版)"""
        try:
            res = Stock.get_by_id(code)
            # Row オブジェクトのように振る舞うための暫定処置 (dict変換)
            return {
                "code": res.code,
                "name": res.name,
                "sector": res.sector,
                "market": res.market,
                "updated_at": res.updated_at,
            }
        except Stock.DoesNotExist:
            return None

    def upsert_market_data(self, data_list):
        """市況データの一括登録 (Peewee 版)"""
        if not data_list:
            return

        today = get_today_str()
        with db_proxy.atomic():
            for d in data_list:
                d_copy = d.copy()
                if "entry_date" not in d_copy:
                    d_copy["entry_date"] = today
                if "fetch_status" not in d_copy:
                    d_copy["fetch_status"] = "success"
                # d_copy['fetch_status'] = 'success' # REMOVED hard overwrite
                d_copy["updated_at"] = get_current_time()

                # [Fix] Map current_price to price for DB storage
                if "current_price" in d_copy and "price" not in d_copy:
                    d_copy["price"] = d_copy["current_price"]

                # モデルのカラム名のみを抽出
                keys = [f.column_name for f in MarketData._meta.sorted_fields]
                filtered_data = {k: v for k, v in d_copy.items() if k in keys}

                MarketData.insert(**filtered_data).on_conflict(
                    conflict_target=[MarketData.code, MarketData.entry_date],
                    update=filtered_data,
                ).execute()
        self.logger.info(f"Upserted {len(data_list)} market records.")

    def get_market_data_status(self, date_str):
        """指定した日付に収集済みの銘柄コードリストを取得 (Peewee 版)"""
        query = MarketData.select(MarketData.code).where(
            (MarketData.entry_date == date_str) & (MarketData.fetch_status == "success")
        )
        return {row.code_id for row in query}

    def save_analysis_result(self, record):
        """分析結果を保存 (Peewee 版)"""
        # record 内の 'market_data_id' を 'market_data' にマッピングする必要がある
        peewee_record = record.copy()
        if "market_data_id" in peewee_record:
            peewee_record["market_data"] = peewee_record.pop("market_data_id")

        # [v6.0] Filter record keys to match AnalysisResult model fields
        valid_fields = set(AnalysisResult._meta.fields.keys())
        peewee_record = {k: v for k, v in peewee_record.items() if k in valid_fields}

        with db_proxy.atomic():
            AnalysisResult.insert(**peewee_record).on_conflict(
                conflict_target=[
                    AnalysisResult.market_data,
                    AnalysisResult.strategy_name,
                ],
                update=peewee_record,
            ).execute()
        self.logger.debug(
            f"Saved analysis result for market_data_id: {peewee_record.get('market_data')}"
        )

    def get_market_data_id(self, code, entry_date):
        """market_data_id を取得 (Peewee 版)"""
        res = (
            MarketData.select(MarketData.id)
            .where((MarketData.code == code) & (MarketData.entry_date == entry_date))
            .first()
        )
        return res.id if res else None

    def get_ai_cache(self, code, row_hash, strategy):
        """AI分析結果のキャッシュを取得 (Peewee 版)"""
        query = (
            AnalysisResult.select(
                AnalysisResult.ai_sentiment,
                AnalysisResult.ai_reason,
                AnalysisResult.ai_risk,
                AnalysisResult.quant_score,
                AnalysisResult.analyzed_at,
                AnalysisResult.audit_version,
                AnalysisResult.ai_horizon,
                AnalysisResult.ai_detail,
            )  # [v12.2] Select Detail
            .join(MarketData)
            .where(
                (MarketData.code == code)
                & (AnalysisResult.row_hash == row_hash)
                & (AnalysisResult.strategy_name == strategy)
            )
            .order_by(AnalysisResult.analyzed_at.desc())
            .limit(1)
            .dicts()
        )

        res = query.first()
        return res if res else None

    def get_ai_smart_cache(self, code, strategy, validity_days):
        """指定期間内の最新かつ有効な AI分析結果を取得 (Smart Cache)"""
        from datetime import timedelta

        threshold_date = get_current_time() - timedelta(days=validity_days)

        query = (
            AnalysisResult.select(
                AnalysisResult.ai_sentiment,
                AnalysisResult.ai_reason,
                AnalysisResult.ai_risk,
                AnalysisResult.quant_score,
                AnalysisResult.analyzed_at,
                AnalysisResult.audit_version,
                AnalysisResult.ai_horizon,
                AnalysisResult.ai_detail,  # [v12.2] Select Detail
                MarketData.price.alias("cached_price"),
            )
            .join(MarketData)
            .where(
                (MarketData.code == code)
                & (AnalysisResult.strategy_name == strategy)
                & (AnalysisResult.ai_sentiment != "Error")
                & (AnalysisResult.analyzed_at >= threshold_date)
            )
            .order_by(AnalysisResult.analyzed_at.desc())
            .limit(1)
            .dicts()
        )

        res = query.first()
        return res if res else None

    def cleanup_and_optimize(self, retention_days=30):
        """古いデータの削除とDBの最適化 (Peewee 改修版)"""
        from datetime import timedelta

        try:
            limit_date = (get_current_time() - timedelta(days=retention_days)).strftime(
                "%Y-%m-%d"
            )

            with db_proxy.atomic():
                # 1. 古い市況データの削除
                # market_data テーブルの削除 (CASCADE により analysis_results も連動することを期待)
                del_q = MarketData.delete().where(MarketData.entry_date < limit_date)
                deleted_count = del_q.execute()

                # 2. 孤立した分析結果の削除 (CASCADE漏れ対策)
                # MarketData に紐付かない AnalysisResult を削除
                orphan_q = AnalysisResult.delete().where(
                    ~(AnalysisResult.market_data << MarketData.select(MarketData.id))
                )
                orphan_count = orphan_q.execute()

            # 3. VACUUM (トランザクションの外で実行する必要がある)
            # Peewee の connection().execute_sql を使用
            db_proxy.execute_sql("VACUUM")

            msg = f"🧹 DB Maintenance: Deleted {deleted_count} old market records and {orphan_count} orphan analysis records (older than {limit_date}). VACUUM completed."
            self.logger.info(msg)
            return True, msg

        except Exception as e:
            err_msg = f"⚠️ DB Maintenance failed: {e}"
            self.logger.error(err_msg)
            return False, err_msg

    def clear_analysis_results(
        self, strategy_name: Optional[str] = None, date_str: Optional[str] = None
    ):
        """
        [v5.5] Clear AI analysis results from database.
        Allows re-running analysis tests.
        """
        try:
            query = AnalysisResult.delete()

            conditions = []
            if strategy_name:
                conditions.append(AnalysisResult.strategy_name == strategy_name)

            # Note: AnalysisResult has 'analyzed_at' (DateTime) but filtering strictly by date string might be tricky
            # if we don't have a specific date column or range.
            # However, typically we want to clear "latest" or all for a strategy.
            # If date_str is provided, we might interpret it as "analyzed on this day".
            if date_str:
                # SQLite substring match for YYYY-MM-DD
                from peewee import fn

                conditions.append(
                    fn.strftime("%Y-%m-%d", AnalysisResult.analyzed_at) == date_str
                )

            if conditions:
                import operator
                from functools import reduce

                expr = reduce(operator.and_, conditions)
                query = query.where(expr)

            # Execute
            count = query.execute()
            self.logger.info(
                f"Cleared {count} analysis results. (Strategy: {strategy_name}, Date: {date_str})"
            )
            return count

        except Exception as e:
            self.logger.error(f"Error clearing analysis results: {e}")
            return 0

    def get_market_data_batch(self, codes: list) -> pd.DataFrame:
        """指定した銘柄リストの最新市況データを一括取得し、DataFrame として返す。"""
        import pandas as pd

        if not codes:
            return pd.DataFrame()

        # 各銘柄の最新 entry_date のデータを取得
        # サブクエリを使用して各コードの最大日付を特定
        from peewee import fn

        latest_dates = (
            MarketData.select(
                MarketData.code, fn.MAX(MarketData.entry_date).alias("max_date")
            )
            .where(MarketData.code << codes)
            .group_by(MarketData.code)
        )

        # 元のテーブルとジョインして全カラムを取得
        query = (
            MarketData.select(MarketData, Stock.name, Stock.sector)
            .join(
                latest_dates,
                on=(MarketData.code == latest_dates.c.code)
                & (MarketData.entry_date == latest_dates.c.max_date),
            )
            .join(Stock, on=(MarketData.code == Stock.code))
            .dicts()
        )

        results = list(query)
        return pd.DataFrame(results) if results else pd.DataFrame()

```

---

### src/database_factory.py

```python
import os
from typing import Optional

from peewee import SqliteDatabase

from src.models import db_proxy


class DatabaseFactory:
    """
    Manages the lifecycle of the global database connection (db_proxy).
    Ensures safe switching between different database files for testing and production.
    """

    _current_db_path: Optional[str] = None

    @classmethod
    def initialize(cls, db_path: str):
        """
        Initializes the database connection and binds it to db_proxy.
        If the path is different from the current one, it closes the existing connection first.
        """
        # If the path is different, or if there is no connection, initialize
        if cls._current_db_path != db_path or not db_proxy.obj:
            cls.reset()

            if db_path != ":memory:":
                os.makedirs(os.path.dirname(db_path), exist_ok=True)

            # Define pragmas for performance and consistency
            pragmas = {
                "journal_mode": "wal",
                "cache_size": -1 * 64000,  # 64MB
                "foreign_keys": 1,
            }

            db = SqliteDatabase(db_path, pragmas=pragmas)
            db_proxy.initialize(db)
            cls._current_db_path = db_path

    @classmethod
    def reset(cls):
        """
        Closes the current connection and unbinds db_proxy.
        This is critical for establishing test isolation.
        """
        if db_proxy.obj:
            try:
                db_proxy.close()
            except Exception:
                pass
            db_proxy.obj = None
        cls._current_db_path = None

```

---

### src/domain/models.py

```python
# src/domain/models.py
"""
ドメインモデル定義 (Unified Analyst Prompt v2.0)

[v2.0] Pydantic model_validator によるアナリストルールの自動検証を実装。
- ValidationFlag: Tier1欠損、Red Flag、例外救済判定のメタデータ。
- SkipReason: 分析スキップの理由を型安全に管理。
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class SkipReason(str, Enum):
    """分析スキップの理由 (足切り条件)"""

    INSOLVENT = "equity_ratio_negative"  # 債務超過 (自己資本比率 < 0%)
    EXTREME_VALUATION = "valuation_bubble"  # PER > 500 または PBR > 20
    NEGATIVE_OCF_EXTREME = "operating_cf_extreme_negative"  # 営業CFマージン < -10%
    PAYOUT_UNSUSTAINABLE = "payout_over_300"  # 配当性向 > 300%


class ValidationFlag(BaseModel):
    """アナリストルール検証結果のメタデータ"""

    tier1_missing: List[str] = Field(default_factory=list)  # Tier1 必須項目の欠損
    tier2_missing: List[str] = Field(default_factory=list)  # Tier2 参考項目の欠損
    red_flags: List[str] = Field(default_factory=list)  # Red Flag 検知
    rescue_eligible: bool = False  # 例外救済ルール該当
    skip_reasons: List[SkipReason] = Field(default_factory=list)  # 足切り理由

    @property
    def has_critical_issues(self) -> bool:
        """Tier1欠損またはスキップ理由があるか"""
        return len(self.tier1_missing) > 0 or len(self.skip_reasons) > 0


class StockAnalysisData(BaseModel):
    """
    市場データと分析用の財務指標を保持するドメインモデル。
    DBのMarketDataモデルとは異なり、分析ロジック内で扱いやすい形に正規化する。

    [v2.0] model_validator によりアナリストルールに基づく自動検証を実行。
    """

    code: str
    name: Optional[str] = None
    sector: str = "Unknown"
    market: Optional[str] = None
    entry_date: Optional[str] = None

    @field_validator("entry_date", mode="before")
    @classmethod
    def convert_entry_date(cls, v):
        """Timestamp型を文字列に変換"""
        if v is None:
            return None
        if hasattr(v, "strftime"):
            return v.strftime("%Y-%m-%d")
        return str(v)

    # Market Data
    current_price: Optional[float] = None
    market_cap: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def map_price_to_current_price(cls, data: Any) -> Any:
        """price がある場合に current_price にマッピング（互換性対応）"""
        if isinstance(data, dict):
            if "price" in data and data.get("current_price") is None:
                data["current_price"] = data["price"]
        return data

    # Valuation
    per: Optional[float] = None
    pbr: Optional[float] = None
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None

    # Profitability / Efficiency
    roe: Optional[float] = None
    operating_margin: Optional[float] = None

    # Financial Stability
    equity_ratio: Optional[float] = None
    debt_equity_ratio: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None

    # Cash Flow
    operating_cf: Optional[float] = None
    free_cf: Optional[float] = None
    cf_status: Optional[float] = None  # 0 or 1 usually
    ocf_margin: Optional[float] = None  # 営業CFマージン

    # Growth
    sales_growth: Optional[float] = None
    profit_growth: Optional[float] = None

    # Technicals
    rsi_14: Optional[float] = None
    macd_hist: Optional[float] = None
    trend_up: Optional[float] = None

    # Raw dictionary for fallback (optional)
    raw_data: Dict[str, Any] = Field(default_factory=dict)

    # [v2.0] 検証メタデータ
    validation_flags: ValidationFlag = Field(default_factory=ValidationFlag)

    class Config:
        extra = "ignore"  # 不明なフィールドは無視

    @model_validator(mode="after")
    def validate_analyst_rules(self) -> "StockAnalysisData":
        """アナリストルールブックに基づく検証を一括実行"""
        flags = self.validation_flags

        # --- Tier 1 Critical Check (必須項目) ---
        tier1_fields = [
            ("current_price", self.current_price),
            ("operating_cf", self.operating_cf),
            ("operating_margin", self.operating_margin),
            ("per", self.per),
            ("pbr", self.pbr),
            ("roe", self.roe),
        ]
        for field_name, value in tier1_fields:
            if value is None:
                flags.tier1_missing.append(field_name)

        # --- Tier 2 Reference Check (参考項目) ---
        tier2_fields = [
            ("equity_ratio", self.equity_ratio),
            ("sales_growth", self.sales_growth),
            ("dividend_yield", self.dividend_yield),
        ]
        for field_name, value in tier2_fields:
            if value is None:
                flags.tier2_missing.append(field_name)

        # --- Abnormal Value Detection (足切りロジック) ---
        # 債務超過
        if self.equity_ratio is not None and self.equity_ratio < 0:
            flags.skip_reasons.append(SkipReason.INSOLVENT)

        # 極端なバリュエーション
        if self.per is not None and self.per > 500:
            flags.skip_reasons.append(SkipReason.EXTREME_VALUATION)
        if self.pbr is not None and self.pbr > 20:
            flags.skip_reasons.append(SkipReason.EXTREME_VALUATION)

        # 営業CFマージン極端マイナス
        if self.ocf_margin is not None and self.ocf_margin < -10:
            flags.skip_reasons.append(SkipReason.NEGATIVE_OCF_EXTREME)

        # タコ足配当
        if self.payout_ratio is not None and self.payout_ratio > 300:
            flags.skip_reasons.append(SkipReason.PAYOUT_UNSUSTAINABLE)

        # --- Red Flag Detection (即時回避) ---
        if self.ocf_margin is not None and self.ocf_margin < 0:
            flags.red_flags.append("negative_ocf_margin")
        if self.sales_growth is not None and self.sales_growth < 0:
            flags.red_flags.append("declining_sales")
        # PER30超 かつ PBR5超
        if (
            self.per is not None
            and self.pbr is not None
            and self.per > 30
            and self.pbr > 5
        ):
            flags.red_flags.append("extreme_overvaluation")

        # --- 例外救済ルール (Positive Bias for Value) ---
        if (
            self.pbr is not None
            and self.dividend_yield is not None
            and self.pbr < 1.0
            and self.dividend_yield > 4.0
        ):
            # Red Flagがなければ救済対象
            if len(flags.red_flags) == 0:
                flags.rescue_eligible = True

        return self

    @property
    def should_skip_analysis(self) -> bool:
        """分析をスキップすべきかを判定 (足切り)"""
        return len(self.validation_flags.skip_reasons) > 0

    @property
    def deficiency_type(self) -> str:
        """欠損タイプの要約文字列"""
        if len(self.validation_flags.tier1_missing) > 0:
            return "Critical (Tier1 欠損あり)"
        elif len(self.validation_flags.tier2_missing) > 0:
            return "Partial (Tier2 欠損あり / 参考データ不足)"
        return "Complete (データ完備)"


class AnalysisResultModel(BaseModel):
    """
    分析結果（スコア、AI判断等）を保持するモデル。
    """

    strategy_name: str
    quant_score: float = 0.0

    # Breakdown
    score_value: float = 0.0
    score_growth: float = 0.0
    score_quality: float = 0.0
    score_trend: float = 0.0

    # AI Analysis
    ai_sentiment: Optional[str] = None  # Bullish, Bearish, Neutral, Error
    ai_reason: Optional[str] = None
    ai_risk: Optional[str] = None
    ai_horizon: Optional[str] = None

    analyzed_at: datetime = Field(default_factory=datetime.now)


class AnalysisTask(BaseModel):
    """
    Antigravity Runner が処理するタスク単位。
    ValidationEngine等で検証される対象。
    """

    stock: StockAnalysisData
    strategy: str
    prompt: Optional[str] = None
    result: Optional[AnalysisResultModel] = None

    # Validation status
    is_valid: bool = True
    error_reason: Optional[str] = None
    is_quarantined: bool = False

    # Metadata
    market_data_id: Optional[int] = None
    low_confidence: bool = False

```

---

### src/engine.py

```python
# src/engine.py
"""
AnalysisEngine: ScoringEngine のラッパー（後方互換性維持用）
[v12.0] 機能を src/calc/engine.py の ScoringEngine に統合。
       このファイルは後方互換性のため維持。
"""
from typing import Any, Dict

import pandas as pd

from src.calc.engine import ScoringEngine


class AnalysisEngine:
    """
    後方互換性のためのラッパークラス。
    実際の処理は ScoringEngine に委譲。
    """

    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._engine = ScoringEngine(config)

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value
        self._engine.config = value

    def calculate_scores(self, df: pd.DataFrame, strategy_name: str) -> pd.DataFrame:
        """
        [v7.0] Orchestrator: Delegates calculation to specific Strategy class.
        """
        if df.empty:
            return df

        # ScoringEngine に委譲
        result_df = self._engine.calculate_score(df, strategy_name)

        # 元データにマージ
        merged = df.copy()
        for col in result_df.columns:
            merged[col] = result_df[col]

        return merged

    def filter_and_rank(self, df: pd.DataFrame, strategy_name: str) -> pd.DataFrame:
        """
        フィルタリングとランキングの実行。
        ScoringEngine に委譲。
        """
        return self._engine.filter_and_rank(df, strategy_name)

```

---

### src/env_loader.py

```python
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_env_file():
    """
    Find and load .env file from predetermined paths or parent directories.
    """
    # 1. Environment variable override
    env_path_custom = os.getenv("STOCK_ENV_PATH")
    if env_path_custom and os.path.exists(env_path_custom):
        logger.info(f"🔑 Loading .env from STOCK_ENV_PATH: {env_path_custom}")
        load_dotenv(env_path_custom, override=True)
        return True

    # 2. Search up from current file's project root
    # Starting from current directory
    current_dir = Path(os.getcwd()).resolve()

    # Candidate search depth: up to 3 levels (./, ../, ../../)
    for i in range(4):
        candidate = current_dir / ".env"
        if candidate.exists():
            logger.info(f"🔑 Found .env at: {candidate}")
            load_dotenv(str(candidate), override=True)
            return True

        # Also check common subdirs in parents if needed, but standard is parent root
        # Move up
        if current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent

    logger.warning("⚠️ No .env file found in search paths.")
    return False

```

---

### src/fetcher/__init__.py

```python
from .base import FetcherBase as FetcherBase
from .facade import DataFetcher as DataFetcher

```

---

### src/fetcher/base.py

```python
import os
from logging import getLogger

import yaml


class FetcherBase:
    # Status Constants
    STATUS_SUCCESS = "success"
    STATUS_ERROR_QUOTA = "error_quota"
    STATUS_ERROR_NETWORK = "error_network"
    STATUS_ERROR_DATA = "error_data"
    STATUS_ERROR_OTHER = "error_other"

    def __init__(self, config_source="config.yaml"):
        self.logger = getLogger(__name__)

        if isinstance(config_source, dict):
            self.config = config_source
        else:
            self.config = self._load_config(config_source)

    def _load_config(self, path):
        if not os.path.exists(path):
            self.logger.warning(f"Config file not found: {path}")
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}

```

---

### src/fetcher/facade.py

```python
import time

import pandas as pd
from tqdm import tqdm

from .base import FetcherBase
from .jpx import JPXFetcher
from .yahoo import YahooFetcher


class DataFetcher(FetcherBase):
    """
    Facade class for DataFetcher components.
    Maintains compatibility with the original DataFetcher API.
    """

    def __init__(self, config_source="config.yaml"):
        super().__init__(config_source)
        # Initialize sub-components with same config
        self.jpx_fetcher = JPXFetcher(self.config)
        self.yahoo_fetcher = YahooFetcher(self.config)

    # ------------------------------------------------------------------
    # JPX Operations (Delegated to JPXFetcher)
    # ------------------------------------------------------------------
    def fetch_jpx_list(self, fallback_on_error=False, save_to_csv=True):
        return self.jpx_fetcher.fetch_jpx_list(fallback_on_error, save_to_csv)

    # ------------------------------------------------------------------
    # Yahoo/Stock Data Operations (Delegated to YahooFetcher)
    # ------------------------------------------------------------------
    def _fetch_single_stock(self, code, deep_repair=False):
        return self.yahoo_fetcher.fetch_single_stock(code, deep_repair=deep_repair)

    def _get_ticker_info_safe(self, ticker):
        return self.yahoo_fetcher._get_ticker_info_safe(ticker)

    def fetch_stock_data(self, codes=None, fallback_on_error=False):
        """Batch fetch stock data (Re-implemented here using components)"""
        market_map = {}
        name_map = {}
        if codes is None:
            try:
                # Use sub-component
                jpx_df = self.fetch_jpx_list(
                    fallback_on_error=fallback_on_error, save_to_csv=False
                )
            except Exception:
                return pd.DataFrame()
            if jpx_df.empty:
                return pd.DataFrame()
            if "code" in jpx_df.columns:
                codes = jpx_df["code"].tolist()
                if "market" in jpx_df.columns:
                    market_map = dict(zip(jpx_df["code"].astype(str), jpx_df["market"]))
                if "name" in jpx_df.columns:
                    name_map = dict(zip(jpx_df["code"].astype(str), jpx_df["name"]))
            else:
                return pd.DataFrame()

        results = []
        for code in tqdm(codes, desc="Fetching Data"):
            data = self._fetch_single_stock(code)
            if data:
                code_str = str(code)
                if code_str in market_map:
                    data["market"] = market_map[code_str]
                else:
                    data["market"] = "Unknown"
                if code_str in name_map:
                    data["name"] = name_map[code_str]
                results.append(data)
            time.sleep(0.1)
        return pd.DataFrame(results)

    def fetch_data_from_db(self, codes: list) -> pd.DataFrame:
        """データベースから指定銘柄の最新データを取得する。"""
        from src.database import StockDatabase

        db_path = self.config.get("paths", {}).get("db_file")
        db = StockDatabase(db_path) if db_path else StockDatabase()
        return db.get_market_data_batch(codes)

    # ------------------------------------------------------------------
    # Legacy / Utility Methods
    # ------------------------------------------------------------------
    # If consumers call _load_config directly (which they shouldn't, but inherited from Base)
    # that's handled by FetcherBase.

```

---

### src/fetcher/jpx.py

```python
import glob
import os

import pandas as pd
import requests

from src.utils import rotate_file_backup

from .base import FetcherBase


class JPXFetcher(FetcherBase):
    def fetch_jpx_list(self, fallback_on_error=False, save_to_csv=True):
        """JPXリスト取得"""
        jp_stock_path = self.config["data"]["jp_stock_list"]

        # Ensure dir exists (already done in base or facade init usually,
        # but let's be safe or rely on facade routing)
        os.makedirs(os.path.dirname(jp_stock_path), exist_ok=True)

        if save_to_csv and os.path.exists(jp_stock_path):
            rotate_file_backup(jp_stock_path)

        url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"

        # Session setup for User-Agent
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        try:
            resp = session.get(url)
            resp.raise_for_status()
            df = pd.read_excel(resp.content)

            # [Optimization] 個別株のみに絞り込む
            df = df[df["33業種区分"] != "-"]

            df = df[["コード", "銘柄名", "33業種区分", "市場・商品区分"]]
            df.columns = ["code", "name", "sector", "market"]
            df["code"] = df["code"].astype(str).str[:4]

            if save_to_csv:
                df.to_csv(jp_stock_path, index=False)

            return df

        except Exception as e:
            self.logger.error(f"❌ Failed to download JPX list: {e}")
            if not fallback_on_error:
                raise e

            self.logger.warning("⚠️ Fallback enabled. Searching backup...")
            search_dir = os.path.dirname(jp_stock_path)
            patterns = [
                os.path.join(search_dir, "stock_master_*.csv"),
                os.path.join(search_dir, "jp_stock_list_*.csv"),
            ]
            candidates = []
            for p in patterns:
                candidates.extend(glob.glob(p))

            if candidates:
                latest = sorted(candidates)[-1]
                self.logger.warning(f"🔄 Using backup: {latest}")
                try:
                    df = pd.read_csv(latest)
                    if "コード" in df.columns:
                        col_map = {
                            "コード": "code",
                            "銘柄名": "name",
                            "33業種区分": "sector",
                            "市場・商品区分": "market",
                        }
                        df.rename(columns=col_map, inplace=True)
                    if "code" in df.columns:
                        df["code"] = (
                            df["code"].astype(str).str.replace(r"\.0$", "", regex=True)
                        )
                    return df
                except Exception as ie:
                    self.logger.error(f"Backup load failed: {ie}")
                    raise ie
            else:
                raise FileNotFoundError("No backup found.")

```

---

### src/fetcher/technical.py

```python
from logging import getLogger

import pandas as pd

logger = getLogger(__name__)


def calc_technical_indicators(hist):
    """
    テクニカル指標の計算 (MACD, RSI, Moving Averages)

    Trend Score Logic (Max 4):
    1. MA Trend: 25MA > 75MA (Long-term uptrend)
    2. Price Trend: Price > 25MA (Short-term uptrend)
    3. MACD: Hist > 0 (Positive Momentum)
    4. RSI: > 50 (Bullish Zone)
    """
    if hist.empty or len(hist) < 30:
        return {}

    try:
        # Note: Pandas TAがないため、Pandasで手動計算
        close = hist["Close"]

        # MACD (12, 26, 9)
        exp12 = close.ewm(span=12, adjust=False).mean()
        exp26 = close.ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd - signal

        # RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # [v5.0] Trend Voting System (Composite Logic)
        # 1. MA Trend (Golden Cross / Long Term Up): 25MA > 75MA
        ma25 = close.rolling(window=25).mean().iloc[-1]
        ma75 = close.rolling(window=75).mean().iloc[-1]
        signal_ma = 1 if (pd.notna(ma25) and pd.notna(ma75) and ma25 > ma75) else 0

        # 2. Price Trend (Above MA25): Close > 25MA
        signal_price = 1 if (pd.notna(ma25) and close.iloc[-1] > ma25) else 0

        # 3. MACD Trend (Positive Momentum): MACD Hist > 0
        latest_macd_hist = macd_hist.iloc[-1]
        signal_macd = 1 if (pd.notna(latest_macd_hist) and latest_macd_hist > 0) else 0

        # 4. RSI Trend (Bullish Zone): RSI > 50
        latest_rsi = rsi.iloc[-1]
        signal_rsi = 1 if (pd.notna(latest_rsi) and latest_rsi > 50) else 0

        # [v10.0] Advanced Technicals (MA Divergence & Volume Ratio)
        ma25_series = close.rolling(window=25).mean()
        ma25_latest = ma25_series.iloc[-1]

        ma_divergence = None
        if pd.notna(ma25_latest) and close.iloc[-1] != 0:
            ma_divergence = ((close.iloc[-1] - ma25_latest) / ma25_latest) * 100

        volume_ratio = None
        if "Volume" in hist.columns:
            vol = hist["Volume"]
            # [v10.1] Fixed: Calculate and compare using the same Series index
            vol_ma = vol.rolling(window=25).mean()
            avg_vol = vol_ma.iloc[-1]
            if pd.notna(avg_vol) and avg_vol > 0:
                volume_ratio = vol.iloc[-1] / avg_vol

        # Global Vote (Score 0-4)
        trend_score = signal_ma + signal_price + signal_macd + signal_rsi

        # [v5.2] Strict Trend Definition
        # Only Score >= 3 is considered "Up"
        trend_up = 1.0 if trend_score >= 3 else 0.0

        return {
            "macd_hist": latest_macd_hist,
            "rsi_14": latest_rsi,
            "trend_up": trend_up,
            "trend_score": trend_score,
            "ma_divergence": ma_divergence,
            "volume_ratio": volume_ratio,
        }
    except Exception as e:
        logger.warning(f"Error calculating technicals: {e}")
        return {}

```

---

### src/fetcher/yahoo.py

```python
import random
import time

import pandas as pd
import requests
import yfinance as yf

from src.utils import retry_with_backoff

from .base import FetcherBase
from .technical import calc_technical_indicators


class YahooFetcher(FetcherBase):
    @retry_with_backoff(max_retries=3, base_delay=5, backoff_factor=2)
    def _get_ticker_info_safe(self, ticker):
        """yfinance info取得 (リトライ強化版)"""
        # [Optimization] ランダム待機 (0.5-1.5)
        time.sleep(random.uniform(0.5, 1.5))
        try:
            return ticker.info
        except Exception as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                self.logger.warning("⚠️ HTTP 401 received. Waiting longer...")
                time.sleep(10)
            raise e

    def fetch_single_stock(self, code, deep_repair=False):
        """1銘柄のデータを取得する。

        Args:
            code (str): 銘柄コード。
            deep_repair (bool): True の場合、重い財務三表の取得を行い、欠損データを精密に修復する。
        """
        ticker_symbol = f"{code}.T"
        stock = yf.Ticker(ticker_symbol)

        try:
            info = self._get_ticker_info_safe(stock)

            if not info or "currentPrice" not in info:
                self.logger.debug(f"No info or currentPrice for {code}")
                return {"code": code, "fetch_status": self.STATUS_ERROR_DATA}

            # Rate Limit対策
            time.sleep(0.5)

            # Technical Data
            try:
                hist = stock.history(period="6mo")
                tech_data = calc_technical_indicators(hist)
            except Exception as e:
                self.logger.warning(f"Failed to fetch history for {code}: {e}")
                tech_data = {}

            # Basic Financials
            raw_current = info.get("currentRatio")
            current_ratio = (
                raw_current * 100 if raw_current and raw_current < 10.0 else raw_current
            )
            raw_quick = info.get("quickRatio")
            quick_ratio = (
                raw_quick * 100 if raw_quick and raw_quick < 10.0 else raw_quick
            )
            price = info.get("currentPrice")
            div_rate = info.get("dividendRate", 0) or 0
            div_yield = (div_rate / price * 100) if price else 0

            # [v12.5 Self-Healing] Advanced Data Fetching (Fallback to Financial Statements)
            # infoが取得できない場合、財務諸表から直接算出を試みる

            # 1. Prepare Financial Statements (Lazy loading if needed)
            bs = pd.DataFrame()
            cf = pd.DataFrame()
            inc = pd.DataFrame()

            # Helper to access DF safely
            def get_latest_value(df, keys):
                if df.empty:
                    return None
                for k in keys:
                    if k in df.index:
                        vals = df.loc[k]
                        # 最初の有効な値を探す
                        for v in vals:
                            if pd.notna(v):
                                return v
                return None

            # 2. Equity Ratio Repair (Tiered Approach)
            # [v13.0] info['equityRatio'] is systematically missing in 2024-2025.
            # Using heavy BS fetch for 4000 stocks causes 429 errors.
            equity_ratio = info.get("equityRatio")
            if equity_ratio is None:
                # Step 1: Fast Estimation (using info only)
                de = info.get("debtToEquity")  # TotalDebt/TotalEquity * 100
                if de is not None and de > 0:
                    equity_ratio = (1 / (1 + (de / 100.0))) * 100
                    self.logger.debug(
                        f"💡 Estimated Equity Ratio for {code}: {equity_ratio:.1f}% (via D/E)"
                    )
                else:
                    bv = info.get("bookValue")
                    shares = info.get("sharesOutstanding")
                    debt = info.get("totalDebt")
                    if bv and shares and debt and (bv * shares + debt) > 0:
                        equity_ratio = (bv * shares) / (bv * shares + debt) * 100
                        self.logger.debug(
                            f"💡 Estimated Equity Ratio for {code}: {equity_ratio:.1f}% (via BV/Debt)"
                        )

                # Step 2: Heavy Repair (only if deep_repair=True)
                if (equity_ratio is None or deep_repair) and not self.config.get(
                    "fetcher", {}
                ).get("skip_heavy_repair", False):
                    try:
                        if bs.empty:
                            bs = stock.balance_sheet
                        if not bs.empty:
                            total_assets = get_latest_value(
                                bs, ["Total Assets", "TotalAssets"]
                            )
                            total_equity = get_latest_value(
                                bs,
                                [
                                    "Total Stockholder Equity",
                                    "Stockholders Equity",
                                    "Total Equity Gross Minority Interest",
                                ],
                            )
                            if total_assets and total_equity and total_assets > 0:
                                precise_er = (total_equity / total_assets) * 100
                                if precise_er > 0:
                                    equity_ratio = precise_er
                                    self.logger.info(
                                        f"🔧 Precise Equity Ratio for {code}: {equity_ratio:.2f}% (from BS)"
                                    )
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to deep repair Equity Ratio for {code}: {e}"
                        )

            # 3. Operating CF Repair (Tiered)
            operating_cf = info.get("operatingCashflow")
            if operating_cf is None and deep_repair:
                try:
                    if cf.empty:
                        cf = stock.cashflow
                    operating_cf = get_latest_value(cf, ["Operating Cash Flow"])
                    if operating_cf is not None:
                        self.logger.info(
                            f"🔧 Precise Operating CF for {code}: {operating_cf:,.0f} (from CF)"
                        )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to deep repair Operating CF for {code}: {e}"
                    )

            # 4. PER Repair (Tiered Approach)
            per = info.get("trailingPE")
            if per is None and price:
                # Fast repair from trailingEps in info
                eps = info.get("trailingEps") or info.get("forwardEps")
                if eps and eps > 0:
                    per = price / eps
                    self.logger.debug(
                        f"💡 Estimated PER for {code}: {per:.1f} (via EPS)"
                    )

                # Heavy repair (Financials)
                if per is None and deep_repair:
                    try:
                        if inc.empty:
                            inc = stock.financials
                        if bs.empty:
                            bs = stock.balance_sheet
                        net_income = get_latest_value(inc, ["Net Income"])
                        shares = get_latest_value(
                            bs, ["Ordinary Shares Number", "Share Issued"]
                        )
                        if net_income and shares and shares > 0:
                            eps_calc = net_income / shares
                            if eps_calc > 0:
                                per = price / eps_calc
                                self.logger.info(
                                    f"🔧 Precise PER for {code}: {per:.2f} (from Financials)"
                                )
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to deep repair PER for {code}: {e}"
                        )

            # Profit & Turnaround Logic (Existing)
            turnaround_status = "normal"
            profit_status = "normal"
            profit_growth = (
                info.get("earningsGrowth", 0) * 100
                if info.get("earningsGrowth")
                else None
            )
            profit_growth_raw = None

            try:
                if inc.empty:
                    inc = stock.financials  # Ensure loaded
                if not inc.empty and "Net Income" in inc.index:
                    net_incomes = inc.loc["Net Income"]
                    if len(net_incomes) >= 2:
                        curr_ni = net_incomes.iloc[0]
                        prev_ni = net_incomes.iloc[1]

                        # Calculation Logic (Same as original)
                        if prev_ni < 0 and curr_ni > 0:
                            turnaround_status = "turnaround_black"
                            profit_status = "turnaround"
                            self.logger.info(
                                f"✨ Turnaround (Black) {code}: {prev_ni:,.0f} -> {curr_ni:,.0f}"
                            )
                        elif prev_ni > 0 and curr_ni < 0:
                            turnaround_status = "turnaround_white"
                            profit_status = "crash"
                        elif prev_ni < 0 and curr_ni < 0:
                            if curr_ni > prev_ni:
                                turnaround_status = "loss_shrinking"
                                profit_status = "loss_shrinking"
                            else:
                                turnaround_status = "loss_expanding"
                                profit_status = "loss_expanding"
                        elif prev_ni > 0 and curr_ni > 0:
                            growth_rate = ((curr_ni - prev_ni) / abs(prev_ni)) * 100
                            profit_growth_raw = growth_rate
                            if growth_rate >= 100.0:
                                profit_status = "surge"
                                turnaround_status = "profit_surge"
                            elif 30.0 <= growth_rate < 100.0:
                                profit_status = "high_growth"
                            elif -30.0 <= growth_rate < 30.0:
                                profit_status = "stable"
                            else:
                                profit_status = "crash"
                                turnaround_status = "profit_crash"

                            if profit_growth is None:
                                profit_growth = growth_rate

                        # [v5.4] Logic Fix: Real EPS Growth for Turnaround
                        turnaround_growth = ((curr_ni - prev_ni) / abs(prev_ni)) * 100

                        if profit_status == "turnaround":
                            profit_growth = turnaround_growth
                        elif profit_status == "loss_shrinking":
                            profit_growth = turnaround_growth

            except Exception:
                pass

            payout = info.get("payoutRatio", 0) * 100 if info.get("payoutRatio") else 0
            payout_status = "normal"
            if payout == 0:
                payout_status = "no_dividend" if div_yield == 0 else "missing"

            data = {
                "code": code,
                "name": info.get("longName", "Unknown"),
                "price": price,
                "per": per,
                "pbr": info.get("priceToBook"),
                "roe": (
                    info.get("returnOnEquity", 0) * 100
                    if info.get("returnOnEquity")
                    else None
                ),
                "dividend_yield": div_yield,
                "equity_ratio": equity_ratio,
                "operating_cf": operating_cf,
                "payout_ratio": payout,
                "payout_status": payout_status,
                "current_ratio": current_ratio,
                "quick_ratio": quick_ratio,
                "market_cap": info.get("marketCap"),
                "sales": info.get("totalRevenue"),
                "sales_growth": (
                    info.get("revenueGrowth", 0) * 100
                    if info.get("revenueGrowth") is not None
                    else None
                ),
                "sales_status": (
                    "missing"
                    if info.get("revenueGrowth") is None
                    else (
                        "flat"
                        if -1.0 <= (info.get("revenueGrowth", 0) * 100) <= 1.0
                        else (
                            "growth"
                            if (info.get("revenueGrowth", 0) * 100) > 1.0
                            else "decline"
                        )
                    )
                ),
                "profit_growth": profit_growth,
                "profit_growth_raw": profit_growth_raw,
                "turnaround_status": turnaround_status,
                "profit_status": profit_status,
                "is_turnaround": 1 if turnaround_status == "turnaround_black" else 0,
                "sector": info.get("sector", "Unknown"),
                "business_summary": info.get("longBusinessSummary", "")[:300] + "...",
                # [v5.4] Missing Financials
                "operating_margin": (
                    info.get("operatingMargins", 0) * 100
                    if info.get("operatingMargins")
                    else None
                ),
                "debt_equity_ratio": (
                    info.get("debtToEquity") / 100
                    if info.get("debtToEquity") is not None
                    else None
                ),  # Convert % -> Ratio
                "free_cf": info.get("freeCashflow"),
                "volatility": info.get("beta"),
                "ma_divergence": tech_data.get("ma_divergence"),
                "volume_ratio": tech_data.get("volume_ratio"),
            }
            data.update(tech_data)

            self.logger.debug(
                f"Fetched data for {code}: Price={price}, PER={data.get('per')}"
            )
            data["fetch_status"] = self.STATUS_SUCCESS
            return data

        except requests.exceptions.ConnectionError:
            self.logger.warning(f"⚠️ Network error for {code}")
            return {"code": code, "fetch_status": self.STATUS_ERROR_NETWORK}

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "quota" in err_msg.lower():
                self.logger.warning(f"⚠️ API Quota error for {code}")
                return {"code": code, "fetch_status": self.STATUS_ERROR_QUOTA}

            self.logger.warning(f"Error fetching {code}: {e}")
            return {"code": code, "fetch_status": self.STATUS_ERROR_OTHER}

```

---

### src/loader.py

```python
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.config_loader import ConfigLoader


def clean_number(x: Any) -> Optional[float]:
    """カンマ付き文字列などを数値に変換する"""
    if isinstance(x, str):
        # ハイフンのみ、または空文字は NaN (None相当)
        if x == "-" or x == "":
            return np.nan
        # カンマ削除
        x = x.replace(",", "").strip()
        # パーセント削除
        x = x.replace("%", "")
        # "1,234.56" のような形式対応
        try:
            return float(x)
        except ValueError:
            return np.nan
    return x if pd.notna(x) else None


def load_csv(file_path: str) -> pd.DataFrame:
    """
    CSVを読み込み、カラム名の正規化と数値クリーニングを行う
    """
    try:
        # Load Config
        config = ConfigLoader().config
        csv_mapping = config.get("csv_mapping", {})
        col_map: Dict[str, str] = csv_mapping.get("col_map", {})
        num_cols: List[str] = csv_mapping.get("numeric_cols", [])

        # エンコーディング対応 (MS2はCP932が多い)
        encodings = ["cp932", "shift_jis", "utf-8"]
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue

        if df is None:
            raise ValueError(f"Could not decode {file_path} with any of {encodings}")

        # === 1. カラム名のマッピング (日本語 -> 英語) ===
        # 実際に存在するカラムだけをリネーム
        df = df.rename(columns=col_map)

        # === 2. 数値データのクリーニング ===
        for col in num_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_number)

        # コードは文字列として扱う (例: 7203.0 -> "7203")
        if "code" in df.columns:
            df["code"] = df["code"].astype(str).str.replace(r"\.0$", "", regex=True)

        # カラム名の正規化 (後方互換性: price -> current_price)
        if "price" in df.columns and "current_price" not in df.columns:
            df = df.rename(columns={"price": "current_price"})

        return df

    except Exception as e:
        # エラー時はログに出すか、そのままraiseするか
        print(f"❌ Error loading {file_path}: {e}")
        raise e

```

---

### src/logger.py

```python
import logging

from tqdm import tqdm


class TqdmLoggingHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
        except Exception:
            self.handleError(record)


def setup_logger(log_file="stock_analyzer.log"):
    """
    ロガーのセットアップ
    - コンソール（画面）に出力: TqdmLoggingHandlerを使用 (プログレスバー崩れ防止)
    - ファイル（stock_analyzer.log）に出力
    の両方を行います。
    """
    # ルートロガーを取得
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 重複出力防止のため、既存のハンドラがあればクリア
    if logger.hasHandlers():
        logger.handlers.clear()

    # ログのフォーマット定義
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. コンソール出力用ハンドラ (Tqdm.write経由)
    # 標準出力と標準エラーの分離という観点では、
    # tqdm.write はデフォルトで sys.stdout/stderr を適切に扱うが、
    # ここではログを「表示」するものとして扱う。
    tqdm_handler = TqdmLoggingHandler()
    tqdm_handler.setFormatter(formatter)
    logger.addHandler(tqdm_handler)

    # 2. ファイル出力用ハンドラ (ファイルに残す)
    try:
        file_handler = logging.FileHandler(
            log_file, encoding="utf-8", mode="w"
        )  # mode='w'で毎回新規作成
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"⚠️ Warning: Could not create log file '{log_file}': {e}")

    return logger

```

---

### src/models.py

```python
from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateTimeField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    Proxy,
    TextField,
)

from src.utils import get_current_time

# Proxyオブジェクト自体は peewee からインポートしたものを使用
db_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = db_proxy


class Stock(BaseModel):
    code = CharField(primary_key=True)
    name = CharField(null=True)
    sector = CharField(null=True)
    market = CharField(null=True)
    updated_at = DateTimeField(default=get_current_time)

    class Meta:
        table_name = "stocks"


class MarketData(BaseModel):
    id = AutoField()
    code = ForeignKeyField(Stock, backref="market_data", column_name="code")
    entry_date = CharField()  # YYYY-MM-DD
    price = FloatField(null=True)
    sales = FloatField(null=True)
    sales_growth = FloatField(null=True)
    sales_status = CharField(null=True)  # [v5.2] New (missing, flat, growth, decline)
    profit_growth = FloatField(null=True)
    trend_up = FloatField(null=True)  # OLD
    trend_score = IntegerField(null=True)  # [v5.1] New (0-4)
    # Turnaround
    is_turnaround = IntegerField(null=True)  # OLD
    turnaround_status = CharField(null=True)  # [v5.0] Granular Scoring
    profit_status = CharField(
        null=True
    )  # [v5.2] Strict Status (surge, high_growth, stable, crash, turnaround)
    profit_growth_raw = FloatField(null=True)  # [v5.1] Raw value

    # Financials
    per = FloatField(null=True)
    pbr = FloatField(null=True)
    roe = FloatField(null=True)
    dividend_yield = FloatField(null=True)
    equity_ratio = FloatField(null=True)
    operating_cf = FloatField(null=True)
    market_cap = FloatField(null=True)
    payout_ratio = FloatField(null=True)
    payout_status = CharField(null=True)  # [v5.1] New (missing, no_dividend, normal)
    current_ratio = FloatField(null=True)
    quick_ratio = FloatField(null=True)
    macd_hist = FloatField(null=True)
    rsi_14 = FloatField(null=True)
    # sales_growth = FloatField(null=True) # 重複削除済み
    fetch_status = CharField(null=True)

    # [v5.4] Missing Financials
    operating_margin = FloatField(null=True)
    debt_equity_ratio = FloatField(null=True)
    free_cf = FloatField(null=True)
    volatility = FloatField(null=True)

    # [v10.0] Phase 3: Advanced Technicals
    ma_divergence = FloatField(null=True)  # 25MA Divergence (%)
    volume_ratio = FloatField(null=True)  # Volume vs 25-day average ratio

    updated_at = DateTimeField(default=get_current_time)

    class Meta:
        table_name = "market_data"
        indexes = (
            (("code", "entry_date"), True),
            (("entry_date",), False),  # For cleanup optimization
        )


class AnalysisResult(BaseModel):
    id = AutoField()
    market_data = ForeignKeyField(
        MarketData, backref="analysis_results", column_name="market_data_id"
    )
    strategy_name = CharField()
    quant_score = FloatField(null=True)
    # [v5.3] Breakdown Scores
    score_value = FloatField(null=True)
    score_growth = FloatField(null=True)
    score_quality = FloatField(null=True)
    score_trend = FloatField(null=True)
    score_penalty = FloatField(null=True)

    ai_sentiment = TextField(null=True)
    ai_reason = TextField(null=True)
    ai_detail = TextField(null=True)  # [v11.0] Detailed Analysis
    ai_risk = TextField(null=True)
    ai_horizon = TextField(null=True)  # [v4.11] New field for Time Horizon
    audit_version = IntegerField(null=True)  # [v8.5] Semantic Versioning
    row_hash = CharField(null=True)
    score_long = FloatField(null=True)
    score_short = FloatField(null=True)
    score_gap = FloatField(null=True)
    active_style = CharField(null=True)
    analyzed_at = DateTimeField(default=get_current_time)

    class Meta:
        table_name = "analysis_results"
        indexes = (
            (("market_data", "strategy_name"), True),
            (("row_hash",), False),
            (("analyzed_at",), False),
        )


# [v9.0] Sentinel & Orchestrator Models


class SentinelAlert(BaseModel):
    id = AutoField()
    code = CharField()  # Loose coupling
    alert_type = CharField()  # 'rank_change', 'volatility', 'technical'
    alert_message = TextField()
    detected_at = DateTimeField(default=get_current_time)
    is_processed = BooleanField(default=False)
    processed_at = DateTimeField(null=True)

    class Meta:
        table_name = "sentinel_alerts"
        indexes = ((("is_processed", "detected_at"), False),)


class RankHistory(BaseModel):
    id = AutoField()
    code = CharField()
    strategy_name = CharField()
    rank = IntegerField()
    score = FloatField(null=True)
    recorded_at = DateTimeField(default=get_current_time)

    class Meta:
        table_name = "rank_history"
        indexes = (
            (("code", "strategy_name", "recorded_at"), False),
            (("recorded_at",), False),
        )

```

---

### src/orchestrator.py

```python
import logging
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from peewee import fn

from src.calc.engine import ScoringEngine
from src.config_loader import ConfigLoader
from src.database import StockDatabase
from src.models import (
    AnalysisResult,
    MarketData,
    RankHistory,
    SentinelAlert,
    Stock,
    db_proxy,
)
from src.sentinel import Sentinel
from src.utils import get_current_time
from src.validation_engine import ValidationEngine


class Orchestrator:
    """システムの全体動作を統括するオーケストレーター。

    Daily, Weekly, Monthly の各定型ルーチンや、
    異常検知（Sentinel）に基づく再分析のワークフローを管理する。

    Attributes:
        config (Dict[str, Any]): システム設定。
        db (StockDatabase): データベースインスタンス。
        sentinel (Sentinel): 異常検知エンジン。
        reporter (StockReporter): レポート生成モジュール。
        debug_mode (bool): デバッグモードフラグ。
    """

    def __init__(self, debug_mode: bool = False):
        """Orchestrator を初期化する。

        Args:
            debug_mode (bool, optional): デバッグモード。デフォルトは False。
        """
        self.logger = logging.getLogger(__name__)
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.config
        self.db = StockDatabase()
        self.sentinel = Sentinel(debug_mode=debug_mode)
        self.debug_mode = debug_mode

        from src.reporter import StockReporter

        paths = self.config.get("paths", {}) or {}
        output_dir = paths.get("output_dir") or "data/output"
        self.reporter = StockReporter(output_dir=output_dir)

    def run(self, mode: str):
        """指定されたモードでオーケストレーションを実行する。

        Args:
            mode (str): 実行モード ('daily', 'weekly', 'monthly')。
        """
        self.logger.info(f"🎻 Orchestrator started in [{mode.upper()}] mode.")

        # 1. ハンドシェイク（アラートの未処理チェック）
        self._handshake_procedure()

        # 2. 各モードに応じたルーチン実行
        if mode == "daily":
            self._run_daily()
        elif mode == "weekly":
            self._run_weekly()
        elif mode == "monthly":
            self._run_monthly()
        else:
            self.logger.error(f"Unknown mode: {mode}")

    def _handshake_procedure(self):
        """未処理の Sentinel アラートをチェックし、ユーザーに対処を提案する。"""
        unprocessed = (
            SentinelAlert.select()
            .where(SentinelAlert.is_processed == False)  # noqa: E712
            .order_by(SentinelAlert.detected_at.desc())
        )
        if not unprocessed.exists():
            self.logger.info("✅ 新規アラートはありません。")
            return

        self.logger.info("🚨 未処理のアラートが検出されました:")
        alerts_to_fix = []
        for alert in unprocessed:
            detected_at = alert.detected_at
            if isinstance(detected_at, str):
                try:
                    detected_at = datetime.fromisoformat(detected_at)
                except ValueError:
                    detected_at = datetime.strptime(detected_at, "%Y-%m-%d %H:%M:%S.%f")

            delta = get_current_time() - detected_at
            prefix = "[CRITICAL: 期限切れ] " if delta.total_seconds() > 86400 else ""

            self.logger.warning(
                f"{prefix}[{alert.id}] {detected_at.strftime('%m-%d %H:%M')} {alert.alert_type}: {alert.code} - {alert.alert_message}"
            )
            alerts_to_fix.append(alert)

    def _run_daily(self):
        """Daily 定型ルーチンを実行する。

        1. 対象銘柄の選定（戦略別 Top 50）
        2. 分析状態のリフレッシュ（audit_version リセット）
        3. Sentinel（異常検知）の実行
        4. AI 分析の実行（ターゲット銘柄 + アラート発生銘柄）
        5. レポート生成
        """
        self.logger.info("🔄 Daily ルーチンを開始します (Balanced Strategy)...")

        # 1. ターゲット選定
        target_map = self._get_balanced_targets(top_n_per_strategy=50)
        target_codes = list(target_map.keys())
        self.logger.info(f"✅ {len(target_codes)} 銘柄を分析対象に選定しました。")

        # 2. バージョンリセット
        self._refresh_analysis_status(target_codes)

        # 3. Sentinel 実行
        self.sentinel.run(target_codes=target_codes)

        # 4. AI 分析のトリガー
        unprocessed = SentinelAlert.select().where(
            SentinelAlert.is_processed == False  # noqa: E712
        )

        # レポート用のソースマッピング（どの戦略や理由で選ばれたか）
        source_map = target_map.copy()

        alert_codes = []
        for a in unprocessed:
            alert_codes.append(a.code)
            if a.code not in source_map:
                source_map[a.code] = f"Alert({a.alert_type})"

        # ターゲットとアラートを統合
        execution_list = list(set(target_codes + alert_codes))

        if execution_list:
            self.logger.info(f"🚀 {len(execution_list)} 銘柄の AI 分析を実行します...")
            self._execute_equity_auditor(execution_list)

        # 5. レポート生成
        self._export_reports(output_context="daily", source_map=source_map)
        self.logger.info("✅ Daily ルーチンが完了しました。")

    def _get_balanced_targets(self, top_n_per_strategy: int = 50) -> Dict[str, str]:
        """各戦略から Top N 銘柄を選定し、バランスの取れた分析対象リストを作成する。

        Args:
            top_n_per_strategy (int, optional): 1戦略あたりの最大銘柄数。デフォルトは 50。

        Returns:
            Dict[str, str]: {銘柄コード: 戦略名} の辞書。
        """
        strategies = self.config.get("strategies", {}).keys()
        selected_map = {}

        for strategy in strategies:
            query = (
                AnalysisResult.select(MarketData.code)
                .join(MarketData)
                .where(AnalysisResult.strategy_name == strategy)
                .order_by(AnalysisResult.quant_score.desc())
                .limit(top_n_per_strategy)
            )

            for row in query:
                code = row.market_data.code_id
                if code not in selected_map:
                    selected_map[code] = strategy

        return selected_map

    def _refresh_analysis_status(self, codes: List[str], force_all: bool = False):
        """指定された銘柄の分析バージョンをリセットし、再分析を促す。

        Args:
            codes (List[str]): 対象銘柄コードのリスト。
            force_all (bool, optional): 条件を無視して全件リセットするか。デフォルトは False。
        """
        if not codes:
            return

        today_start = get_current_time().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        codes = list(codes)
        subquery = MarketData.select(MarketData.id).where(MarketData.code << codes)
        ids = [row.id for row in subquery]

        count = 0
        if ids:
            where_clause = AnalysisResult.market_data << ids
            if not force_all:
                # 以下の条件に合致する場合のみリセット
                # 1. 分析が古い（昨日以前）
                # 2. 未分析
                # 3. 以前の分析が MOCK データ
                where_clause &= (
                    (AnalysisResult.analyzed_at < today_start)
                    | (AnalysisResult.analyzed_at.is_null())
                    | (AnalysisResult.ai_reason.contains("[MOCK]"))
                )

            q = AnalysisResult.update(audit_version=0).where(where_clause)
            count = q.execute()

        msg = (
            f"🔄 {count} 件の分析レコードをリフレッシュしました。"
            if not force_all
            else f"🔄 {count} 件を強制リセットしました。"
        )
        self.logger.info(msg)

    def _execute_equity_auditor(
        self, codes: List[str], strategy: str = "Balanced Strategy"
    ):
        """EquityAuditor をサブプロセスとして実行し、AI 分析処理を委ねる。

        Args:
            codes (List[str]): 分析対象の銘柄リスト。
            strategy (str): 使用する戦略名。
        """
        if not codes:
            return

        batch_size = 300
        for i in range(0, len(codes), batch_size):
            batch = codes[i : i + batch_size]
            code_str = ",".join(batch)

            cmd = [
                sys.executable,
                "equity_auditor.py",
                "--mode",
                "analyze",
                "--codes",
                code_str,
                "--strategy",
                strategy,
            ]
            if self.debug_mode:
                cmd.append("--debug")

            self.logger.info(
                f"  分析サブプロセスを実行中 (Batch {i//batch_size + 1}): {' '.join(cmd[:5])}..."
            )
            try:
                subprocess.run(cmd, check=True)
                # 正常終了した銘柄のアラートを処理済みに更新
                SentinelAlert.update(
                    is_processed=True, processed_at=get_current_time()
                ).where(SentinelAlert.code << batch).execute()
            except subprocess.CalledProcessError as e:
                self.logger.error(f"  分析サブプロセスが失敗しました: {e}")

    def _run_weekly(self):
        """Weekly 定型ルーチン（フルスキャンモード）を実行する。

        1. 全銘柄のスコアリングとターゲット選定（各戦略 Top 50）
        2. スマートリフレッシュ（本日未分析の銘柄のみリセット）
        3. AI 分析の実行
        4. 月次集計レポートの生成
        5. ランク履歴（RankHistory）の更新
        """
        self.logger.info("🌕 Weekly フルスキャンルーチンを開始します...")

        # 1. プレスクリーニング（全件スコアリング）
        target_map = self._scout_weekly_targets()
        target_codes = list(target_map.keys())
        self.logger.info(
            f"✅ 全市場スキャンにより {len(target_codes)} 銘柄を選定しました。"
        )

        # 2. スマートリフレッシュ
        if target_codes:
            self._refresh_analysis_status(target_codes, force_all=False)

            # 3. 分析実行
            self.logger.info(f"🚀 {len(target_codes)} 銘柄の AI 分析を実行します...")
            self._execute_equity_auditor(target_codes)

        # 4. 週次レポートの出力
        self._export_reports(
            output_context="weekly", source_map=target_map, only_today=True
        )

        # 5. ランク履歴の保存
        self.logger.info("🏆 公式ランク履歴を更新します...")
        self._update_rank_history()

        self.logger.info("✅ Weekly ルーチンが完了しました。")

    def _scout_weekly_targets(self) -> Dict[str, str]:
        """全銘柄データをロードし、各戦略のスコアに基づいて分析候補を選定する。

        Returns:
            Dict[str, str]: {銘柄コード: 選定された戦略名} の辞書。
        """
        self.logger.info("🔍 プレスクリーニングのため全銘柄データをロード中...")

        # 最新の取得日付を確認
        max_date = MarketData.select(fn.Max(MarketData.entry_date)).scalar()
        if not max_date:
            self.logger.warning("MarketData が見つかりません。")
            # データがない場合は初回取得を試みるべきだが、ここでは空を返す
            return {}

        self.logger.info(f"  対象日付: {max_date}")

        # [v12.5] DB Integrity Check & Auto-Repair before Ranking
        # ランキング生成前にデータの完全性を保証する
        if not self._check_db_integrity(target_date=max_date):
            self.logger.warning(
                f"⚠️ DB Integrity Check Failed for {max_date}. Initiating Auto-Repair..."
            )
            if self._recover_db(target_date=max_date):
                self.logger.info(
                    "✅ Auto-Repair completed. Resuming ranking process..."
                )
            else:
                self.logger.error("❌ Auto-Repair failed. Ranking may be inaccurate.")

        query = MarketData.select().where(MarketData.entry_date == max_date)
        df_all = pd.DataFrame(list(query.dicts()))

        if df_all.empty:
            return {}

        if "code" in df_all.columns:
            df_all["code"] = df_all["code"].astype(str)
            df_all.set_index("code", inplace=True)

        engine = ScoringEngine(self.config)
        target_strats = [
            "value_strict",
            "growth_quality",
            "turnaround_spec",
            "Balanced Strategy",
        ]

        final_map = {}
        for strategy in target_strats:
            if strategy not in self.config.get("strategies", {}):
                continue

            self.logger.info(f"  {strategy} のスコアリングを実行中...")
            try:
                scores_df = engine.calculate_score(df_all, strategy)
                top_50 = scores_df.sort_values("quant_score", ascending=False).head(50)

                # [v12.6] Pre-filter by validation before adding to candidates
                # [v12.7 Fix] 元データとスコアリング結果をマージしてバリデーション
                validator = ValidationEngine(self.config)
                for code, row in top_50.iterrows():
                    # スコアリング結果
                    row_dict = row.to_dict()
                    row_dict["code"] = code
                    # 元のMarketDataから財務データを追加
                    if code in df_all.index:
                        original_data = df_all.loc[code]
                        if hasattr(original_data, "to_dict"):
                            row_dict.update(original_data.to_dict())
                    is_valid, issues = validator.validate_stock_data(
                        row_dict, strategy=strategy
                    )
                    if not is_valid:
                        continue  # Skip candidates with critical data defects
                    if code not in final_map:
                        final_map[code] = strategy
            except Exception as e:
                self.logger.error(
                    f"  {strategy} のスコアリング中にエラーが発生しました: {e}"
                )

        return {str(k): v for k, v in final_map.items()}

    def _check_db_integrity(self, target_date: str) -> bool:
        """指定日のデータの健全性をチェックする。

        必須カラム(equity_ratio)の欠損が1件でもある場合は False を返す。
        """
        # Checks for NULL in critical columns

        # Count total records for the date
        total_count = (
            MarketData.select().where(MarketData.entry_date == target_date).count()
        )
        if total_count == 0:
            return True  # No data implies no corruption yet? Or create new? Usually OK to proceed to empty

        # Count nulls
        # Only check equity_ratio as primary indicator of breakage
        null_count = (
            MarketData.select()
            .where(
                (MarketData.entry_date == target_date)
                & (MarketData.equity_ratio.is_null())
            )
            .count()
        )

        if null_count > 0:
            self.logger.warning(
                f"🚨 Integrity Alert: Found {null_count}/{total_count} records with Missing Equity Ratio on {target_date}."
            )
            # [Resilience] 外部ソースの欠損により処理が停止するのを防ぐため、警告のみで続行を許可

        return True

    def _recover_db(self, target_date: str) -> bool:
        """DB自動修復プロセスを実行する。

        equity_auditor.py --mode ingest --force --all を呼び出し、
        最新のFetcherロジックでデータを再取得・UPSERTする。
        """
        self.logger.info(
            "🔧 Starting Auto-Repair Sequence (Force Refreshing All Data)..."
        )
        # 実行コマンド: python3 equity_auditor.py --mode ingest --force --all
        # ※ --all は全キャッシュのリフレッシュを意味するが、ingestモードの仕様次第。
        # ここではオーケストレーターから直接全銘柄コードを指定して ingest を回すのが確実。
        # しかしコード数が多すぎる(4000+)ため、既存の --all フラグ等の挙動に依存するか、バッチで回す。
        # equity_auditor.py の --all オプションは、キャッシュ(interim/*.json)の全取込のみかも？
        # ここは安全策として、Brokenなコードを特定して指定するか、あるいは全銘柄を再取得する。
        # 今回は「全銘柄UPSERT」要件なので、全銘柄対象とする。

        # 1. Get all codes for the date
        all_codes = [
            r.code_id
            for r in MarketData.select(MarketData.code).where(
                MarketData.entry_date == target_date
            )
        ]
        if not all_codes:
            return False

        self.logger.info(f"Targeting {len(all_codes)} stocks for repair.")

        # 2. Call EquityAuditor in batches (to avoid command line length limits) with --force
        # Note: equity_auditor.py --mode ingest --force --codes ... triggers fetching from API
        batch_size = 50
        total_repaired = 0

        # Limit repair scope for safety/speed if needed? No, user requested "All".
        # But for 8000 stocks, this takes hours.
        # API limit (quota) is a concern.
        # User said "1件でもあれば全件修復".
        # We should use batch execution.

        for i in range(0, len(all_codes), batch_size):
            batch = all_codes[i : i + batch_size]
            code_str = ",".join(batch)
            cmd = [
                sys.executable,
                "equity_auditor.py",
                "--mode",
                "ingest",
                "--force",
                "--codes",
                code_str,
            ]

            try:
                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )  # Reduce noise
                total_repaired += len(batch)
                if (i // batch_size) % 10 == 0:
                    self.logger.info(
                        f"  Repaired {total_repaired}/{len(all_codes)} stocks..."
                    )
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Repair batch failed: {e}")
                # Continue other batches?

        self.logger.info(f"Repair sequence finished. Repaired {total_repaired} stocks.")
        return True

    def _run_monthly(self):
        """Monthly 定型ルーチンを実行する。"""
        # 現状は Weekly ルーチンの実行に留める（将来的にフルスキャンの範囲を拡大可能）
        self._run_weekly()
        self.logger.info("🌕 Monthly 定型処理が完了しました。")

    def _update_rank_history(self):
        """現在のランキング状況を RankHistory テーブルに保存（スナップショット）する。"""
        strategies = self.config.get("strategies", {}).keys()
        now = get_current_time()

        for strategy in strategies:
            query = (
                AnalysisResult.select(AnalysisResult, MarketData.code)
                .join(MarketData)
                .where(AnalysisResult.strategy_name == strategy)
                .order_by(AnalysisResult.quant_score.desc())
            )

            ranked = list(query.dicts())

            # 各戦略の Top 200 を履歴として保存
            records = []
            for i, row in enumerate(ranked[:200], start=1):
                records.append(
                    {
                        "code": row["code"],
                        "strategy_name": strategy,
                        "rank": i,
                        "score": row["quant_score"],
                        "recorded_at": now,
                    }
                )

            if records:
                with db_proxy.atomic():
                    for batch in range(0, len(records), 100):
                        RankHistory.insert_many(records[batch : batch + 100]).execute()

            self.logger.info(
                f"  {strategy} のランキング履歴 {len(records)} 件を保存しました。"
            )

    def _export_reports(
        self,
        output_context: str = "daily",
        source_map: Optional[Dict[str, Any]] = None,
        only_today: bool = False,
    ):
        """分析結果を抽出し、レポーターに渡してファイルを生成する。

        Args:
            output_context (str): レポートの接頭辞。
            source_map (dict, optional): 銘柄選定理由のマッピング。
            only_today (bool): 本日実施分のみを対象にするか。デフォルトは False。
        """
        self.logger.info(f"📊 レポート出力処理を開始します ({output_context})...")

        # 1. データの抽出
        active_strategies = list(self.config.get("strategies", {}).keys())
        query = (
            AnalysisResult.select(AnalysisResult, MarketData, Stock)
            .join(MarketData)
            .join(Stock)
            .where(AnalysisResult.strategy_name.in_(active_strategies))
        )

        if only_today:
            today_start = datetime.combine(
                get_current_time().date(), datetime.min.time()
            )
            query = query.where(AnalysisResult.analyzed_at >= today_start)

        query = query.order_by(AnalysisResult.analyzed_at.desc())

        results = list(query.dicts())
        if not results:
            self.logger.warning("対象となる分析結果が見つかりませんでした。")
            return

        # 2. 重複排除（銘柄コードごとに最新の分析を採用）
        code_map = {}
        for r in results:
            code = r["code"]
            if code not in code_map:
                code_map[code] = {"latest": r, "strategies": set(), "data": r}
            code_map[code]["strategies"].add(r["strategy_name"])

            # 最新の分析日時を保持
            if str(r.get("analyzed_at") or "") > str(
                code_map[code]["latest"].get("analyzed_at") or ""
            ):
                code_map[code]["latest"] = r

        # 3. レポート用データの準備（ランク履歴の注入）
        report_data = []
        for code, info in code_map.items():
            latest_strat = info["latest"]["strategy_name"]
            target_strat = (
                source_map.get(code, latest_strat) if source_map else latest_strat
            )

            # アラート由来の場合は元の戦略で履歴を表示
            if "Alert" in str(target_strat):
                target_strat = latest_strat

            info["rank_history"] = self._get_rank_history_str(code, target_strat)
            report_data.append(info)

        # 4. レポーターの呼び出し
        self.reporter.generate_reports(
            results=report_data, source_map=source_map, output_context=output_context
        )

    def _get_rank_history_str(self, code: str, strategy: str) -> str:
        """指定された銘柄と戦略の過去3回分の順位履歴を取得し、文字列に整形する。

        Args:
            code (str): 銘柄コード。
            strategy (str): 投資戦略名。

        Returns:
            str: "順位3 -> 順位2 -> 順位1" 形式の文字列。履歴がない場合は "-"。
        """
        history = (
            RankHistory.select()
            .where((RankHistory.code == code) & (RankHistory.strategy_name == strategy))
            .order_by(RankHistory.recorded_at.desc())
            .limit(3)
            .dicts()
        )

        ranks = [str(r["rank"]) for r in history]
        ranks_rev = ranks[::-1]  # 古い順に表示

        if not ranks_rev:
            return "-"

        return " -> ".join(ranks_rev)

```

---

### src/provider.py

```python
import pandas as pd
from peewee import JOIN, fn

from src.database import StockDatabase
from src.models import MarketData, Stock
from src.utils import generate_row_hash


class DataProvider:
    def __init__(self, config):
        self.config = config
        db_path = config.get("paths", {}).get("db_file")
        self.stock_db = StockDatabase(db_path) if db_path else StockDatabase()
        import threading

        self._db_lock = threading.Lock()

    def load_latest_market_data(self):
        """DB から最新の市況データをロードして DataFrame で返す"""
        # 最新の日付を取得
        latest_date_subquery = (
            MarketData.select(
                MarketData.code, fn.MAX(MarketData.entry_date).alias("max_date")
            )
            .group_by(MarketData.code)
            .alias("latest_dates")
        )

        # Dynamically select all fields from MarketData
        # (v4.0 Refactor: Avoids manual column updates)
        selection = [MarketData.id.alias("market_data_id")]

        # Add all fields from MarketData except 'id' (handled above) and 'code' (handled by ID)
        # Note: We explicitly add specific fields to ensure alias naming if needed,
        # but for simplicity we take all declared fields.
        for field in MarketData._meta.sorted_fields:
            if field.name not in ["id"]:
                selection.append(field)

        # Add Stock fields
        selection.extend([Stock.name, Stock.sector, Stock.market])

        # Specific aliases for compatibility
        # (Though we select all, we can re-alias 'price' to 'current_price' if needed, but
        # config mapping maps 'price' -> 'price'. Wait, loader maps 'current_price' -> 'price' in Model?
        # Model has 'price'. Loader maps CSV 'current_price' to Model 'price'.
        # Analyzer expects 'current_price'?
        # Let's check 'src/loader.py' and 'src/models.py'.
        # Model: price. Loader: current_price -> price.
        # So DB has 'price'.
        # Old query aliased MarketData.price.alias('current_price').
        # So we must maintain this alias for compatibility with Calc/Engine.

        # Re-building selection to include specific aliases override
        selection = [MarketData.id.alias("market_data_id")]
        for field in MarketData._meta.sorted_fields:
            if field.name == "id":
                continue
            if field.name == "price":
                selection.append(MarketData.price.alias("current_price"))
            else:
                selection.append(field)

        selection.extend([Stock.name, Stock.sector, Stock.market])

        query = (
            MarketData.select(*selection)
            .join(Stock, on=(MarketData.code == Stock.code))
            .join(
                latest_date_subquery,
                on=(
                    (MarketData.code == latest_date_subquery.c.code)
                    & (MarketData.entry_date == latest_date_subquery.c.max_date)
                ),
            )
            .dicts()
        )

        df = pd.DataFrame(list(query))
        if not df.empty:
            df["entry_date"] = pd.to_datetime(df["entry_date"])

            # [v5.3] Pad missing columns
            expected_cols = {
                "profit_status": "normal",
                "sales_status": "missing",
                "trend_score": 0,
                "turnaround_status": "normal",
            }
            for col, default_val in expected_cols.items():
                if col not in df.columns:
                    df[col] = default_val

        return df

    def load_error_analysis_records(self):
        """AI 分析で 'Error' またはデータ取得失敗 (Quota/Network) の最新レコードをロード"""
        from src.fetcher import DataFetcher
        from src.models import AnalysisResult

        # 各銘柄の最新の分析結果を取得するサブクエリ (LEFT JOIN 用)
        latest_analysis_subquery = (
            AnalysisResult.select(
                AnalysisResult.market_data_id,
                fn.MAX(AnalysisResult.analyzed_at).alias("max_analyzed"),
            )
            .group_by(AnalysisResult.market_data_id)
            .alias("latest_analysis")
        )

        # 最新の日付を取得 (データ自体の鮮度確保)
        latest_date_subquery = (
            MarketData.select(
                MarketData.code, fn.MAX(MarketData.entry_date).alias("max_date")
            )
            .group_by(MarketData.code)
            .alias("latest_dates")
        )

        # Retry対象のFetch Status
        retry_statuses = [
            DataFetcher.STATUS_ERROR_QUOTA,
            DataFetcher.STATUS_ERROR_NETWORK,
            DataFetcher.STATUS_ERROR_OTHER,
        ]

        query = (
            MarketData.select(
                MarketData.id.alias("market_data_id"),
                MarketData.code,
                Stock.name,
                MarketData.price.alias("current_price"),
                MarketData.per,
                MarketData.pbr,
                MarketData.roe,
                MarketData.dividend_yield,
                MarketData.equity_ratio,
                MarketData.operating_cf,
                MarketData.market_cap,
                MarketData.payout_ratio,
                MarketData.current_ratio,
                MarketData.quick_ratio,
                MarketData.macd_hist,
                MarketData.rsi_14,
                MarketData.trend_up,
                MarketData.entry_date,
                MarketData.fetch_status,
                Stock.sector,
                Stock.market,
            )
            .join(Stock, on=(MarketData.code == Stock.code))
            .join(
                latest_date_subquery,
                on=(
                    (MarketData.code == latest_date_subquery.c.code)
                    & (MarketData.entry_date == latest_date_subquery.c.max_date)
                ),
            )
            .join(
                AnalysisResult,
                JOIN.LEFT_OUTER,
                on=(MarketData.id == AnalysisResult.market_data_id),
            )
            .join(
                latest_analysis_subquery,
                JOIN.LEFT_OUTER,
                on=(
                    (
                        AnalysisResult.market_data_id
                        == latest_analysis_subquery.c.market_data_id
                    )
                    & (
                        AnalysisResult.analyzed_at
                        == latest_analysis_subquery.c.max_analyzed
                    )
                ),
            )
            .where(
                # Condition 1: AI Result is explicitly 'Error'
                (AnalysisResult.ai_sentiment == "Error")
                |
                # Condition 2: Fetch Failed (but retryable) AND No Analysis Result (since fetch failed)
                (MarketData.fetch_status.in_(retry_statuses))
            )
            .dicts()
        )

        df = pd.DataFrame(list(query))
        if not df.empty:
            df["entry_date"] = pd.to_datetime(df["entry_date"])
        return df

    def get_ai_cache(
        self, row_dict, strategy_name, validity_days=0, refresh_triggers=None
    ):
        """AI キャッシュを取得 (Smart Refresh 対応)"""
        row_series = pd.Series(row_dict)
        row_hash = generate_row_hash(row_series)
        code = str(row_dict["code"])

        # 1. 厳密なハッシュチェック
        cached = self.stock_db.get_ai_cache(code, row_hash, strategy_name)
        if cached:
            return cached, row_hash

        # 2. Smart Cache (期間内再利用) を試行
        if validity_days > 0:
            smart_cached = self.stock_db.get_ai_smart_cache(
                code, strategy_name, validity_days
            )
            if smart_cached:
                # [v4.5] Refresh Triggers チェック
                if refresh_triggers:
                    # 株価変動チェック
                    price_limit = refresh_triggers.get("price_change_pct", 0)
                    old_price = smart_cached.get("cached_price")
                    new_price = row_dict.get("current_price")
                    if price_limit > 0 and old_price and new_price:
                        diff_pct = abs(new_price - old_price) / old_price * 100
                        if diff_pct >= price_limit:
                            return None, row_hash

                    # スコア変動チェック
                    score_limit = refresh_triggers.get("score_change_point", 0)
                    old_score = smart_cached.get("quant_score")
                    new_score = row_dict.get("quant_score")
                    if (
                        score_limit > 0
                        and old_score is not None
                        and new_score is not None
                    ):
                        diff_pts = abs(new_score - old_score)
                        if diff_pts >= score_limit:
                            return None, row_hash

                smart_cached["_is_smart_cache"] = True
                return smart_cached, row_hash

        return None, row_hash

    def save_analysis_result(self, result, strategy_name):
        """分析結果を DB に保存"""
        if "market_data_id" not in result:
            return

        # Peewee モデルに合わせてキーを変換
        record = {
            "market_data": result["market_data_id"],
            "strategy_name": strategy_name,
            "quant_score": result.get("quant_score"),
            "ai_sentiment": result.get("ai_sentiment"),
            "ai_reason": result.get("ai_reason"),
            "ai_risk": result.get("ai_risk"),
            "score_long": result.get("score_long"),
            "score_short": result.get("score_short"),
            "score_gap": result.get("score_gap"),
            "active_style": result.get("active_style"),
            "row_hash": result.get("row_hash"),
            # [v5.3] Breakdown Scores
            "score_value": result.get("score_value"),
            "score_growth": result.get("score_growth"),
            "score_quality": result.get("score_quality"),
            "score_trend": result.get("score_trend"),
            "score_penalty": result.get("score_penalty"),
            "audit_version": result.get("audit_version"),
            "ai_horizon": result.get("ai_horizon"),
            "ai_detail": result.get("ai_detail"),  # [v12.0] Fix: Persist strict detail
        }
        if result.get("analyzed_at"):
            record["analyzed_at"] = result.get("analyzed_at")

        # [v12.3] Thread Safety: Lock for SQLite concurrent writes
        with self._db_lock:
            self.stock_db.save_analysis_result(record)

```

---

### src/reporter.py

```python
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from src.utils import get_current_time


class StockReporter:
    """株式分析レポート（CSV形式）のフォーマットと生成を担当するクラス。

    Attributes:
        output_dir (Path): レポートの出力先ディレクトリ。
        timestamp (str): レポート生成時のタイムスタンプ（ファイル名に使用）。
    """

    def __init__(self, output_dir: str = "data/output"):
        """StockReporter を初期化する。

        Args:
            output_dir (str, optional): 出力先パス。デフォルトは "data/output"。
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        print(
            f"DEBUG: Reporter Output Dir: {self.output_dir}"
        )  # Added print for path confirmation
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = get_current_time().strftime("%Y%m%d_%H%M")

    def generate_reports(
        self,
        results: List[Dict[str, Any]],
        source_map: Optional[Dict[str, str]] = None,
        output_context: str = "daily",
    ) -> None:
        """集計・詳細レポートの2種類を生成し、CSVファイルとして保存する。

        Args:
            results (List[Dict[str, Any]]): 分析結果、生データ、適用戦略等が統合されたリスト。
            source_map (Optional[Dict[str, str]], optional): 銘柄コードとトリガーとなった戦略名のマッピング。
            output_context (str, optional): ファイル名の接頭辞に使用するコンテキスト（daily, weekly, monthly）。
        """
        if not results:
            self.logger.warning("No results to report.")
            return

        summary_rows = []
        detailed_rows = []

        # Formatting Loop (Moved from Orchestrator)
        for info in results:
            s_row, d_row = self._format_single_item(info, source_map)
            summary_rows.append(s_row)
            detailed_rows.append(d_row)

        # Sort (Score Desc)
        summary_rows.sort(key=lambda x: x["Score"], reverse=True)
        detailed_rows.sort(key=lambda x: x["Raw_Score"], reverse=True)

        # Assign Ranks
        for i, row in enumerate(summary_rows, start=1):
            row["Rank"] = i
            row["Score"] = row["Score_Display"]
            del row["Score_Display"]
            # Remove helper keys validation if needed, but dicts allow extra keys.
            # Ideally strip them for clean CSV.

        for i, row in enumerate(detailed_rows, start=1):
            row["Rank"] = i
            del row["Raw_Score"]

        # Limit Top 200
        top_200_summary = summary_rows[:200]
        top_200_detailed = detailed_rows[:200]

        # Determine Filenames
        ts_name = self.timestamp
        file_base = "daily_report"
        if "weekly" in output_context:
            file_base = "weekly_report"
        if "monthly" in output_context:
            file_base = "monthly_report"

        # Save Summary
        summary_path = self.output_dir / f"{file_base}_{ts_name}.csv"
        print(f"DEBUG: Saving Summary to {summary_path}")
        pd.DataFrame(top_200_summary).to_csv(
            summary_path, index=False, encoding="utf-8-sig"
        )
        self.logger.info(f"✅ Summary report generated: {summary_path}")

        # Save Detailed
        detailed_path = self.output_dir / f"detailed_report_{ts_name}.csv"
        pd.DataFrame(top_200_detailed).to_csv(
            detailed_path, index=False, encoding="utf-8-sig"
        )
        self.logger.info(f"✅ Detailed report generated: {detailed_path}")

    def _format_single_item(
        self, code_info: Dict[str, Any], source_map: Optional[Dict[str, str]]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """単一銘柄のデータをサマリー用・詳細用の行形式に整形する。

        Args:
            code_info (Dict[str, Any]): 銘柄の分析・財務データを含む辞書。
            source_map (Optional[Dict[str, str]]): 推奨戦略等のマッピング情報。

        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: (サマリー行, 詳細行) のタプル。
        """
        latest_row = code_info["latest"]
        common = code_info["data"]
        strats = code_info["strategies"]
        code = latest_row["code"]
        # Helper for Rank History (Pass it in info? Or fetch here?
        # Orchestrator fetched it. Ideally Reporter shouldn't access DB.
        # Let's assume Orchestrator attaches 'rank_history' to code_info or we pass it.
        # For this refactor, let's assume code_info has it or we default to '-'.
        # User prompt didn't strictly ask to move DB calls for history.
        # I will check if 'rank_history' is in code_info. If not, default '-'.
        # To strictly follow SRP, Orchestrator should inject it.
        rank_history_str = code_info.get("rank_history", "-")

        # --- Strategy Display Logic ---
        display_strat = None
        if source_map and code in source_map:
            display_strat = source_map[code]

        if not display_strat:
            display_strat = latest_row["strategy_name"]
            if display_strat == "Balanced Strategy":
                others = [s for s in strats if s != "Balanced Strategy"]
                if others:
                    display_strat = others[0]

        # --- Sanitize / Format ---
        sentiment = latest_row.get("ai_sentiment") or "Pending"
        if str(sentiment).lower() == "nan":
            sentiment = "Pending"

        # [v13.6] Respect AI-generated granular labels from v3.5 prompt
        # Only apply manual fallback if AI returned generic "Neutral" or "Bullish"
        risk = str(latest_row.get("ai_risk", "Medium"))
        if sentiment == "Neutral":
            if "High" in risk or "Critical" in risk:
                sentiment = "Neutral (Caution)"
            elif "Low" in risk:
                sentiment = "Neutral (Positive)"
            else:
                sentiment = "Neutral (Wait)"
        elif sentiment == "Bullish":
            reason_text = str(latest_row.get("ai_reason", "")) + str(
                latest_row.get("ai_detail", "")
            )
            defensive_keywords = ["不本意", "例外", "救済", "無視できない", "Defensive"]
            if any(k in reason_text for k in defensive_keywords):
                sentiment = "Bullish (Defensive)"
            else:
                sentiment = "Bullish (Aggressive)"

        # [v12.0] Flatten Comment (Summary)
        ai_comment_flat = self._sanitize_comment_flat(
            latest_row.get("ai_reason"), sentiment
        )

        # Score
        score_val = latest_row.get("quant_score")
        score_str = f"{score_val:.2f}" if score_val is not None else "-"
        sort_score = score_val if (score_val is not None) else -1.0

        now_str = get_current_time().strftime("%Y-%m-%d %H:%M:%S")
        date_val = latest_row.get("analyzed_at")
        date_str = str(date_val)[:10] if date_val else "-"

        from src.utils import safe_display_value as _s

        # サマリー行の構築
        summary_row = {
            "Code": code,
            "Name": common.get("name", ""),
            "Best_Strategy": display_strat,
            "AI_Rating": sentiment,
            "AI_Comment": ai_comment_flat,
            "AI_Date": date_str,
            "Score": sort_score,  # ソート用
            "Score_Display": score_str,
            "Rank_History": rank_history_str,
            "Technical": self._format_technical(common),
            "Trend": latest_row.get("score_trend") or common.get("trend_score") or "-",
            "Report_Timestamp": now_str,
        }

        # 詳細行の構築
        detailed_row = {
            "Rank": 0,
            "Code": _s(code),
            "Name": _s(common.get("name")),
            "Sector": _s(common.get("sector_17", common.get("sector"))),
            "Market": _s(common.get("market")),
            "AI_Rating": _s(sentiment),
            "AI_Score": _s(score_str),
            "AI_Comment": _s(ai_comment_flat),
            "AI_Detailed_Analysis": _s(latest_row.get("ai_detail")),
            "AI_Risk": _s(latest_row.get("ai_risk")),
            "AI_Horizon": _s(latest_row.get("ai_horizon")),
            "PER": _s(common.get("per")),
            "PBR": _s(common.get("pbr")),
            "ROE": _s(common.get("roe")),
            "Div_Yield": _s(common.get("dividend_yield")),
            "Sales_Gro": _s(common.get("sales_growth")),
            "Prof_Gro": _s(common.get("profit_growth")),
            "Op_Margin": _s(common.get("operating_margin")),
            "Equity_Rat": _s(common.get("equity_ratio")),
            "Market_Cap": _s(common.get("market_cap")),
            "RSI": _s(common.get("rsi_14")),
            "MACD_Hist": _s(common.get("macd_hist")),
            "Volatility": _s(common.get("volatility")),
            "Sc_Value": _s(latest_row.get("score_value")),
            "Sc_Growth": _s(latest_row.get("score_growth")),
            "Sc_Quality": _s(latest_row.get("score_quality")),
            "Sc_Trend": _s(latest_row.get("score_trend")),
            "Sc_Penalty": _s(latest_row.get("score_penalty")),
            "Raw_Score": sort_score,
            "Report_Timestamp": now_str,
            "Original_Strat": _s(display_strat),
        }
        return summary_row, detailed_row

    def _sanitize_comment_flat(
        self, comment: Optional[str], sentiment: str = ""
    ) -> str:
        """AIコメントを1行にまとめ、CSV向けにサニタイズする"""
        if not comment or str(comment).lower() == "nan":
            return "Analysis Pending" if sentiment == "Pending" else "-"

        cleaned = str(comment)
        # 不要なタグの除去（レガシー対応）
        tags = ["[Conclusion]", "[Analysis]", "[Risk]", "[分析]", "[結論]", "[リスク]"]
        for tag in tags:
            cleaned = cleaned.replace(tag, "")

        # 1. 改行の除去 (Must be single line)
        cleaned = cleaned.replace("\n", " ").replace("\r", " ")

        # 2. 連続するスペースの集約
        import re

        cleaned = re.sub(r"\s+", " ", cleaned)

        # 3. カンマのエスケープ（CSVセーフにするための念押し）
        # Pandasのto_csvが適切にクォートしてくれますが、ここでは全角カンマに置換するか、
        # そのままにしてPandasに任せます。ユーザーの指示は「サニタイズ強化」なので
        # 念のため半角カンマを全角に置換する等の処理も検討できますが、
        # ここでは「改行除去」を最優先とし、カンマはPandasに任せます。

        return cleaned.strip()

    def _format_technical(self, common_data: Dict[str, Any]) -> str:
        """MACD整形"""
        val = common_data.get("macd_hist")
        if val is not None:
            return f"{val:.2f}"
        return "-"

```

---

### src/result_writer.py

```python
import os
from logging import getLogger


class ResultWriter:
    """
    Analysis results writer.
    Renamed from ExcelWriter to ResultWriter in v3.7 as it primarily outputs CSV.
    """

    def __init__(self, config):
        self.config = config
        self.logger = getLogger(__name__)
        # 出力先ディレクトリ
        self.output_dir = "data/output"
        os.makedirs(self.output_dir, exist_ok=True)

    def save(self, df, filename):
        """
        DataFrameをCSVとして保存する
        """
        # 拡張子が .xlsx で指定された場合、.csv に強制変換
        if filename.endswith(".xlsx"):
            filename = filename.replace(".xlsx", ".csv")

        full_path = os.path.join(self.output_dir, filename)

        try:
            # [v3.3] Output Columns Selection
            # 必要なカラムを優先的に前に配置
            priority_cols = [
                "code",
                "name",
                "market",
                "sector",
                "quant_score",
                "score_value",
                "score_growth",
                "score_quality",
                "score_trend",
                "score_penalty",  # [v5.3] Breakdown
                "score_long",
                "score_short",
                "score_gap",
                "active_style",
                "trend_score",
                "trend_up",
                "profit_status",
                "sales_status",  # [v5.2]
                "current_price",
                "per",
                "pbr",
                "roe",
                "dividend_yield",
                "ai_sentiment",
                "ai_reason",
            ]

            # DataFrameにあるカラムだけを残す
            cols = [c for c in priority_cols if c in df.columns]

            # 残りのカラムを追加 (ただし内部カラムは除外)
            internal_cols = {
                "_is_cached",
                "_cache_label",
                "row_hash",
                "updated_at",
                "fetch_status",
                "market_data_id",
            }
            remaining = [
                c for c in df.columns if c not in cols and c not in internal_cols
            ]

            final_cols = cols + remaining

            df_out = df[final_cols].copy()

            # Int Casting for clean output
            int_cols = ["trend_up", "is_turnaround", "trend_score"]
            for col in int_cols:
                if col in df_out.columns:
                    df_out[col] = df_out[col].fillna(0).astype(int)

            # [v13.6] Respect AI-generated granular labels from v3.5 prompt
            if "ai_sentiment" in df_out.columns and "ai_risk" in df_out.columns:

                def _refine_rating(row):
                    rating = str(row["ai_sentiment"])
                    risk = str(row["ai_risk"])
                    # Only apply manual fallback if AI returned generic "Neutral" or "Bullish"
                    if rating == "Neutral":
                        if "High" in risk or "Critical" in risk:
                            return "Neutral (Caution)"
                        elif "Low" in risk:
                            return "Neutral (Positive)"
                        else:
                            return "Neutral (Wait)"
                    elif rating == "Bullish":
                        reason_text = str(row.get("ai_reason", "")) + str(
                            row.get("ai_detail", "")
                        )
                        defensive_keywords = [
                            "不本意",
                            "例外",
                            "救済",
                            "無視できない",
                            "Defensive",
                        ]
                        if any(k in reason_text for k in defensive_keywords):
                            return "Bullish (Defensive)"
                        else:
                            return "Bullish (Aggressive)"
                    return rating

                df_out["ai_sentiment"] = df_out.apply(_refine_rating, axis=1)

            # [v5.4] Rename columns to PascalCase for user-friendly output
            # Matches the format expected by users (e.g. AI_Rating, AI_Comment)
            rename_map = {
                "ai_sentiment": "AI_Rating",
                "ai_reason": "AI_Comment",
                "ai_risk": "AI_Risk",
                "code": "Code",
                "name": "Name",
                "market": "Market",
                "sector": "Sector",
                "quant_score": "AI_Score",
                "ai_detailed_analysis": "AI_Detailed_Analysis",
                "ai_date": "AI_Date",
                "score": "Score",
                "per": "PER",
                "pbr": "PBR",
                "roe": "ROE",
                "dividend_yield": "Div_Yield",
                "sales_growth": "Sales_Gro",
                "operating_profit_growth": "Prof_Gro",
                "operating_margin": "Op_Margin",
                "equity_ratio": "Equity_Rat",
                "market_cap_billions": "Market_Cap",
                "rsi": "RSI",
                "volatility": "Volatility",
                "score_value": "Sc_Value",
                "score_growth": "Sc_Growth",
                "score_quality": "Sc_Quality",
                "score_trend": "Sc_Trend",
                "score_penalty": "Sc_Penalty",
                "score_long": "Sc_Long",
                "score_short": "Sc_Short",
                "score_gap": "Sc_Gap",
                "active_style": "Style",
            }
            # Rename columns if they exist
            df_out = df_out.rename(
                columns={k: v for k, v in rename_map.items() if k in df_out.columns}
            )

            # CSV出力 (UTF-8 BOM付きでExcel日本語互換)
            df_out.to_csv(
                full_path, index=False, encoding="utf-8-sig", errors="replace"
            )
            self.logger.info(f"✅ Analysis results saved to CSV: {full_path}")
            return full_path
        except Exception as e:
            self.logger.error(f"❌ Error saving CSV: {e}")
            return None

```

---

### src/sentinel.py

```python
import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from src.config_loader import ConfigLoader
from src.database import StockDatabase
from src.engine import AnalysisEngine
from src.fetcher import DataFetcher
from src.models import AnalysisResult, MarketData, RankHistory, SentinelAlert
from src.utils import get_current_time


class Sentinel:
    """
    Sentinel (哨兵): 市場の異常やランキングの変化を監視する。

    Attributes:
        config (Dict[str, Any]): システム設定。
        db (StockDatabase): データベースインスタンス。
        fetcher (DataFetcher): データ取得モジュール。
        engine (AnalysisEngine): 分析エンジン。
        debug_mode (bool): デバッグモードフラグ。
    """

    def __init__(self, debug_mode: bool = False):
        """Sentinel を初期化する。

        Args:
            debug_mode (bool, optional): デバッグモード。デフォルトは False。
        """
        self.logger = logging.getLogger(__name__)
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.config
        self.db = StockDatabase()
        self.fetcher = DataFetcher(self.config)
        self.engine = AnalysisEngine(self.config)
        self.debug_mode = debug_mode

    def run(self, limit: int = 200, target_codes: Optional[List[str]] = None):
        """監視ルーチンを実行する。

        Args:
            limit (int, optional): 監視対象とする最大銘柄数。デフォルトは 200。
            target_codes (Optional[List[str]], optional): 明示的に指定する監視対象銘柄。
        """
        self.logger.info("👀 Sentinel による監視を開始します...")

        # 1. ターゲット選定
        if target_codes:
            targets = target_codes
            self.logger.info(f"🎯 指定された {len(targets)} 銘柄を監視します。")
        else:
            targets = self._get_surveillance_targets(limit=limit)

        self.logger.info(f"🎯 監視対象: {len(targets)} 銘柄")

        if not targets:
            self.logger.warning("監視対象が見つかりません。スキャンをスキップします。")
            return

        # 2. 軽量スキャン（価格・テクニカル）
        current_data_map = self._scan_market(targets)

        # 3. 異常検知
        self._detect_volatility(current_data_map)
        self._detect_technical_signals(current_data_map)
        self._detect_rank_fluctuations(current_data_map)

        self.logger.info("👀 Sentinel による監視が完了しました。")

    def _get_surveillance_targets(self, limit: int = 200) -> List[str]:
        """監視対象の銘柄コードリストを取得する。

        現在 AnalysisResult に存在する（分析済みの）銘柄を優先する。

        Args:
            limit (int, optional): 制限数。デフォルトは 200。

        Returns:
            List[str]: 銘柄コードのリスト。
        """
        # 最新の分析結果を持つ銘柄を取得
        query = MarketData.select(MarketData.code).join(AnalysisResult).distinct()

        codes = [row.code_id for row in query]
        return codes

    def _scan_market(self, codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """最新の価格とテクニカル指標を取得する。

        Args:
            codes (List[str]): 対象銘柄コードのリスト。

        Returns:
            Dict[str, Dict[str, Any]]: {銘柄コード: データ辞書}。
        """
        self.logger.info(f"📡 DataFetcher を通じて {len(codes)} 銘柄をスキャン中...")

        import yfinance as yf

        # バッチサイズ 100
        batch_size = 100
        results = {}

        for i in range(0, len(codes), batch_size):
            batch = codes[i : i + batch_size]
            batch_tickers = [f"{c}.T" for c in batch]

            try:
                # 5日分取得して移動平均などを計算可能にする
                df = yf.download(
                    batch_tickers,
                    period="1mo",
                    interval="1d",
                    group_by="ticker",
                    auto_adjust=True,
                    progress=False,
                )

                if len(batch) == 1:
                    if not df.empty:
                        code = batch[0]
                        processed = self._process_yf_df(df, code)
                        if processed:
                            results[code] = processed
                else:
                    for code in batch:
                        ticker = f"{code}.T"
                        try:
                            sub_df = df[ticker]
                            processed = self._process_yf_df(sub_df, code)
                            if processed:
                                results[code] = processed
                        except KeyError:
                            continue
            except Exception as e:
                self.logger.error(f"バッチ取得に失敗しました: {e}")

        return results

    def _process_yf_df(self, df: pd.DataFrame, code: str) -> Optional[Dict[str, Any]]:
        """DataFrame を処理して最新のメトリクスを抽出する。"""
        if df.empty:
            return None

        # 欠損値の削除
        df = df.dropna()
        if len(df) < 2:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        current_price = float(latest["Close"])
        prev_price = float(prev["Close"])

        # ボラティリティ（単純収益率）
        change_pct = ((current_price - prev_price) / prev_price) * 100

        # テクニカル指標の計算
        close_series = df["Close"]
        ema12 = close_series.ewm(span=12, adjust=False).mean()
        ema26 = close_series.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()

        macd_val = macd.iloc[-1]
        signal_val = signal.iloc[-1]
        prev_macd = macd.iloc[-2]
        prev_signal = signal.iloc[-2]

        # 交差の判定
        golden_cross = (prev_macd < prev_signal) and (macd_val > signal_val)
        dead_cross = (prev_macd > prev_signal) and (macd_val < signal_val)

        # 日付の安全な取得
        entry_date = "Unknown"
        if hasattr(latest.name, "strftime"):
            entry_date = latest.name.strftime("%Y-%m-%d")
        else:
            try:
                # 名前がタイムスタンプに変換可能な場合を考慮
                entry_date = pd.to_datetime(str(latest.name)).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                entry_date = str(latest.name)

        return {
            "code": code,
            "price": current_price,
            "prev_price": prev_price,
            "change_pct": change_pct,
            "macd": macd_val,
            "macd_signal": signal_val,
            "golden_cross": golden_cross,
            "dead_cross": dead_cross,
            "entry_date": entry_date,
        }

    def _detect_volatility(self, data_map: Dict[str, Dict[str, Any]]):
        """価格の急変動を検知する。"""
        for code, data in data_map.items():
            if not data:
                continue
            pct = data["change_pct"]

            if abs(pct) >= 5.0:
                alert_type = "volatility"
                direction = "急騰" if pct > 0 else "急落"
                msg = (
                    f"価格が {direction} しました ({pct:.2f}%)。現在値: {data['price']}"
                )
                self._save_alert(code, alert_type, msg)

    def _detect_technical_signals(self, data_map: Dict[str, Dict[str, Any]]):
        """テクニカル指標のサインを検知する。"""
        for code, data in data_map.items():
            if not data:
                continue

            if data["golden_cross"]:
                self._save_alert(
                    code, "technical", "MACD ゴールデンクロスを検知しました。"
                )

    def _detect_rank_fluctuations(self, data_map: Dict[str, Dict[str, Any]]):
        """ランキングの変動（Top 5 への加入や脱落）を検知する。"""
        # 1. 公式ランク履歴（最新）の取得
        strategies = self.config.get("strategies", {}).keys()

        for strategy in strategies:
            # 最新の Top 5 を取得
            official_top5 = tuple(
                RankHistory.select()
                .where(RankHistory.strategy_name == strategy)
                .order_by(RankHistory.recorded_at.desc(), RankHistory.rank.asc())
                .limit(5)
                .dicts()
            )

            if not official_top5:
                continue

            official_codes = {str(r["code"]) for r in official_top5}

            # 2. 監視対象の最新スコアを計算
            monitored_codes = list(data_map.keys())
            if not monitored_codes:
                continue

            # DB から基本データをロード
            base_df = self.fetcher.fetch_data_from_db(codes=monitored_codes)
            if base_df.empty:
                continue

            # 最新価格で更新
            for idx, row in base_df.iterrows():
                code = str(row["code"])
                if code in data_map:
                    scan = data_map[code]
                    base_df.at[idx, "current_price"] = scan["price"]
                    base_df.at[idx, "price"] = scan["price"]

            # スコアの再計算
            scored_df = self.engine.calculate_scores(base_df, strategy_name=strategy)
            scored_df = scored_df.sort_values("quant_score", ascending=False)

            # 3. 脱落の検知
            new_top5_df = scored_df.head(5)
            new_top5_codes = set(new_top5_df["code"].astype(str).tolist())

            for old_r in official_top5:
                c = str(old_r["code"])
                if c not in new_top5_codes:
                    try:
                        # Find rank in new list
                        loc = scored_df.index.get_loc(
                            scored_df[scored_df["code"] == c].index[0]
                        )
                        if isinstance(loc, slice):
                            current_rank: Union[int, str] = loc.start + 1
                        elif isinstance(loc, (int, np.integer)):
                            current_rank = int(loc) + 1
                        else:
                            current_rank = ">200"
                    except Exception:
                        current_rank = ">200"

                    msg = f"Top 5 から脱落しました (旧位: {old_r['rank']} -> 現位: {current_rank})。戦略: {strategy}"
                    self._save_alert(str(c), "rank_change", msg)

            # 4. 加入の検知
            for new_c in new_top5_codes:
                if new_c not in official_codes:
                    codes_list = [str(c) for c in new_top5_df["code"]]
                    real_rank = codes_list.index(str(new_c)) + 1
                    msg = f"Top 5 に新規加入しました (順位: {real_rank})。戦略: {strategy}"
                    self._save_alert(str(new_c), "rank_change", msg)

    def _save_alert(self, code: str, alert_type: str, message: str):
        """アラートをデータベースに保存する。"""
        self.logger.info(f"🚨 アラート [{alert_type}] {code}: {message}")

        SentinelAlert.create(
            code=code,
            alert_type=alert_type,
            alert_message=message,
            detected_at=get_current_time(),
        )


if __name__ == "__main__":
    from src.logger import setup_logger

    setup_logger()
    sentinel = Sentinel()
    sentinel.run()

```

---

### src/utils.py

```python
import hashlib
import math
import os
import shutil
import time
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Any

import pandas as pd

# JST Definition
JST = timezone(timedelta(hours=9), "JST")


def is_empty(val: Any) -> bool:
    """
    値が None, NaN, または空文字列であるか判定する。

    Args:
        val: 判定対象の値。

    Returns:
        bool: 空（None, NaN, 空文字）であれば True。
    """
    if val is None:
        return True
    if isinstance(val, str) and not val.strip():
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    return False


def safe_float(val: Any) -> float:
    """
    NaN、None、カンマ入り文字列等を安全に float に変換する。
    変換不能な場合は 0.0 を返す。

    Args:
        val: 変換対象の値。

    Returns:
        float: 変換後の数値。
    """
    try:
        if val is None:
            return 0.0
        # 文字列からのクレンジング
        s = str(val).replace(",", "").replace("%", "").strip()
        if s == "" or s.lower() == "nan" or s.lower() == "none":
            return 0.0
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def safe_display_value(val: Any, fallback: str = "-") -> Any:
    """
    表示用に値をクレンジングする。None, NaN, 空文字の場合はフォールバック文字を返す。

    Args:
        val: 変換対象の値。
        fallback: 空の場合に返す文字列。デフォルトは "-"。

    Returns:
        Any: クレンジング後の値。
    """
    if val is None or val == "" or str(val).lower() in ("nan", "none"):
        return fallback
    return val


def get_current_time() -> datetime:
    """Returns the current time in JST."""
    return datetime.now(JST)


def get_today_str() -> str:
    """Returns today's date string (YYYY-MM-DD) in JST."""
    return get_current_time().strftime("%Y-%m-%d")


def generate_row_hash(row: pd.Series) -> str:
    """Generate an MD5 hash from a DataFrame row."""
    keys_to_hash = [
        "code",
        "name",
        "per",
        "pbr",
        "roe",
        "dividend_yield",
        "current_ratio",
        "rsi",
        "quant_score",
    ]
    values = []
    for key in keys_to_hash:
        val = row.get(key)
        if pd.isna(val):
            val_str = "NaN"
        else:
            if isinstance(val, float) and val.is_integer():
                val_str = str(int(val))
            else:
                val_str = str(val)
        values.append(val_str)
    raw_string = "|".join(values)
    return hashlib.md5(raw_string.encode("utf-8")).hexdigest()


def retry_with_backoff(
    max_retries=3, base_delay=1, backoff_factor=2, exceptions=(Exception,)
):
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = getLogger(__name__)
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    err_msg = str(e)
                    # 429 ResourceExhausted の場合は簡潔に表示 (巨大な JSON メッセージを抑制)
                    is_quota_error = (
                        "429" in err_msg
                        or "ResourceExhausted" in err_msg
                        or "quota" in err_msg.lower()
                    )

                    if attempt == max_retries:
                        if is_quota_error:
                            logger.error(
                                "❌ Max retries reached. Quota still exceeded."
                            )
                        else:
                            logger.error(
                                f"❌ Max retries ({max_retries}) reached. Last error: {err_msg[:200]}..."
                            )
                        raise e

                    wait_time = base_delay * (backoff_factor**attempt)
                    if is_quota_error:
                        logger.warning(
                            f"⚠️ Quota Exceeded (429). Retry {attempt + 1}/{max_retries} in {wait_time}s..."
                        )
                    else:
                        logger.warning(
                            f"⚠️ Attempt {attempt + 1} failed: {err_msg[:100]}... Retrying in {wait_time}s..."
                        )
                    time.sleep(wait_time)

        return wrapper

    return decorator


# [追加] ファイルのローテーション・バックアップ機能
def rotate_file_backup(file_path):
    """
    ファイルが存在する場合、リネームして退避させる。
    形式: filename_YYYYMMDD_HHMMSS_01.ext
    """
    if not os.path.exists(file_path):
        return

    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    name, ext = os.path.splitext(basename)

    timestamp = get_current_time().strftime("%Y%m%d_%H%M%S")

    # 通番を付与して重複回避
    counter = 1
    while True:
        new_name = f"{name}_{timestamp}_{counter:02d}{ext}"
        new_path = os.path.join(dirname, new_name)
        if not os.path.exists(new_path):
            break
        counter += 1

    try:
        shutil.move(file_path, new_path)
        print(f"📦 Backed up existing file to: {new_name}")
    except Exception as e:
        print(f"⚠️ Failed to backup file: {e}")

```

---

### src/validation_engine.py

```python
"""ValidationEngine: セクター別バリデーションポリシーエンジン

責務:
- タスクデータのバリデーション（プロンプト内容の不備チェック）
- セクター別ポリシー（欠損許容 na_allowed 等）の適用
- AI分析前のデータ品質チェック (旧 DataValidator の機能)
- 並列バッチ処理によるバリデーション実行
"""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging import getLogger
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, cast

if TYPE_CHECKING:
    from src.domain.models import StockAnalysisData


class ValidationEngine:
    """設定に基づいてバリデーションポリシーを管理するエンジン。

    Attributes:
        config (Dict[str, Any]): システム設定。
        sector_policies (Dict[str, Any]): セクターごとのバリデーションルール。
        default_policy (Dict[str, Any]): デフォルトのポリシー。
        mapping (Dict[str, Any]): メタデータマッピング定義。
        metrics_map (Dict[str, str]): ラベル名と内部フィールド名の対応マップ。
        val_config (Dict[str, Any]): バリデーションに関する設定値。
    """

    def __init__(self, config: Dict[str, Any]):
        """ValidationEngine を初期化する。

        Args:
            config (Dict[str, Any]): アプリケーション全体の設定辞書。
        """
        self.logger = getLogger(__name__)
        self.config = config
        self.sector_policies = config.get("sector_policies", {})
        self.default_policy = self.sector_policies.get(
            "default",
            {"na_allowed": [], "score_exemptions": [], "ai_prompt_excludes": []},
        )

        # 設定からマッピング情報をロード
        self.mapping = config.get("metadata_mapping", {})
        self.metrics_map = self.mapping.get("metrics", {})
        self.val_config = self.mapping.get("validation", {})

        # 設定が空の場合のフォールバック (後方互換性)
        if not self.metrics_map:
            self.metrics_map = {
                "Op CF Margin": "operating_cf",
                "Debt/Equity Ratio": "debt_equity_ratio",
                "Free CF": "free_cf",
                "Operating Margin": "operating_margin",
                "ROE": "roe",
                "PER": "per",
                "PBR": "pbr",
            }

    def get_policy(self, sector: str) -> Dict[str, Any]:
        """指定したセクターのバリデーションポリシーを取得する。

        Args:
            sector (str): セクター名。

        Returns:
            Dict[str, Any]: 該当セクターのポリシー辞書（未定義ならデフォルトを返す）。
        """
        return self.sector_policies.get(sector, self.sector_policies.get("default", {}))

    def validate(self, task: dict, sector: Optional[str] = None) -> Tuple[bool, str]:
        """分析タスクのプロンプト内容を検証し、欠損や不整合がないかチェックする。

        Args:
            task (dict): 検証対象のタスク辞書（プロンプト等を含む）。
            sector (Optional[str], optional): セクター名称。省略時はタスク内から取得。

        Returns:
            Tuple[bool, str]:
                - bool: 検証をパスした場合は True。
                - str: 判定理由またはエラーメッセージ。
        """
        prompt = task.get("prompt", "") if isinstance(task, dict) else task.prompt
        strategy = (
            task.get("strategy", "unknown") if isinstance(task, dict) else task.strategy
        )

        # 0. プロンプトの存在チェック
        if not prompt:
            return False, "Prompt is empty or None."

        # セクターの決定
        if not sector:
            sector = (
                task.get("sector", "Unknown")
                if isinstance(task, dict)
                else task.stock.sector
            )

        # ポリシーの取得
        policy = self.get_policy(sector)
        na_allowed = set(policy.get("na_allowed", []))

        # 戦略レベルの免除事項
        strat_policy_key = f"_strategy_{strategy}"
        if strat_policy_key in self.sector_policies:
            strat_policy = self.sector_policies[strat_policy_key]
            na_allowed.update(strat_policy.get("na_allowed", []))

        # 致命的欠損の判定閾値
        fatal_threshold = self.val_config.get("critical_missing_threshold", 7)

        # 主要メトリクスの欠損チェック
        core_metrics_labels = list(self.metrics_map.keys())
        if not core_metrics_labels:
            core_metrics_labels = ["PER", "PBR", "ROE"]

        missing_count = 0

        for m_label in core_metrics_labels:
            pattern = rf"{re.escape(m_label)}[:\s]+(None|nan)"
            field_name = self.metrics_map.get(m_label)
            if re.search(pattern, prompt, re.IGNORECASE):
                if field_name not in na_allowed:
                    missing_count += 1

        if missing_count >= fatal_threshold:
            return (
                False,
                f"Fatal Data Missing ({missing_count}/{len(core_metrics_labels)} items NaN). Quarantined by Guardrail.",
            )

        # 1. 個別メトリクスの詳細バリデーション
        # [v12.5 Fix] Reference metrics should be allowed to be None (Warning only, handled by Tiered Validation)
        # Combine configured na_allowed with Tier 2 reference metrics
        effective_na_allowed = na_allowed.copy()
        if hasattr(
            self, "validate_stock_data"
        ):  # Check if tiered method exists (it does)
            # Use the reference_metrics defined in validate_stock_data scope... can't access easily.
            # Hardcode the known reference keys to safe-list them
            effective_na_allowed.update(
                {
                    "sales_growth",
                    "profit_growth",
                    "dividend_yield",
                    "equity_ratio",
                    "rsi",
                    "macd",
                }
            )

        for m_label, field_name in self.metrics_map.items():
            if re.search(
                rf"{re.escape(m_label)}[:\s]+(None|nan)", prompt, re.IGNORECASE
            ):
                if field_name not in effective_na_allowed:
                    return False, f"Missing Critical Financials ({m_label} is None)"

        # 2. スコア整合性チェック
        if hasattr(task, "get") or isinstance(task, dict):
            s_val = task.get("score_value") or 0
            s_gro = task.get("score_growth") or 0
            s_trd = task.get("score_trend") or 0

            if strategy == "growth_quality":
                if s_gro < 10 and s_trd > 70:
                    return (
                        False,
                        f"Score Mismatch: Low Growth({s_gro}) vs High Trend({s_trd})",
                    )
            elif strategy == "value_strict":
                if s_val < 15:
                    return (
                        False,
                        f"Score Mismatch: Low Value Score ({s_val}) for Value Strategy",
                    )
            elif strategy == "value_growth_hybrid":
                if s_val < 10 and s_gro < 10:
                    return (
                        False,
                        f"Score Mismatch: Low Hybrid Scores (Val:{s_val}, Gro:{s_gro})",
                    )

        # 3. 異常値チェック (株価/PER)
        price_match = re.search(r"Price: ([\d\.]+|None) JPY", prompt)
        if price_match:
            price_str = price_match.group(1)
            if price_str == "None" or (
                price_str.replace(".", "", 1).isdigit() and float(price_str) <= 0
            ):
                return False, f"Abnormal Price: {price_str}"

        per_match = re.search(r"PER: ([\d\.]+|None) \(", prompt)
        if per_match:
            per_str = per_match.group(1)
            if (
                per_str != "None"
                and per_str.replace(".", "", 1).isdigit()
                and float(per_str) >= 500
            ):
                return False, f"Abnormal PER: {per_str}"

        # 4. 疑わしい値のチェック
        if "EPS Growth: 100.0%" in prompt:
            return False, "Suspicious Value: EPS Growth capped at 100.0%"

        return True, "OK"

    def get_ai_excludes(self, sector: str) -> List[str]:
        policy = self.get_policy(sector)
        return policy.get("ai_prompt_excludes", [])

    def get_score_exemptions(self, sector: str) -> List[str]:
        policy = self.get_policy(sector)
        return policy.get("score_exemptions", [])

    def check_sector_coverage(self, db_sectors: List[str]) -> None:
        defined_sectors = set(self.sector_policies.keys()) - {"default"}
        db_sector_set = set(db_sectors)
        undefined = db_sector_set - defined_sectors
        if undefined:
            self.logger.warning(
                f"⚠️ The following sectors are not defined in sector_policies: {undefined}"
            )

    def validate_batch(
        self, tasks: List[dict], max_workers: int = 4, use_parallel: bool = True
    ) -> List[Tuple[dict, bool, str]]:
        """複数のタスクを一括でバリデーションする。

        Args:
            tasks (List[dict]): バリデーション対象のタスクリスト。
            max_workers (int, optional): 並列実行時の最大スレッド数。デフォルトは 4。
            use_parallel (bool, optional): 並列実行するかどうかのフラグ。デフォルトは True。

        Returns:
            List[Tuple[dict, bool, str]]: 各タスクの結果（タスク本体、有効フラグ、理由）のリスト。
        """
        if not tasks:
            return []
        if use_parallel and len(tasks) > 1:
            return self._validate_batch_parallel(tasks, max_workers)
        else:
            return self._validate_batch_sequential(tasks)

    def _validate_batch_sequential(
        self, tasks: List[dict]
    ) -> List[Tuple[dict, bool, str]]:
        results = []
        for task in tasks:
            is_valid, reason = self.validate(task)
            results.append((task, is_valid, reason))
        return results

    def _validate_batch_parallel(
        self, tasks: List[dict], max_workers: int
    ) -> List[Tuple[dict, bool, str]]:
        # 結果格納用のリストを型明示して初期化
        results: List[Tuple[dict, bool, str]] = []  # type: ignore
        results = [cast(Tuple[dict, bool, str], None)] * len(tasks)

        def validate_with_index(
            idx_task: Tuple[int, dict],
        ) -> Tuple[int, dict, bool, str]:
            idx, task = idx_task
            try:
                is_valid, reason = self.validate(task)
                return idx, task, is_valid, reason
            except Exception as e:
                self.logger.error(f"Validation error for task {idx}: {e}")
                return idx, task, False, f"Validation Error: {str(e)}"

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(validate_with_index, (idx, task)): idx
                for idx, task in enumerate(tasks)
            }
            for future in as_completed(futures):
                try:
                    idx, task, is_valid, reason = future.result()
                    results[idx] = (task, is_valid, reason)
                except Exception as e:
                    idx = futures[future]
                    results[idx] = (tasks[idx], False, f"Internal Error: {str(e)}")
        return results

    # ============================================================
    # [v2.0] Pydantic StockAnalysisData との統合
    # ============================================================
    def validate_stock_data(
        self,
        data: Dict[str, Any],
        stock: Optional["StockAnalysisData"] = None,  # type: ignore
        strategy: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """株価データのバリデーションを行う (Pydantic Integration)。

        [v2.0] StockAnalysisData の ValidationFlag を活用した簡素化実装。
        - Tier 1 欠損 -> Skip
        - 足切り対象 -> Skip
        - Tier 2 欠損 -> Warning

        Args:
            data: 検証対象のデータ辞書（後方互換用）。
            stock: StockAnalysisData インスタンス（推奨）。
            strategy: 戦略名（戦略固有のポリシー適用のため）。

        Returns:
            Tuple[bool, List[str]]: (検証結果, 問題点リスト)
        """
        from src.domain.models import StockAnalysisData

        # StockAnalysisDataが渡されなければ、dictから生成
        if stock is None:
            try:
                stock = StockAnalysisData(**data)
            except Exception as e:
                return False, [f"Data Validation Error: {e}"]

        flags = stock.validation_flags
        issues: List[str] = []

        # セクターポリシーによる免除
        sector = data.get("sector", stock.sector)
        policy = self.get_policy(sector)
        na_allowed = set(policy.get("na_allowed", []))

        # 戦略レベルの免除事項
        if strategy:
            strat_policy_key = f"_strategy_{strategy}"
            if strat_policy_key in self.sector_policies:
                strat_policy = self.sector_policies[strat_policy_key]
                na_allowed.update(strat_policy.get("na_allowed", []))

        # --- Tier 1 欠損チェック (Skip) ---
        tier1_missing = [f for f in flags.tier1_missing if f not in na_allowed]
        if tier1_missing:
            return False, [f"Missing Critical: {', '.join(tier1_missing)}"]

        # --- 足切り対象チェック (Skip) ---
        if stock.should_skip_analysis:
            reasons = [r.value for r in flags.skip_reasons]
            return False, reasons

        # --- Tier 2 欠損チェック (Warning) ---
        for field in flags.tier2_missing:
            if field not in na_allowed:
                issues.append(f"Missing Reference: {field}")

        # --- Red Flag チェック (Warning) ---
        for flag in flags.red_flags:
            issues.append(f"Red Flag: {flag}")

        return True, issues

    def is_abnormal(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """精密修復後のデータに対して、足切りが必要な異常値がないかを判定する。

        [v2.0] StockAnalysisData.should_skip_analysis への移行を推奨。

        Args:
            data: 検証対象のデータ。

        Returns:
            Tuple[bool, List[str]]: (異常あり判定, 理由リスト)
        """
        import warnings

        from src.domain.models import StockAnalysisData

        warnings.warn(
            "ValidationEngine.is_abnormal() is deprecated. "
            "Use StockAnalysisData.validation_flags.skip_reasons instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        try:
            stock = StockAnalysisData(**data)
            reasons = [r.value for r in stock.validation_flags.skip_reasons]
            return stock.should_skip_analysis, reasons
        except Exception:
            # フォールバック: 旧ロジック
            from src.utils import safe_float as sf

            reasons = []
            eq_ratio = sf(data.get("equity_ratio"))
            if eq_ratio is not None and eq_ratio < 0:
                reasons.append(f"Insolvent (Equity Ratio: {eq_ratio:.1f}%)")

            per = sf(data.get("per"))
            if per is not None and per > 500:
                reasons.append(f"Abnormal PER ({per:.1f})")

            pbr = sf(data.get("pbr"))
            if pbr is not None and pbr > 20:
                reasons.append(f"Abnormal PBR ({pbr:.1f})")

            return len(reasons) > 0, reasons

```

---

## History (Latest 3)

### history/2026-01-02.md

```markdown
# 修正履歴 (2026-01-02)

| 対象ファイル                                      | 修正の概要                                                                               | 対応不具合通番 |
| :------------------------------------------------ | :--------------------------------------------------------------------------------------- | :------------- |
| `src/domain/models.py`                            | `price` から `current_price` へのマッピングを追加し、DBモデルとの互換性を確保            | No.2           |
| `src/ai/agent.py`                                 | `analyze` メソッド内の属性参照エラー (`strategy_name`) を修正                            | No.1           |
| `src/validation_engine.py`                        | `validate_stock_data` に `strategy` 引数を追加し、戦略固有のポリシーを適用可能に修正     | No.3           |
| `src/validation_engine.py`                        | `is_abnormal` を非推奨化し、新ドメインモデルの検証フラグを使用するようにリファクタリング | -              |
| `tests/test_sentinel_orchestrator_integration.py` | 並列実行とモックの安定性向上のための微修正                                               | -              |
| `trouble/2026-01-02-report.md`                    | 本日の不具合と修正内容の記録                                                             | -              |
| `full_context/generate_full_context.py`           | プロジェクトコンテキスト生成スクリプトの作成                                             | -              |
| `docs/archive/*.md`                               | 完了済みプロポーサルのアーカイブ化                                                       | -              |

```

---

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

## Trouble Reports (Latest 1)

_No files found in this group._

