import numpy as np
import pytest

from src.validation_engine import ValidationEngine


@pytest.fixture
def advanced_config():
    return {
        "sector_policies": {
            "銀行業": {
                "na_allowed": ["debt_equity_ratio", "operating_cf", "free_cf"],
                "score_exemptions": ["debt_equity_ratio"],
            },
            "default": {"na_allowed": [], "score_exemptions": []},
        }
    }


@pytest.fixture
def engine(advanced_config):
    return ValidationEngine(advanced_config)


def test_validate_stock_data_sector_specifics(engine):
    """セクター別のバリデーション特例テスト"""
    # 銀行業: debt_equity_ratio が欠損していても Valid
    bank_data = {
        "code": "8306",
        "name": "MUFG",
        "sector": "銀行業",
        "current_price": 1500,
        "debt_equity_ratio": None,
        "roe": 8.5,
        "per": 10.0,
        "pbr": 1.0,
        "sales_growth": 5.0,
        "profit_growth": 10.0,
        "equity_ratio": 5.0,
        "free_cf": None,
        "operating_cf": 100,
        "operating_margin": 10.0,
        "sales": 1000,
    }
    is_valid, issues = engine.validate_stock_data(bank_data)
    assert is_valid is True
    assert not any("Missing Critical" in i for i in issues)

    # 小売業: debt_equity_ratio が欠損していると Invalid
    retail_data = {
        "code": "9983",
        "name": "FastRetailing",
        "sector": "小売業",
        "current_price": 35000,
        "debt_equity_ratio": None,
        "roe": 15.0,
        "per": 20.0,
        "pbr": 1.0,
        "sales_growth": 10.0,
        "profit_growth": 15.0,
        "equity_ratio": 50.0,
        "operating_cf": 100,
        "operating_margin": 10.0,
        "sales": 1000,
    }
    is_valid, issues = engine.validate_stock_data(retail_data)
    assert is_valid is True
    assert any("Missing Reference: Debt/Equity Ratio" in i for i in issues)


def test_validate_stock_data_anomalies(engine):
    """異常値検知の境界条件テスト"""
    # 1. 売上成長率 500% (境界値 - 正常)
    data_500 = {
        "code": "1111",
        "name": "GrowthA",
        "current_price": 100,
        "sales_growth": 500.0,
        "per": 15.0,
        "pbr": 1.0,
        "roe": 10.0,
        "operating_cf": 100,
        "operating_margin": 10.0,
        "sales": 1000,
    }
    _, issues = engine.validate_stock_data(data_500)
    assert not any("Anomaly: High Sales Growth" in i for i in issues)


def test_validate_stock_data_robustness(engine):
    """不正な値や特殊な型への堅牢性テスト"""
    # NaN (float) の扱い (Pandas等から来るケース)
    nan_data = {
        "code": "2222",
        "name": "NaNCorp",
        "current_price": np.nan,  # 必須項目がNaN
        "per": 15.0,
        "pbr": 1.0,
    }
    is_valid, issues = engine.validate_stock_data(nan_data)
    # Price is Critical -> False
    assert is_valid is False
    assert any("Missing Essential: Stock Code/Price" in i for i in issues)

    # ゼロ値の扱い (ROE 0% は Valid であるべき)
    zero_data = {
        "code": "3333",
        "name": "ZeroCorp",
        "current_price": 100,
        "roe": 0.0,
        "per": 10.0,
        "pbr": 1.0,
        "debt_equity_ratio": 0.0,
        "sales_growth": 0.0,
        "profit_growth": 0.0,
        "equity_ratio": 0.0,
        "free_cf": 0.0,
        "operating_cf": 0.0,
        "operating_margin": 0.0,
        "sales": 1000,
    }
    is_valid, issues = engine.validate_stock_data(zero_data)
    assert is_valid is True
    assert not any("Missing ROE" in i for i in issues)


def test_validate_stock_data_undefined_sector(engine):
    """未定義セクター指定時のフォールバックテスト"""
    # 未定義セクター -> defaultポリシーが適用される
    weird_sector_data = {
        "code": "4444",
        "name": "Unknown",
        "sector": "宇宙開発業",
        "current_price": 1000,
        "debt_equity_ratio": None,
        "per": 15.0,
        "pbr": 1.0,
        "roe": 10.0,
        "sales_growth": 5.0,
        "profit_growth": 5.0,
        "equity_ratio": 50.0,
        "operating_cf": 100,
        "operating_margin": 10.0,
        "sales": 1000,
    }
    # default では na_allowed が空だが、debt_equity_ratio はチェック対象外(Tier 2以下かつリストにない)、Dividend Yield はReference
    is_valid, issues = engine.validate_stock_data(weird_sector_data)
    assert is_valid is True
    assert any("Missing Reference: Dividend Yield" in i for i in issues)
