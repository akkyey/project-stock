
import pandas as pd
import pytest
from src.calc.strategies.generic import GenericStrategy

class TestTurnaroundLogic:
    """
    Private Test for Turnaround Strategy Logic.
    This ensures the 'GenericStrategy' correctly implements the specific 
    bonuses/penalties defined in config.yaml for the 'tunaround_spec' strategy.
    """

    @pytest.fixture
    def strategy(self):
        # Load real config or mock that mimics real config
        # Here we mock the specific parts relevant to Turnaround to isolate logic testing
        # independently of file I/O, but reflects the structure in config.yaml.
        
        config = {
            "strategies": {
                "turnaround_spec": {
                   "base_score": 50,
                   "metrics_metadata": {
                       "roe": {"missing_penalty": 10.0, "category": "quality"}
                   },
                   "status_bonuses": {
                       "turnaround_status": {
                           "turnaround_black": 20, 
                           "fall_red": -15
                        },
                       "trend_up": {"0": -10} # Penalty for no trend
                   },
                   "points": {}, # Minimal for testing specific logic
                   "thresholds": {}
                }
            },
            "styles": {
                "test_style": {"weight_fund": 1.0, "weight_tech": 0.0}
            },
            "tech_points": {},
            "macro": {},
            "penalty_rules": {},
            "sector_policies": {},
            "scoring": {"lower_is_better": []},
        }
        
        # Inject default style to test_style
        config["strategies"]["turnaround_spec"]["default_style"] = "test_style"
        
        strat = GenericStrategy(config, "turnaround_spec")
        strat.v2_config = config # Ensure flattened access works if needed
        return strat

    def test_turnaround_black_bonus(self, strategy):
        """Verify +20 points for 'turnaround_black' status"""
        df = pd.DataFrame([{
            "code": "1111",
            "turnaround_status": "turnaround_black",
            "roe": 5.0 # Present
        }])
        
        # We need mock points map to avoid empty loop issues? 
        # GenericStrategy loops over points_map. 
        # But status_bonuses is a separate loop (Step 7).
        # So it should work even if points_map is empty.
        
        res = strategy.calculate_score(df)
        
        # Base 50 + 20 = 70.
        assert res.loc[0, "quant_score"] == 70.0
        assert res.loc[0, "score_growth"] == 20.0
        
    def test_missing_roe_penalty(self, strategy):
        """Verify -10 points penalty if ROE is missing"""
        # Note: missing_penalty logic is inside the points_map loop.
        # So we MUST have 'roe' in points_map to trigger it.
        strategy.config["strategies"]["turnaround_spec"]["points"] = {"roe": 5}
        
        df = pd.DataFrame([{
            "code": "2222",
            "turnaround_status": "normal",
            "roe": None # Missing
        }])
        
        res = strategy.calculate_score(df)
        
        # Base 50 - 10 (penalty) = 40.
        # Also, points loop for ROE is skipped for points addition because it's missing.
        assert res.loc[0, "quant_score"] == 40.0
        assert res.loc[0, "score_penalty"] == 10.0
        assert res.loc[0, "score_quality"] == -10.0

    def test_trend_penalty(self, strategy):
        """Verify -10 points penalty if trend_up is 0"""
        df = pd.DataFrame([{
            "code": "3333",
            "trend_up": "0" # String '0' match
        }])
        
        res = strategy.calculate_score(df)
        
        # Base 50 - 10 = 40.
        assert res.loc[0, "quant_score"] == 40.0
        assert res.loc[0, "score_penalty"] == 10.0
