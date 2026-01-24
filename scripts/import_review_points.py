#!/usr/bin/env python3
"""
审查要点数据导入工具
支持从JSON/YAML文件批量导入审查要点数据
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

# 添加tools目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from db_accessor import get_db_accessor


class ReviewPointsImporter:
    """审查要点导入器"""

    def __init__(self, db_path: str = "data/case_types.db"):
        """
        初始化导入器

        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self.db = get_db_accessor(db_path)

    def import_from_json(self, json_file: str, overwrite: bool = False) -> Dict:
        """
        从JSON文件导入审查要点

        JSON格式示例:
        {
            "case_id": 1,
            "review_points": [
                {
                    "framework_id": 1,
                    "point_name": "审查要点名称",
                    "point_type": "审查",
                    "review_content": "审查内容",
                    "attention_points": "注意事项",
                    "legal_basis": "法律依据",
                    "sort_order": 1,
                    "is_core": true
                }
            ]
        }

        Args:
            json_file: JSON文件路径
            overwrite: 是否覆盖已存在的要点（默认False）

        Returns:
            导入结果统计
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        case_id = data.get('case_id')
        if not case_id:
            raise ValueError("JSON文件必须包含case_id字段")

        review_points = data.get('review_points', [])
        if not review_points:
            raise ValueError("JSON文件必须包含review_points数组")

        # 导入统计
        stats = {
            'total': len(review_points),
            'success': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for rp in review_points:
                try:
                    # 验证必需字段
                    if not all(k in rp for k in ['framework_id', 'point_name']):
                        stats['failed'] += 1
                        stats['errors'].append(f"缺少必需字段: {rp}")
                        continue

                    # 检查是否已存在
                    cursor.execute("""
                        SELECT point_id FROM review_points
                        WHERE case_id = ? AND framework_id = ? AND point_name = ?
                    """, (case_id, rp['framework_id'], rp['point_name']))

                    exists = cursor.fetchone() is not None

                    if exists and not overwrite:
                        stats['skipped'] += 1
                        continue

                    if exists and overwrite:
                        # 删除已存在的记录
                        cursor.execute("""
                            DELETE FROM review_points
                            WHERE case_id = ? AND framework_id = ? AND point_name = ?
                        """, (case_id, rp['framework_id'], rp['point_name']))

                    # 插入新记录
                    cursor.execute("""
                        INSERT INTO review_points (
                            case_id, framework_id, point_name, point_type,
                            review_content, attention_points, legal_basis,
                            sort_order, is_core
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        case_id,
                        rp['framework_id'],
                        rp['point_name'],
                        rp.get('point_type', '审查'),
                        rp.get('review_content', ''),
                        rp.get('attention_points', ''),
                        rp.get('legal_basis', ''),
                        rp.get('sort_order', 999),
                        1 if rp.get('is_core', False) else 0
                    ))

                    stats['success'] += 1

                except Exception as e:
                    stats['failed'] += 1
                    stats['errors'].append(f"导入失败: {rp.get('point_name', 'Unknown')} - {str(e)}")

            conn.commit()

        # 清空缓存
        self.db.clear_cache()

        return stats

    def import_from_list(self, case_id: int, review_points: List[Dict], overwrite: bool = False) -> Dict:
        """
       从列表直接导入审查要点

        Args:
            case_id: 案件ID
            review_points: 审查要点列表
            overwrite: 是否覆盖已存在的要点

        Returns:
            导入结果统计
        """
        # 创建临时JSON结构
        data = {
            'case_id': case_id,
            'review_points': review_points
        }

        # 保存为临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            temp_file = f.name

        try:
            return self.import_from_json(temp_file, overwrite)
        finally:
            # 删除临时文件
            Path(temp_file).unlink(missing_ok=True)

    def export_to_json(self, case_id: int, output_file: str):
        """
        导出审查要点到JSON文件

        Args:
            case_id: 案件ID
            output_file: 输出文件路径
        """
        # 获取审查要点
        review_points = self.db.get_review_points(case_id)

        # 获取框架信息
        frameworks = self.db.get_case_framework(case_id)

        # 构建framework_id到part_number的映射
        fw_map = {fw['framework_id']: fw['part_number'] for fw in frameworks}

        # 转换为导出格式
        export_data = {
            'case_id': case_id,
            'review_points': []
        }

        for rp in review_points:
            fw_id = self._get_framework_id(case_id, rp['point_id'])
            export_rp = {
                'framework_id': fw_id,
                'point_name': rp['point_name'],
                'point_type': '审查',
                'review_content': rp.get('review_content', ''),
                'attention_points': rp.get('attention_points', ''),
                'legal_basis': rp.get('legal_basis', ''),
                'sort_order': rp.get('sort_order', 999),
                'is_core': rp.get('is_core', False)
            }
            export_data['review_points'].append(export_rp)

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"已导出 {len(export_data['review_points'])} 个审查要点到 {output_file}")

    def _get_framework_id(self, case_id: int, point_id: int) -> Optional[int]:
        """获取审查要点对应的框架ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT framework_id FROM review_points
                WHERE point_id = ?
            """, (point_id,))
            result = cursor.fetchone()
            return result[0] if result else None


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='审查要点数据导入工具')
    parser.add_argument('action', choices=['import', 'export'], help='操作类型')
    parser.add_argument('--case-id', type=int, help='案件ID')
    parser.add_argument('--file', type=str, help='JSON文件路径')
    parser.add_argument('--overwrite', action='store_true', help='覆盖已存在的数据')

    args = parser.parse_args()

    importer = ReviewPointsImporter()

    if args.action == 'import':
        if not args.file:
            print("错误: 导入操作需要指定--file参数")
            return

        print(f"开始导入: {args.file}")
        stats = importer.import_from_json(args.file, args.overwrite)

        print(f"\n导入完成:")
        print(f"  总计: {stats['total']}")
        print(f"  成功: {stats['success']}")
        print(f"  跳过: {stats['skipped']}")
        print(f"  失败: {stats['failed']}")

        if stats['errors']:
            print("\n错误详情:")
            for error in stats['errors']:
                print(f"  - {error}")

    elif args.action == 'export':
        if not args.case_id or not args.file:
            print("错误: 导出操作需要指定--case-id和--file参数")
            return

        importer.export_to_json(args.case_id, args.file)


if __name__ == "__main__":
    main()
