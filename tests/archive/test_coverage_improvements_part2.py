import unittest
from unittest.mock import MagicMock, patch, call, AsyncMock
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
import pandas as pd
import asyncio

# プロジェクトルートにパスを通す (必要に応じて)
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# モジュールのインポート (依存関係解決後)
try:
    from src.commands.extract import ExtractCommand
    from src.database import StockDatabase
    from src.models import Stock, MarketData, AnalysisResult, SentinelAlert, RankHistory
except ImportError:
    # srcが見つからない場合（テスト環境の構成による）
    pass

class TestExtractCommandExtended(unittest.TestCase):
    """src.commands.extract.ExtractCommand のカバレッジ改善テスト"""

    def setUp(self):
        self.config = {
            "ai": {"model_name": "test-model"},
            "sector_policies": {},
            "system": {"max_workers": 2}
        }
        self.extract_cmd = ExtractCommand(self.config, debug_mode=True)
        self.extract_cmd.logger = MagicMock()
        self.extract_cmd.db = MagicMock()
        self.extract_cmd.provider = MagicMock()
        self.extract_cmd.fetcher = MagicMock()
        # Validatorのモック
        self.extract_cmd.validator = MagicMock()
        self.extract_cmd.validator.validate.return_value = (True, "OK")

    def test_execute_no_candidates(self):
        """候補なしの場合の早期リターン"""
        # _fetch_candidates_by_code をモック
        with patch.object(self.extract_cmd, "_fetch_candidates_by_code", return_value=[]):
            self.extract_cmd.execute(strategy="test", codes=["1111"])
            self.extract_cmd.logger.info.assert_any_call("ℹ️  No candidates found.")

    def test_execute_success_flow(self):
        """正常系の実行フロー (候補あり)"""
        candidates = [{"code": "1001", "market_data_id": 1, "entry_date": "2025-01-01"}]
        
        with patch.object(self.extract_cmd, "_fetch_candidates_logic", return_value=candidates):
            with patch.object(self.extract_cmd, "_run_async_batch") as mock_run:
                # 実行結果: (task, is_valid, reason)
                mock_run.return_value = [(candidates[0], True, "OK")]
                
                with tempfile.TemporaryDirectory() as tmp_dir:
                    out_path = os.path.join(tmp_dir, "tasks.json")
                    self.extract_cmd.execute(strategy="test", output_path=out_path)
                    
                    self.assertTrue(os.path.exists(out_path))
                    self.extract_cmd.logger.info.assert_any_call(f"✅ Saved 1 tasks to: {out_path}")

    @patch("src.commands.extract.asyncio.gather", new_callable=AsyncMock)
    @patch("src.commands.extract.asyncio.Semaphore")
    def test_run_async_batch(self, mock_sem_cls, mock_gather):
        """非同期バッチ処理の呼び出し確認"""
        # Semaphoreのコンテキストマネージャ設定
        mock_sem = mock_sem_cls.return_value
        mock_sem.__aenter__ = AsyncMock(return_value=None)
        mock_sem.__aexit__ = AsyncMock(return_value=None)

        # モックの返り値設定
        mock_gather.return_value = [({"code": "1001"}, True, "OK")]
        
        candidates = [{"code": "1001"}]
        
        # asyncメソッドを実行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(self.extract_cmd._run_async_batch(candidates, "test"))
        finally:
            loop.close()
        
        self.assertEqual(len(results), 1)

    def test_process_single_candidate(self):
        """単一候補の処理ロジック (Deep Repair, Prompt, Validation)"""
        row = {"code": "1001", "name": "Test", "entry_date": "2025-01-01"}
        
        # Deep Repairが無効 (debug_mode=True)
        # Prompt生成のモック
        self.extract_cmd.agent._create_prompt = MagicMock(return_value="Prompt Text")
        # DB ID取得
        self.extract_cmd.db.get_market_data_id.return_value = 123
        
        task, is_valid, reason = self.extract_cmd._process_single_candidate(row, "strategy_A")
        
        self.assertEqual(task["code"], "1001")
        self.assertEqual(task["prompt"], "Prompt Text")
        self.assertEqual(task["market_data_id"], 123)
        self.assertTrue(is_valid)


class TestDatabaseExtended(unittest.TestCase):
    """src.database.StockDatabase のカバレッジ改善テスト"""

    def setUp(self):
        # 一時ファイルDBを作成
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "test_stock.db")
        # StockDatabaseを初期化 (これにより db_proxy もこのDBを向く)
        self.db = StockDatabase(self.db_path)

    def tearDown(self):
        # ディレクトリ削除
        shutil.rmtree(self.tmp_dir)

    def test_fetch_candidates_logic(self):
        """_fetch_candidates_logic の動作確認 (AnalysisEngine連携)"""
        # プロバイダのモック
        df_mock = pd.DataFrame([
            {"code": "1001", "name": "Test", "entry_date": "2025-01-01", "market_data_id": 1}
        ])
        self.extract_cmd.provider.load_latest_market_data.return_value = df_mock
        
        # AnalysisEngineのモックをパッチ
        with patch("src.commands.extract.AnalysisEngine") as mock_engine_cls:
            mock_engine = mock_engine_cls.return_value
            # calculate_scores はDataFrameを返す
            mock_engine.calculate_scores.return_value = df_mock
            # filter_and_rank もDataFrameを返す
            mock_engine.filter_and_rank.return_value = df_mock
            
            # DBキャッシュチェック (get_ai_cache) -> None (未分析)
            self.extract_cmd.db.get_ai_cache.return_value = None
            
            res = self.extract_cmd._fetch_candidates_logic("strategy_A", limit=10)
            
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0]["code"], "1001")


class TestDatabaseExtended(unittest.TestCase):
    """src.database.StockDatabase のカバレッジ改善テスト"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "test_stock.db")
        self.db = StockDatabase(self.db_path)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_init_creates_tables(self):
        """初期化時にテーブルが作成されるか"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        expected = ["stocks", "market_data", "analysis_results", "sentinel_alerts", "rank_history"]
        for t in expected:
            self.assertIn(t, tables)

    def test_manual_migration_adds_columns(self):
        """マイグレーション: カラム追加の分岐テスト"""
        db_path_legacy = os.path.join(self.tmp_dir, "legacy.db")
        import sqlite3
        conn = sqlite3.connect(db_path_legacy)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE market_data (id INTEGER PRIMARY KEY, code TEXT, entry_date TEXT)")
        conn.commit()
        conn.close()
        
        # このDBを開く
        db = StockDatabase(db_path_legacy)
        
        conn = sqlite3.connect(db_path_legacy)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(market_data)")
        cols = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        self.assertIn("payout_ratio", cols)
        self.assertIn("profit_growth", cols)

    def test_manual_migration_no_error(self):
        """通常時のマイグレーション（エラーなし確認）"""
        try:
            self.db._manual_migration()
        except Exception as e:
            self.fail(f"_manual_migration raised exception: {e}")

    def test_upsert_stocks(self):
        """銘柄マスタのUpsert"""
        stocks = [
            {"code": "9001", "name": "Train", "sector": "Transport", "market": "Prime"},
            {"code": "9002", "name": "Bus", "sector": "Transport", "market": "Standard"}
        ]
        self.db.upsert_stocks(stocks)
        
        res = self.db.get_stock("9001")
        self.assertEqual(res["name"], "Train")

    def test_upsert_market_data_and_cleanup(self):
        """MarketDataのUpsertとCleanup"""
        from src.utils import get_today_str
        
        # FK制約回避のためマスタを投入
        self.db.upsert_stocks([{"code": "9001", "name": "Test", "sector": "S", "market": "M"}])
        
        data = [
            {"code": "9001", "price": 100, "current_price": 100, "entry_date": "2020-01-01"}, # 古いデータ
            {"code": "9001", "price": 120, "entry_date": get_today_str()} # 新しいデータ
        ]
        
        self.db.upsert_market_data(data)
        
        # Check insert
        self.assertEqual(MarketData.select().count(), 2)
        
        # Cleanup (retention=30 days)
        # 2020 data is definitely older than 30 days
        success, msg = self.db.cleanup_and_optimize(retention_days=30)
        self.assertTrue(success)
        
        # 残りは1件のはず
        self.assertEqual(MarketData.select().count(), 1)
        remaining = MarketData.select().first()
        self.assertNotEqual(remaining.entry_date, "2020-01-01")


class TestPromptBuilderExtended(unittest.TestCase):
    """src.ai.prompt_builder.PromptBuilder のカバレッジ改善テスト"""

    def setUp(self):
        # テンプレート設定のモックが必要
        self.mock_config = {
            "strategies": {
                "test_strat": {"persona": "Tester", "default_horizon": "Short"}
            },
            "sector_policies": {
                "Technology": {"ai_prompt_excludes": ["per"]}
            },
            "sector_risks": {
                "Technology": "High Volatility"
            }
        }
        
        with patch("src.ai.prompt_builder.PromptBuilder._load_prompt_template") as mock_pt:
            with patch("src.ai.prompt_builder.PromptBuilder._load_thresholds") as mock_th:
                mock_pt.return_value = {
                    "base_template": "{metrics_section}\nDo analyze {name}",
                    "metrics_section": "PER: {per}"  # simple
                }
                mock_th.return_value = {"Basic": {"per_min": 10}}
                
                from src.ai.prompt_builder import PromptBuilder
                self.builder = PromptBuilder(self.mock_config)

    def test_prepare_variables_logic(self):
        """変数生成ロジックの網羅 (Sector Policy, Special Instruction, Deficiency)"""
        row = {
            "code": "1001", "name": "Tech Corp", "sector": "Technology",
            "per": -5.0, # Negative PER -> Special Instruction
            "pbr": None, # Missing -> Deficiency
            "operating_cf": None, # Missing CF -> Deficiency
            "sales": 100, "operating_margin": 0.1
        }
        
        vars_dict = self.builder.prepare_variables(row, "test_strat")
        
        # Sector Policy Excludes
        self.assertIn("exclusion_notice", vars_dict)
        self.assertIn("per", vars_dict.get("exclusion_notice", ""))
        
        # Special Instruction (need strategy="turnaround_spec" to trigger?)
        # Code: if strategy_name == "turnaround_spec": ...
        vars_dict_spec = self.builder.prepare_variables(row, "turnaround_spec")
        self.assertIn("SPECIAL ANALYST INSTRUCTION", vars_dict_spec.get("special_instruction", ""))

        # Deficiency Type: BS欠損(PBR) + CF欠損(OpCF) => 複合欠損?
        # Check logic: has_cf_missing=True, has_pl_missing=False, has_bs_missing=True
        # per is present (negative), so valid? No, if row.get('per') is -5.0, missing logic says:
        # if val is None or (float and isnan). -5.0 is not None/NaN.
        # But PBR is None. OpCF is None.
        # So "CF欠損型", "BS欠損型". len(types)>=2 => "複合欠損型"
        self.assertEqual(vars_dict["deficiency_type"], "複合欠損型")

    def test_create_prompt_error_handling(self):
        """テンプレートフォーマットエラーのハンドリング"""
        # テンプレートが壊れている場合
        self.builder.prompt_config["base_template"] = "{broken_key}"
        
        row = {"code": "1001", "name": "Test"}
        res = self.builder.create_prompt(row, "test_strat")
        
        # Fallback message
        self.assertIn("Analyze stock 1001", res)


class TestAnalyzerExtended(unittest.TestCase):
    """src.analyzer.StockAnalyzer のカバレッジ改善テスト"""

    def setUp(self):
        self.config = {
            "ai": {"interval_sec": 0, "max_concurrency": 1},
            "circuit_breaker": {"consecutive_failure_threshold": 5}
        }
        from src.analyzer import StockAnalyzer
        
        with patch("src.analyzer.DataProvider"), \
             patch("src.analyzer.AnalysisEngine"), \
             patch("src.analyzer.ResultWriter"), \
             patch("src.analyzer.AIAgent"):
            self.analyzer = StockAnalyzer(self.config, debug_mode=True)
            self.analyzer.logger = MagicMock()
            self.analyzer.provider = MagicMock()
            self.analyzer.engine = MagicMock()
            self.analyzer.writer = MagicMock()
            self.analyzer.ai_agent = MagicMock()

    def test_run_analysis_input_path(self):
        """CSV入力からの実行"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
            tmp.write("code,name\n9999,TestComp\n")
            tmp_path = tmp.name
        
        try:
            self.analyzer.run_analysis(input_path=tmp_path, limit=1)
            # provider.load_latest... should NOT be called
            self.analyzer.provider.load_latest_market_data.assert_not_called()
            # AI analysis loop executed?
            # Mock _run_async_batch or check calls
            # As run_analysis calls asyncio.run(_run_async_batch), mocking it is hard inside method
            # But process_single_stock is called.
            
            # Since mocking inner async function is hard without patching class method that wraps it,
            # we can assume if log "Loaded ... records" appears we passed input loading.
            self.analyzer.logger.info.assert_any_call(f"Loaded 1 records from CSV.")
        finally:
            os.remove(tmp_path)

    def test_process_single_stock_smart_cache(self):
        """Smart Cacheの動作確認"""
        row = {"code": "1001"}
        
        # Cache Hit (Smart Cache)
        cached_data = {
            "ai_sentiment": "Bullish",
            "_is_smart_cache": True,
            "analyzed_at": datetime(2025, 1, 1)
        }
        self.analyzer.provider.get_ai_cache.return_value = (cached_data, "hash123")
        
        res = self.analyzer.process_single_stock(row, "test_strat")
        
        self.assertEqual(res["_cache_label"], "♻️  Smart Cache (from 2025-01-01)")
        # AI analyze NOT called
        self.analyzer.ai_agent.analyze.assert_not_called()

    def test_process_single_stock_no_cache(self):
        """キャッシュなしでAI実行"""
        row = {"code": "1001"}
        self.analyzer.provider.get_ai_cache.return_value = (None, "hash_new")
        self.analyzer.ai_agent.analyze.return_value = {"ai_sentiment": "Bearish"}
        
        res = self.analyzer.process_single_stock(row, "test_strat")
        
        self.assertEqual(res["ai_sentiment"], "Bearish")
        self.analyzer.provider.save_analysis_result.assert_called()

if __name__ == "__main__":
    unittest.main()
