"""
[Outdated] test_integration_manual_workflow.py
 Refactoring Phase 1-3により、AntigravityRunnerの内部メソッド(_generate_prompts, _merge_responses等)が
 Facadeから削除されました。
 Manual Workflow は 'gen_prompt', 'merge' モードのマイグレーションが完了するまでテストできません。
"""

import unittest

import pytest


@pytest.mark.integration
class TestManualWorkflowDisabled(unittest.TestCase):
    def test_placeholder(self):
        pass
