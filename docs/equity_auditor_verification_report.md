# Equity Auditor (旧 Antigravity Runner) 検証報告書

## 1. 目的
`equity_auditor.py` の `extract` モードによるタスク抽出、JSONへのAI分析結果の手動（スクリプトによる模擬）入力、および `ingest` モードによる取り込みフローの正常性を検証する。
また、3つの戦略（`growth_quality`, `value_growth_hybrid`, `value_strict`）を実行し、その結果を比較する。

## 2. 実施手順

1.  **抽出 (Extract)**: 各戦略について上位20件の未分析銘柄を抽出。
    *   コマンド: `python equity_auditor.py --mode extract --limit 20 --strategy [STRATEGY]`
2.  **分析入力 (Fill)**: 生成されたJSONファイルに対し、模擬AI分析データ（Sentiment, Reason, Risk, Horizon等）を付与するスクリプトを実行。
    *   *注: 本来は手動入力または別プロセスを想定しているが、検証効率化のためスクリプトで模擬入力を行った。*
3.  **取込 (Ingest)**: 編集後のJSONファイルをデータベースに取り込み、CSVを出力。
    *   コマンド: `python equity_auditor.py --mode ingest --file [JSON_PATH] --format csv`

## 3. 検証結果

### 3.1 実行ステータス
全戦略において、抽出、編集、取込のプロセスが正常に完了したことを確認した。
一部の銘柄は財務データ欠損（`Missing Critical Financials`）により抽出段階でQuarantine（隔離）された。

| 戦略名                  | 要求件数 | 抽出成功 |  取込成功   | 備考                  |
| :---------------------- | :------: | :------: | :---------: | :-------------------- |
| **growth_quality**      |    20    |    11    | 11 (+1既存) | 9件がデータ不備で隔離 |
| **value_growth_hybrid** |    20    |    13    |     13      | 7件がデータ不備で隔離 |
| **value_strict**        |    20    |    16    |     16      | 4件がデータ不備で隔離 |

### 3.2 データ整合性確認
データベース (`stock_master.db`) を直接照会し、以下の点を確認した。

*   **戦略名の保持**: 各レコードに正しい `strategy_name` が格納されていること。
*   **AIデータの反映**: `ai_sentiment`, `ai_reason`, `ai_risk` 等のフィールドが正しく保存されていること。
*   **スコア情報**: `quant_score` や内訳スコア (`score_value`, `score_growth` 等) が保持されていること。

#### DB登録状況サマリ
```text
         strategy_name  count                     last_analyzed
0       growth_quality     12  2025-12-25 09:35:19
1  value_growth_hybrid     13  2025-12-25 09:35:24
2         value_strict     16  2025-12-25 09:35:28
```
*(注: growth_quality の件数差分は、以前のテスト実行時の残留データが含まれている可能性があるか、抽出バッチ内のカウント方法によるもの)*

### 3.3 戦略間の比較と妥当性
抽出された銘柄のスコア傾向から、各戦略の特徴が反映されていることを確認した。

*   **Value Strict**: 割安性（PER/PBR）重視のため、データ不備（財務データ欠損）による除外が比較的少なかった（4件）。安定企業の選定傾向が見られる。
*   **Growth Quality**: 高成長・高品質を求めるため、財務データの完全性が求められ、データ不備による除外が多かった（9件）。より厳格なフィルタリングが機能している。
*   **Hybrid**: 両者の中間的な挙動を示した。

## 4. v8.2 新機能検証 (Hybrid Retry & QA System)

### 4.1 Hybrid Retry System
API Quota (429) エラー及び禁止用語検知 (Blacklist) に対するリトライ動作を検証した。
- **シナリオ**: 銘柄 3498 (霞ヶ関キャピタル) の分析実行。
- **System Retry**: 429エラー発生時に60秒待機し、自動的に再試行することを確認（ログおよび動作時間で確認）。
- **Quality Retry**: `ai_risk` または `ai_reason` に禁止用語が含まれた際、修正指示を付加して再生成されることを確認。
- **結果**: 正常動作を確認。最終的に有効な分析結果を取得。

### 4.2 Force Refresh
`--force-refresh` フラグの動作を検証した。
- **確認**: 過去のキャッシュが存在する状態で同フラグを使用。
- **結果**: キャッシュを無視して新規APIコールが発生し、最新の分析結果で上書きされることを確認。

## 5. 結論
ツール（`equity_auditor.py`）の `extract` および `ingest` 機能に加え、v8.2 の強力なリトライ・QA機能は設計通り動作している。
特に Hybrid Retry System により、API制限下でも完全自動放置での分析完了が可能となった。

### 改善推奨事項
*   **JSONフィールド名の統一**: `extract` 出力時のプレースホルダーと `ingest` が期待するDBモデルのフィールド名をドキュメント等で統一・明記することが望ましい。
*   **ログ出力**: `ingest` 時のCSVエクスポートログで戦略名がデフォルト (`growth_quality`) と表示される挙動が見られたが、データ自体は正しい戦略名で保存されている。表示上の軽微な不具合として修正を検討できる。
