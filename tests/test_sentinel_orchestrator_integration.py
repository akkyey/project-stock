import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.database import StockDatabase
from src.models import (
    AnalysisResult,
    MarketData,
    RankHistory,
    SentinelAlert,
    Stock,
    db_proxy,
)
from src.orchestrator import Orchestrator
from src.sentinel import Sentinel
from src.utils import get_current_time


# Helper to setup minimal DB state
def setup_module(module):
    # Ensure test env
    # Using a temporary test db to avoid messing up main DB?
    # Or assuming test fixture handles it.
    # We'll use :memory: if possible, but the system uses `db_proxy` which is global.
    # And StockDatabase default path.
    # Let's mock StockDatabase init to use a specific test file.
    pass


@pytest.mark.integration
class TestSentinelOrchestratorIntegration:

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Patch StockDatabase in Orchestrator and Sentinel to use our test DB environment
        # Note: In 'test' env, ConfigLoader forces a temp DB path.
        # But StockDatabase(db_path=...) arg takes precedence if provided.
        # Here we want to respect the Env variable STOCK_TEST_DB_PATH set by conftest.

        test_db_path = os.getenv("STOCK_TEST_DB_PATH")
        if not test_db_path:
            # Fallback for standalone run without pytest fixture
            test_db_path = "tests/test_stock_master.db"

        # Initialize DB at this path
        self.db = StockDatabase(db_path=test_db_path)

        with db_proxy.connection_context():
            db_proxy.drop_tables(
                [Stock, MarketData, AnalysisResult, SentinelAlert, RankHistory],
                safe=True,
            )
            db_proxy.create_tables(
                [Stock, MarketData, AnalysisResult, SentinelAlert, RankHistory],
                safe=True,
            )

        patcher_orch = patch("src.orchestrator.StockDatabase", return_value=self.db)
        patcher_sent = patch("src.sentinel.StockDatabase", return_value=self.db)
        patcher_orch.start()
        patcher_sent.start()

        # Clean output dir
        # Managed by conftest.py or ConfigLoader override.
        # We don't need to manually delete data/output anymore.
        pass

        yield

        patcher_orch.stop()
        patcher_sent.stop()

        # Teardown
        # Teardown - conftest handles dir cleanup
        pass

    def test_sentinel_alert_generation(self):
        """Verify Sentinel generates alerts for volatility and rank changes."""

        # 1. Setup Data
        with db_proxy.atomic():
            Stock.create(code="9999", name="TestCorp", sector="Tech", market="Prime")
            AnalysisResult.create(
                market_data=MarketData.create(
                    code="9999", price=1000, entry_date="2025-01-01"
                ),
                strategy_name="test_strat",
                quant_score=90,
                analyzed_at=get_current_time() - timedelta(days=7), # Set to a past date
            )
            print("DEBUG: Initial Stock and AnalysisResult created.")

        # 2. Mock DataFetcher to return market data with volatility
        # Sentinel calls: _scan_market -> _process_yf_df
        # We'll mock _scan_market directly to return our crafted map to avoid yfinance call

        mock_scan_data = {
            "9999": {
                "code": "9999",
                "price": 1100.0,
                "prev_price": 1000.0,
                "change_pct": 10.0,  # +10% volatility
                "macd": 5.0,
                "macd_signal": 4.0,
                "golden_cross": True,  # Technical signal
                "dead_cross": False,
                "entry_date": "2025-01-01",
            }
        }

        sentinel = Sentinel(debug_mode=True)
        # Mocking external calls
        assigned_scan = MagicMock(return_value=mock_scan_data)
        sentinel._scan_market = assigned_scan

        # Mock _get_surveillance_targets
        sentinel._get_surveillance_targets = MagicMock(return_value=["9999"])

        # Mock Engine for Rank Calc (Simulating Rank Fall)
        # We need RankHistory state.
        RankHistory.create(
            code="9999",
            strategy_name="test_strat",
            rank=1,
            score=95,
            recorded_at=get_current_time(),
        )

        # Sentinel Run
        # We mock engine.calculate_scores inside Sentinel if needed, or assume real engine works with mocked data fetch.
        # Ideally we let Sentinel rely on `calculate_scores`.
        # Sentinel calls fetcher.fetch_data_from_db. We need data in DB.
        # We already added MarketData above.

        # But Sentinel update:
        # It updates `base_df` with scan price.
        # Then calls `engine.calculate_scores`.

        sentinel.run(limit=1)

        # 3. Validation
        alerts = list(SentinelAlert.select())
        assert len(alerts) >= 2  # Volatility + Technical (maybe Rank?)

        types = [a.alert_type for a in alerts]
        assert "volatility" in types
        assert "technical" in types
        # Rank change depends on logic. If score dropped enough?

    def test_orchestrator_daily_flow(self):
        """Verify Orchestrator processes alerts and generates report."""

        # 1. Setup Alerts
        SentinelAlert.create(
            code="8888",
            alert_type="volatility",
            alert_message="Test Volatility",
            detected_at=get_current_time(),
        )

        # 2. Setup Analysis Result for Reporting
        with db_proxy.atomic():
            Stock.create(code="8888", name="OrchCorp", sector="Tech", market="Prime")
            md = MarketData.create(
                code="8888",
                price=2000,
                trend_score=3,
                macd_hist=0.5,
                # Essential financial data for validation
                sales=10000,
                operating_cf=1000,
                operating_margin=10.0,
                debt_equity_ratio=0.5,
                free_cf=500.0,
                volatility=0.2,
                roe=10.0,
                per=15.0,
                pbr=1.5,
                equity_ratio=50.0,
                entry_date="2025-01-01",
            )
            # 4. Create an older analysis result (manual)
            # Use 'Balanced Strategy' to match orchestrator config
            ar = AnalysisResult.create(
                market_data=md,
                strategy_name="Balanced Strategy",
                quant_score=85,
                ai_sentiment="Bullish",
                analyzed_at=get_current_time() - timedelta(days=1),  # Yesterday
            )

        # Prepare Config
        test_db_path = os.getenv("STOCK_TEST_DB_PATH", "tests/test_stock_master.db")
        test_out_dir = os.getenv("STOCK_TEST_OUTPUT_PATH", "tests/data/output")

        test_config = {
            "strategies": {
                "Balanced Strategy": {
                    "base_score": 0,
                    "min_requirements": {},
                    "thresholds": {},
                }
            },
            "system": {"concurrency": 1},
            "ai": {"max_concurrency": 1},
            "paths": {
                "db_file": test_db_path,
                "output_dir": test_out_dir,
            },
            "scoring_v2": {"styles": {"default": {}}},
        }

        # Patch ConfigLoader to return our test_config
        with patch("src.orchestrator.ConfigLoader") as mock_cfg_loader_cls:
            mock_cfg_loader = MagicMock()
            mock_cfg_loader.config = test_config
            mock_cfg_loader_cls.return_value = mock_cfg_loader

            orchestrator = Orchestrator(debug_mode=True)
            # Ensure internal config is set
            orchestrator.config = test_config

        # Mock subprocess.run to execute analysis in-process so it sees our mocked config
        # and runs in the same environment (mocked DB path etc)
        # Also patch yfinance to prevent potential fetch attempts in Fallback/Enrichment
        with (
            patch("src.orchestrator.subprocess.run") as mock_run,
            patch("yfinance.download") as mock_yf,
        ):

            mock_yf.side_effect = Exception("Network blocked in test")

            def run_analysis_in_process(cmd, **kwargs):
                import subprocess

                from src.commands.analyze import AnalyzeCommand

                args = cmd
                codes = []
                strategy = "Balanced Strategy"
                if "--codes" in args:
                    idx = args.index("--codes")
                    codes = args[idx + 1].split(",")
                if "--strategy" in args:
                    idx_strat = args.index("--strategy")
                    strategy = args[idx_strat + 1]

                # Use the SAME config as orchestrator
                analyze_cmd = AnalyzeCommand(
                    config=orchestrator.config, debug_mode=True
                )
                analyze_cmd.execute(codes=codes, strategy=strategy)

                return subprocess.CompletedProcess(args=cmd, returncode=0)

            mock_run.side_effect = run_analysis_in_process

            # Run Daily
            orchestrator.run("daily")

        # 3. Verify Report
        from pathlib import Path
    
        # Use the overridden output path
        output_dir = Path(test_out_dir)
        report_files = list(output_dir.glob("daily_report_*.csv"))
        assert len(report_files) > 0, "No daily report generated"

        # Open latest
        latest_report = max(report_files, key=os.path.getctime)
        df = pd.read_csv(latest_report)
        assert len(df) >= 1
        # Check if 8888 is present in Code column
        assert 8888 in df["Code"].values or "8888" in df["Code"].astype(str).values

    def test_orchestrator_weekly_flow(self):
        """Verify Orchestrator usage of RankHistory update."""
        import time

        # 一意のentry_dateを生成
        unique_date = f"2025-01-{int(time.time() % 100):02d}"

        # Setup Data - 重複を避けるためget_or_createを使用
        with db_proxy.atomic():
            s, created = Stock.get_or_create(
                code="7777",
                defaults={"name": "RankCorp", "sector": "Retail", "market": "Prime"},
            )
            md = MarketData.create(code="7777", price=500, entry_date=unique_date)
            AnalysisResult.create(
                market_data=md,
                strategy_name="strategy_B",
                quant_score=99,
                analyzed_at=get_current_time(),
            )

        orchestrator = Orchestrator(debug_mode=True)
        # Mock Sentinel
        orchestrator.sentinel.run = MagicMock()
        # Mock Config for Strategy Loop
        orchestrator.config = {"strategies": {"strategy_B": {}}}

        # Run Weekly
        orchestrator.run("weekly")

        # Verify RankHistory
        history = list(RankHistory.select().where(RankHistory.code == "7777"))
        assert len(history) == 1
        assert history[0].rank == 1
        assert history[0].strategy_name == "strategy_B"

    def test_orchestrator_balanced_refresh(self):
        """Verify Balanced Strategy Target Selection and Status Refresh."""

        # Setup Data
        with db_proxy.atomic():
            Stock.create(code="1111", name="BalCorp1", sector="Tech", market="Prime")
            Stock.create(code="2222", name="BalCorp2", sector="Tech", market="Prime")
            md1 = MarketData.create(code="1111", price=1000, entry_date="2025-01-01")
            md2 = MarketData.create(code="2222", price=2000, entry_date="2025-01-01")

            # 1111 is rank 1 in strategy_X, analyzed long ago
            AnalysisResult.create(
                market_data=md1,
                strategy_name="strategy_X",
                quant_score=100,
                audit_version=9,
                analyzed_at="2020-01-01 12:00:00",
            )
            # 2222 is rank 2 in strategy_X, analyzed just now (should not refresh)
            AnalysisResult.create(
                market_data=md2,
                strategy_name="strategy_X",
                quant_score=50,
                audit_version=9,
                analyzed_at=get_current_time(),
            )

        orchestrator = Orchestrator(debug_mode=True)
        orchestrator.config = {"strategies": {"strategy_X": {}}}

        # Test Get Balanced Targets
        targets = orchestrator._get_balanced_targets(top_n_per_strategy=1)
        # Should only get 1111
        assert len(targets) == 1
        assert "1111" in targets
        assert "2222" not in targets

        # Test Refresh Status
        orchestrator._refresh_analysis_status(targets)

        # Verify Audit Version Reset
        ar = (
            AnalysisResult.select()
            .join(MarketData)
            .where(MarketData.code == "1111")
            .first()
        )
        assert ar.audit_version == 0

        ar2 = (
            AnalysisResult.select()
            .join(MarketData)
            .where(MarketData.code == "2222")
            .first()
        )
        assert ar2.audit_version == 9  # Should not change
