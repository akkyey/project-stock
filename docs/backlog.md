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
- [x] **Calculate Real Volatility from History** (Status: Completed - 2026-01-07)
  - **Details**: Implemented in `technical.py` using daily log returns (6mo history) and integrated into `ScoringEngine` as a risk adjustment factor.

---

## Maintenance & Compliance
- [ ] **Maintain Mypy Compliance** (Status: Proposed)
  - **Proposed**: 2026-01-01
  - **Details**: `Success: no issues found` を維持するための CI 連携や開発ガイドラインの整備。
  - **Reason**: 長期的なプロジェクトの保守性確保。

---
*Note: Completed integration tests and test isolation issues have been resolved and removed from the active backlog (2026-01-02).*
