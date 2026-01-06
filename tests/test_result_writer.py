import os
import shutil
import unittest

import pandas as pd
from src.result_writer import ResultWriter


class TestResultWriter(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data/test_output"
        os.makedirs(self.test_dir, exist_ok=True)
        self.writer = ResultWriter({})
        self.writer.output_dir = self.test_dir

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_csv(self):
        df = pd.DataFrame(
            {
                "code": ["1001", "1002"],
                "name": ["Stock A", "Stock B"],
                "quant_score": [80, 60],
            }
        )
        filename = "test_result.csv"
        path = self.writer.save(df, filename)

        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))

        # Verify content
        loaded = pd.read_csv(path)
        self.assertEqual(len(loaded), 2)
        # [v12.0] ResultWriterはcode->Code, name->Nameにリネームする
        self.assertEqual(loaded.iloc[0]["Name"], "Stock A")

    def test_save_xlsx_converted_to_csv(self):
        """ext .xlsx replaced with .csv"""
        df = pd.DataFrame({"code": ["1"]})
        filename = "test.xlsx"
        path = self.writer.save(df, filename)

        self.assertTrue(path.endswith(".csv"))
        self.assertTrue(os.path.exists(path))

    def test_column_reordering(self):
        """Priority columns should come first"""
        df = pd.DataFrame({"other_col": [1], "code": ["1001"], "ai_reason": ["Good"]})

        path = self.writer.save(df, "reorder.csv")
        loaded = pd.read_csv(path)
        cols = list(loaded.columns)

        # [v12.0] ResultWriterはカラムをPascalCaseにリネーム (code->Code, ai_reason->AI_Comment)
        self.assertEqual(cols[0], "Code")
        self.assertIn("AI_Comment", cols)  # ai_reason -> AI_Comment
        self.assertEqual(cols[-1], "other_col")  # リネーム対象外は末尾

    def test_save_error(self):
        """Error handling when path is invalid"""
        self.writer.output_dir = "/invalid_path/output"
        df = pd.DataFrame({"code": ["1"]})
        path = self.writer.save(df, "fail.csv")
        self.assertIsNone(path)


if __name__ == "__main__":
    unittest.main()
