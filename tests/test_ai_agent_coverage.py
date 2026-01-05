import unittest
from unittest.mock import MagicMock, patch

from src.ai.agent import AIAgent


class TestAIAgentCoverage(unittest.TestCase):
    def setUp(self):
        self.agent = AIAgent(model_name="test-model", debug_mode=True)
        # Mock API logic to avoid real calls even if debug_mode=False
        self.agent.model = MagicMock()
        # Mock key_manager state for logic that reads stats
        self.agent.key_manager.api_keys = ["key1", "key2"]
        self.agent.key_manager.key_stats = [
            {
                "status": "active",
                "total_calls": 0,
                "success_count": 0,
                "retry_count": 0,
                "error_429_count": 0,
                "errors": 0,
                "is_exhausted": False,
                "usage": 0,
            },
            {
                "status": "active",
                "total_calls": 0,
                "success_count": 0,
                "retry_count": 0,
                "error_429_count": 0,
                "errors": 0,
                "is_exhausted": False,
                "usage": 0,
            },
        ]

    def test_json_parsing_edge_cases(self):
        """Test _parse_response with various formats"""
        # 1. Clean JSON
        resp_text = '{"ai_sentiment": "Bullish", "ai_reason": "Good"}'
        parsed = self.agent._parse_response(resp_text)
        self.assertEqual(parsed["ai_sentiment"], "Bullish")

        # 2. Markdown code block
        resp_text = '```json\n{"ai_sentiment": "Bearish"}\n```'
        parsed = self.agent._parse_response(resp_text)
        self.assertEqual(parsed["ai_sentiment"], "Bearish")

    @patch("src.ai.agent.time.sleep")
    def test_retry_logic_exceptions(self, mock_sleep):
        """Test _generate_content_with_retry with exceptions"""
        self.agent.debug_mode = False

        # Mock model response to raise Exception then succeed
        mock_resp = MagicMock()
        mock_resp.text = '{"success": true}'

        self.agent.model.generate_content.side_effect = [
            Exception("Simulated API Error"),  # Just Exception triggers retry
            mock_resp,
        ]

        # Mock self.client
        self.agent.client = MagicMock()
        self.agent.client.models.generate_content = self.agent.model.generate_content

        # Mock get_current_client to return the mock client (for rotation or re-init logic)
        self.agent.key_manager.get_current_client = MagicMock(
            return_value=self.agent.client
        )

        res = self.agent._generate_content_with_retry("prompt")

        self.assertEqual(res.text, '{"success": true}')
        self.assertTrue(mock_sleep.called)

    @patch("src.ai.agent.time.sleep")
    def test_retry_logic_params(self, mock_sleep):
        """Test retry with specific error codes for 429 handling"""
        self.agent.debug_mode = False

        mock_resp = MagicMock()
        mock_resp.text = '{"ok": 1}'

        # Mock self.client
        self.agent.client = MagicMock()
        self.agent.model.generate_content.side_effect = [
            Exception("429 Too Many Requests"),
            mock_resp,
        ]
        self.agent.client.models.generate_content = self.agent.model.generate_content

        # Mock get_current_client to return the mock client
        self.agent.key_manager.get_current_client = MagicMock(
            return_value=self.agent.client
        )

        res = self.agent._generate_content_with_retry("prompt")
        self.assertEqual(res.text, '{"ok": 1}')
        # Sleep is not called if rotation succeeds immediately

    def test_analyze_debug_mode(self):
        """Test analyze in debug mode returns mock directly"""
        self.agent.debug_mode = True
        res = self.agent.analyze({"code": "1001", "name": "Test"}, "test_strat")
        self.assertEqual(res["ai_sentiment"], "Neutral")
        self.assertIn("MOCK ANALYSIS", res["ai_reason"])

    @patch("src.ai.agent.PromptBuilder")
    def test_create_prompt_logic(self, mock_pb_cls):
        """Test delegated prompt creation logic"""
        # Setup mock
        mock_pb = mock_pb_cls.return_value
        self.agent.prompt_builder = mock_pb
        mock_pb.create_prompt.return_value = "Mocked Prompt with 1001"

        data = {"code": "1001", "name": "T"}
        p = self.agent._create_prompt(data, "test_strat")

        mock_pb.create_prompt.assert_called_with(data, "test_strat")
        self.assertEqual(p, "Mocked Prompt with 1001")

    @patch("src.ai.agent.ValidationEngine")
    @patch("src.ai.agent.ResponseParser")
    def test_analyze_validation_loop(self, mock_parser_cls, mock_val_cls):
        """Test analyze loops and re-prompts on invalid JSON"""
        self.agent.debug_mode = False

        # Mock Parser
        mock_parser = mock_parser_cls.return_value
        self.agent.response_parser = mock_parser

        # 1. Invalid, 2. Valid
        mock_parser.parse_response.side_effect = [
            {},  # First parse empty/invalid
            {"ai_sentiment": "Bullish"},  # Second valid
        ]
        mock_parser.validate_response.side_effect = [(False, "Parse Error"), (True, [])]

        self.agent.client = MagicMock()
        self.agent.key_manager.get_current_client = MagicMock(
            return_value=self.agent.client
        )

        # Responses: 1. Invalid JSON, 2. Valid JSON
        mock_resp1 = MagicMock()
        mock_resp1.text = "Not JSON"
        mock_resp2 = MagicMock()
        mock_resp2.text = '{"ai_sentiment": "Bullish"}'

        self.agent.client.models.generate_content.side_effect = [mock_resp1, mock_resp2]

        res = self.agent.analyze({"code": "1001"}, "test_strat")

        self.assertEqual(res["ai_sentiment"], "Bullish")
        self.assertEqual(self.agent.client.models.generate_content.call_count, 2)


class TestAIAgentCoverageExtended(unittest.TestCase):
    def setUp(self):
        self.agent = AIAgent(model_name="test")
        self.agent.key_manager = MagicMock()
        self.agent.config = {}

    def test_properties_and_setters(self):
        """Test all property getters and setters"""
        # api_keys
        self.agent.api_keys = ["k1"]
        self.assertEqual(self.agent.api_keys, ["k1"])

        # current_key_idx
        self.agent.current_key_idx = 1
        self.assertEqual(self.agent.current_key_idx, 1)

        # key_stats
        stats = [{"usage": 10}]
        self.agent.key_stats = stats
        self.assertEqual(self.agent.key_stats, stats)

        # thresholds_cfg (getter delegation check)
        self.agent.prompt_builder = MagicMock()
        _ = self.agent.thresholds_cfg
        # Since it's a property on mock, it just returns a mock, access is enough.

        # sector_policies
        self.agent.sector_policies = {"Retail": "Avoid"}
        self.assertEqual(self.agent.sector_policies, {"Retail": "Avoid"})
        self.assertEqual(self.agent.config["sector_policies"], {"Retail": "Avoid"})

    def test_set_config_initializes_validator(self):
        """Test config injection"""
        config = {"test": 1}
        self.agent.validator = None

        with patch("src.ai.agent.ValidationEngine") as mock_val:
            self.agent.set_config(config)
            mock_val.assert_called_with(config)
            self.assertIsNotNone(self.agent.validator)
            self.assertEqual(self.agent.config, config)

    def test_get_total_calls(self):
        """Test delegation to key manager"""
        self.agent.get_total_calls()
        self.agent.key_manager.get_total_calls.assert_called()

    def test_generate_usage_report(self):
        """Test report generation string format"""
        self.agent.key_stats = [
            {
                "status": "active",
                "total_calls": 10,
                "success_count": 9,
                "retry_count": 1,
                "error_429_count": 0,
                "errors": 0,
                "is_exhausted": False,
                "usage": 100,
            }
        ]
        report = self.agent.generate_usage_report()
        self.assertIn("API Usage Audit Report", report)
        self.assertIn("Total Calls: 10", report)
        self.assertIn("Key #1: ✅ active", report)

    def test_analyze_from_text(self):
        """Test direct text analysis"""
        # Debug Mode
        self.agent.debug_mode = True
        res = self.agent.analyze_from_text("prompt")
        self.assertEqual(res["ai_sentiment"], "Neutral")
        self.assertIn("MOCK", res["ai_reason"])

        # Real Mode (Mocked)
        self.agent.debug_mode = False
        with patch.object(self.agent, "_generate_content_with_retry") as mock_gen:
            with patch.object(self.agent, "_parse_response") as mock_parse:
                mock_gen.return_value.text = "{}"
                mock_parse.return_value = {"ai_sentiment": "Ok"}

                res = self.agent.analyze_from_text("prompt")
                self.assertEqual(res["ai_sentiment"], "Ok")
                mock_gen.assert_called_with("prompt")

    def test_load_prompt_template_wrapper(self):
        """Test wrapper for prompt template loading"""
        self.agent.prompt_builder = MagicMock()
        self.agent._load_prompt_template()
        self.agent.prompt_builder._load_prompt_template.assert_called()
