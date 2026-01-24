"""
数据库访问工具类
提供统一的数据库访问接口，支持连接池管理和查询优化
"""

import sqlite3
import json
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager
from pathlib import Path


class DatabaseAccessor:
    """
    数据库访问工具类

    功能：
    - 连接池管理
    - 查询优化
    - 数据缓存
    - 事务管理
    """

    def __init__(self, db_path: str = "data/case_types.db"):
        """
        初始化数据库访问器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._connection = None
        self._cache = {}

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接（上下文管理器）

        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 支持字典式访问
        try:
            yield conn
        finally:
            conn.close()

    def get_case_type(self, case_id: int) -> Optional[Dict]:
        """
        获取案件类型信息

        Args:
            case_id: 案件ID

        Returns:
            案件类型字典，包含：case_id, case_name, keywords, description, legal_basis
        """
        # 检查缓存
        cache_key = f"case_type_{case_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT case_id, case_name, keywords, description, legal_basis
                FROM case_types
                WHERE case_id = ?
            """, (case_id,))
            row = cursor.fetchone()

            if row:
                result = {
                    "case_id": row["case_id"],
                    "case_name": row["case_name"],
                    "keywords": row["keywords"].split(",") if row["keywords"] else [],
                    "description": row["description"],
                    "legal_basis": row["legal_basis"]
                }
                # 缓存结果
                self._cache[cache_key] = result
                return result

        return None

    def get_all_case_types(self) -> List[Dict]:
        """
        获取所有案件类型

        Returns:
            案件类型列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT case_id, case_name, keywords, description
                FROM case_types
                ORDER BY case_id
            """)
            rows = cursor.fetchall()

            return [
                {
                    "case_id": row["case_id"],
                    "case_name": row["case_name"],
                    "keywords": row["keywords"].split(",") if row["keywords"] else [],
                    "description": row["description"]
                }
                for row in rows
            ]

    def search_case_types_by_keyword(self, keyword: str) -> List[Dict]:
        """
        根据关键词搜索案件类型

        Args:
            keyword: 关键词

        Returns:
            匹配的案件类型列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT case_id, case_name, keywords
                FROM case_types
                WHERE keywords LIKE ?
                ORDER BY case_id
            """, (f"%{keyword}%",))
            rows = cursor.fetchall()

            return [
                {
                    "case_id": row["case_id"],
                    "case_name": row["case_name"],
                    "keywords": row["keywords"].split(",") if row["keywords"] else []
                }
                for row in rows
            ]

    def get_case_framework(self, case_id: int) -> List[Dict]:
        """
        获取案件的六段式框架

        Args:
            case_id: 案件ID

        Returns:
            框架部分列表，每个部分包含：framework_id, part_number, part_name, part_content
        """
        cache_key = f"framework_{case_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT framework_id, part_number, part_name, part_content
                FROM case_frameworks
                WHERE case_id = ?
                ORDER BY part_number
            """, (case_id,))
            rows = cursor.fetchall()

            result = [
                {
                    "framework_id": row["framework_id"],
                    "part_number": row["part_number"],
                    "part_name": row["part_name"],
                    "part_content": row["part_content"]
                }
                for row in rows
            ]

            self._cache[cache_key] = result
            return result

    def get_review_points(self, case_id: int, framework_id: Optional[int] = None) -> List[Dict]:
        """
        获取审查要点

        Args:
            case_id: 案件ID
            framework_id: 框架ID（可选，不指定则返回所有框架的要点）

        Returns:
            审查要点列表，每个要点包含：point_id, point_name, review_content, sort_order, is_core
        """
        cache_key = f"review_points_{case_id}_{framework_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if framework_id:
                cursor.execute("""
                    SELECT point_id, point_name, review_content, sort_order, is_core
                    FROM review_points
                    WHERE case_id = ? AND framework_id = ?
                    ORDER BY sort_order
                """, (case_id, framework_id))
            else:
                cursor.execute("""
                    SELECT point_id, point_name, review_content, sort_order, is_core
                    FROM review_points
                    WHERE case_id = ?
                    ORDER BY framework_id, sort_order
                """, (case_id,))

            rows = cursor.fetchall()

            result = [
                {
                    "point_id": row["point_id"],
                    "point_name": row["point_name"],
                    "review_content": row["review_content"],
                    "sort_order": row["sort_order"],
                    "is_core": bool(row["is_core"])
                }
                for row in rows
            ]

            self._cache[cache_key] = result
            return result

    def get_evidence_checklist(self, case_id: int, party_type: Optional[str] = None) -> List[Dict]:
        """
        获取证据清单

        Args:
            case_id: 案件ID
            party_type: 当事人类型（plaintiff/defendant，可选）

        Returns:
            证据清单列表，每个证据包含：evidence_id, evidence_name, necessity_level, description
        """
        cache_key = f"evidence_{case_id}_{party_type}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if party_type:
                cursor.execute("""
                    SELECT evidence_id, evidence_name, necessity_level, description
                    FROM evidence_checklists
                    WHERE case_id = ? AND party_type = ?
                    ORDER BY evidence_id
                """, (case_id, party_type))
            else:
                cursor.execute("""
                    SELECT evidence_id, evidence_name, necessity_level, description, party_type
                    FROM evidence_checklists
                    WHERE case_id = ?
                    ORDER BY party_type, evidence_id
                """, (case_id,))

            rows = cursor.fetchall()

            if party_type:
                result = [
                    {
                        "evidence_id": row["evidence_id"],
                        "evidence_name": row["evidence_name"],
                        "necessity_level": row["necessity_level"],
                        "description": row["description"]
                    }
                    for row in rows
                ]
            else:
                result = [
                    {
                        "evidence_id": row["evidence_id"],
                        "evidence_name": row["evidence_name"],
                        "necessity_level": row["necessity_level"],
                        "description": row["description"],
                        "party_type": row["party_type"]
                    }
                    for row in rows
                ]

            self._cache[cache_key] = result
            return result

    def get_case_statistics(self) -> Dict[str, int]:
        """
        获取数据库统计信息

        Returns:
            统计信息字典
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # 案件类型数量
            cursor.execute("SELECT COUNT(*) as count FROM case_types")
            stats["total_case_types"] = cursor.fetchone()["count"]

            # 框架部分数量
            cursor.execute("SELECT COUNT(*) as count FROM case_frameworks")
            stats["total_frameworks"] = cursor.fetchone()["count"]

            # 审查要点数量
            cursor.execute("SELECT COUNT(*) as count FROM review_points")
            stats["total_review_points"] = cursor.fetchone()["count"]

            # 证据清单数量
            cursor.execute("SELECT COUNT(*) as count FROM evidence_checklists")
            stats["total_evidences"] = cursor.fetchone()["count"]

            return stats

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """
        执行自定义查询

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]


# 单例模式的全局访问器
_global_accessor = None


def get_db_accessor(db_path: str = "data/case_types.db") -> DatabaseAccessor:
    """
    获取全局数据库访问器（单例模式）

    Args:
        db_path: 数据库路径

    Returns:
        DatabaseAccessor实例
    """
    global _global_accessor
    if _global_accessor is None:
        _global_accessor = DatabaseAccessor(db_path)
    return _global_accessor


if __name__ == "__main__":
    # 测试数据库访问器
    db = get_db_accessor()

    print("=== 数据库统计信息 ===")
    stats = db.get_case_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\n=== 案件类型示例 ===")
    case_type = db.get_case_type(1)
    if case_type:
        print(f"案件名称: {case_type['case_name']}")
        print(f"关键词: {', '.join(case_type['keywords'][:5])}")
        print(f"描述: {case_type['description'][:100]}...")

    print("\n=== 六段式框架示例 ===")
    frameworks = db.get_case_framework(1)
    for fw in frameworks[:3]:
        print(f"{fw['part_number']}. {fw['part_name']}: {fw['part_content'][:50]}...")

    print("\n=== 证据清单示例 ===")
    evidences = db.get_evidence_checklist(1, "plaintiff")
    for ev in evidences[:3]:
        print(f"- {ev['evidence_name']} ({ev['necessity_level']})")