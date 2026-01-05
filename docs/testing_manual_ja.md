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
