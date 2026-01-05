<<<<<<< HEAD
# ユーザーマニュアル: DB 診断ツール (DB Checker)

## 概要
`src/check_db.py` は、SQLite データベース (`data/stock_history.db`) の中身を直接確認するためのツールです。
SQL クライアントを使わずに、コマンドラインから手軽にデータを CSV 形式で出力できます。

## 使い方

### 先頭 N 件を表示
デフォルトでは先頭 5 件を表示します。
```bash
python src/check_db.py
```

件数を指定する場合（例: 10件）:
```bash
python src/check_db.py -n 10
```

### 全件を表示
保存されているすべてのレコードを出力します。
```bash
python src/check_db.py -a
```

## 出力形式
- **標準出力 (stdout)**: CSV 形式のデータ。ファイルにリダイレクトして保存可能です。
- **標準エラー (stderr)**: `Total records: 175` などのメタ情報。

### 活用例: CSV ファイルへの保存
```bash
python src/check_db.py -a > db_dump.csv
```
このコマンドを実行すると、メタ情報はコンソールに表示され、データ部分だけが `db_dump.csv` に保存されます。
=======
# ユーザーマニュアル: DB 診断ツール (DB Checker)

## 概要
`src/check_db.py` は、SQLite データベース (`data/stock_history.db`) の中身を直接確認するためのツールです。
SQL クライアントを使わずに、コマンドラインから手軽にデータを CSV 形式で出力できます。

## 使い方

### 先頭 N 件を表示
デフォルトでは先頭 5 件を表示します。
```bash
python src/check_db.py
```

件数を指定する場合（例: 10件）:
```bash
python src/check_db.py -n 10
```

### 全件を表示
保存されているすべてのレコードを出力します。
```bash
python src/check_db.py -a
```

## 出力形式
- **標準出力 (stdout)**: CSV 形式のデータ。ファイルにリダイレクトして保存可能です。
- **標準エラー (stderr)**: `Total records: 175` などのメタ情報。

### 活用例: CSV ファイルへの保存
```bash
python src/check_db.py -a > db_dump.csv
```
このコマンドを実行すると、メタ情報はコンソールに表示され、データ部分だけが `db_dump.csv` に保存されます。
>>>>>>> 2466ef38d8256ab6703eab59874909499acd6d9e
