"""
补强建议引擎
整合缺失要素识别和建议匹配，提供统一的补强建议接口

整合自case-type-guide，适配china-lawyer-analyst架构
"""

from typing import Dict, List, Optional
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from db_accessor import get_db_accessor
import sqlite3


class ReinforcementEngine:
    """补强建议引擎（统一接口）"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化补强建议引擎

        Args:
            db_path: 数据库路径（可选，默认自动查找）
        """
        if db_path is None:
            current_dir = Path(__file__).resolve()
            # 从 tools/advisor/ 回到项目根目录需要 parent.parent.parent
            db_path = current_dir.parent.parent.parent / "data" / "case_types.db"

        self.db_path = str(db_path)
        self.conn = None

    def _get_connection(self):
        """获取数据库连接"""
        if not self.conn:
            # 确保数据库路径正确
            db_path = Path(self.db_path)
            if not db_path.exists():
                # 尝试相对于当前脚本的路径
                current_dir = Path(__file__).resolve()
                # 从 tools/advisor/ 回到项目根目录需要 parent.parent.parent
                db_path = current_dir.parent.parent.parent / "data" / "case_types.db"

            self.conn = sqlite3.connect(str(db_path))
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def identify_gaps(
        self,
        case_id: int,
        existing_materials: Optional[Dict],
        user_role: str = "plaintiff"
    ) -> List[Dict]:
        """
        识别缺失要素

        Args:
            case_id: 案件类型ID
            existing_materials: 现有材料（字典，包含'evidences'列表）
            user_role: 用户角色（plaintiff/defendant/neutral）

        Returns:
            缺失要素列表，每个要素包含：
            - point_id: 要点ID
            - evidence_id: 证据ID
            - name: 要素名称
            - necessity: 必要性级别（必需/重要/补充）
            - type: 类型
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

    def get_advices(
        self,
        case_id: int,
        gaps: List[Dict]
    ) -> List[Dict]:
        """
        为缺失要素匹配补强建议

        Args:
            case_id: 案件类型ID
            gaps: 缺失要素列表

        Returns:
            补强建议列表，按优先级排序
        """
        if not gaps:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        all_advices = []

        for gap in gaps:
            point_id = gap.get('point_id')

            # 查询补强建议模板
            cursor.execute("""
                SELECT gap_type, gap_description, reinforcement_advice,
                       priority, difficulty, time_required
                FROM reinforcement_templates
                WHERE case_id = ? AND point_id = ?
                ORDER BY priority
            """, (case_id, point_id))

            templates = cursor.fetchall()

            if templates:
                for row in templates:
                    all_advices.append({
                        'gap_name': gap['name'],
                        'gap_type': row["gap_type"],
                        'description': row["gap_description"],
                        'advice': row["reinforcement_advice"],
                        'priority': row["priority"],
                        'difficulty': row["difficulty"],
                        'time': row["time_required"]
                    })
            else:
                # 默认建议
                all_advices.append({
                    'gap_name': gap['name'],
                    'gap_type': '证据缺失',
                    'description': f'缺少{gap["name"]}相关材料',
                    'advice': f'请尽快收集{gap["name"]}相关证据材料',
                    'priority': 2,
                    'difficulty': '中等',
                    'time': '1-2周'
                })

        # 按优先级排序
        all_advices.sort(key=lambda x: x['priority'])

        return all_advices

    def analyze_and_recommend(
        self,
        case_id: int,
        existing_materials: Optional[Dict],
        user_role: str = "plaintiff"
    ) -> Dict:
        """
        完整的缺失分析和建议流程

        Args:
            case_id: 案件类型ID
            existing_materials: 现有材料
            user_role: 用户角色

        Returns:
            分析和建议结果
        """
        # 识别缺失
        gaps = self.identify_gaps(case_id, existing_materials, user_role)

        # 获取建议
        advices = self.get_advices(case_id, gaps)

        return {
            'case_id': case_id,
            'user_role': user_role,
            'gaps_count': len(gaps),
            'gaps': gaps,
            'advices': advices,
            'summary': self._generate_summary(gaps, advices)
        }

    def _generate_summary(self, gaps: List[Dict], advices: List[Dict]) -> str:
        """生成摘要"""
        if not gaps:
            return "✅ 材料完整，无缺失要素"

        high_priority = len([a for a in advices if a['priority'] == 1])
        medium_priority = len([a for a in advices if a['priority'] == 2])
        low_priority = len([a for a in advices if a['priority'] == 3])

        summary = f"发现 {len(gaps)} 个缺失要素：\n"
        summary += f"- 高优先级补强：{high_priority} 项\n"
        summary += f"- 中优先级补强：{medium_priority} 项\n"
        summary += f"- 低优先级补强：{low_priority} 项"

        return summary

    def format_recommendations(self, result: Dict) -> str:
        """
        格式化为可读的补强建议报告

        Args:
            result: analyze_and_recommend的返回结果

        Returns:
            Markdown格式报告
        """
        md = f"# 补强建议报告\n\n"
        md += f"**案件ID**: {result['case_id']}\n"
        md += f"**用户角色**: {result['user_role']}\n"
        md += f"**缺失要素**: {result['gaps_count']} 个\n\n"

        # 摘要
        md += "## 摘要\n\n"
        md += f"{result['summary']}\n\n"

        # 缺失要素列表
        if result['gaps']:
            md += "## 缺失要素\n\n"
            for gap in result['gaps']:
                md += f"- ❌ {gap['name']} （{gap['necessity']}）\n"
            md += "\n"

        # 补强建议（按优先级分组）
        if result['advices']:
            md += "## 补强建议\n\n"

            # 按优先级分组
            high = [a for a in result['advices'] if a['priority'] == 1]
            medium = [a for a in result['advices'] if a['priority'] == 2]
            low = [a for a in result['advices'] if a['priority'] == 3]

            if high:
                md += "### 🔴 高优先级（立即处理）\n\n"
                for advice in high:
                    md += f"#### {advice['gap_name']}\n\n"
                    md += f"**问题**: {advice['description']}\n\n"
                    md += f"**建议**: {advice['advice']}\n\n"
                    md += f"- 难度: {advice['difficulty']}\n"
                    md += f"- 时间: {advice['time']}\n\n"

            if medium:
                md += "### 🟡 中优先级（建议尽快处理）\n\n"
                for advice in medium:
                    md += f"#### {advice['gap_name']}\n\n"
                    md += f"**问题**: {advice['description']}\n\n"
                    md += f"**建议**: {advice['advice']}\n\n"
                    md += f"- 难度: {advice['difficulty']}\n"
                    md += f"- 时间: {advice['time']}\n\n"

            if low:
                md += "### 🟢 低优先级（可选）\n\n"
                for advice in low:
                    md += f"#### {advice['gap_name']}\n\n"
                    md += f"**建议**: {advice['advice']}\n\n"
        else:
            md += "✅ 无需补强\n"

        return md

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """上下文管理器支持"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器支持"""
        self.close()


# 导出独立的GapIdentifier和AdviceMatcher类
class GapIdentifier(ReinforcementEngine):
    """缺失要素识别器（向后兼容）"""
    def identify(self, case_id: int, existing_materials: Dict, user_role: str = "plaintiff") -> List[Dict]:
        return self.identify_gaps(case_id, existing_materials, user_role)


class AdviceMatcher:
    """建议匹配器（向后兼容）"""
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            current_dir = Path(__file__).resolve()
            # 从 tools/advisor/ 回到项目根目录需要 parent.parent.parent
            db_path = current_dir.parent.parent.parent / "data" / "case_types.db"
        self.db_path = str(db_path)

    def match(self, case_id: int, point_id: int, gap_type: str) -> List[Dict]:
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

        conn.close()
        return templates


# 使用示例
if __name__ == "__main__":
    print("=== 补强建议引擎测试 ===\n")

    # 使用绝对路径初始化（从tools/advisor目录回到项目根目录需要parent.parent.parent）
    current_dir = Path(__file__).resolve().parent.parent.parent  # 回到项目根目录
    db_path = current_dir / "data" / "case_types.db"

    engine = ReinforcementEngine(str(db_path))

    # 测试1：识别缺失要素
    print("1. 识别缺失要素:")
    existing_materials = {
        'evidences': [
            {'name': '借条'},
            {'name': '转账记录'}
        ]
    }

    gaps = engine.identify_gaps(
        case_id=7,  # 民间借贷
        existing_materials=existing_materials,
        user_role='plaintiff'
    )

    print(f"  发现 {len(gaps)} 个缺失要素")
    for gap in gaps[:3]:  # 只显示前3个
        print(f"    - {gap['name']} ({gap['necessity']})")
    if len(gaps) > 3:
        print(f"    ... 还有 {len(gaps)-3} 个")

    # 测试2：完整分析和建议
    print("\n2. 完整分析和建议:")
    result = engine.analyze_and_recommend(
        case_id=7,
        existing_materials=existing_materials,
        user_role='plaintiff'
    )

    print(f"  缺失要素: {result['gaps_count']} 个")
    print(f"  补强建议: {len(result['advices'])} 条")
    print(f"\n  摘要:\n{result['summary']}")

    # 测试3：生成报告
    print("\n3. 生成Markdown报告:")
    report = engine.format_recommendations(result)
    print(f"  报告长度: {len(report)}字符")
    print(f"  报告预览（前400字符）:")
    print("  " + report[:400].replace('\n', '\n  '))
    print("  ...")

    engine.close()

    print("\n✅ 测试完成")
