import pandas as pd
import pytest
from src.calc.engine import ScoringEngine
from src.calc.strategies.base import BaseStrategy


@pytest.fixture
def scoring_config():
    return {
        "filter": {"min_quant_score": 50},
        "hard_filters": {
            "per": 0,  # PER 0以上 (グローバル)
            "per_max": 30,  # PER 30以下 (グローバル)
        },
        "strategies": {
            "strict_value": {
                "min_requirements": {
                    "pbr_max": 1.0,  # PBR 1.0以下 (戦略固有)
                    "roe": 10.0,  # ROE 10%以上 (戦略固有)
                }
            }
        },
    }


@pytest.fixture
def engine(scoring_config):
    return ScoringEngine(scoring_config)


def test_filter_and_rank_global_filters(engine):
    """グローバルフィルターの適用テスト"""
    df = pd.DataFrame(
        [
            {"code": "1001", "quant_score": 60, "per": 10.0},  # Pass
            {"code": "1002", "quant_score": 60, "per": 35.0},  # Fail (per_max)
            {"code": "1003", "quant_score": 30, "per": 10.0},  # Fail (min_score)
            {"code": "1004", "quant_score": 60, "per": -1.0},  # Fail (per >= 0)
        ]
    )

    # 未定義の戦略 'generic' を使うことでグローバルフィルターが適用される
    result = engine.filter_and_rank(df, "generic")

    assert len(result) == 1
    assert result.iloc[0]["code"] == "1001"


def test_filter_and_rank_strategy_specific_filters(engine):
    """戦略固有フィルターの適用テスト (PBR上限など)"""
    df = pd.DataFrame(
        [
            {"code": "2001", "quant_score": 70, "pbr": 0.8, "roe": 12.0},  # Pass
            {
                "code": "2002",
                "quant_score": 70,
                "pbr": 1.2,
                "roe": 12.0,
            },  # Fail (pbr_max)
            {
                "code": "2003",
                "quant_score": 70,
                "pbr": 0.8,
                "roe": 5.0,
            },  # Fail (roe < 10)
        ]
    )

    result = engine.filter_and_rank(df, "strict_value")

    assert len(result) == 1
    assert result.iloc[0]["code"] == "2001"


def test_strategy_fallback_and_error_handling(engine):
    """未知の戦略へのフォールバックとエラーハンドリング"""
    df = pd.DataFrame([{"code": "3001"}], index=[0])

    # 1. 未知の戦略 -> GenericStrategy で計算継続される
    # (GenericStrategy は 0.0 を返すはず)
    result = engine.calculate_score(df, "unknown_strat")
    assert result.iloc[0]["strategy_name"] == "unknown_strat"
    assert "quant_score" in result.columns

    # 2. 計算中に例外が発生した場合 -> デフォルトスコア返却
    class ErrorStrategy(BaseStrategy):
        def calculate_score(self, data):
            raise ValueError("Calculation Error")

    engine.register_strategy("error_strat", ErrorStrategy)
    result = engine.calculate_score(df, "error_strat")

    assert result.iloc[0]["quant_score"] == 0.0
    assert result.iloc[0]["score_trend"] == 50.0


def test_dynamic_strategy_registration(engine):
    """戦略の動的登録テスト"""

    class CustomStrategy(BaseStrategy):
        def calculate_score(self, data):
            data = data.copy()
            data["quant_score"] = 99.0
            return data

    engine.register_strategy("custom", CustomStrategy)
    df = pd.DataFrame([{"code": "4001"}])

    result = engine.calculate_score(df, "custom")
    assert result.iloc[0]["quant_score"] == 99.0
    assert "custom" in engine.list_strategies()


def test_filter_and_rank_sorting(engine):
    """ランキング（ソート）順のテスト"""
    df = pd.DataFrame(
        [
            {"code": "5001", "quant_score": 60},
            {"code": "5002", "quant_score": 80},
            {"code": "5003", "quant_score": 80},
        ]
    )

    # quant_score 降順、code 昇順
    result = engine.filter_and_rank(df, "generic")

    assert result.iloc[0]["code"] == "5002"  # 80, small code
    assert result.iloc[1]["code"] == "5003"  # 80, large code
    assert result.iloc[2]["code"] == "5001"  # 60
