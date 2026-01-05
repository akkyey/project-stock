# ソースコード最適化・リファクタリング提案書

**作成日:** 2025年12月16日
**ステータス:** 提案中 (Proposed)

## 1. 概要 (Executive Summary)

現在の `stock-analyzer3` コードベースを調査した結果、いくつかの冗長性、パフォーマンスのボトルネック、および可読性の改善点が確認されました。本プロポーサルでは、これらの課題を解決し、将来のメンテナンス性と拡張性を高めるための具体的なリファクタリング計画を提案します。

## 2. 現状の課題 (Current Issues)

### 2.1 エントリーポイントの冗長性
*   `stock_analyzer.py` と `analyze_db.py` という2つの類似したエントリーポイントが存在しています。
*   `analyze_db.py` の機能はほぼ `stock_analyzer.py` に包含されており、二重管理の状態になっています。

### 2.2 処理効率 (Performance)
*   **スコア計算のループ処理:** `StockAnalyzer.run_analysis` 内で `df.iterrows()` を使用して行ごとにスコア計算 (`Calculator.calc_v2_score`) を行っています。PandasのDataFrameを使用している利点（ベクトル化演算）が活かされておらず、データ量が増加した際に処理速度が著しく低下する原因となります。
*   **データ取得の直列実行:** `DataFetcher` が銘柄ごとに同期的にAPIリクエストと待機 (`time.sleep`) を繰り返しています。

### 2.3 可読性と保守性 (Readability & Maintainability)
*   **レガシーコードの残骸:** `src/analyzer.py` 等に、CSVモード時代の古いコメントアウトされたコードや、使用されていないメソッド (`load_data` の名残など) が散見されます。
*   **責任の分離:** `StockDatabase` クラスがデータベース接続、テーブル作成（スキーマ管理）、マイグレーション的な処理、CRUD操作のすべてを一手に引き受けており、肥大化しています。

## 3. 最適化・リファクタリング提案 (Proposed Changes)

以下の4つのフェーズに分けて実施することを提案します。

### Phase 1: エントリーポイントの統合とクリーンアップ (High Priority)
*   **統合:** `stock_analyzer.py` を唯一のエントリーポイントとし、`analyze_db.py` を廃止・削除します。
*   **CLI引数の整理:** `stock_analyzer.py` にデバッグモード等の必要なフラグを統合します。
*   **不要コード削除:** 大量のコメントアウトされたレガシーコード（旧CSVロジックなど）を削除し、可読性を向上させます。

### Phase 2: スコア計算のベクトル化 (High Priority / Performance)
*   **Calculatorの改修:** `src/calc.py` の `calc_v2_score` および `calc_quant_score` を、1行ずつ処理するのではなく、DataFrame全体を受け取って一括で計算するように書き換えます。
    *   *Before:* `for row in df: score += ...`
    *   *After:* `df['score'] = np.where(df['metric'] > th, pts, 0) ...`
*   **効果:** これにより、計算処理速度が数倍〜数十倍に高速化される見込みです。

### Phase 3: データ取得フローの最適化 (Medium Priority)
*   **不要なI/Oの削減:** `DataFetcher.fetch_jpx_list` が必ずCSVファイルを書き出している処理を、オプション化またはオンメモリ処理に変更し、I/O負荷を下げます（バックアップ目的以外での書き込みを抑制）。
*   **待機ロジックの改善:** 冗長な `time.sleep` を見直し、必要最低限かつ効率的なレートリミット制御（`src/utils.py` のデコレータ活用など）に統一します。

### Phase 4: ロギングとUIの改善 (User Request)
*   **ログ出力の分離:** `DataFetcher` や `yfinance` 関連の処理において、プログレスバー (`tqdm`) と通常のログ出力 (`logger.info`) が混在して表示が崩れる問題を解消します。
    *   `tqdm` は標準出力 (stdout) を使用。
    *   詳細なログ（`logger.info`）はファイルのみに出力するか、標準エラー出力 (stderr) に逃がす、あるいは `tqdm.write` を使用して適切にハンドリングします。
    *   **デフォルト:** コンソールには「進行状況と重要なエラーのみ」を表示し、詳細はログファイル (`stock_analyzer.log`) に集約する構成に変更します。

### Phase 5: 型ヒントとドキュメントの充実 (Low Priority / Quality)
*   **Type Hinting:** 主要なメソッド引数と戻り値に型ヒント (`list[str]`, `pd.DataFrame` 等) を追加し、IDEでの補完や静的解析を容易にします。
*   **Docstring:** クラスやメソッドの役割を明確にするため、Google Style等の標準的なDocstringを追記します。

## 4. 実施計画 (Preliminary Plan)

承認された場合、以下の順序で作業を進めます。

1.  **Phase 1 & Cleanup:** `analyze_db.py` 削除、`stock_analyzer.py` 統合、不要コメント削除。
2.  **Phase 2 Vectorization:** `Calculator` クラスのベクトル化対応とテスト。
3.  **Verification:** 既存の統合テスト (`tests/verify_v33_integration.py` 等) をパスすることを確認。

## 5. ユーザーへの確認事項

*   上記の方針で進めて問題ないでしょうか？
*   特に「ベクトル化」によるロジック変更は計算結果に厳密な一致をもたらさない場合があります（浮動小数点計算の微差など）。許容範囲でしょうか？（基本的にはロジックを変えないため一致します）
*   `analyze_db.py` を削除して `stock_analyzer.py` に一本化することに同意いただけますか？

以上、ご検討をお願いいたします。
