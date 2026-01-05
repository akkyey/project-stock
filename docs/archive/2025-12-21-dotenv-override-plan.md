# 環境変数の強制上書き設定適用プラン

`.env` ファイルの設定をシステム環境変数より優先させるため、`load_dotenv()` に `override=True` を追加します。

## 調査結果概要
以下のファイルで `load_dotenv()` が呼び出されていることを確認しました。
- [stock_analyzer.py](file:///home/irom/stock-analyzer3/stock_analyzer.py)
- [check_models.py](file:///home/irom/stock-analyzer3/check_models.py)

## 提案される変更

### [Core]
#### [MODIFY] [stock_analyzer.py](file:///home/irom/stock-analyzer3/stock_analyzer.py)
- `load_dotenv()` を `load_dotenv(override=True)` に変更します。

### [Tools]
#### [MODIFY] [check_models.py](file:///home/irom/stock-analyzer3/check_models.py)
- `load_dotenv()` を `load_dotenv(override=True)` に変更します。

## 検証プラン

### Automated Tests
- `python3 self_diagnostic.py` を実行し、既存の機能に影響がないことを確認します。
- `venv/bin/python3 check_models.py` を実行し、引き続き正常に動作することを確認します。

### Manual Verification
- 必要に応じて、一時的にシステム環境変数を設定し、`.env` の値で上書きされることを手動テストで確認できます（ユーザーによる最終確認）。
