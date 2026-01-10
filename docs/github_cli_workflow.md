# GitHub CLI (gh) セットアップ・運用ガイド

VSCodeのターミナルから、GitHubの操作（PR作成・マージなど）を効率的に行うためのマニュアルです。


## 1. インストール (Linux / Ubuntu)

```bash
# ツール準備
sudo apt-get update
sudo apt-get install -y wget

# キーリング追加
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg

# リポジトリ追加
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

# インストール実行
sudo apt-get update
sudo apt-get install gh
```


## 2. 認証 (初回のみ)

リモート環境やヘッドレス環境では、トークン認証が推奨されます。

1.  **トークン取得**: [GitHub Tokens (Classic)](https://github.com/settings/tokens/new)
    *   Scopes: `repo`, `read:org`, `workflow` にチェック
2.  **認証コマンド**:
    ```bash
    gh auth login
    ```
    *   `GitHub.com` -> `HTTPS` -> `Yes` -> `Paste an authentication token` の順に選択し、トークンを貼り付け。

## 3. 基本ワークフロー

AIエージェントに依頼する場合のコマンド例としても使用できます。

### ブランチ作成と作業
```bash
git checkout main
git pull
git checkout -b feat/feature-name
# ...コード修正とコミット...
git push origin feat/feature-name
```

### Pull Request (PR) の作成
ブラウザを開かずにPRを作成します。

```bash
# 通常のPR
gh pr create --title "feat: 新機能追加" --body "機能の詳細説明"

# Draft PR (作業中)
gh pr create --draft --title "feat: 作業中" --body "まだマージしないでください"

# 親ブランチ(Base)を指定する場合（Epic運用など）
gh pr create --base epic/target-branch --title "feat: 子タスク"
```

### PRのマージ
承認が降りたら、ブランチの削除まで一発で行います。

```bash
# マージ ＆ リモートブランチ削除 ＆ ローカルブランチ削除（手動）
gh pr merge --merge --delete-branch
```

## 4. AIエージェントへの依頼方法

AIエージェントは `gh` コマンドを使用できるため、以下のように依頼するとスムーズです。

> 「〇〇の修正をして、PRを作ってください（マージまでお願い）」

エージェントは以下の手順で代行します：
1.  コード修正 & Push
2.  `gh pr create` でPR作成 & URL提示
3.  (ユーザー確認後) `gh pr merge` で完了
