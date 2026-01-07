# Stock Analyzer 運用マニュアル

## 概要
本プロジェクトは、開発を **Antigravity (IDE)** で行い、日々の定期実行（運用）を **Google Colab** で行う体制をとっています。

## ノートブック構成

| ノートブック名             | 役割                                                                       | 格納場所                                        |
| -------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------- |
| **`run_analysis.ipynb`**   | **本番運用用**。日次/週次レポートの生成、DB更新を行う。                    | `stock-analyzer4/notebook/run_analysis.ipynb`   |
| **`run_diagnostic.ipynb`** | **正常性確認用**。環境構築テスト、依存関係チェック、簡易接続テストを行う。 | `stock-analyzer4/notebook/run_diagnostic.ipynb` |

## 運用フロー (Daily/Weekly)

### 1. Colab で `run_analysis.ipynb` を開く
GitHub 上の `run_analysis.ipynb` を Google Colab で開きます。

### 2. 環境変数の設定 (初回/セッション切れ時)
ノートブックを実行すると、以下の入力が求められます。
- **GitHub Username / Token (PAT)**: Privateリポジトリ (`project-stock`) およびサブモジュール (`stock-analyzer`) の取得用。
- **Gemini API Key**: AI分析 (`equity_auditor.py`) 実行用。

### 3. パラメータ設定
セル内のフォームで動作モードを設定します。

| パラメータ       | 説明                                            | 推奨設定                               |
| ---------------- | ----------------------------------------------- | -------------------------------------- |
| `MOUNT_DRIVE`    | Google Drive をマウントし、データを永続化するか | `True` (運用時) / `False` (テスト時)   |
| `INITIALIZE_DB`  | データベースを初期化（全消去＆再構築）するか    | **`False`** (通常) / `True` (初回のみ) |
| `EXECUTION_MODE` | 分析モード (`daily` / `weekly`)                 | 用途に合わせて選択                     |

### 4. 実行
すべてのセルを上から順に実行（または「すべてのセルを実行」）します。
正常に完了すると、`✅ 実行完了` と表示されます。

### 5. 結果の確認
- `data/output/` フォルダ（Driveマウント時は `Drive/MyDrive/StockAnalyzer_Prod/output`）に CSV レポートが生成されていることを確認します。

## トラブルシューティング

### Q. `ImportError` や `ModuleNotFoundError` が出る
- **A.** `requirements.txt` の同期遅れやパス設定ミスの可能性があります。ノートブック冒頭の `setup_production_env()` が `✅ 同期完了` となっているか確認してください。

### Q. サブモジュールが見つからない / path エラー
- **A.** Privateリポジトリの認証に失敗している可能性があります。ノートブックを再起動し、正しい PAT (Personal Access Token) を入力してください。

### Q. 実行引数エラー (`unrecognized arguments`)
- **A.** ノートブックのバージョンが古い可能性があります。GitHub 上の最新コード (`git reset --hard` が走ることで解消されますが、セル自体の記述が古い場合はブラウザのリロードを行ってください)。
