# データ収集・分析パイプライン改修提案

## 1. はじめに

本ドキュメントは、現在の株価分析システムにおけるデータ収集および分析パイプラインの現状を整理し、CSVモードとDBモード間の結果の不一致という課題に対する改修案を提案するものです。最終的な目標は、データベースを主軸とした堅牢で一貫性のある分析システムを構築することです。

## 2. 現状の課題

### 2.1 CSVモード (`analyze.py`) とDBモード (`analyze_db.py`) の不一致

これまでの検証の結果、CSVモードとDBモードで分析結果が完全に一致しないという問題が確認されています。

*   **データソースの違い:**
    *   **CSVモード (`analyze.py`)**: `data/input`ディレクトリ内の`stock_master_*.csv`形式の**全ファイルを結合して分析**しています。しかし、`fetch_data.py`の動作により、タイムスタンプ付きのバックアップファイルも含まれてしまい、**実質的にデータが重複したまま分析されていた**という問題がありました。この問題は、`src/analyzer.py`でタイムスタンプ付きファイルを読み込まないように修正することで部分的に改善されましたが、それでも`pd.concat`による単純結合では、論理的に「最新のユニークなデータ」を厳密に保証できるわけではありません。
    *   **DBモード (`analyze_db.py`)**: `data/stock_master.db`からデータを読み込みます。`collector.py`がAPIから取得したデータをこのDBに保存しますが、`analyze_db.py`の`load_data_from_db`メソッドは`MAX(entry_date)`でフィルタリングするため、**DBに存在する最新日付のデータのみを分析対象**としています。

*   **APIからのデータ取得の課題:**
    `collector.py`が`yfinance`を介してAPIからデータを取得する際、多くの銘柄で必要な情報（`currentPrice`など）が取得できないことが判明しました。これにより、API経由でDBに保存されるレコード数が少なく、DBモードでの分析候補が0になるという問題が発生しています。CSVモードで分析できている銘柄も、APIから取得できない場合があるため、CSVのデータソースの完全性は`yfinance`単体では再現できない可能性があります。

### 2.2 データフローの不整合

現在は以下の3つの主要なデータフローが混在しており、混乱を招いています。

1.  **API -> CSVファイル -> CSVモード分析 (`fetch_data.py` -> `analyze.py`)**:
    `fetch_data.py`がAPIからデータを取得しCSVファイルに保存。`analyze.py`がそのCSVを読み込んで分析。

2.  **API -> DB -> DBモード分析 (`collector.py` -> `analyze_db.py`)**:
    `collector.py`がAPIからデータを取得し直接DBに保存。`analyze_db.py`がそのDBを読み込んで分析。

3.  **CSVファイル -> DB -> DBモード分析 (`tools/import_csv_to_db.py` -> `analyze_db.py`)**:
    手動でCSVファイルをDBにインポートし、`analyze_db.py`がそれを読み込んで分析。

この不整合により、各分析スクリプトが参照する「最新のデータ」の定義や、データセットの完全性が異なっています。

## 3. 改修案：CSVモードロジックの統合とデータフローの一本化

現状のCSVモードは「既に生成済みの完全なデータ」を分析しており、これは結果の基準点として機能しています。このCSVモードのデータ読み込みと前処理のロジックをデータベース版に統合し、データフローを一本化することで、システム全体の性能と一貫性を向上させます。

### 3.1 目標

*   `analyze.py` (CSVモード) と `analyze_db.py` (DBモード) の両方が、**同一のデータセットとロジックで分析を行う**ようにする。
*   データ収集（API）から分析までのデータフローを明確にし、管理しやすい構造にする。
*   `analyze.py` と `analyze_db.py` を統合し、`StockAnalyzer`クラスがデータソース（CSV/DB）を透過的に扱えるようにする。

### 3.2 具体的な改修内容

1.  **データ収集 (`collector.py` / `fetch_data.py`) の強化:**
    *   `collector.py` (または `fetch_data.py`) がAPIからデータを取得する際に、**取得できなかった銘柄に対して代替データソース（例：既存のCSVバックアップ、外部API）から補完**するロジックを追加検討します。これにより、DBに格納されるデータの完全性を向上させます。（これは長期的な課題）
    *   一時的な対策として、APIで取得したデータをDBに保存する際に、**Pandasの`drop_duplicates(subset='code', keep='last')`を適用**し、常に銘柄ごとの最新データのみがDBに登録されることを保証します。

2.  **`src/analyzer.py` の `load_data_from_db` の改善:**
    *   `load_data_from_db`メソッドのSQLクエリから`WHERE m.entry_date = (SELECT MAX(entry_date) FROM market_data)`の日付フィルタリングを削除し、**DB内の全`market_data`を取得**するようにします。
    *   取得したPandas DataFrameに対し、`code`と`entry_date`をキーにして、`entry_date`が最新のレコードのみを残すように`drop_duplicates(subset=['code'], keep='last')`を適用します。これにより、DBに複数日付のデータが混在しても、常に銘柄ごとの最新データが分析対象となります。

3.  **`analyze.py` と `analyze_db.py` の統合（または一本化）:**
    *   `analyze.py`を廃止し、`analyze_db.py`がメインの分析スクリプトとなります。
    *   `StockAnalyzer`クラスの`run_analysis`メソッドは、`use_db`フラグを継続してサポートし、データロードの切り替え (`load_data` / `load_data_from_db`) を行います。
    *   将来的には、`load_data`メソッド（CSV読み込み）のロジックを`load_data_from_db`（DB読み込み）に完全に置き換え、CSVファイルはデータ収集時の一時的な保存形式またはバックアップとしてのみ扱うようにします。

## 4. 検証計画

改修後、以下の手順でシステム全体の健全性と一貫性を検証します。

1.  **DBリセット:** `data/stock_master.db`を削除し、クリーンな状態にする。
2.  **APIデータ収集:** `python collector.py --force` を実行し、APIからデータを取得してDBを構築する。
3.  **DBモード分析:** `python analyze_db.py --debug --limit 10` を実行し、分析結果（`data/output/db_analysis_result.csv`）を確認する。
4.  **CSVモード分析 (既存CSV使用):** `python analyze.py --debug --top 10` を実行し、分析結果（`data/output/analysis_result.csv`）を確認する。（このステップはCSVモードの基準データとして必要）
5.  **結果比較:** 両モードの出力結果に含まれる銘柄コードの集合を比較し、完全に一致することを確認する。

## 5. ロードマップ

*   **フェーズ1 (本提案):** `src/analyzer.py`の`load_data_from_db`を改善し、`collector.py`のDB保存ロジックも調整して、APIからのデータ取得・DB構築後の分析結果の整合性を高める。
*   **フェーズ2 (将来):** `yfinance`で取得できない銘柄のデータ補完戦略の検討、あるいは別のデータソースへの移行。
*   **フェーズ3 (将来):** CSVモードの廃止と`analyze_db.py`への完全統合。

---
