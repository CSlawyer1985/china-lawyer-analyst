"""
建议匹配器
为缺失要素匹配补强建议

整合自case-type-guide
"""

from typing import Dict, List, Optional
from pathlib import Path
import sqlite3


class AdviceMatcher:
    """建议匹配器"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化建议匹配器

        Args:
            db_path: 数据库路径（可选，默认自动查找）
        """
        if db_path is None:
            current_dir = Path(__file__).resolve()
            db_path = current_dir.parent.parent / "data" / "case_types.db"

        self.db_path = str(db_path)

    def match(
        self,
        case_id: int,
        point_id: int,
        gap_type: str
    ) -> List[Dict]:
        """
        匹配补强建议

        Args:
            case_id: 案件类型ID
            point_id: 要点ID
            gap_type: 缺失类型

        Returns:
            建议列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT gap_type, gap_description, reinforcement_advice,
                   priority, difficulty, time_required
            FROM reinforcement_templates
            WHERE case_id = ? AND point_id = ?
            ORDER BY priority
        """, (case_id, point_id))

        templates = []
        for row in cursor.fetchall():
            templates.append({
                'type': row["gap_type"],
                'description': row["gap_description"],
                'advice': row["reinforcement_advice"],
                'priority': row["priority"],
                'difficulty': row["difficulty"],
                'time': row["time_required"]
            })

        # 如果没有模板，返回默认建议
        if not templates:
            templates.append({
                'type': gap_type,
                'description': '缺失要素',
                'advice': '请根据案件情况收集相关材料',
                'priority': 2,
                'difficulty': '中等',
                'time': '1-2周'
            })

        conn.close()
        return templates
