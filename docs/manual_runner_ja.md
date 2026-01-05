# 手動ブラウザ分析ツール (`manual_runner.py`)

## 概要
このツールは、API の制限を回避したり、ブラウザベースの AI モデル（Web 検索機能付きの ChatGPT や Gemini Advanced など）の高度な機能を活用したりするために設計されています。分析プロセスを「準備」と「取込」の2つのステップに分割します。

## アーキテクチャ

### ワークフロー
1.  **ステップ 1: 準備**
    -   入力 CSV を読み込みます。
    -   `config.yaml` に基づいて銘柄をフィルタリングします。
    -   プロンプトファイル (`manual_prompt.txt`) とコンテキストファイル (`data/temp/manual_context.csv`) を生成します。
2.  **人間の操作 (ブラウザ)**
    -   ユーザーがプロンプトをブラウザ AI にコピーします。
    -   ユーザーが AI の JSON レスポンスを `manual_response.json` に保存します。
3.  **ステップ 2: 取込**
    -   `manual_response.json` と `manual_context.csv` を読み込みます。
    -   データをマージします。
    -   結果をデータベースと Excel に保存します。

### ファイル
-   **`manual_prompt.txt`**: AI への指示と銘柄データが含まれています。
-   **`manual_response.json`**: AI からの期待される出力ファイル（JSON 配列である必要があります）。
-   **`data/temp/manual_context.csv`**: 候補銘柄の生のデータを保存する中間ファイルです。

## ユーザーマニュアル

### ステップ 1: 準備
以下のコマンドを実行して銘柄をフィルタリングし、プロンプトを生成します。
```bash
python manual_runner.py --step 1
```
**出力:**
-   `manual_prompt.txt` が作成されます。
-   **アクション:** このファイルの内容をすべてコピーして、ブラウザ AI に貼り付けてください。

### ステップ 2: 取込
AI からレスポンスを得た後:
1.  レスポンスの JSON 部分をコピーします。
2.  プロジェクトルートに `manual_response.json` として保存します。
3.  取込コマンドを実行します:
```bash
python manual_runner.py --step 2
```
**出力:**
-   結果は `data/stock_history.db` に保存されます（戦略名: `manual_browser`）。
-   Excel レポートは `data/output/manual_result.xlsx` に保存されます。

### ヒント
-   **JSON 形式**: AI が有効な JSON 配列を返すようにしてください。AI がマークダウンのコードブロック (```json ... ```) を追加した場合、ツールが処理できない可能性があります（プロンプトでは生の JSON を要求していますが）。
-   **日本語ヘッダー**: ツールは入力 CSV の日本語カラムヘッダーを自動的に処理します。
# 手動ブラウザ分析ツール (`manual_runner.py`)

## 概要
このツールは、API の制限を回避したり、ブラウザベースの AI モデル（Web 検索機能付きの ChatGPT や Gemini Advanced など）の高度な機能を活用したりするために設計されています。分析プロセスを「準備」と「取込」の2つのステップに分割します。

## アーキテクチャ

### ワークフロー
1.  **ステップ 1: 準備**
    -   入力 CSV を読み込みます。
    -   `config.yaml` に基づいて銘柄をフィルタリングします。
    -   プロンプトファイル (`manual_prompt.txt`) とコンテキストファイル (`data/temp/manual_context.csv`) を生成します。
2.  **人間の操作 (ブラウザ)**
    -   ユーザーがプロンプトをブラウザ AI にコピーします。
    -   ユーザーが AI の JSON レスポンスを `manual_response.json` に保存します。
3.  **ステップ 2: 取込**
    -   `manual_response.json` と `manual_context.csv` を読み込みます。
    -   データをマージします。
    -   結果をデータベースと Excel に保存します。

### ファイル
-   **`manual_prompt.txt`**: AI への指示と銘柄データが含まれています。
-   **`manual_response.json`**: AI からの期待される出力ファイル（JSON 配列である必要があります）。
-   **`data/temp/manual_context.csv`**: 候補銘柄の生のデータを保存する中間ファイルです。

## ユーザーマニュアル

### ステップ 1: 準備
以下のコマンドを実行して銘柄をフィルタリングし、プロンプトを生成します。
```bash
python manual_runner.py --step 1
```
**出力:**
-   `manual_prompt.txt` が作成されます。
-   **アクション:** このファイルの内容をすべてコピーして、ブラウザ AI に貼り付けてください。

### ステップ 2: 取込
AI からレスポンスを得た後:
1.  レスポンスの JSON 部分をコピーします。
2.  プロジェクトルートに `manual_response.json` として保存します。
3.  取込コマンドを実行します:
```bash
python manual_runner.py --step 2
```
**出力:**
-   結果は `data/stock_history.db` に保存されます（戦略名: `manual_browser`）。
-   Excel レポートは `data/output/manual_result.xlsx` に保存されます。

### ヒント
-   **JSON 形式**: AI が有効な JSON 配列を返すようにしてください。AI がマークダウンのコードブロック (```json ... ```) を追加した場合、ツールが処理できない可能性があります（プロンプトでは生の JSON を要求していますが）。
-   **日本語ヘッダー**: ツールは入力 CSV の日本語カラムヘッダーを自動的に処理します。
