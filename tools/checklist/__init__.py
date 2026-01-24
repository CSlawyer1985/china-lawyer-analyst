"""
要件清单生成工具包
整合自 case-type-guide skill

模块：
- checklist_framework: 六段式框架定义
- checklist_plaintiff: 原告视角审查
- checklist_defendant: 被告视角审查
- checklist_generator: 统一生成器（主入口）
"""

from .checklist_framework import ChecklistFramework, UserRole
from .checklist_plaintiff import PlaintiffChecklist
from .checklist_defendant import DefendantChecklist
from .checklist_generator import ChecklistGenerator

__all__ = [
    'ChecklistFramework',
    'UserRole',
    'PlaintiffChecklist',
    'DefendantChecklist',
    'ChecklistGenerator'
]