# Proposal: Strict Analyst Rules & 3-Line Summary Standardization

## 背景
ユーザーより、アナリストの分析ルール（閾値、判定ロジック）の厳格化および、出力されるサマリの標準化（3行構成）の要望があった。
これに基づき、設定ファイル、ドキュメント、およびAIプロンプトの改修を提案する。

## 1. アナリストルールの厳格化 (Analyst Rulebook)

### 1.1 閾値設定 (`config/thresholds.yaml`) の拡張
既存の設定に加え、以下の項目を追加する。

```yaml
thresholds:
  # ... (Existing items: valuation, profitability, quality, growth, safety) ...
  
  # [NEW] Anomaly Detection
  anomaly:
    dividend_yield_max: 10.0  # > 10% -> Anomaly
    payout_ratio_max: 200.0   # > 200% -> Anomaly
    payout_ratio_min: 0.0     # = 0% -> Anomaly (if applicable)
    pbr_bubble: 10.0          # > 10x -> Bubble Warning
    roe_bubble: 50.0          # > 50% -> Transient Warning

  # [NEW] Technical
  technical:
    rsi_high: 60  # >= 60 -> Momentum Strong
    rsi_low: 40   # <= 40 -> Momentum Weak
```

### 1.2 判定ロジックの明文化 (`docs/analyst_rules.md`)
以下の判定基準をドキュメントに追加し、プロンプトにも反映させる。

*   **Bullish**: 成長性・収益性・CF・財務が基準クリア AND 割高すぎない AND テクニカル上昇
*   **Neutral**: 強弱混在、または割高成長株、CF懸念の利益改善株など
*   **Bearish**: 売上減少、OCFマイナス、営業利益率5%未満、または著しい割高+トレンド下降

## 2. 出力フォーマットの標準化 (3-Line Summary)

### 2.1 必須フォーマット
AIは以下の形式でのみテキストを生成するように指示する。

1.  **結論行**: `【結論】{判定}。{一言要約}。`
2.  **強み行**: `【強み】{要素1}、{要素2}。（最大3つまで）`
3.  **懸念行**: `【懸念】{要素1}、{要素2}。（最大3つまで）`

### 2.2 詳細解説の構造 (Numbered Structure)
`ai_detail_body` は必ず以下の番号付き構造で出力するようAIに指示する。

```text
① 現状の位置づけ
② 強み
③ 弱み
④ 持続可能性
⑤ 異常値
⑥ テクニカル
⑦ 最終結論
```

### 2.3 出力制御 (Prompt & CSV Logic)
ユーザー要望に基づき、API呼び出しは1回のみとし、レスポンスのJSONスキーマに以下の2つのフィールドを含めることで、両方の解説を同時に取得する。

```json
{
  "ai_sentiment": "Bullish",
  "ai_summary": "【結論】... \n【強み】... \n【懸念】...",    // 3行サマリ (必須)
  "ai_detail_body": "①現状の位置づけ... \n②強み... \n..."  // 詳細解説 (必須)
}
```

*   **Prompt Logic:**
    *   `simple=true` の場合: `ai_summary` のみ生成し、`ai_detail_body` は空文字または生成しないよう指示する。
    *   `simple=false` の場合: `ai_summary` と `ai_detail_body` の両方を生成する。
*   **(A) Simple Report (Summary CSV):**
    *   **出力項目:** `ai_reason` (3行サマリ) を含む。
    *   **除外項目:** `ai_detail` (詳細解説) カラムは**出力しない**（カラム自体を含めない）。
*   **(B) Detailed Report (Full CSV):**
    *   **出力項目:** `ai_reason` (3行サマリ) **かつ** `ai_detail` (詳細解説) の両方を、独立したカラムとして出力する。

### 2.4 データベース拡張 (Migration)
*   **カラム追加:** `AnalysisResult` テーブルに `ai_detail` (TextField, Nullable) を追加する。
*   **目的:** 詳細解説 (`ai_detail_body`) を永続化し、将来の参照や再出力に対応するため。

## 3. 実装計画

### Phase 1: 設定とドキュメントの更新
1.  `config/thresholds.yaml` に異常値・テクニカル閾値を追加。
2.  `docs/analyst_rules.md` に判定ロジックとサマリ生成ルールを追記。

### Phase 2: プロンプト（AI Agent）の改修
1.  `src/ai_agent.py` 内の `_create_prompt` メソッドを改修。
2.  新ルールブックのテキストをプロンプトに埋め込む。
3.  出力スキーマ（JSON）に `ai_summary` (3行固定) と `ai_detail_body` を定義。

### Phase 3: レポーター（Output）の改修
1.  `src/result_writer.py` または `reporter.py` を修正。
2.  `AnalysisResult` モデルに `ai_summary`, `ai_detail_body` カラムを追加（または既存の `ai_reason` を構造化データとして扱う）。
3.  CSV出力時にモード（Simple/Detailed）に応じて出力内容を切り替えるロジックを追加。

## 承認依頼事項
上記方針にて実装を進めて良いか、承認をお願いします。
特に「CSV出力形式（物理2行 vs カラム分離）」について、システム的にはカラム分離が望ましいですが、ユーザー指示の「2行構成」を優先して実装する方針で良いか確認が必要です。
