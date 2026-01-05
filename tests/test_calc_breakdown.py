import os
import sys

import pandas as pd
import pytest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calc import Calculator


@pytest.fixture
def calculator():
    config = {
        "current_strategy": "value_strict",
        "strategies": {
            "value_strict": {
                "base_score": 50,
                "points": {
                    "per": 10,
                    "pbr": 10,
                    "roe": 10,  # Value/Quality
                    "sales_growth": 10,  # Growth
                },
                "thresholds": {
                    "per": 15.0,
                    "pbr": 1.5,
                    "roe": 8.0,
                    "sales_growth": 5.0,
                    "rsi_oversold": 30,
                },
                "lower_is_better": ["per", "pbr"],
            }
        },
        "scoring_v2": {
            "styles": {"value_balanced": {"weight_fund": 1.0, "weight_tech": 0.0}},
            "tech_points": {"rsi_oversold": 5},
        },
    }
    return Calculator(config)


def test_calc_sub_score_breakdown(calculator):
    # Create sample data
    data = {
        "code": ["1111", "2222"],
        "per": [10.0, 20.0],  # 1111: OK(10), 2222: NG
        "pbr": [1.0, 2.0],  # 1111: OK(10), 2222: NG
        "roe": [10.0, 5.0],  # 1111: OK(10), 2222: NG
        "sales_growth": [10.0, 0.0],  # 1111: OK(10), 2222: NG
        "rsi_14": [25, 50],  # 1111: Oversold(5), 2222: Normal
        "profit_status": ["surge", "crash"],  # Bonus/Penalty cases
        "turnaround_status": ["normal", "fall_red"],
    }
    df = pd.DataFrame(data)

    # Calculate
    res = calculator.calc_v2_score(df, style="value_balanced")

    # Check Columns
    expected_cols = [
        "score_value",
        "score_growth",
        "score_quality",
        "score_trend",
        "score_penalty",
    ]
    for col in expected_cols:
        assert col in res.columns, f"Missing column: {col}"

    # Check Values for 1111 (Good stock)
    # Value: PER(10) + PBR(10) = 20
    # Quality: ROE(10) = 10
    # Growth: SalesGrowth(10) + ProfitSurge(5) = 15
    # Trend: 50 (Base) + RSI(5) = 55
    # Penalty: 0 (Normal)

    row1 = res.iloc[0]
    assert row1["score_value"] == 20
    assert row1["score_quality"] == 10
    assert row1["score_growth"] == 15
    assert row1["score_trend"] == 55
    assert row1["score_penalty"] == 0

    # Check Values for 2222 (Bad stock)
    # Points: None matched thresholds (assuming base logic)
    # Bonuses:
    # Profit Crash -> Penalty 10
    # Fall Red -> Penalty 10
    # Total Penalty = 20

    row2 = res.iloc[1]
    assert row2["score_value"] == 0
    assert row2["score_growth"] == 0
    assert row2["score_penalty"] == 20


if __name__ == "__main__":
    # Integration style run
    calc = calculator()
    test_calc_sub_score_breakdown(calc)
    print("Test Passed!")
