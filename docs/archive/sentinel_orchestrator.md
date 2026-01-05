# Sentinel & Orchestrator 実装プロポーサル

## 1. 概要
本プロポーサルでは、既存の株価分析システム（`equity_auditor.py`）上に、市場監視を行う「Sentinel（哨兵）」と、分析プロセスを統括する「Orchestrator（司令塔）」を導入し、運用の自動化と効率化を実現するアーキテクチャを定義します。

## 2. アーキテクチャ設計

### 2.1 全体像
```mermaid
graph TD
    External[市場データ (yfinance/JPX)] --> Sentinel[Sentinel (哨兵)]
    DB[(stock.db)] <--> Sentinel
    Sentinel -->|異変検知| Alerts[SentinelAlert Table]
    
    User((User)) --> Orchestrator[Orchestrator (司令塔)]
    Orchestrator <--> DB
    Orchestrator -->|分析指示 (Reset Version)| DB
    Orchestrator -->|分析実行 (Subprocess)| EquityAuditor[EquityAuditor (分析機)]
    EquityAuditor -->|結果保存| DB
    Orchestrator -->|レポート出力| CSV[Daily/Weekly Report]
```

### 2.2 コンポーネント定義

#### A. Sentinel (sentinel.py & src/sentinel.py)
*   **役割**: 市場の常時監視と「異変」の検知。独立コマンドとして実行。
*   **動作**:
    1.  `python sentinel.py --limit 200` 等で起動。
    2.  `stock.db` から最新の「ランキング上位200銘柄」を取得。
    3.  `yfinance` 等を使用して、対象銘柄の最新株価・技術指標を軽量スキャン。
    3.  **異変検知ロジック**:
        *   **Elite変動**: 戦略別TOP5への入賞/転落。
            *   **注**: 「TOP5からの陥落」判定は、前日の暫定データではなく、**RankHistory テーブルにある最新の公式レコード**と比較して判定する。これにより、Orchestratorが処理しない限りアラートは継続する。
        *   **Volatility**: 前日比 ±5% 以上の急騰落。
        *   **Technical**: MACDゴールデンクロス等のシグナル検知。
    4.  検知結果を `sentinel_alerts` テーブルに保存（未処理ステータス）。

#### B. Orchestrator (orchestrator.py & src/orchestrator.py)
*   **役割**: システム全体の指揮・統制。独立コマンドとして実行。
*   **実行モード**:
    *   **Daily**: `sentinel` ロジックの呼び出し（または結果確認）、上位200銘柄の簡易更新、CSV出力。
        *   **Overdue Alert**: `is_processed=0` かつ `detected_at` が24時間以上前のアラートは、ログやCSV出力時に **`[CRITICAL: OVERDUE]`** 接頭辞を付与して警告する。
    *   **Weekly**: ランキング確定処理、`rank_history` への履歴保存。
    *   **Monthly**: 全銘柄（約3,800件）のフルスキャン指示。
*   **出力仕様（案B - Best Strategy選定）**:
    *   同一銘柄が複数の戦略（例: ValueとGrowth）でランクインしている場合、**「より順位が高い（数字が小さい）方の戦略」**を `Best_Strategy` として採用する。もう一方は出力しない（または詳細情報として保持）。
    *   **履歴表示**: `RankHistory` にデータが存在しない期間（圏外）は、CSV出力時に「`-`」として整形する。
*   **公式順位の定義と更新**:
    *   `RankHistory` テーブルへのレコード追加は、原則として **Weekly実行時** または **Orchestratorが公式に認めたタイミング** に限定する（Daily実行では更新しない）。これにより、Sentinelの陥落判定基準がブレることを防ぐ。
*   **ハンドシェイク機能**:
    *   起動時に `sentinel_alerts` の未処理件数を確認。
    *   ユーザーに対し、対象銘柄の「AI再分析（Audit Versionリセット）」を提案・実行。
    *   処理完了後、アラートを処理済み（is_processed=1）に更新。

#### C. EquityAuditor (equity_auditor.py)
*   **役割**: 個別分析（アナリスト）に特化。Sentinel/Orchestrator機能は持たない。
*   **コマンド**: `python equity_auditor.py --mode analyze` 等。

---

## 3. データベース拡張 (src/models.py)

既存の `stock.db` に対し、以下の2テーブルを追加します。

### 3.1 SentinelAlert
異変検知イベントを管理します。

| Column          | Type      | Description                                         |
| :-------------- | :-------- | :-------------------------------------------------- |
| `id`            | AutoField | PK                                                  |
| `code`          | CharField | 銘柄コード (FK)                                     |
| `alert_type`    | CharField | 異変種別 ('rank_change', 'volatility', 'technical') |
| `alert_message` | TextField | 詳細メッセージ（例: "Rank limit exceeded: 3 -> 6"） |
| `detected_at`   | DateTime  | 検知日時                                            |
| `is_processed`  | Boolean   | 処理済みフラグ (Default: False)                     |
| `processed_at`  | DateTime  | 処理日時                                            |

### 3.2 RankHistory
銘柄の順位変動履歴を保持します。

| Column          | Type      | Description                |
| :-------------- | :-------- | :------------------------- |
| `id`            | AutoField | PK                         |
| `code`          | CharField | 銘柄コード (FK)            |
| `strategy_name` | CharField | 戦略名                     |
| `rank`          | Integer   | 当該時点の順位             |
| `score`         | Float     | 当該時点のスコア           |
| `recorded_at`   | DateTime  | 記録日時（Weekly実行時等） |

---

## 4. 実装計画

### Phase 1: データベース拡張
1.  `src/models.py` に `SentinelAlert`, `RankHistory` クラスを追加。
2.  マイグレーション（または `check_db.py`）によりテーブル作成。

### Phase 2: Sentinel 実装
1.  `src/sentinel.py` の作成。
    *   ランキング取得ロジック（`AnalysisResult` から集計）。
    *   `src/fetcher` を活用した軽量データ取得。
    *   検知ロジックの実装。
2.  `EquityAuditor` へのコマンド統合。

### Phase 3: Orchestrator 実装
1.  `src/orchestrator.py` の作成。
    *   モード管理（Daily/Weekly/Monthly）。
    *   `sentinel_alerts` の読み出しとハンドシェイクUI。
    *   AI再分析トリガー（`audit_version` リセット処理）。
    *   CSVレポート生成（`pandas` を活用）。

### Phase 4: 統合テスト
1.  一連のフロー（Sentinel検知 -> Orchestrator確認 -> 再分析 -> レポート）の導通確認。

## 5. 既存資産の活用方針
*   **データ取得**: `src/fetcher/data_fetcher.py` を再利用し、コードの重複を防ぎます。
*   **DB操作**: `src/models.py` および `src/database.py` の `db_proxy` を経由し、一貫性を保ちます。
*   **AI分析**: 直接AIを呼び出すのではなく、`audit_version` を操作して既存の `AnalyzeCommand` に処理を委譲することで、ロジックの一元化を図ります。
