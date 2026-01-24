#!/usr/bin/env python3
"""
临时脚本：生成要件清单
"""
import sys
import json

# 添加tools目录到路径
sys.path.insert(0, '/Users/CS/.claude/skills/china-lawyer-analyst/tools')

from checklist_generator import ChecklistGenerator
from checklist_framework import UserRole

# 创建生成器
generator = ChecklistGenerator()

# 用户基本信息
user_role = UserRole.NEUTRAL  # 中立视角（全面分析）
case_id = 2  # 股权转让

# 生成清单
checklist = generator.generate(
    case_id=case_id,
    user_role=user_role
)

# 输出结果
print(checklist)