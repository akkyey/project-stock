# Unified Analyst Prompt v2.0 プロポーサル

## 背景と目的

本プロポーサルは、現行の株式分析システムにおける「コード（Python）で計算・検証した結果」と「AI（LLM）が生成した解説」の**完全な一致**を保証する「**Single Source of Truth**」アーキテクチャを構築することを目的とする。

> [!IMPORTANT]
> **ゴール**: Pydanticによる厳格な型定義、戦略別ユニットテスト、統合プロンプトv2.0を連携させ、システム全体の信頼性と透明性を極限まで高める。

---

## A. データモデル設計（Pydantic完全移行）

### A-1. 現状の課題
- `StockAnalysisData` は基本的な型定義のみで、**閾値検証**や**異常値検知**がモデル外（`ValidationEngine`）に依存している。
- dict との混在が一部に残り、異常値検出ロジックが分散している。

### A-2. 提案: `StockAnalysisData` の強化

```python
# src/domain/models.py (提案)
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class SkipReason(str, Enum):
    INSOLVENT = "equity_ratio_negative"    # 債務超過
    EXTREME_VALUATION = "valuation_bubble"  # PER500超/PBR20超
    NEGATIVE_OCF = "operating_cf_negative"  # 営業CF破綻
    PAYOUT_UNSUSTAINABLE = "payout_over_300" # タコ足配当

class ValidationFlag(BaseModel):
    """どのルールに抵触したかのメタデータ"""
    tier1_missing: List[str] = Field(default_factory=list)
    tier2_missing: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    rescue_eligible: bool = False  # 例外救済ルール該当
    skip_reasons: List[SkipReason] = Field(default_factory=list)

class StockAnalysisData(BaseModel):
    code: str
    name: Optional[str] = None
    # ... (既存フィールド)

    # --- メタデータ (AI連携用) ---
    validation_flags: ValidationFlag = Field(default_factory=ValidationFlag)

    @field_validator("equity_ratio", mode="before")
    @classmethod
    def check_equity_ratio(cls, v, info):
        if v is not None and v < 0:
            # 債務超過: skip_reasonsに追加するためのフラグを立てる
            # (model_validatorで最終処理)
            pass
        return v

    @model_validator(mode="after")
    def validate_analyst_rules(self):
        """アナリストルールブックに基づく検証を一括実行"""
        flags = self.validation_flags

        # Tier 1 Critical Check
        tier1_fields = ["current_price", "operating_cf", "operating_margin", 
                        "per", "pbr", "roe"]
        for field in tier1_fields:
            if getattr(self, field, None) is None:
                flags.tier1_missing.append(field)

        # Abnormal Value Detection (足切り)
        if self.equity_ratio is not None and self.equity_ratio < 0:
            flags.skip_reasons.append(SkipReason.INSOLVENT)
        if self.per is not None and self.per > 500:
            flags.skip_reasons.append(SkipReason.EXTREME_VALUATION)
        if self.pbr is not None and self.pbr > 20:
            flags.skip_reasons.append(SkipReason.EXTREME_VALUATION)

        # Red Flag Detection
        if self.operating_cf is not None and self.operating_cf < 0:
            flags.red_flags.append("negative_ocf")
        if self.sales_growth is not None and self.sales_growth < 0:
            flags.red_flags.append("declining_sales")

        # 例外救済ルール判定
        if self.pbr is not None and self.dividend_yield is not None:
            if self.pbr < 1.0 and self.dividend_yield > 4.0:
                flags.rescue_eligible = True

        return self

    @property
    def should_skip_analysis(self) -> bool:
        """分析をスキップすべきかを判定"""
        return len(self.validation_flags.skip_reasons) > 0
```

### A-3. AIプロンプトへのメタデータ連携

```yaml
# config/ai_prompts.yaml (追加セクション)
validation_metadata_template: |
  【検証メタデータ (Pydantic Validated)】
  - Tier 1 欠損: {tier1_missing}
  - Red Flags: {red_flags}
  - 例外救済該当: {rescue_eligible}
  ※このデータはシステムで事前検証済みです。独自の計算は行わず、提供された数値に基づいて判断してください。
```

---

## B. 戦略テスト仕様（Unit Test拡充）

### B-1. 現状の課題
- 戦略テスト (`tests/test_strategies.py`) はスコア計算の基本動作のみを検証。
- **Red Flag検知時のAI判定誘導**や**例外救済ルール**の検証が不足。

### B-2. 提案: 戦略・ルール整合性テストの追加

```python
# tests/test_strategy_analyst_rules_integration.py (新規)
import pytest
from src.domain.models import StockAnalysisData, SkipReason
from src.calc.strategies.value_strict import ValueStrictStrategy
from src.ai.prompt_builder import PromptBuilder

class TestValueStrictAnalystRulesConsistency:
    """value_strict戦略とアナリストルールの数学的整合性を検証"""

    @pytest.fixture
    def config(self):
        return get_mock_config()  # 既存のモック設定

    def test_red_flag_forces_bearish_prompt(self, config):
        """Red Flag検知時、プロンプトにBearish誘導が含まれること"""
        stock = StockAnalysisData(
            code="9999",
            name="Test Corp",
            operating_cf=-1000000,  # Red Flag: 営業CF赤字
            per=10.0,
            pbr=0.8,
        )
        assert "negative_ocf" in stock.validation_flags.red_flags

        builder = PromptBuilder(config)
        prompt = builder.build(stock, "value_strict")

        # プロンプトにBearish強制文言が含まれること
        assert "Bearish判定の必須要件" in prompt
        assert "営業CFマージンがマイナス" in prompt

    def test_rescue_rule_triggers_positive_bias(self, config):
        """例外救済ルール (PBR<1.0 & 利回り>4.0%) が正しく発動"""
        stock = StockAnalysisData(
            code="8888",
            name="Deep Value Corp",
            pbr=0.7,
            dividend_yield=5.2,
            per=8.0,
            operating_cf=500000,  # No Red Flag
        )
        assert stock.validation_flags.rescue_eligible is True
        assert len(stock.validation_flags.red_flags) == 0

    def test_abnormal_value_skips_analysis(self, config):
        """異常値 (PER>500) で分析がスキップされること"""
        stock = StockAnalysisData(
            code="7777",
            name="Bubble Corp",
            per=600.0,  # 異常値
            pbr=1.5,
        )
        assert stock.should_skip_analysis is True
        assert SkipReason.EXTREME_VALUATION in stock.validation_flags.skip_reasons

    def test_score_priority_matches_strategy(self, config):
        """value_strictの優先順位: バリュエーション > 成長 > 品質"""
        strategy = ValueStrictStrategy(config)
        
        # バリュエーション良好 + 成長悪い
        high_value = {"code": "A", "per": 8.0, "pbr": 0.6, "roe": 5.0, "sales_growth": -5.0}
        # バリュエーション悪い + 成長良好
        high_growth = {"code": "B", "per": 30.0, "pbr": 3.0, "roe": 20.0, "sales_growth": 30.0}

        result = strategy.calculate_score(pd.DataFrame([high_value, high_growth]))
        
        # value_strictではバリュエーション重視のため、high_valueが高スコア
        assert result.loc[result["code"] == "A", "quant_score"].iloc[0] > \
               result.loc[result["code"] == "B", "quant_score"].iloc[0]
```

---

## C. 統合プロンプト v2.0 への昇華

### C-1. プロンプトへの「検証済み宣言」追加

```yaml
# config/ai_prompts.yaml の base_template 修正案
base_template: |
  あなたは「市場の番人」として、投資家を甘い誘惑から守る厳格なシニア証券アナリストです。

  **【重要】データ検証ステータス**
  本銘柄のデータは **Pydantic StockAnalysisData** モデルによって以下の検証を完了しています:
  - 型チェック: ✅ 完了
  - 欠損値処理: ✅ 完了 (欠損項目: {tier1_missing_count}件)
  - 異常値検知: ✅ 完了 (Red Flags: {red_flag_count}件)
  - 例外救済判定: {rescue_status}

  ⚠️ **あなたの役割**: システムから渡された「検証済みデータ」に忠実に従い、独自の計算や推測は**一切行わないでください**。
  {persona}として、{default_horizon}の視点から分析を行ってください。
  
  # ... (以降は既存テンプレート)
```

### C-2. JSON出力スキーマの拡張

```json
{
  "code": "{code}",
  "ai_sentiment": "Bullish/Neutral/Bearish",
  "ai_summary": "...",
  "ai_detail": "...",
  "ai_risk": "...",
  "ai_horizon": "...",
  "_metadata": {
    "pydantic_validated": true,
    "validation_flags": {
      "tier1_missing": [],
      "red_flags": [],
      "rescue_eligible": false
    },
    "model_version": "v2.0"
  }
}
```

---

## 実装ロードマップ

| Phase       | 内容                 | ファイル                                                  | 工数目安 |
| :---------- | :------------------- | :-------------------------------------------------------- | :------- |
| **Phase 1** | Pydanticモデル強化   | `src/domain/models.py`                                    | 2h       |
| **Phase 2** | PromptBuilder連携    | `src/ai/prompt_builder.py`                                | 1h       |
| **Phase 3** | 戦略テスト拡充       | `tests/test_strategy_analyst_rules_integration.py` (新規) | 2h       |
| **Phase 4** | プロンプトv2.0更新   | `config/ai_prompts.yaml`                                  | 1h       |
| **Phase 5** | 統合テスト・回帰確認 | `self_diagnostic.py` 実行                                 | 1h       |

---

## 検証計画

### 自動テスト
```bash
# 新規テストスイートの実行
pytest tests/test_strategy_analyst_rules_integration.py -v

# 全体回帰テスト
python self_diagnostic.py
```

### 手動検証
- E2E: `orchestrator.py weekly` 実行後、レポート出力を確認
- JSON出力に `_metadata.pydantic_validated: true` が含まれることを確認

---

> [!NOTE]
> 本プロポーサルは既存の `ValidationEngine` と共存可能な設計としている。将来的には `ValidationEngine` の責務の一部を Pydantic モデルへ移行し、単一責任原則をより厳密に適用することも検討可能。
