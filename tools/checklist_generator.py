"""
要件事实审查模块
核心的数据库查询和清单生成逻辑
"""

from typing import Dict, List, Optional
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from checklist_framework import UserRole, ChecklistFramework
from db_accessor import get_db_accessor


class ChecklistGenerator:
    """
    要件清单生成器（重构版）

    整合框架、原告、被告和事实审查模块
    """

    def __init__(self, db_path: str = None):
        """
        初始化要件清单生成器

        Args:
            db_path: 数据库路径
        """
        # 自动查找数据库路径（与case_identifier.py相同逻辑）
        if db_path is None:
            from pathlib import Path
            current_dir = Path(__file__).resolve()
            db_path = current_dir.parent.parent / "data" / "case_types.db"

        self.db = get_db_accessor(str(db_path))
        self.framework = ChecklistFramework()

    def generate(
        self,
        case_id: int,
        user_role: UserRole = UserRole.NEUTRAL
    ) -> Dict:
        """
        生成要件清单（主入口方法）

        Args:
            case_id: 案件类型ID
            user_role: 用户角色（原告/被告/中立）

        Returns:
            要件清单字典，包含：
            - case_type: 案件类型名称
            - case_id: 案件ID
            - user_role: 用户角色
            - sections: 审查部分列表
        """
        # 获取案件信息
        case_info = self.db.get_case_type(case_id)
        if not case_info:
            raise ValueError(f"案件ID {case_id} 不存在")

        # 根据角色获取相关部分
        relevant_parts = self.framework.get_relevant_parts(user_role)

        # 加载各部分的审查要点
        sections = []
        for part_info in relevant_parts:
            section = self._load_section(
                case_id=case_id,
                part_number=part_info['part_number'],
                part_name=part_info['part_name']
            )
            if section:
                sections.append(section)

        return {
            'case_type': case_info['case_name'],
            'case_id': case_id,
            'user_role': user_role.value,
            'sections': sections
        }

    def _load_section(
        self,
        case_id: int,
        part_number: int,
        part_name: str
    ) -> Optional[Dict]:
        """
        加载特定部分的内容

        Args:
            case_id: 案件类型ID
            part_number: 部分编号
            part_name: 部分名称

        Returns:
            部分内容字典，包含：
            - part_name: 部分名称
            - part_number: 部分编号
            - checklist_items: 审查要点列表
        """
        # 获取该部分的审查要点
        review_points = self.db.get_review_points(
            case_id=case_id,
            framework_id=part_number
        )

        if not review_points:
            return None

        # 转换为标准格式
        items = []
        for rp in review_points:
            items.append({
                'point_id': rp['point_id'],
                'item_name': rp['point_name'],
                'point_type': rp.get('point_type', '审查'),
                'review_content': rp.get('review_content', ''),
                'attention_points': rp.get('attention_points', ''),
                'legal_basis': rp.get('legal_basis', ''),
                'is_core': rp.get('is_core', False),
                'status': 'pending'
            })

        return {
            'part_name': part_name,
            'part_number': part_number,
            'checklist_items': items
        }

    def format_markdown(self, checklist: Dict) -> str:
        """
        格式化为Markdown输出

        Args:
            checklist: 要件清单字典

        Returns:
            Markdown格式字符串
        """
        return self.framework.format_checklist(checklist)

    def format_checklist_items(
        self,
        case_id: int,
        user_role: UserRole = UserRole.NEUTRAL
    ) -> List[str]:
        """
        格式化为简化的审查要点列表

        Args:
            case_id: 案件ID
            user_role: 用户角色

        Returns:
            要点列表字符串
        """
        checklist = self.generate(case_id, user_role)
        items = []

        for section in checklist['sections']:
            for item in section['checklist_items']:
                status_icon = "❌" if item['status'] == 'pending' else "✅"
                core_mark = "[核心] " if item['is_core'] else ""

                item_str = f"{status_icon} {core_mark}{item['item_name']}"

                if item['review_content']:
                    item_str += f"\n  要点: {item['review_content'][:100]}..."

                items.append(item_str)

        return items


# 使用示例和测试
if __name__ == "__main__":
    print("=== 要件清单生成器测试 ===\n")

    generator = ChecklistGenerator()

    # 测试1：中立视角
    print("1. 中立视角清单（融资租赁合同）：")
    checklist = generator.generate(case_id=1, user_role=UserRole.NEUTRAL)
    print(f"  案件类型: {checklist['case_type']}")
    print(f"  部分数量: {len(checklist['sections'])}")
    for section in checklist['sections']:
        print(f"    - {section['part_name']}: {len(section['checklist_items'])}个要点")
    print()

    # 测试2：原告视角
    print("2. 原告视角清单（融资租赁合同）：")
    plaintiff_checklist = generator.generate(case_id=1, user_role=UserRole.PLAINTIFF)
    print(f"  案件类型: {plaintiff_checklist['case_type']}")
    print(f"  部分数量: {len(plaintiff_checklist['sections'])}")
    print()

    # 测试3：被告视角
    print("3. 被告视角清单（融资租赁合同）：")
    defendant_checklist = generator.generate(case_id=1, user_role=UserRole.DEFENDANT)
    print(f"  案件类型: {defendant_checklist['case_type']}")
    print(f"  部分数量: {len(defendant_checklist['sections'])}")
    print()

    # 测试4：民间借贷（case_id=7）
    print("4. 民间借贷中立视角清单：")
    lending_checklist = generator.generate(case_id=7, user_role=UserRole.NEUTRAL)
    print(f"  案件类型: {lending_checklist['case_type']}")
    print(f"  部分数量: {len(lending_checklist['sections'])}")
    for section in lending_checklist['sections']:
        print(f"    - {section['part_name']}: {len(section['checklist_items'])}个要点")