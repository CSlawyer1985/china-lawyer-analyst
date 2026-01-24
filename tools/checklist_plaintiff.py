"""
原告视角要件审查模块
专门处理原告角度的案件审查要点
"""

from typing import Dict, List
from .checklist_framework import UserRole
from .db_accessor import get_db_accessor


class PlaintiffChecklist:
    """原告视角要件审查器"""

    def __init__(self, db_path: str = None):
        """
        初始化原告审查器

        Args:
            db_path: 数据库路径
        """
        self.db = get_db_accessor(db_path)

    def load_plaintiff_review_points(
        self,
        case_id: int,
        part_numbers: List[int]
    ) -> List[Dict]:
        """
        加载原告视角的审查要点

        Args:
            case_id: 案件ID
            part_numbers: 部分编号列表（如[2, 3, 5]）

        Returns:
            审查要点列表
        """
        all_items = []

        for part_number in part_numbers:
            # 从数据库获取该部分的审查要点
            review_points = self.db.get_review_points(
                case_id=case_id,
                framework_id=part_number
            )

            # 转换为标准格式
            for rp in review_points:
                all_items.append({
                    'point_id': rp['point_id'],
                    'item_name': rp['point_name'],
                    'point_type': rp.get('point_type', '审查'),
                    'review_content': rp.get('review_content', ''),
                    'attention_points': rp.get('attention_points', ''),
                    'legal_basis': rp.get('legal_basis', ''),
                    'is_core': rp.get('is_core', False),
                    'status': 'pending',
                    'part_number': part_number
                })

        return all_items

    def generate_plaintiff_checklist(self, case_id: int) -> Dict:
        """
        生成原告视角的完整要件清单

        Args:
            case_id: 案件ID

        Returns:
            要件清单字典
        """
        # 获取案件信息
        case_info = self.db.get_case_type(case_id)

        # 获取原告相关部分（1, 2, 3, 5）
        relevant_parts = [1, 2, 3, 5]

        # 加载审查要点
        all_items = self.load_plaintiff_review_points(case_id, relevant_parts)

        # 组织成六段式结构
        sections = []
        current_part = None
        part_items = []

        for item in all_items:
            part_number = item['part_number']

            if part_number != current_part:
                if current_part is not None:
                    part_name = self._get_part_name(current_part)
                    sections.append({
                        'part_name': part_name,
                        'part_number': current_part,
                        'checklist_items': part_items
                    })

                current_part = part_number
                part_items = []

            part_items.append(item)

        # 添加最后一部分
        if current_part is not None:
            part_name = self._get_part_name(current_part)
            sections.append({
                'part_name': part_name,
                'part_number': current_part,
                'checklist_items': part_items
            })

        return {
            'case_type': case_info['case_name'],
            'case_id': case_id,
            'user_role': 'plaintiff',
            'sections': sections
        }

    def _get_part_name(self, part_number: int) -> str:
        """获取部分名称"""
        part_names = {
            1: '总体情况概述',
            2: '立案审查',
            3: '原告诉请的审查',
            5: '要件事实审查和裁判规则'
        }
        return part_names.get(part_number, f'部分{part_number}')


# 使用示例
if __name__ == "__main__":
    generator = PlaintiffChecklist()
    checklist = generator.generate_plaintiff_checklist(1)
    print(f"案件类型: {checklist['case_type']}")
    print(f"部分数量: {len(checklist['sections'])}")
    for section in checklist['sections']:
        print(f"  - {section['part_name']}: {len(section['checklist_items'])}个要点")