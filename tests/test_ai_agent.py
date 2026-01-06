# tests/test_ai_agent.py

import json
import os
import unittest
from unittest.mock import MagicMock, patch

from src.ai.agent import AIAgent


class TestAIAgent(unittest.TestCase):

    def setUp(self):
        """各テストメソッド実行前に呼び出されるセットアップメソッド"""
        # デバッグモードでAIエージェントを初期化（APIキー不要、モックレスポンス前提）
        self.ai_agent_debug = AIAgent(model_name="gemini-2.0-flash", debug_mode=True)

        # プロダクションモード用のAIエージェントインスタンス (APIキーがない場合を想定)
        # __init__ 内での genai.configure 呼び出しは @patch でモックされる
        self.ai_agent_prod = AIAgent(model_name="gemini-2.0-flash", debug_mode=False)

    # `genai.Client` は `__init__` 内で呼ばれるため、これをモックする
    @patch("src.ai.key_manager.genai.Client")
    @patch("src.ai.agent.AIAgent._generate_content_with_retry")
    def test_analyze_mocked_api_success(self, mock_generate_retry, mock_genai_client):
        """APIが成功した場合の analyze メソッドの動作をテスト (モック使用)"""
        # --- Mock Setup ---
        # [Phase 2-3] 新しいDual Output形式のモックレスポンス
        mock_response_text = json.dumps(
            {
                "ai_sentiment": "Bullish",
                "ai_summary": "【結論】Bullish。安定した成長を期待。｜【強み】高いROE、堅実なCF。｜【懸念】市場環境の変化に注意。",
                "ai_detail": "①現状分析。②強み。③弱み。④持続可能性。⑤異常値。⑥テクニカル。⑦結論。",
                "ai_risk": "Low",
                "ai_horizon": "Long-term",
            }
        )
        # _generate_content_with_retry の戻り値は response オブジェクト
        mock_response_obj = MagicMock()
        mock_response_obj.text = mock_response_text
        mock_generate_retry.return_value = mock_response_obj

        # Validation mock (新形式ではvalidationを通過させる)
        self.ai_agent_prod._validate_response = MagicMock(return_value=(True, None))

        # genai.Client の戻り値もモック化
        mock_genai_client.return_value = MagicMock()

        # --- Test Data ---
        row_data = {
            "code": "1234",
            "name": "Test Stock",
            "sector": "Technology",
            "current_price": 1000,
            "per": 20,
            "pbr": 2.0,
            "peg_ratio": 1.5,
            "ocf_margin": 15,
            "free_cf": 5000000,
            "debt_equity_ratio": 50,
            "current_ratio": 1.5,
            "cf_status": 1,
            "roe": 10,
            "sales_growth": "10%",
            "profit_growth": "15",
            "operating_margins": "12",
            "dividend_yield": "1.0",
            "payout_ratio": "30",
            "volatility": "20",
            "rsi": 55,
            "macd": "0.5",
            "trend_signal": 1,
        }
        strategy_name = "Growth"

        # --- Execution ---
        result = self.ai_agent_prod.analyze(row_data, strategy_name)

        # --- Assertions ---
        # `_generate_content_with_retry` が正しく呼ばれたことを確認
        mock_generate_retry.assert_called_once()

        # 解析結果の検証 (新形式: ai_summary -> ai_reason にマッピング)
        self.assertEqual(result["ai_sentiment"], "Bullish")
        self.assertIn("【結論】", result["ai_reason"])
        self.assertEqual(result["ai_risk"], "Low")
        self.assertEqual(result["ai_horizon"], "Long-term")

    @patch("src.ai.key_manager.genai.Client")
    @patch("src.ai.agent.AIAgent._generate_content_with_retry")
    def test_analyze_api_error(self, mock_generate_retry, mock_genai_client):
        """APIエラー発生時の analyze メソッドの動作をテスト"""
        # --- Mock Setup ---
        # APIエラーをシミュレート(通常エラー)
        mock_generate_retry.return_value = None  # Emptyを返す場合

        # --- Test Data ---
        row_data = {
            "code": "5678",
            "name": "Error Stock",
            "current_price": 100,
            "per": 10,
            "roe": 5,
        }
        strategy_name = "Value"

        # --- Execution ---
        result = self.ai_agent_prod.analyze(row_data, strategy_name)

        # --- Assertions ---
        # リトライループがあるため複数回呼ばれる可能性
        mock_generate_retry.assert_called()

        self.assertEqual(result["ai_sentiment"], "Neutral")
        self.assertIn("ANALYSIS FAILED", result["ai_reason"])
        self.assertEqual(result["ai_horizon"], "Wait")

    def test_parse_response_success(self):
        """JSONレスポンスのパースが成功するケースのテスト (新形式)"""
        # [Phase 2-3] 新しいDual Output形式
        mock_text = json.dumps(
            {
                "ai_sentiment": "Neutral",
                "ai_summary": "【結論】Neutral。｜【強み】安定性。｜【懸念】成長鈍化。",
                "ai_detail": "①分析。②強み。③弱み。④持続性。⑤異常値。⑥テクニカル。⑦結論。",
                "ai_risk": "Medium",
                "ai_horizon": "Wait",
            }
        )
        result = self.ai_agent_debug._parse_response(mock_text)

        # _parse_response は ai_summary を ai_reason にマッピングする
        self.assertEqual(result["ai_sentiment"], "Neutral")
        self.assertIn("【結論】", result["ai_reason"])
        self.assertEqual(result["ai_risk"], "Medium")
        self.assertEqual(result["ai_horizon"], "Wait")

    def test_parse_response_json_decode_error(self):
        """JSONデコードエラーが発生するケースのテスト"""
        # 無効なJSON文字列
        invalid_json_text = '{"ai_sentiment": "Bearish","ai_reason": "Some reason...'

        result = self.ai_agent_debug._parse_response(invalid_json_text)

        self.assertEqual(result["ai_sentiment"], "Error")
        self.assertEqual(result["ai_reason"], "Failed to parse JSON response.")
        self.assertEqual(result["ai_risk"], "Unknown")
        self.assertEqual(result["ai_horizon"], "Wait")

    def test_create_prompt_with_market_context(self):
        """市場コンテキストを含むプロンプト生成テスト (日本語プロンプト対応)"""
        # --- Mock Setup (market_context.txt の作成) ---
        mock_market_context_content = "Current market is volatile. Rate hikes expected."
        with open("market_context.txt", "w", encoding="utf-8") as f:
            f.write(mock_market_context_content)

        # --- Test Data ---
        row_data = {
            "code": "9999",
            "name": "Context Stock",
            "sector": "Finance",
            "current_price": 500,
            "per": 10,
            "pbr": 1.0,
            "peg_ratio": 1.0,
            "ocf_margin": 20,
            "free_cf": 1000000,
            "debt_equity_ratio": 80,
            "current_ratio": 1.2,
            "cf_status": 1,
            "roe": 9,
            "sales_growth": "5%",
            "profit_growth": "7",
            "operating_margins": "10",
            "dividend_yield": "2.0",
            "payout_ratio": "40",
            "volatility": "15",
            "rsi": 45,
            "macd": "-0.2",
            "trend_signal": 0,
        }
        strategy_name = "Value"

        # --- Execution ---
        prompt = self.ai_agent_debug._create_prompt(row_data, strategy_name)

        # --- Assertions (日本語プロンプト形式に対応) ---
        # プロンプトにはコードとセクターの情報が含まれること
        self.assertIn("9999", prompt)
        self.assertIn("Finance", prompt)
        # 市場コンテキストが含まれること
        self.assertIn(mock_market_context_content, prompt)

        # --- Cleanup ---
        os.remove("market_context.txt")

    @patch("os.path.exists")
    def test_create_prompt_without_market_context(self, mock_exists):
        """市場コンテキストファイルが存在しない場合のプロンプト生成テスト"""

        # 全ての探索パス（market_context.txt関連）に対して False を返すように設定
        # ただし config/ai_prompts.yaml 等は存在する必要がある
        def side_effect(path):
            if "market_context.txt" in path:
                return False
            return (
                os.path.original_exists(path)
                if hasattr(os, "original_exists")
                else True
            )

        # Note: os.path.exists をパッチすると無限ループや他の不具合のリスクがあるため、
        # より安全に "ai.prompt_builder.os.path.exists" をパッチします。
        with patch("src.ai.prompt_builder.os.path.exists") as mock_p_exists:
            mock_p_exists.side_effect = lambda p: (
                False if "market_context.txt" in p else os.path.exists(p)
            )

            # --- Test Data ---
            row_data = {
                "code": "1111",
                "name": "NoContext Stock",
                "sector": "Service",
                "current_price": 2000,
                "per": 15,
            }
            strategy_name = "Momentum"

            # --- Execution ---
            prompt = self.ai_agent_debug._create_prompt(row_data, strategy_name)

            # --- Assertions ---
            self.assertIn("No specific market context available", prompt)
            self.assertIn("1111", prompt)

    def test_ai_agent_debug_mode(self):
        """デバッグモードでAIエージェントがモックレスポンスを返すテスト (新形式対応)"""
        # -- Test Data --
        row_data = {
            "code": "9999",
            "name": "Debug Test",
            "current_price": 100,
            "per": 10,
            "roe": 5,
        }
        strategy_name = "Test Strategy"

        # -- Execution --
        result = self.ai_agent_debug.analyze(row_data, strategy_name)

        # -- Assertions (新形式: Mock応答は【結論】【強み】【懸念】形式) --
        self.assertEqual(result["ai_sentiment"], "Neutral")
        # 新しいMock形式では ai_summary が返される（ai_reasonにマッピング済み）
        self.assertIn(
            "【結論】", result.get("ai_summary", "") or result.get("ai_reason", "")
        )
        self.assertEqual(result["ai_risk"], "Low (Reason: Mock)")
        self.assertEqual(result["ai_horizon"], "Wait")


if __name__ == "__main__":
    unittest.main()
