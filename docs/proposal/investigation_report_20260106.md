# プロジェクト評価およびリファクタリング提案書 (Investigation Report)

## 1. 概要
現状のプロジェクト `project-stock2` (および `stock-analyzer4`) の評価を実施しました。コードは一定の構造化がなされており、`Orchestrator`, `Database`, `AIAgent` といった主要コンポーネントが分離されています。しかし、保守性・拡張性の観点からいくつかの改善点が見受けられました。

## 2. 評価結果

### A. プロジェクト構造 (Maintenance)
*   **現状:** `project-stock2/` 直下に `stock-analyzer4/` があり、その中に `src/` が存在するという入れ子構造になっています。また、`tests/` がルートにありますが、`stock-analyzer4/equity_auditor.py` 等の実行スクリプトが中間に配置されています。
*   **課題:** プロジェクトルートとソースルートが曖昧で、パス解決（`sys.path.append` 等）が複雑化しています。
*   **提案:** ディレクトリ構造のフラット化、または `src` の明確な分離。今回は「破壊的変更」を避けるため、既存構造を維持しつつ `sys.path` 依存を減らす方向で調整します。

### B. テスト構成 (Reliability)
*   **現状:** `self_diagnostic.py` が約1000行の巨大なテストファイルとなっており、単体テスト、統合テスト、モック定義が混在しています。
*   **課題:** テストの追加・修正が困難で、特定の機能だけをテストする際に不便です。また、テスト実行時間が長くなる傾向があります。
*   **提案:** **`self_diagnostic.py` の解体と再編成**。`tests/` ディレクトリ配下に機能別（`test_database.py`, `test_orchestrator.py` 等）に分割し、`pytest` 標準のディスカバリを利用できる形にします。

### C. データベース管理 (Stability)
*   **現状:** `StockDatabase` クラス内で `_manual_migration` メソッドによりカラムの存在確認と `ALTER TABLE` を実行しています。
*   **課題:** マイグレーション管理がコード依存であり、バージョン管理されていません。スキーマ変更時の履歴が追いにくい状態です。
*   **提案:** 簡易的ながらもバージョン管理されたマイグレーション管理（`db_version` テーブルとマイグレーションスクリプト）の導入、または現状の仕組みの整理。

### D. コード品質 (Readability & Logic)
*   **Orchestrator:** `subprocess` を用いて `equity_auditor.py` を呼び出す設計は、プロセスの完全分離としては有効ですが、デバッグやログ集約が複雑になります。
*   **Type Hinting:** 一部のメソッドで型ヒントが欠落しており、静的解析の恩恵を十分に受けられていません。

### E. リポジトリ構成案（公開に向けた最適化・改）
ユーザー様より「テストコードは公開せず、Git管理下には置きたい」というご要望をいただきました。
これを実現するため、**「プライベート・ラッパー構成 (Private Wrapper)」** を提案します。

*   **推奨構成:**
    ```
    project-stock2/ (Private Repo: コントロールタワー)
    ├── .git/
    ├── data/ (Private Data)
    ├── config/ (Private Config & Keys)
    ├── tests/ (Private Tests: 全テストをここに集約) ★ここなら公開されません
    │   ├── unit/ (stock-analyzer4のロジックを外部からテスト)
    │   └── integration/ (実データを使った結合テスト)
    └── stock-analyzer4/ (Public Repo: 純粋なライブラリ)
        ├── .git/
        ├── pyproject.toml
        └── src/ (Core Logic)
            └── (テストコードを含まない)
    ```

*   **メリット:**
    *   **秘匿性の確保:** `stock-analyzer4` を公開リポジトリにPushしても、テストコード（独自の検証ロジックやエッジケースのノウハウ）は一切流出しません。
    *   **品質保証:** `project-stock2` 側で開発を行う限り、`pytest` は `sys.path` を通して `stock-analyzer4/src` をテストできるため、開発体験は変わりません。

### F. ユーザー提案のクリーンアップ・リファクタリング (Recommended Cleanup)
ユーザー様よりご提案いただいた以下のクリーンアップ案について評価し、計画に組み込みます。これらは「機能追加を止めるほどではないが、保守性を高める有効な施策」として位置づけます。

1.  **AnalysisEngine の完全廃止と移行 (Effect: High / Risk: Low)**
    *   **評価:** 承認。`AnalysisEngine` は現状 `ScoringEngine` の薄いラッパーに過ぎず、削除することでインポート階層を単純化できます。
    *   **計画:** フェーズ2（レガシー整理）の一環として実施します。

2.  **バリデーション・ロジックの集約 (Effect: High / Risk: Low)**
    *   **評価:** 承認。`ValidationEngine.is_abnormal()` 等の古いロジックを廃止し、Pydantic モデル (`StockAnalysisData`) に集約することで、データの整合性管理を一元化します。
    *   **計画:** フェーズ3.5（追加フェーズ）として実施、あるいはフェーズ2に追加します。今回はフェーズ2に追加します。

3.  **非同期 I/O の一貫性向上 (Effect: Medium / Risk: Medium)**
    *   **評価:** 保留（Backlog）。SQLite環境では緊急性は低いですが、Sentinel強化時には重要になります。
    *   **計画:** 「将来的な検討事項 (Future Consideration)」としてバックログに記録します。

4.  **戦略定義の外部化 (YAML化) (Effect: High / Risk: High)**
    *   **評価:** 保留（Backlog）。Pythonコードを減らせるメリットは大きいですが、ロジックの抽象化に伴う工数が大きいため、フェーズ1〜3完了後の検討課題とします。

---

本タスクでは、最も効果が高くリスクが低い **「B. テスト構成の再編成」** と **「D. コード品質（型ヒント・不要コード削除）」** を優先して実施することを提案します。
フェーズ1では、**`self_diagnostic.py` を解体し、`project-stock2/tests/unit/` へ移動** します。

### 実施計画 (Implementation Plan)

#### フェーズ1: テスト環境の整備 (優先度: 高)
*   [ ] `project-stock2/tests` ディレクトリの構成を整理する。
    *   `tests/unit/` (新規作成: ライブラリ単体テスト用)
    *   `tests/integration/` (既存テストの整理: 結合テスト用)
*   [ ] `self_diagnostic.py` を以下のモジュールに分割し、`tests/unit/` へ移動する。
    *   `test_database_system.py`
    *   `test_analyzer_engine.py`
    *   `test_utils.py`
*   [ ] `pytest` の設定 (`pytest.ini`) を調整し、`project-stock2` ルートから透過的にテストを実行できるようにする。

#### フェーズ2: レガシーコードの整理 & クリーンアップ (優先度: 中)
*   [ ] ユーザー提案: `src/engine.py` (AnalysisEngine) の削除と呼び出し元の修正。
*   [ ] ユーザー提案: `ValidationEngine` のバリデーションロジックを `StockAnalysisData` (Pydantic) へ完全移行。
*   [ ] 未使用の `tools/legacy/` 配下のスクリプトの影響調査とアーカイブ化。
*   [ ] `src/` 内の未使用インポートやデッドコードの削除。

#### フェーズ3: 型ヒントの導入 (優先度: 低〜中)
*   [ ] 主要モジュール (`src/orchestrator.py`, `src/database.py`, `src/ai/agent.py`) への完全な型ヒント付与。

## 4. ユーザー承認のお願い・確認事項
上記 **リポジトリ構成案(E)** および **クリーンアップ案(F)** を含めた計画で確定し、**フェーズ1（テスト環境の整備）** から着手してよろしいでしょうか？
`self_diagnostic.py` の解体は、将来的な公開を見据えた重要なステップとなります。
