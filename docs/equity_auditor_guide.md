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
