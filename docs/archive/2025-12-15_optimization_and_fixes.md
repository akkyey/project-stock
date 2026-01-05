# プロポーサル: SQL最適化とテスト修正

**作成日**: 2025-12-15
**ステータス**: 提案中

## 背景
v3.7の緊急修正実施後、以下の2つの改善事項が特定されました。
1. **データロードの非効率性**: `load_data_from_db` が全履歴データをメモリに読み込んでからフィルタリングしており、効率が悪くメモリを浪費しています。
2. **テストインポートの不整合**: `self_diagnostic.py` がリネーム前の `ExcelWriter` をインポートしようとしており、テストが失敗します。

## 提案される変更

### 1. データロードの最適化 (`src/analyzer.py`)
**課題**: 全行を取得してからPandasで `drop_duplicates` するのは非効率です。
**解決策**:
* SQLクエリを変更し、各銘柄の最新データのみを取得するようにします。
* `MAX(entry_date)` を使用したサブクエリを利用します。

**変更後のSQLイメージ**:
```sql
SELECT 
    m.id as market_data_id,
    m.code, s.name, m.price as current_price, 
    ...
    m.entry_date, s.sector, s.market
FROM market_data m
JOIN stocks s ON m.code = s.code
WHERE m.entry_date = (
    SELECT MAX(entry_date) 
    FROM market_data m2 
    WHERE m2.code = m.code
)
```

### 2. テストの修正 (`self_diagnostic.py`)
**課題**: `from src.excel_writer import ExcelWriter` が `ImportError` になります。
**解決策**:
* インポート元を `from src.result_writer import ResultWriter` に変更します。
* テストコード内の使用箇所も修正します。

## 検証計画
1. **動作確認**: `stock_analyzer.py --limit 5` を実行し、結果が変わらないことを確認します。
2. **テスト実行**: `python self_diagnostic.py` を実行し、エラーなく通過することを確認します。
