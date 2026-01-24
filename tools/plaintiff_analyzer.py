"""
原告分析器
专注于原告视角的案件分析

整合自case-type-guide，适配china-lawyer-analyst架构
"""

import sqlite3
from typing import Dict, List, Optional
from pathlib import Path


class PlaintiffAnalyzer:
    """原告视角分析器"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化原告分析器

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
            self.conn.row_factory = sqlite3.Row  # 支持字典式访问
        return self.conn

    def analyze(
        self,
        case_id: int,
        case_materials: Optional[Dict] = None,
        user_role: str = 'plaintiff'
    ) -> Dict:
        """
        原告视角分析

        Args:
            case_id: 案件类型ID
            case_materials: 案件材料（可选）
            user_role: 用户角色（plaintiff/defendant/neutral）

        Returns:
            分析结果字典，包含：
            - case_type: 案件类型名称
            - strengths: 优势识别列表
            - gaps: 缺失识别列表
            - claims: 诉请建议列表
            - evidence: 证据清单
            - winning_probability: 胜诉概率（0-1）
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # 获取案件类型信息
        cursor.execute("SELECT case_name FROM case_types WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"案件ID {case_id} 不存在")
        case_name = row["case_name"]

        # 要件检核
        strengths, gaps = self._check_elements(cursor, case_id, case_materials)

        # 诉请构建建议
        claims = self._get_claims(cursor, case_id)

        # 证据清单
        evidence = self._get_evidence_list(cursor, case_id, user_role)

        # 胜诉概率计算
        total = len(strengths) + len(gaps)
        probability = len(strengths) / total if total > 0 else 0.5

        return {
            'case_type': case_name,
            'case_id': case_id,
            'user_role': user_role,
            'strengths': strengths,
            'gaps': gaps,
            'claims': claims,
            'evidence': evidence,
            'winning_probability': probability
        }

    def _check_elements(
        self,
        cursor,
        case_id: int,
        materials: Optional[Dict]
    ) -> tuple:
        """
        检核案件要素

        Args:
            cursor: 数据库游标
            case_id: 案件ID
            materials: 案件材料

        Returns:
            (strengths, gaps) 元组
        """
        cursor.execute("""
            SELECT point_id, point_name, review_content
            FROM review_points
            WHERE case_id = ? AND is_core = 1
            ORDER BY sort_order
        """, (case_id,))

        points = cursor.fetchall()
        strengths = []
        gaps = []

        # 简化判断逻辑（实际使用时需要更复杂的分析）
        for point in points:
            point_data = {
                'point_id': point["point_id"],
                'name': point["point_name"],
                'content': point["review_content"]
            }

            # 如果提供了案件材料，尝试判断
            if materials and 'evidences' in materials and materials['evidences']:
                strengths.append(point_data)
            else:
                gaps.append(point_data)

        return strengths, gaps

    def _get_claims(self, cursor, case_id: int) -> List[Dict]:
        """
        获取诉请建议

        Args:
            cursor: 数据库游标
            case_id: 案件ID

        Returns:
            诉请建议列表
        """
        cursor.execute("""
            SELECT point_name, review_content, legal_basis
            FROM review_points
            WHERE case_id = ? AND framework_id = 3
            ORDER BY sort_order
        """, (case_id,))

        claims = []
        for row in cursor.fetchall():
            claims.append({
                'name': row["point_name"],
                'content': row["review_content"] if row["review_content"] else "",
                'basis': row["legal_basis"] if row["legal_basis"] else ""
            })

        return claims

    def _get_evidence_list(
        self,
        cursor,
        case_id: int,
        party_type: str = 'plaintiff'
    ) -> List[Dict]:
        """
        获取证据清单

        Args:
            cursor: 数据库游标
            case_id: 案件ID
            party_type: 当事人类型（plaintiff/defendant）

        Returns:
            证据清单列表
        """
        cursor.execute("""
            SELECT evidence_name, evidence_type, necessity_level, description
            FROM evidence_checklists
            WHERE case_id = ? AND party_type = ?
            ORDER BY necessity_level DESC, evidence_id
        """, (case_id, party_type))

        evidence_list = []
        for row in cursor.fetchall():
            evidence_list.append({
                'name': row["evidence_name"],
                'type': row["evidence_type"] if row["evidence_type"] else "其他",
                'level': row["necessity_level"] if row["necessity_level"] else "补充",
                'desc': row["description"] if row["description"] else ""
            })

        return evidence_list

    def format_report(self, analysis: Dict) -> str:
        """
        格式化为可读的报告

        Args:
            analysis: 分析结果字典

        Returns:
            Markdown格式报告
        """
        md = f"# {analysis['case_type']} - {analysis['user_role']}视角分析报告\n\n"
        md += f"**案件ID**: {analysis['case_id']}\n"
        md += f"**胜诉概率**: {analysis['winning_probability']*100:.1f}%\n\n"

        # 优势识别
        md += "## 一、优势识别\n\n"
        if analysis['strengths']:
            for strength in analysis['strengths']:
                md += f"- ✅ {strength['name']}\n"
                if strength.get('content'):
                    md += f"  {strength['content']}\n"
        else:
            md += "暂无识别的优势\n"
        md += "\n"

        # 缺失识别
        md += "## 二、缺失识别\n\n"
        if analysis['gaps']:
            for gap in analysis['gaps']:
                md += f"- ❌ {gap['name']}\n"
                if gap.get('content'):
                    md += f"  {gap['content']}\n"
        else:
            md += "✅ 要件完整，无明显缺失\n"
        md += "\n"

        # 诉请建议
        md += "## 三、诉请建议\n\n"
        if analysis['claims']:
            for claim in analysis['claims']:
                md += f"### {claim['name']}\n\n"
                if claim['content']:
                    md += f"{claim['content']}\n\n"
                if claim['basis']:
                    md += f"**法律依据**: {claim['basis']}\n\n"
        else:
            md += "暂无诉请建议\n"
        md += "\n"

        # 证据清单
        md += "## 四、证据清单\n\n"
        if analysis['evidence']:
            # 按必要性分组
            necessary = [e for e in analysis['evidence'] if e['level'] == '必需']
            important = [e for e in analysis['evidence'] if e['level'] == '重要']
            supplementary = [e for e in analysis['evidence'] if e['level'] == '补充']

            if necessary:
                md += "### 必需证据\n\n"
                for ev in necessary:
                    md += f"- **{ev['name']}** ({ev['type']})\n"
                    if ev['desc']:
                        md += f"  {ev['desc']}\n"
                md += "\n"

            if important:
                md += "### 重要证据\n\n"
                for ev in important:
                    md += f"- **{ev['name']}** ({ev['type']})\n"
                    if ev['desc']:
                        md += f"  {ev['desc']}\n"
                md += "\n"

            if supplementary:
                md += "### 补充证据\n\n"
                for ev in supplementary:
                    md += f"- **{ev['name']}** ({ev['type']})\n"
                    if ev['desc']:
                        md += f"  {ev['desc']}\n"
        else:
            md += "暂无证据清单\n"

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


# 使用示例
if __name__ == "__main__":
    print("=== 原告分析器测试 ===\n")

    analyzer = PlaintiffAnalyzer()

    # 测试：民间借贷案件
    print("1. 民间借贷-原告视角分析:")
    analysis = analyzer.analyze(
        case_id=7,
        case_materials={'evidences': ['借条', '转账记录']},  # 模拟提供部分证据
        user_role='plaintiff'
    )

    print(f"  案件类型: {analysis['case_type']}")
    print(f"  优势数量: {len(analysis['strengths'])}")
    print(f"  缺失数量: {len(analysis['gaps'])}")
    print(f"  诉请数量: {len(analysis['claims'])}")
    print(f"  证据数量: {len(analysis['evidence'])}")
    print(f"  胜诉概率: {analysis['winning_probability']*100:.1f}%")

    # 生成Markdown报告
    print("\n2. 生成Markdown报告:")
    report = analyzer.format_report(analysis)
    print(f"  报告长度: {len(report)}字符")
    print(f"  报告预览（前300字符）:")
    print("  " + report[:300].replace('\n', '\n  '))
    print("  ...")

    analyzer.close()

    print("\n✅ 测试完成")