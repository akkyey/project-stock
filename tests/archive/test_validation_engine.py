"""
Tests for ValidationEngine
"""

import pytest
from src.validation_engine import ValidationEngine


@pytest.fixture
def sample_config():
    """Sample config with sector policies."""
    return {
        "sector_policies": {
            "銀行業": {
                "na_allowed": ["debt_equity_ratio", "operating_cf", "free_cf"],
                "score_exemptions": ["debt_equity_ratio"],
                "ai_prompt_excludes": ["Debt/Equity Ratio"],
            },
            "情報・通信業": {
                "na_allowed": ["free_cf"],
                "score_exemptions": ["free_cf"],
                "ai_prompt_excludes": ["Free CF"],
            },
            "default": {
                "na_allowed": [],
                "score_exemptions": [],
                "ai_prompt_excludes": [],
            },
        }
    }


@pytest.fixture
def engine(sample_config):
    return ValidationEngine(sample_config)


class TestGetPolicy:
    """get_policy メソッドのテスト"""

    def test_defined_sector_returns_policy(self, engine):
        """定義済みセクターは対応するポリシーを返す"""
        policy = engine.get_policy("銀行業")
        assert "debt_equity_ratio" in policy["na_allowed"]

    def test_undefined_sector_returns_default(self, engine):
        """未定義セクターは default を返す"""
        policy = engine.get_policy("未知のセクター")
        assert policy["na_allowed"] == []


class TestValidate:
    """validate メソッドのテスト"""

    def test_bank_sector_allows_debt_equity_missing(self, engine):
        """銀行業では debt_equity_ratio 欠損を許容"""
        task = {
            "prompt": "Debt/Equity Ratio: None%",
            "strategy": "value_strict",
            "score_value": 20,
            "sector": "銀行業",
        }
        is_valid, reason = engine.validate(task)
        assert is_valid is True

    def test_other_sector_rejects_debt_equity_missing(self, engine):
        """他セクターでは debt_equity_ratio 欠損は拒否"""
        task = {
            "prompt": "Debt/Equity Ratio: None%",
            "strategy": "value_strict",
            "score_value": 20,
            "sector": "小売業",
        }
        is_valid, reason = engine.validate(task)
        assert is_valid is False
        assert "Missing Critical" in reason

    def test_info_comm_allows_free_cf_missing(self, engine):
        """情報・通信業では free_cf 欠損を許容"""
        task = {
            "prompt": "Free CF: None",
            "strategy": "growth_quality",
            "score_value": 20,
            "score_growth": 30,
            "sector": "情報・通信業",
        }
        is_valid, reason = engine.validate(task)
        assert is_valid is True

    def test_strategy_score_mismatch_rejected(self, engine):
        """戦略スコア不整合は拒否"""
        task = {
            "prompt": "Some valid prompt",
            "strategy": "value_strict",
            "score_value": 5,  # < 15 threshold
            "sector": "銀行業",
        }
        is_valid, reason = engine.validate(task)
        assert is_valid is False
        assert "Low Value Score" in reason


class TestHelperMethods:
    """ヘルパーメソッドのテスト"""

    def test_get_ai_excludes(self, engine):
        """AI除外リスト取得"""
        excludes = engine.get_ai_excludes("銀行業")
        assert "Debt/Equity Ratio" in excludes

    def test_get_score_exemptions(self, engine):
        """スコア除外リスト取得"""
        exemptions = engine.get_score_exemptions("情報・通信業")
        assert "free_cf" in exemptions
