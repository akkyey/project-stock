from typing import Any, Dict

import pytest
from src.validation_engine import ValidationEngine

# Mock Config
config: Dict[str, Any] = {
    "sector_policies": {"default": {"na_allowed": []}},
    "metadata_mapping": {},
}


@pytest.fixture
def engine():
    return ValidationEngine(config)


def test_tier1_critical_missing(engine):
    """Tier 1 (Critical) 欠損は False を返す"""
    # 1. Basic Info Missing (Code is required by Pydantic, check current_price instead)
    data = {"code": "1234", "name": "Test", "current_price": None}
    valid, issues = engine.validate_stock_data(data)
    assert valid is False
    assert "Missing Critical: current_price" in issues[0]

    # 2. Critical Financials Missing (e.g. Operating CF)
    data = {
        "code": "1234",
        "name": "Test",
        "current_price": 100,
        "equity_ratio": 50,
        "operating_cf": None,  # MISSING
        "operating_margin": 0.1,
        "per": 10,
        "pbr": 1,
        "roe": 5,
        "sales_growth": 0,  # Provide Tier 2 defaults to avoid Tier2 warnings mixing in (optional)
        "dividend_yield": 0,
    }
    valid, issues = engine.validate_stock_data(data)
    assert valid is False
    assert "Missing Critical: operating_cf" in issues[0]


def test_tier2_reference_missing(engine):
    """Tier 2 (Reference) 欠損は True を返し、Warning を出す"""
    data = {
        "code": "1234",
        "name": "Test",
        "current_price": 100,
        "equity_ratio": 50,
        "operating_cf": 100,
        "operating_margin": 0.1,
        "per": 10,
        "pbr": 1,
        "roe": 5,
        "roa": 2,
        # Reference Missing
        "sales_growth": None,
        "dividend_yield": None,
    }
    valid, issues = engine.validate_stock_data(data)
    assert valid is True
    assert any("Missing Reference: sales_growth" in i for i in issues)
    assert any("Missing Reference: dividend_yield" in i for i in issues)


def test_anomalies_warning(engine):
    """Red Flag (異常値) は True を返し、Warning を出す"""
    data = {
        "code": "1234",
        "name": "Test",
        "current_price": 100,
        "equity_ratio": 50,
        "operating_cf": 100,
        "operating_margin": 0.1,
        "per": 10,
        "pbr": 1,
        "roe": 5,
        "sales_growth": -10.0,  # Declining Sales -> Red Flag
        "dividend_yield": 2,
    }
    valid, issues = engine.validate_stock_data(data)
    assert valid is True
    assert any("Red Flag: declining_sales" in i for i in issues)


if __name__ == "__main__":
    # If run directly, minimal manual check
    eng = ValidationEngine(config)
    print("Running Manual Checks...")
    test_tier1_critical_missing(eng)
    test_tier2_reference_missing(eng)
    test_anomalies_warning(eng)
    print("✅ All Manual Checks Passed")
