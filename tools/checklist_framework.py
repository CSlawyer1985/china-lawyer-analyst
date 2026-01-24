"""
要件清单框架模块
定义六段式审判框架的基础结构和角色过滤逻辑
"""

from enum import Enum
from typing import Dict, List


class UserRole(Enum):
    """用户角色"""
    PLAINTIFF = "plaintiff"  # 原告
    DEFENDANT = "defendant"  # 被告
    NEUTRAL = "neutral"      # 中立（完整框架）


class ChecklistFramework:
    """六段式审判框架定义器"""

    # 六段式框架定义（上海法院标准）
    FRAMEWORK_PARTS = [
        {'part_number': 1, 'part_name': '总体情况概述'},
        {'part_number': 2, 'part_name': '立案审查'},
        {'part_number': 3, 'part_name': '原告诉请的审查'},
        {'part_number': 4, 'part_name': '被告抗辩的审查'},
        {'part_number': 5, 'part_name': '要件事实审查和裁判规则'},
        {'part_number': 6, 'part_name': '知识图谱'}
    ]

    @staticmethod
    def get_relevant_parts(user_role: UserRole) -> List[Dict]:
        """
        根据用户角色获取相关部分

        Args:
            user_role: 用户角色

        Returns:
            相关部分列表
        """
        if user_role == UserRole.PLAINTIFF:
            # 原告视角：立案审查 + 原告诉请 + 要件事实
            return [p for p in ChecklistFramework.FRAMEWORK_PARTS
                   if p['part_number'] in [1, 2, 3, 5]]
        elif user_role == UserRole.DEFENDANT:
            # 被告视角：总体情况 + 被告抗辩 + 要件事实
            return [p for p in ChecklistFramework.FRAMEWORK_PARTS
                   if p['part_number'] in [1, 4, 5]]
        else:
            # 中立视角：完整框架
            return ChecklistFramework.FRAMEWORK_PARTS

    @staticmethod
    def format_checklist(checklist: Dict) -> str:
        """
        格式化为Markdown输出

        Args:
            checklist: 要件清单字典

        Returns:
            Markdown格式字符串
        """
        md = f"# {checklist['case_type']} - {checklist.get('user_role', 'neutral')}视角要件清单\n\n"
        md += f"**案件ID**: {checklist['case_id']}\n\n"

        for section in checklist.get('sections', []):
            md += f"## {section['part_name']}\n\n"

            for item in section.get('checklist_items', []):
                status_icon = "❌" if item.get('status') == 'pending' else "✅"
                core_mark = " **[核心]**" if item.get('is_core') else ""

                md += f"- [{status_icon}] {core_mark}{item['item_name']}\n"

                if item.get('review_content'):
                    md += f"  - **审查要点**: {item['review_content']}\n"

                if item.get('attention_points'):
                    md += f"  - **注意事项**: {item['attention_points']}\n"

                if item.get('legal_basis'):
                    md += f"  - **法律依据**: {item['legal_basis']}\n"

                md += "\n"

        return md


# 使用示例
if __name__ == "__main__":
    framework = ChecklistFramework()

    # 测试角色过滤
    plaintiff_parts = framework.get_relevant_parts(UserRole.PLAINTIFF)
    print("原告视角相关部分：")
    for part in plaintiff_parts:
        print(f"  - {part['part_number']}. {part['part_name']}")