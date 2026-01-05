from unittest.mock import mock_open, patch

import pytest
import yaml

from src.config_loader import ConfigLoader, load_config


@pytest.fixture
def mock_config_data(tmp_path):
    return {
        "current_strategy": "value_strict",
        "config_defaults": {
            "paths": {"db_file": str(tmp_path / "stock.db"), "output_dir": str(tmp_path / "output"), "output_file": str(tmp_path / "output/result.csv")},
            "logging": {"level": "INFO", "file": "stock_analyzer.log"},
            "api": {"wait_time": 1.0, "max_retries": 3, "timeout": 30},
            "scoring": {"weights": {"value": 0.3, "growth": 0.3, "quality": 0.2, "trend": 0.2}, "thresholds": {"per_max": 20.0, "pbr_max": 2.0, "roe_min": 8.0, "equity_ratio_min": 30.0}},
            "strategies": {"value_strict": {"per_max": 15.0, "pbr_max": 1.5}, "growth_quality": {"roe_min": 10.0, "profit_growth_min": 10.0}},
            "ai": {"model_name": "gemini-2.0-flash-exp", "temperature": 0.2},
        },
        "data": {
            "jp_stock_list": "data/input/stock_master.csv",
            "output_path": "data/output/result.csv",
        },
        "csv_mapping": {"col_map": {"Code": "code"}, "numeric_cols": ["per"]},
        "ai": {
            "api_keys": ["key1"],
            "model_name": "gemini-pro",
            "analysis_prompt": "prompt",
            "interval_sec": 1,
            "max_concurrency": 1,
        },
        "scoring_v2": {"macro": {"sentiment": "neutral", "interest_rate": "stable"}},
        "scoring": {},
        "strategies": {
            "value_strict": {
                "default_style": "style",
                "persona": "persona",
                "default_horizon": "horizon",
                "base_score": 10,
                "min_requirements": {},
                "points": {},
                "thresholds": {},
            }
        },
        "sector_policies": {},
        "circuit_breaker": {"consecutive_failure_threshold": 5},
    }


def test_load_config_file_not_found():
    # File missing scenario -> ConfigLoader should return valid defaults
    # ファイルが存在しない場合でもデフォルト設定が返されることを確認
    with patch("os.path.exists", return_value=False):
        loader = ConfigLoader("dummy.yaml")
        # Assert that defaults were loaded (from model_construct in validate_config)
        assert loader.config["current_strategy"] == "value_strict"
        assert "data" in loader.config


def test_load_config_valid(mock_config_data):
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=yaml.dump(mock_config_data))),
    ):
        loader = ConfigLoader("config.yaml")
        assert loader.config["ai"]["model_name"] == mock_config_data["ai"]["model_name"]


def test_sync_macro_context(mock_config_data):
    context_content = """
    Some random text...
    [MACRO_SENTIMENT:BULLISH]
    [INTEREST_RATE:RISING]
    [ACTIVE_SECTOR:Energy]
    """

    with (
        patch("os.path.exists", side_effect=[True, True]),
        patch(
            "src.config_loader.ConfigLoader._load_config", return_value=mock_config_data
        ),
        patch("builtins.open", mock_open(read_data=context_content)),
    ):

        loader = ConfigLoader("config.yaml")

        macro = loader.config["scoring_v2"]["macro"]
        assert macro["sentiment"] == "bullish"
        assert macro["interest_rate"] == "rising"
        assert macro["active_sector"] == "Energy"


def test_load_config_helper():
    # Test the standalone function
    with patch("src.config_loader.ConfigLoader") as MockLoader:
        MockLoader.return_value.config = {"key": "val"}
        assert load_config() == {"key": "val"}
