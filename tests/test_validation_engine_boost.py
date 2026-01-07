import pytest
from unittest.mock import MagicMock
from src.validation_engine import ValidationEngine
from src.domain.models import StockAnalysisData

class TestValidationEngineBoost:
    @pytest.fixture
    def engine(self):
        config = {
            "sector_policies": {
                "default": {"na_allowed": [], "score_exemptions": [], "ai_prompt_excludes": []},
                "IT": {"na_allowed": ["pbr"], "score_exemptions": ["value"], "ai_prompt_excludes": ["dividend"]},
                "_strategy_growth_quality": {"na_allowed": ["dividend_yield"]}
            },
            "metadata_mapping": {
                "metrics": {"PBR": "pbr"},
                "validation": {}
            }
        }
        return ValidationEngine(config)

    def test_get_policy_defaults(self, engine):
        """Test policy retrieval for defined and undefined sectors"""
        # Defined
        policy = engine.get_policy("IT")
        assert "pbr" in policy["na_allowed"]
        
        # Undefined (Default)
        policy_def = engine.get_policy("Unknown")
        assert policy_def == engine.sector_policies["default"]

    def test_get_ai_excludes(self, engine):
        """Test AI exclude list retrieval"""
        excludes = engine.get_ai_excludes("IT")
        assert "dividend" in excludes
        
        excludes_def = engine.get_ai_excludes("Unknown")
        assert excludes_def == []

    def test_get_score_exemptions(self, engine):
        """Test score exemption retrieval"""
        exempts = engine.get_score_exemptions("IT")
        assert "value" in exempts

    def test_check_sector_coverage_warns(self, engine):
        """Test logging warning for undefined sectors"""
        # We mock the logger
        engine.logger = MagicMock()
        engine.check_sector_coverage(["IT", "UnknownSector"])
        
        engine.logger.warning.assert_called()
        args = engine.logger.warning.call_args[0][0]
        assert "UnknownSector" in args

    # ... (skipping pydantic error test which is fine) ...

    def test_score_consistency_checks(self, engine):
        """Test logic for Score Consistency in validate_stock_data"""
        # Common data
        base_data = {
            "code": "1111", "name": "Test", 
            "current_price": 100, "price": 100,
            "market_cap": 1000,
            "sales_growth": 10, "operating_margin": 10,
            "roe": 10, "equity_ratio": 50
        }
        
        # Mock stock object to bypass Pydantic validation on incomplete dict
        mock_stock = MagicMock()
        mock_stock.validation_flags.tier1_missing = []
        mock_stock.validation_flags.tier2_missing = []
        mock_stock.validation_flags.red_flags = []
        mock_stock.validation_flags.skip_reasons = []
        mock_stock.should_skip_analysis = False
        mock_stock.sector = "IT" # Default
        
        # Case 1: Growth Quality Mismatch (Low Growth, High Trend)
        data_gq = base_data.copy()
        data_gq["score_growth"] = 5  # Low
        data_gq["score_trend"] = 80 # High
        is_valid, issues = engine.validate_stock_data(data_gq, stock=mock_stock, strategy="growth_quality")
        assert is_valid is False
        assert any("Score Mismatch" in i for i in issues)

        # Case 2: Value Strict Mismatch (Low Value)
        data_val = base_data.copy()
        data_val["score_value"] = 10 # Low
        is_valid, issues = engine.validate_stock_data(data_val, stock=mock_stock, strategy="value_strict")
        assert is_valid is False
        assert any("Score Mismatch" in i for i in issues)

        # Case 3: Hybrid Mismatch (Low Value AND Low Growth)
        data_hybrid = base_data.copy()
        data_hybrid["score_value"] = 5
        data_hybrid["score_growth"] = 5
        is_valid, issues = engine.validate_stock_data(data_hybrid, stock=mock_stock, strategy="value_growth_hybrid")
        assert is_valid is False
        assert any("Score Mismatch" in i for i in issues)

    def test_init_defaults(self):
        """Test fallback when config is empty"""
        engine = ValidationEngine({})
        assert engine.metrics_map is not None
        assert "ROE" in engine.metrics_map
