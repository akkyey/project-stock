# tests/test_validation_pipeline.py
import unittest

from src.domain.models import StockAnalysisData
from src.validation_engine import ValidationEngine


class TestValidationPipeline(unittest.TestCase):
    """DBモデルとバリデーションエンジンの連携、および戦略別ポリシー適用を検証する。"""

    def setUp(self):
        self.config = {
            "metadata_mapping": {
                "metrics": {
                    "PER": "per",
                    "PBR": "pbr",
                    "ROE": "roe",
                    "Equity Ratio": "equity_ratio",
                    "Op CF Margin": "operating_cf",
                },
                "validation": {"critical_missing_threshold": 3},
            },
            "sector_policies": {
                "default": {
                    "na_allowed": [
                        "equity_ratio"
                    ]  # Default permits missing equity ratio
                },
                "_strategy_turnaround_spec": {
                    "na_allowed": [
                        "equity_ratio",
                        "operating_cf",
                        "per",
                        "roe",
                    ]  # Extreme flexibility
                },
                "_strategy_value_strict": {"na_allowed": []},  # Strict
            },
        }
        self.validator = ValidationEngine(self.config)

    def test_db_model_to_validator_mapping(self):
        """DBモデル (MarketData) の辞書が Pydantic (StockAnalysisData) で正しく解釈されるか"""
        # MarketData には 'price' カラムがあるが、StockAnalysisData は 'current_price' を期待する
        db_record = {
            "code": "7777",
            "price": 1500.0,  # <-- マッピングが必要な項目
            "market_cap": 10000.0,
            "per": 12.0,
            "pbr": 1.2,
            "roe": 10.0,
            "operating_cf": 500.0,
            "operating_margin": 10.0,  # <-- 追加
            "equity_ratio": 45.0,
            "sector": "電機",
        }

        # 1. 変換テスト
        stock = StockAnalysisData(**db_record)
        self.assertEqual(
            stock.current_price, 1500.0, "price が current_price にマッピングされること"
        )

        # 2. バリデーションテスト
        is_valid, issues = self.validator.validate_stock_data(db_record)
        self.assertTrue(is_valid, f"正常データが受容されること: {issues}")

    def test_strategy_policy_switching(self):
        """戦略によって同一の欠損データが正しく判定されるか (Matrix Test)"""
        # ROE が欠損しているデータ
        missing_data = {
            "code": "8888",
            "price": 1000.0,
            "roe": None,  # <-- 欠損
            "per": 10.0,
            "pbr": 1.0,
            "operating_margin": 5.0,  # <-- 追加
            "operating_cf": 100.0,  # <-- 追加
            "equity_ratio": 30.0,
            "sector": "Unknown",
        }

        # Case 1: value_strict (厳格) -> ROE欠損は Tier 1 違反なので Skip
        is_valid_strict, issues_strict = self.validator.validate_stock_data(
            missing_data, strategy="value_strict"
        )
        self.assertFalse(is_valid_strict, "value_strict では ROE 欠損を拒否すべき")

        # Case 2: turnaround_spec (緩和) -> ROE欠損も na_allowed なので合格
        is_valid_ta, issues_ta = self.validator.validate_stock_data(
            missing_data, strategy="turnaround_spec"
        )
        self.assertTrue(
            is_valid_ta, f"turnaround_spec では ROE 欠損を許容すべき: {issues_ta}"
        )

    def test_attribute_error_prevention(self):
        """不具合 No.1 (strategy_name 参照エラー) の再発防止確認"""
        from unittest.mock import MagicMock

        from src.ai.agent import AIAgent

        # AIAgent を初期化
        agent = AIAgent(model_name="gemini-flash-latest", debug_mode=True)
        agent.set_config(self.config)
        agent.validator = self.validator

        # モックのプロンプトビルダーなどは必要
        agent.prompt_builder = MagicMock()
        agent.prompt_builder.create_prompt_from_model.return_value = "dummy prompt"

        # モデル層
        row = {
            "code": "1234",
            "price": 100.0,
            "operating_margin": 10.0,
            "operating_cf": 100.0,
            "per": 10.0,
            "pbr": 1.0,
            "roe": 10.0,
            "sector": "Test",
        }

        # analyze メソッドを実行 (API呼び出し部分はモック)
        # 内部で呼ばれるメソッドは _generate_content_with_retry
        mock_res_text = '{"ai_sentiment": "Neutral", "ai_reason": "【結論】Neutral｜【強み】なし｜【懸念】なし", "ai_detail": "①...⑦"}'
        with unittest.mock.patch.object(
            agent,
            "_generate_content_with_retry",
            return_value=MagicMock(text=mock_res_text),
        ):
            try:
                # この呼び出しで AttributeError が起きないことを検証
                agent.analyze(row, strategy_name="turnaround_spec")
            except AttributeError as e:
                self.fail(f"AIAgent.analyze 内部で属性エラーが発生しました: {e}")


if __name__ == "__main__":
    unittest.main()
