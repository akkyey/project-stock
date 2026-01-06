# tests/test_strategy_analyst_rules_integration.py
"""
[v2.0] 戦略とアナリストルールの整合性を検証するテスト。

検証内容:
- Red Flag 検知時の挙動
- 例外救済ルールの発動条件
- 異常値による分析スキップ
- value_strict 戦略の優先順位の数学的整合性
"""


import pytest
from src.domain.models import SkipReason, StockAnalysisData


@pytest.mark.integration
class TestValidationFlagDetection:
    """ValidationFlag の自動検出テスト"""

    def test_tier1_missing_detection(self):
        """Tier1 必須項目の欠損が正しく検出されること"""
        stock = StockAnalysisData(
            code="1001",
            name="Test Corp",
            current_price=None,  # 欠損
            per=None,  # 欠損
            pbr=0.8,
            roe=12.0,
            operating_cf=100000,
            operating_margin=5.0,
        )
        assert "current_price" in stock.validation_flags.tier1_missing
        assert "per" in stock.validation_flags.tier1_missing
        assert len(stock.validation_flags.tier1_missing) == 2

    def test_tier2_missing_detection(self):
        """Tier2 参考項目の欠損が正しく検出されること"""
        stock = StockAnalysisData(
            code="1002",
            name="Test Corp 2",
            current_price=1000.0,
            per=10.0,
            pbr=0.9,
            roe=15.0,
            operating_cf=50000,
            operating_margin=8.0,
            equity_ratio=None,  # Tier2 欠損
            sales_growth=None,  # Tier2 欠損
        )
        assert "equity_ratio" in stock.validation_flags.tier2_missing
        assert "sales_growth" in stock.validation_flags.tier2_missing


@pytest.mark.integration
class TestRedFlagDetection:
    """Red Flag 検知テスト"""

    def test_negative_ocf_margin_red_flag(self):
        """営業CFマージンがマイナスの場合、Red Flagが立つこと"""
        stock = StockAnalysisData(
            code="2001",
            name="Negative OCF Corp",
            current_price=500.0,
            per=15.0,
            pbr=1.2,
            roe=8.0,
            operating_cf=100000,
            operating_margin=5.0,
            ocf_margin=-5.0,  # マイナス -> Red Flag
        )
        assert "negative_ocf_margin" in stock.validation_flags.red_flags

    def test_declining_sales_red_flag(self):
        """売上成長率がマイナスの場合、Red Flagが立つこと"""
        stock = StockAnalysisData(
            code="2002",
            name="Declining Sales Corp",
            current_price=800.0,
            per=12.0,
            pbr=0.7,
            roe=10.0,
            operating_cf=200000,
            operating_margin=6.0,
            sales_growth=-15.0,  # マイナス -> Red Flag
        )
        assert "declining_sales" in stock.validation_flags.red_flags

    def test_extreme_overvaluation_red_flag(self):
        """PER30超 かつ PBR5超 の場合、Red Flagが立つこと"""
        stock = StockAnalysisData(
            code="2003",
            name="Bubble Corp",
            current_price=10000.0,
            per=50.0,  # > 30
            pbr=8.0,  # > 5
            roe=25.0,
            operating_cf=500000,
            operating_margin=15.0,
        )
        assert "extreme_overvaluation" in stock.validation_flags.red_flags


@pytest.mark.integration
class TestRescueRuleEligibility:
    """例外救済ルールのテスト"""

    def test_rescue_eligible_deep_value(self):
        """PBR < 1.0 かつ 配当利回り > 4.0% で救済該当"""
        stock = StockAnalysisData(
            code="3001",
            name="Deep Value Corp",
            current_price=500.0,
            per=8.0,
            pbr=0.6,  # < 1.0
            roe=5.0,
            operating_cf=100000,
            operating_margin=3.0,
            dividend_yield=5.5,  # > 4.0%
        )
        assert stock.validation_flags.rescue_eligible is True

    def test_rescue_not_eligible_with_red_flag(self):
        """Red Flag がある場合は救済非該当"""
        stock = StockAnalysisData(
            code="3002",
            name="Risky Value Corp",
            current_price=400.0,
            per=7.0,
            pbr=0.5,  # < 1.0
            roe=4.0,
            operating_cf=80000,
            operating_margin=2.0,
            dividend_yield=6.0,  # > 4.0%
            sales_growth=-20.0,  # Red Flag!
        )
        assert "declining_sales" in stock.validation_flags.red_flags
        assert stock.validation_flags.rescue_eligible is False

    def test_rescue_not_eligible_conditions_not_met(self):
        """条件を満たさない場合は救済非該当"""
        stock = StockAnalysisData(
            code="3003",
            name="Normal Corp",
            current_price=1000.0,
            per=15.0,
            pbr=1.5,  # >= 1.0 (条件不満)
            roe=12.0,
            operating_cf=150000,
            operating_margin=8.0,
            dividend_yield=2.0,  # < 4.0% (条件不満)
        )
        assert stock.validation_flags.rescue_eligible is False


@pytest.mark.integration
class TestAbnormalValueSkip:
    """異常値による分析スキップのテスト"""

    def test_insolvent_skip(self):
        """債務超過 (自己資本比率 < 0%) で分析スキップ"""
        stock = StockAnalysisData(
            code="4001",
            name="Insolvent Corp",
            current_price=100.0,
            per=5.0,
            pbr=0.3,
            roe=-50.0,
            operating_cf=10000,
            operating_margin=1.0,
            equity_ratio=-15.0,  # 債務超過
        )
        assert stock.should_skip_analysis is True
        assert SkipReason.INSOLVENT in stock.validation_flags.skip_reasons

    def test_extreme_per_skip(self):
        """PER > 500 倍で分析スキップ"""
        stock = StockAnalysisData(
            code="4002",
            name="Extreme PER Corp",
            current_price=50000.0,
            per=600.0,  # > 500
            pbr=2.0,
            roe=0.1,
            operating_cf=5000,
            operating_margin=0.5,
        )
        assert stock.should_skip_analysis is True
        assert SkipReason.EXTREME_VALUATION in stock.validation_flags.skip_reasons

    def test_extreme_pbr_skip(self):
        """PBR > 20 倍で分析スキップ"""
        stock = StockAnalysisData(
            code="4003",
            name="Extreme PBR Corp",
            current_price=100000.0,
            per=80.0,
            pbr=25.0,  # > 20
            roe=50.0,
            operating_cf=1000000,
            operating_margin=20.0,
        )
        assert stock.should_skip_analysis is True
        assert SkipReason.EXTREME_VALUATION in stock.validation_flags.skip_reasons

    def test_unsustainable_payout_skip(self):
        """配当性向 > 300% で分析スキップ"""
        stock = StockAnalysisData(
            code="4004",
            name="Taco Payout Corp",
            current_price=800.0,
            per=10.0,
            pbr=0.8,
            roe=3.0,
            operating_cf=50000,
            operating_margin=2.0,
            payout_ratio=350.0,  # > 300%
        )
        assert stock.should_skip_analysis is True
        assert SkipReason.PAYOUT_UNSUSTAINABLE in stock.validation_flags.skip_reasons


@pytest.mark.integration
class TestDeficiencyType:
    """欠損タイプ分類のテスト"""

    def test_complete_data(self):
        """全データ完備の場合"""
        stock = StockAnalysisData(
            code="5001",
            current_price=1000.0,
            per=12.0,
            pbr=1.0,
            roe=15.0,
            operating_cf=200000,
            operating_margin=10.0,
            equity_ratio=50.0,
            sales_growth=10.0,
            dividend_yield=3.0,
        )
        assert stock.deficiency_type == "Complete (データ完備)"

    def test_tier1_deficiency(self):
        """Tier1 欠損がある場合"""
        stock = StockAnalysisData(
            code="5002",
            current_price=None,  # Tier1 欠損
            per=12.0,
            pbr=1.0,
            roe=15.0,
            operating_cf=200000,
            operating_margin=10.0,
        )
        assert stock.deficiency_type == "Critical (Tier1 欠損あり)"

    def test_tier2_only_deficiency(self):
        """Tier2 のみ欠損がある場合"""
        stock = StockAnalysisData(
            code="5003",
            current_price=1000.0,
            per=12.0,
            pbr=1.0,
            roe=15.0,
            operating_cf=200000,
            operating_margin=10.0,
            equity_ratio=None,  # Tier2 欠損
        )
        assert stock.deficiency_type == "Partial (Tier2 欠損あり / 参考データ不足)"


@pytest.mark.integration
class TestPromptBuilderIntegration:
    """PromptBuilder との連携テスト"""

    def test_validation_metadata_section(self):
        """検証メタデータセクションが正しく生成されること"""
        from src.ai.prompt_builder import PromptBuilder

        stock = StockAnalysisData(
            code="6001",
            name="Meta Test Corp",
            current_price=1000.0,
            per=None,  # Tier1 欠損
            pbr=0.8,
            roe=10.0,
            operating_cf=100000,
            operating_margin=5.0,
            sales_growth=-5.0,  # Red Flag
        )

        builder = PromptBuilder({})
        metadata_section = builder.get_validation_metadata_section(stock)

        assert "Tier 1 欠損: 1件" in metadata_section
        assert "per" in metadata_section
        assert "Red Flags: 1件" in metadata_section
        assert "declining_sales" in metadata_section
