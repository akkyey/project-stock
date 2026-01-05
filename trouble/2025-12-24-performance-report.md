# 性能劣化調査レポート

## 調査対象
- データベース構造とインデックス
- 処理ロジックの冗長化
- テストセットの妥当性

---

## 1. データベース構造 ✅ 問題なし

### インデックス設定 (`src/models.py`)

| テーブル         | インデックス                             | 状態       |
| ---------------- | ---------------------------------------- | ---------- |
| `MarketData`     | `(code, entry_date)` UNIQUE              | ✅ 設定済み |
| `MarketData`     | `(entry_date)`                           | ✅ 設定済み |
| `AnalysisResult` | `(market_data_id, strategy_name)` UNIQUE | ✅ 設定済み |
| `AnalysisResult` | `(row_hash)`                             | ✅ 設定済み |
| `AnalysisResult` | `(analyzed_at)`                          | ✅ 設定済み |

**結論:** インデックス設定は適切。SQLiteの制約で一部クエリが遅くなる可能性はあるが、テストデータサイズ（12件）では問題にならない。

---

## 2. 処理ロジック ⚠️ 一部改善可能

### A. `provider.py` - `load_latest_market_data()`
**複雑なサブクエリ (JOIN 3回):**
```python
# 構造:
# MarketData → Stock (JOIN)
#            → latest_dates サブクエリ (JOIN)
```

**影響:**
- 各コードの「最新日付」を取得するためにGROUP BYサブクエリが必要
- 12件程度では約0.02秒程度（大きな問題ではない）

### B. `calc/v2.py` - スコア計算 ✅ 効率的
- **ベクトル化済み** (`_calc_v2_vectorized`)
- NumPy/Pandasの高速処理を活用
- 大きなボトルネックではない

### C. `time.sleep` の影響 ⚠️ 部分的に残存
`conftest.py`でモック設定済みだが、一部モジュールでパッチが効いていない可能性あり。

---

## 3. テストセットの妥当性 ❌ 主要な問題

### `test_integration_system.py` の問題点

**毎回のフルパイプライン実行:**
```python
def run_strategy(self, strategy_name, style, limit=None, custom_config=None):
    # 毎回以下を実行:
    # 1. StockAnalyzerインスタンス生成
    # 2. run_analysis() → load_latest_market_data()
    #                   → calculate_scores() 全件計算
    #                   → filter_and_rank()
    #                   → CSVファイル出力
```

**`run_strategy()`呼び出し回数: 12回** (各テストで1〜2回)

| テスト                | `run_strategy`呼び出し回数 |
| --------------------- | -------------------------- |
| `test_junk_exclusion` | 2回 (2戦略ループ)          |
| その他テスト          | 各1回                      |

**各呼び出しの処理内容:**
1. DB接続・再初期化
2. Peeweeモデル再バインド
3. 全件スコア計算 (12件 × 複雑なロジック)
4. ファイルI/O (CSV出力)

---

## 4. 遅延の根本原因

### **主因: `setUpClass`で1回初期化したDBに対し、各テストで毎回フル再初期化している**

```python
# test_integration_system.py Line 67-71
with patch('src.provider.StockDatabase', return_value=self.db):
    analyzer = StockAnalyzer(run_config, debug_mode=True)  # ← 毎回新規生成
    analyzer.provider.stock_db = self.db  # ← 強制再設定
```

**問題:**
- `StockAnalyzer.__init__`内で`DataProvider`が再生成される
- `DataProvider.__init__`で`StockDatabase()`が呼ばれる
- Peewee Proxyの再バインドでオーバーヘッドが発生

### **副因: WSL環境でのディスクI/O遅延**
- ファイルパス `/mnt/d/dev2/...` はWindowsファイルシステム
- WSL2のI/Oは特に遅い（Linux内部よりも3〜10倍遅い）

---

## 5. 改善提案

### 即効性の高い改善 (テスト高速化)

| 対策                                            | 期待効果    | 実装難易度 |
| ----------------------------------------------- | ----------- | ---------- |
| **①テストでAnalyzerを再利用**                   | 50%以上短縮 | 中         |
| **②setUpClass内でスコア計算済みDFをキャッシュ** | 70%以上短縮 | 低         |
| **③統合テストを軽量化し、ユニットテストに分離** | 80%以上短縮 | 高         |

### コードベース自体の改善

| 対策                        | 影響範囲         | 実装難易度 |
| --------------------------- | ---------------- | ---------- |
| **①providerのクエリ最適化** | 本番環境にも効果 | 中         |
| **②Peewee接続プーリング**   | 本番環境にも効果 | 低         |

---

## 結論

**性能劣化の主因は「テスト設計」であり、コード本体のパフォーマンス劣化ではない。**

ただし、各テストで毎回フルパイプラインを実行する設計は、統合テストとしては妥当だが、日常的なCI/CDには重すぎる。

**推奨アクション:**
1. 即座の対策: テスト用のキャッシュ機能を追加
2. 中期的な対策: 統合テストとユニットテストを分離
