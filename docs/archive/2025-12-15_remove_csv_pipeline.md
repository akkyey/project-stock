# プロポーサル: データパイプラインの簡素化 - CSV経由ロードの廃止とDB完全移行

**作成日:** 2025年12月15日
**ステータス:** 提案中 (Proposed)

## 1. 背景と目的

Project Stock Analyzer v3.3において、SQLiteを用いたデータ基盤 (`StockDatabase`) が導入されました。現在、システムは以下の2つのデータフローを並行して維持しています。

1.  **旧フロー (Legacy):** `DataFetcher` -> CSVファイル -> `StockAnalyzer` (CSV Load)
2.  **新フロー (v3.3+):** `DataFetcher` -> `StockDatabase` -> `StockAnalyzer` (DB Load)

現状では、`StockAnalyzer` 内にCSV読み込みロジックとDB読み込みロジックが混在しており、コードが肥大化しています。また、`yfinance` で取得したデータを一度CSVに書き出し、それを読み込むプロセスはI/Oの観点からも非効率であり、データ型（日付や数値）の変換トラブルの温床となっています。

本プロポーサルでは、**「yfinanceの結果をCSVで入力するルート」を廃止し、DBを中心としたデータパイプラインへ完全移行すること**を提案します。

## 2. 変更内容の詳細

### 2.1 廃止・削除対象

#### A. StockAnalyzer (`src/analyzer.py`)
*   **メソッド削除:**
    *   `load_data()`: CSVファイル群を検索して読み込むレガシーメソッド。
    *   `_read_and_normalize()`: CSV特有のカラム名ゆらぎ吸収ロジック。
*   **引数/オプション削除:**
    *   `run_analysis(use_db=False)` フラグの廃止（常に `use_db=True` 相当で動作）。
    *   CLI引数 `--source csv` の廃止。

#### B. DataFetcher (`src/data_fetcher.py`)
*   **CSV出力の任意化/廃止:**
    *   `fetch_stock_data` メソッドにおいて、デフォルトでCSVを出力する処理を見直す。
    *   ※ ただし、デバッグやバックアップ目的での「ログとしてのCSV出力」は残す余地があるが、**「次の工程への入力としてのCSV」** という役割は明確に廃止する。

#### C. 設定 (`config.yaml`)
*   `data.input_path` (入力CSVパス) の設定項目を削除、または `deprecated` 扱いとする。

### 2.2 変更後のデータフロー

```mermaid
graph LR
    A[DataFetcher] -->|Upsert| B[(StockDatabase)]
    B -->|Select| C[StockAnalyzer]
    C -->|Save Result| B
    C -->|Export Report| D[CSV/Excel Report]
```

1.  **データ取得:** `DataFetcher` は取得したデータを即座に `StockDatabase` に Upsert します。
2.  **分析:** `StockAnalyzer` は常に `StockDatabase` から最新（または指定日）のデータを取得して分析します。
3.  **レポート:** 分析結果の**閲覧用**としてのみ、CSV/Excelファイルを出力します（これは次のプロセスの入力にはなりません）。

## 3. 移行ステップ

1.  **Import Toolの整備 (Safety Net):**
    *   過去のCSVデータを捨てたくないユーザーのために、既存のCSVをDBに取り込むツール (`tools/import_csv_to_db.py`) の動作を保証・周知する。
2.  **Analyzerの改修:**
    *   `src/analyzer.py` から `load_data` メソッドを削除。
    *   コンストラクタや `run_analysis` をDB前提のシンプルにコードにリファクタリング。
3.  **CLIの更新:**
    *   `stock_analyzer.py` の `--source` 引数を削除（DB固定）。
4.  **ドキュメント更新:**
    *   `README.md`, `manual.md` からCSV入力モードに関する記述を削除。

## 4. 期待される効果

*   **コード品質向上:** 冗長なCSVパース処理、文字コード判定、カラム名マッピング処理が不要になり、バグ混入率が低下する。
*   **パフォーマンス向上:** 巨大なCSVの全件読み込みとPandas変換オーバーヘッドがなくなり、必要なカラムだけをSQLで効率的に取得できる。
*   **データ整合性:** DBの一意性制約により、重複データや矛盾したデータでの分析を防げる。

## 5. 懸念点と対策

*   **懸念:** 「手元のExcelでデータを加工して、それを分析させたい」というニーズがある場合。
*   **対策:** これは「データ入力」のユースケースであるため、正規のルートとして `tools/import_csv_to_db.py` を使用してもらうフローとする。CSVファイルを直接読み込む裏口は塞ぐことで、データ管理を一元化する。

以上
