# Stock Analyzer 運用マニュアル (Standalone)

## 概要
本プロジェクトは、`stock-analyzer` リポジトリ単体で動作します。
開発は IDE (Antigravity等) で行い、日々の定期実行（運用）を **Google Colab** で行います。

## ノートブック構成

| ノートブック名             | 役割                                                    | 格納場所                        |
| -------------------------- | ------------------------------------------------------- | ------------------------------- |
| **`run_analysis.ipynb`**   | **本番運用用**。日次/週次レポートの生成、DB更新を行う。 | `notebook/run_analysis.ipynb`   |
| **`run_diagnostic.ipynb`** | **正常性確認用**。環境構築テスト、DB接続テストを行う。  | `notebook/run_diagnostic.ipynb` |

## 運用フロー (Daily/Weekly)

### 1. Colab で `run_analysis.ipynb` を開く
GitHub 上の `notebook/run_analysis.ipynb` を Google Colab で開きます。

### 2. 環境変数の設定 (初回/セッション切れ時)
ノートブックを実行すると、以下の入力が求められます。
- **GitHub Username / Token (PAT)**: Privateリポジトリ (`stock-analyzer`) の取得用。
- **Gemini API Key**: AI分析 (`equity_auditor.py`) 実行用。

### 3. パラメータ設定
セル内のフォームで動作モードを設定します。

| パラメータ      | 説明                                            | 推奨設定                               |
| --------------- | ----------------------------------------------- | -------------------------------------- |
| `MOUNT_DRIVE`   | Google Drive をマウントし、データを永続化するか | `True` (運用時) / `False` (テスト時)   |
| `INITIALIZE_DB` | データベースを初期化（全消去＆再構築）するか    | **`False`** (通常) / `True` (初回のみ) |

### 4. 実行 (Daily / Weekly)
目的に応じて、以下のいずれかのセルを実行します。
- **5. 分析実行 (日次 - Daily)**: 毎日のルーチンワーク。
- **6. 分析実行 (週次 - Weekly)**: 週末の全件分析・ランキング更新。

### 5. 結果の確認
- `data/output/` フォルダ（Driveマウント時は `Drive/MyDrive/StockAnalyzer_Prod/output`）に CSV レポートが生成されていることを確認します。

## トラブルシューティング

### Q. `ImportError: No module named 'src'`
- **A.** `setup_production_env()` でのクローンに失敗しているか、Pythonパスの設定がうまくいっていません。ノートブックを再起動し、認証情報を正しく入力してください。

### Q. `orchestrator.py` not found
- **A.** 古いノートブックを使用している可能性があります。`stock-analyzer` リポジトリのルートに `orchestrator.py` がある構成であることを確認してください。
