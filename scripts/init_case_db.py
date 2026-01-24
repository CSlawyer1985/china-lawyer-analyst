#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表结构、导入初始数据、更新索引
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List


class DatabaseInitializer:
    """数据库初始化器"""

    def __init__(self, db_path: str = "data/case_types.db"):
        """
        初始化数据库初始化器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path

    def create_tables(self):
        """创建数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建案件类型表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_types (
                case_id INTEGER PRIMARY KEY,
                case_name TEXT NOT NULL,
                category TEXT NOT NULL,
                keywords TEXT NOT NULL,
                description TEXT,
                procedure_type TEXT,
                core_legal_basis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                legal_basis TEXT
            )
        """)

        # 创建六段式框架表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_frameworks (
                framework_id INTEGER PRIMARY KEY,
                case_id INTEGER NOT NULL,
                part_number INTEGER NOT NULL,
                part_name TEXT NOT NULL,
                part_content TEXT,
                parent_id INTEGER,
                sort_order INTEGER,
                FOREIGN KEY (case_id) REFERENCES case_types(case_id)
            )
        """)

        # 创建审查要点表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_points (
                point_id INTEGER PRIMARY KEY,
                case_id INTEGER NOT NULL,
                framework_id INTEGER NOT NULL,
                point_name TEXT NOT NULL,
                point_type TEXT NOT NULL,
                review_content TEXT,
                attention_points TEXT,
                legal_basis TEXT,
                typical_cases TEXT,
                is_core BOOLEAN DEFAULT 0,
                sort_order INTEGER,
                FOREIGN KEY (case_id) REFERENCES case_types(case_id),
                FOREIGN KEY (framework_id) REFERENCES case_frameworks(framework_id)
            )
        """)

        # 创建证据清单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_checklists (
                evidence_id INTEGER PRIMARY KEY,
                case_id INTEGER NOT NULL,
                point_id INTEGER NOT NULL,
                party_type TEXT NOT NULL,
                evidence_name TEXT NOT NULL,
                evidence_type TEXT,
                necessity_level TEXT,
                description TEXT,
                FOREIGN KEY (case_id) REFERENCES case_types(case_id),
                FOREIGN KEY (point_id) REFERENCES review_points(point_id)
            )
        """)

        # 创建补强建议模板表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reinforcement_templates (
                template_id INTEGER PRIMARY KEY,
                case_id INTEGER NOT NULL,
                point_id INTEGER NOT NULL,
                gap_type TEXT NOT NULL,
                gap_description TEXT,
                reinforcement_advice TEXT,
                priority INTEGER,
                difficulty TEXT,
                time_required TEXT,
                FOREIGN KEY (case_id) REFERENCES case_types(case_id),
                FOREIGN KEY (point_id) REFERENCES review_points(point_id)
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_case_types_keywords
            ON case_types(keywords)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_frameworks_case_id
            ON case_frameworks(case_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_review_points_case_id
            ON review_points(case_id, framework_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_evidence_case_id
            ON evidence_checklists(case_id, party_type)
        """)

        conn.commit()
        conn.close()

        print("✅ 数据库表结构创建完成")

    def import_case_types_from_json(self, json_path: str = "data/case_types_list.json"):
        """
        从JSON文件导入案件类型列表

        Args:
            json_path: JSON文件路径
        """
        # 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            case_types_list = json.load(f)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        imported_count = 0
        for idx, item in enumerate(case_types_list, 1):
            # 检查是否已存在
            cursor.execute("""
                SELECT case_id FROM case_types WHERE case_name = ?
            """, (item["类型"],))
            if cursor.fetchone():
                continue

            # 插入案件类型
            cursor.execute("""
                INSERT INTO case_types
                (case_id, case_name, category, keywords, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                idx,
                item["类型"],
                item["类别"],
                item["类型"],  # 暂时使用案件名称作为关键词
                f"{item['类别']}事案件 - {item['类型']}"
            ))
            imported_count += 1

        conn.commit()
        conn.close()

        print(f"✅ 导入 {imported_count} 个案件类型")

    def export_case_types_to_json(self, output_path: str = "data/case_types_export.json"):
        """
        导出案件类型到JSON文件

        Args:
            output_path: 输出文件路径
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT case_id, case_name, category, keywords, description, legal_basis
            FROM case_types
            ORDER BY case_id
        """)

        rows = cursor.fetchall()
        conn.close()

        case_types = []
        for row in rows:
            case_types.append({
                "case_id": row[0],
                "case_name": row[1],
                "category": row[2],
                "keywords": row[3],
                "description": row[4],
                "legal_basis": row[5]
            })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(case_types, f, ensure_ascii=False, indent=2)

        print(f"✅ 导出 {len(case_types)} 个案件类型到 {output_path}")

    def verify_database(self) -> Dict[str, int]:
        """
        验证数据库完整性

        Returns:
            统计信息字典
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # 案件类型数量
        cursor.execute("SELECT COUNT(*) FROM case_types")
        stats["case_types"] = cursor.fetchone()[0]

        # 框架部分数量
        cursor.execute("SELECT COUNT(*) FROM case_frameworks")
        stats["frameworks"] = cursor.fetchone()[0]

        # 审查要点数量
        cursor.execute("SELECT COUNT(*) FROM review_points")
        stats["review_points"] = cursor.fetchone()[0]

        # 证据清单数量
        cursor.execute("SELECT COUNT(*) FROM evidence_checklists")
        stats["evidences"] = cursor.fetchone()[0]

        # 补强建议数量
        cursor.execute("SELECT COUNT(*) FROM reinforcement_templates")
        stats["reinforcements"] = cursor.fetchone()[0]

        conn.close()

        print("\n=== 数据库验证 ===")
        for key, value in stats.items():
            print(f"{key}: {value}")

        return stats

    def backup_database(self, backup_path: str = None):
        """
        备份数据库

        Args:
            backup_path: 备份文件路径（默认为 {db_path}.bak）
        """
        if backup_path is None:
            backup_path = f"{self.db_path}.bak"

        import shutil
        shutil.copy2(self.db_path, backup_path)

        print(f"✅ 数据库已备份到 {backup_path}")

    def restore_database(self, backup_path: str):
        """
        从备份恢复数据库

        Args:
            backup_path: 备份文件路径
        """
        import shutil
        shutil.copy2(backup_path, self.db_path)

        print(f"✅ 数据库已从 {backup_path} 恢复")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="数据库初始化和管理工具")
    parser.add_argument("--db", default="data/case_types.db", help="数据库文件路径")
    parser.add_argument("--init", action="store_true", help="初始化数据库表结构")
    parser.add_argument("--import", dest="import_json", help="从JSON文件导入案件类型")
    parser.add_argument("--export", dest="export_json", help="导出案件类型到JSON文件")
    parser.add_argument("--verify", action="store_true", help="验证数据库完整性")
    parser.add_argument("--backup", help="备份数据库")
    parser.add_argument("--restore", help="从备份恢复数据库")

    args = parser.parse_args()

    initializer = DatabaseInitializer(args.db)

    if args.init:
        print("=== 初始化数据库 ===")
        initializer.create_tables()

        # 自动导入案件类型列表
        json_path = "data/case_types_list.json"
        if Path(json_path).exists():
            initializer.import_case_types_from_json(json_path)

    if args.import_json:
        print(f"=== 导入案件类型 ===")
        initializer.import_case_types_from_json(args.import_json)

    if args.export_json:
        print(f"=== 导出案件类型 ===")
        initializer.export_case_types_to_json(args.export_json)

    if args.verify:
        initializer.verify_database()

    if args.backup:
        print(f"=== 备份数据库 ===")
        initializer.backup_database(args.backup)

    if args.restore:
        print(f"=== 恢复数据库 ===")
        initializer.restore_database(args.restore)

    # 如果没有指定任何操作，显示帮助
    if not any([args.init, args.import_json, args.export_json,
                args.verify, args.backup, args.restore]):
        parser.print_help()


if __name__ == "__main__":
    main()