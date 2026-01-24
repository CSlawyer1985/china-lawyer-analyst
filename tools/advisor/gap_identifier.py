"""
缺失要素识别器
识别案件材料中的缺失要素

整合自case-type-guide
"""

from typing import Dict, List, Optional
from pathlib import Path
import sqlite3


class GapIdentifier:
    """缺失要素识别器"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化缺失要素识别器

        Args:
            db_path: 数据库路径（可选，默认自动查找）
        """
        if db_path is None:
            current_dir = Path(__file__).resolve()
            db_path = current_dir.parent.parent / "data" / "case_types.db"

        self.db_path = str(db_path)
        self.conn = None

    def _get_connection(self):
        """获取数据库连接"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def identify(
        self,
        case_id: int,
        existing_materials: Dict,
        user_role: str = "plaintiff"
    ) -> List[Dict]:
        """
        识别缺失要素

        Args:
            case_id: 案件类型ID
            existing_materials: 现有材料（字典，包含'evidences'列表）
            user_role: 用户角色（plaintiff/defendant/neutral）

        Returns:
            缺失要素列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # 获取必需证据清单
        cursor.execute("""
            SELECT evidence_id, point_id, evidence_name, necessity_level
            FROM evidence_checklists
            WHERE case_id = ? AND party_type = ? AND necessity_level = '必需'
        """, (case_id, user_role))

        required = cursor.fetchall()

        # 提取现有证据名称
        existing_names = []
        if existing_materials and 'evidences' in existing_materials:
            existing_names = [
                str(m.get('name', '')).lower()
                for m in existing_materials['evidences']
            ]

        # 识别缺失
        gaps = []
        for row in required:
            name = row["evidence_name"]
            if name.lower() not in ' '.join(existing_names):
                gaps.append({
                    'point_id': row["point_id"],
                    'evidence_id': row["evidence_id"],
                    'name': name,
                    'necessity': row["necessity_level"],
                    'type': 'evidence'
                })

        return gaps

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None