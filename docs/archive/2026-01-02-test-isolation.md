# Proposal: テスト環境の完全分離によるデータ整合性の保護

## 1. 背景と課題
現在、総合テスト（Integration Tests）を実行すると、本番環境のデータ（週次処理のステータスや日次レポート）が上書きされたり、削除されたりするリスクがあります。特に `tests/test_sentinel_orchestrator_integration.py` などのテストコードが `data/output` ディレクトリを直接操作していることが確認されました。

このままでは、テストを実行するたびに本番運用の連続性が失われ、正常なレポーティングができなくなる恐れがあります。

## 2. 解決策のアプローチ
テスト環境と本番環境を物理的・論理的に完全に分離します。これにより、テストが何度実行されても本番データには一切影響を与えない状態を作ります。

### 2.1 環境変数によるモード制御
環境変数 `STOCK_ENV` を導入し、実行モードを制御します。

- **`production` (デフォルト)**: 既存の動作。`config/config.yaml` を読み、`data/` に出力する。
- **`test`**: テスト用設定 `config/test_config.yaml` (またはモック設定) を読み、`tests/output/` または `tmp/` に出力する。DBはメモリ内または一時ファイルを使用する。

### 2.2 ConfigLoader の改修
`src/config_loader.py` を修正し、環境変数に応じて読み込むファイルとデフォルト値を切り替えます。

```python
class ConfigLoader:
    def __init__(self, config_path=None):
        env = os.getenv("STOCK_ENV", "production")
        if config_path is None:
             if env == "test":
                 config_path = "config/test_config.yaml"
             else:
                 config_path = "config/config.yaml"
        # ...
```

また、`test` モード時は設定値に関わらず、重要なパス（DBパス、出力パス）を強制的にテスト用の一時ディレクトリにオーバーライドする安全装置（セーフガード）を実装することを推奨します。

### 2.3 テストコードの修正
既存のテストコード（特に `tests/` 下のファイル）から、ハードコードされたパス (`data/output` など) を排除し、`ConfigLoader` 経由で取得したパス、または `pytest` の `tmp_path` フィクスチャを使用するように書き換えます。

## 3. 具体的な変更点

### 3.1 `src/config_loader.py`
- 環境変数 `STOCK_ENV` の読み取りを追加。
- テストモード時のパス・オーバーライドロジックを追加。

### 3.2 `conftest.py` (新規作成/更新)
- `pytest` 実行時に自動的に `STOCK_ENV=test` を設定するフィクスチャを追加。
- テスト実行終了後に一時ファイルをクリーンアップする処理の強化。

### 3.3 既存テストの修正
- `tests/test_sentinel_orchestrator_integration.py`: `data/output` の削除ロジックを廃止し、一時ディレクトリに対する操作に変更。

## 4. 期待される効果
- **安全性**: テストを実行しても本番の `data/stock_master.db` や `data/output/*.csv` が変更・削除されることがなくなる。
- **再現性**: テストが常にクリーンな環境（空のDB、空の出力ディレクトリ）で開始されるため、テスト結果が安定する。
- **並列実行**: ファイルの競合がなくなるため、将来的にテストの並列実行が可能になる。

## 5. 次のアクション
このプロポーサルが承認され次第、以下の順で実装を行います。
1. `src/config_loader.py` の改修
2. `conftest.py` の整備
3. 既存テストコードのパス修正
4. 検証（本番データが存在する状態でテストを実行し、影響がないことを確認）
