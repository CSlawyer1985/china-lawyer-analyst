"""
顾问模块包
整合自case-type-guide，提供缺失要素识别和补强建议匹配功能

包含:
- GapIdentifier: 缺失要素识别器
- AdviceMatcher: 补强建议匹配器
- ReinforcementEngine: 补强建议引擎（统一接口）
"""

from .gap_identifier import GapIdentifier
from .advice_matcher import AdviceMatcher
from .reinforcement_engine import ReinforcementEngine

__all__ = ['GapIdentifier', 'AdviceMatcher', 'ReinforcementEngine']