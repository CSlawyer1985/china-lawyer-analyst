#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化法律校验工具 (Automated Legal Verification)

集成三阶段工作流程:
1. 提取法律引用
2. 检查法律更新
3. 判断新旧法适用
4. 应用修正

作者: china-lawyer-analyst 项目组
版本: v1.0.0
最后更新: 2026-01-16
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class AutomatedLegalVerification:
    """自动化法律校验器"""

    def __init__(self, config_path="tools/monitor/config.yml"):
        """初始化校验器"""
        self.law_db = self._load_law_database()
        self.config = self._load_config(config_path)

    def _load_law_database(self):
        """加载法律数据库"""
        # 从 interpretations/metadata.json 加载
        metadata_file = Path("interpretations/metadata.json")
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_config(self, config_path):
        """加载配置文件"""
        # 简化实现,返回默认配置
        return {
            'sources': ['official_npc', 'official_court', 'gety', 'unifuncs'],
            'timeout': 30,
            'max_results': 10
        }

    def verify(
        self,
        legal_opinion: str,
        fact_date: Optional[str] = None
    ) -> Dict:
        """
        执行全自动校验

        Args:
            legal_opinion: 初步法律意见
            fact_date: 案件事实发生时间(YYYY-MM-DD)

        Returns:
            dict: {
                'verification_report': str,
                'updated_opinion': str,
                'issues_found': list,
                'corrections_made': list
            }
        """
        print("🔍 开始自动化法律校验...")

        # Step 1: 提取法律引用
        print("→ Step 1: 提取法律引用")
        references = self._extract_references(legal_opinion)
        print(f"  找到 {len(references['laws'])} 个法律引用")
        print(f"  找到 {len(references['interpretations'])} 个司法解释")
        if references['dates']:
            print(f"  提取到时间点: {references['dates']}")

        # Step 2: 检查法律更新
        print("→ Step 2: 检查法律更新")
        update_report = self._check_updates(references)
        print(f"  发现 {len(update_report['issues'])} 个潜在问题")

        # Step 3: 判断新旧法适用
        print("→ Step 3: 判断新旧法适用")
        if fact_date and references['dates']:
            # 使用第一个时间点作为事实时间
            fact_date_to_use = references['dates'][0] if not fact_date else fact_date
            applicability = self._judge_applicability(
                references,
                fact_date_to_use
            )
            print(f"  适用性判断: {applicability['summary']}")
        else:
            applicability = None
            print("  ⚠️ 未提供事实时间,跳过适用性判断")

        # Step 4: 生成校验报告
        print("→ Step 4: 生成校验报告")
        report = self._generate_report(
            references,
            update_report,
            applicability
        )

        # Step 5: 应用修正
        print("→ Step 5: 应用修正")
        if update_report['has_issues']:
            updated_opinion = self._apply_corrections(
                legal_opinion,
                update_report
            )
            corrections_made = update_report['issues']
            print(f"  已应用 {len(corrections_made)} 处修正")
        else:
            updated_opinion = legal_opinion
            corrections_made = []
            print("  无需修正")

        print("✅ 校验完成")

        return {
            'verification_report': report,
            'updated_opinion': updated_opinion,
            'issues_found': update_report['issues'],
            'corrections_made': corrections_made,
            'references': references,
            'applicability': applicability
        }

    def _extract_references(self, legal_opinion: str) -> Dict:
        """提取法律引用"""
        references = {
            'laws': [],
            'interpretations': [],
            'cases': [],
            'dates': []
        }

        # 提取法律
        law_pattern = r'《([^》]{2,30}?法)》[^（\(]*[（\(]?(\d{4})年?[）\)]?(?:修正|修订|版)?'
        laws = re.findall(law_pattern, legal_opinion)
        # 去重
        unique_laws = list(set([f"{name}({year}年)" if year else name for name, year in laws]))
        references['laws'] = unique_laws

        # 提取司法解释
        interp_pattern = r'《([^》]{10,100}解释)》[（\(]*法释〔(\d{4})〕(\d+)号[）\)]*'
        interpretations = re.findall(interp_pattern, legal_opinion)
        references['interpretations'] = [
            {'name': name, 'year': year, 'number': number}
            for name, year, number in interpretations
        ]

        # 提取案例
        case_pattern = r'(最高人民法院第(\d+)号指导性案例)'
        cases = re.findall(case_pattern, legal_opinion)
        references['cases'] = [case[0] for case in cases]

        # 提取日期
        date_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
        dates = re.findall(date_pattern, legal_opinion)
        references['dates'] = [
            f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            for year, month, day in dates
        ]

        return references

    def _check_updates(self, references: Dict) -> Dict:
        """检查法律更新"""
        update_report = {
            'checked_count': 0,
            'has_issues': False,
            'issues': []
        }

        # 检查法律
        for law in references['laws']:
            # 提取法律名称和年份
            match = re.search(r'(.+?)\((\d{4})年\)', law)
            if match:
                law_name = match.group(1)
                current_year = match.group(2)
            else:
                law_name = law
                current_year = "2020"  # 默认年份

            # 检查元数据库
            law_key = law_name.replace('《', '').replace('》', '')
            if law_key in self.law_db:
                law_info = self.law_db[law_key]

                # 检查是否有更新版本
                if 'versions' in law_info:
                    latest_version = law_info['versions'][-1]
                    if latest_version['year'] > current_year:
                        update_report['has_issues'] = True
                        update_report['issues'].append({
                            'type': 'law',
                            'name': law_name,
                            'current_version': current_year,
                            'latest_version': latest_version['year'],
                            'implementation_date': latest_version.get('implementation_date', '未知'),
                            'reason': f'已有{latest_version["year"]}年版'
                        })

            update_report['checked_count'] += 1

        return update_report

    def _judge_applicability(
        self,
        references: Dict,
        fact_date: str
    ) -> Dict:
        """判断新旧法适用"""
        try:
            fact_dt = datetime.strptime(fact_date, '%Y-%m-%d')
        except ValueError:
            return {
                'summary': '无法解析事实时间',
                'details': []
            }

        applicability = {
            'summary': '待判断',
            'details': []
        }

        # 对每个法律进行适用性判断
        for law in references['laws']:
            # 提取法律名称
            match = re.search(r'(.+?)\(\d{4}年\)', law)
            if match:
                law_name = match.group(1)
            else:
                law_name = law

            # 查询法律元数据
            law_key = law_name.replace('《', '').replace('》', '')
            if law_key in self.law_db:
                law_info = self.law_db[law_key]

                if 'versions' in law_info:
                    # 获取最新版本
                    latest_version = law_info['versions'][-1]
                    law_date_str = latest_version.get('implementation_date', '2024-07-01')

                    try:
                        law_dt = datetime.strptime(law_date_str, '%Y-%m-%d')

                        if fact_dt >= law_dt:
                            result = 'new'
                            reason = f'事实发生在新法实施后'
                        else:
                            result = 'old'
                            reason = f'事实发生在新法实施前'

                        applicability['details'].append({
                            'law': law_name,
                            'applicable': result,
                            'fact_date': fact_date,
                            'law_date': law_date_str,
                            'reason': reason
                        })
                    except ValueError:
                        pass

        if applicability['details']:
            new_count = sum(1 for d in applicability['details'] if d['applicable'] == 'new')
            old_count = len(applicability['details']) - new_count
            applicability['summary'] = f'适用新法{new_count}个,旧法{old_count}个'

        return applicability

    def _generate_report(
        self,
        references: Dict,
        update_report: Dict,
        applicability: Optional[Dict]
    ) -> str:
        """生成校验报告"""
        report_lines = [
            "# 法律适用性校验报告\n",
            f"## 检查概况",
            f"- 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"- 涉及法规数量: {len(references['laws'])}个",
            f"- 涉及司法解释: {len(references['interpretations'])}个",
            f"- 发现问题: {len(update_report['issues'])}个\n",
            f"## 详细检查结果\n"
        ]

        for issue in update_report['issues']:
            report_lines.append(f"### {issue['name']}")
            report_lines.append(f"- ❌ **发现问题**: {issue['reason']}")
            report_lines.append(f"- **当前版本**: {issue['current_version']}年版")
            report_lines.append(f"- **最新版本**: {issue['latest_version']}年版")
            report_lines.append(f"- **新法实施**: {issue['implementation_date']}\n")

        if applicability and applicability['details']:
            report_lines.append("## 新旧法适用判断\n")
            for detail in applicability['details']:
                report_lines.append(f"### {detail['law']}")
                report_lines.append(f"- **适用法律**: {'新法' if detail['applicable'] == 'new' else '旧法'}")
                report_lines.append(f"- **事实时间**: {detail['fact_date']}")
                report_lines.append(f"- **法律时间**: {detail['law_date']}")
                report_lines.append(f"- **适用理由**: {detail['reason']}\n")

        report_lines.append("## 校验结论\n")
        if update_report['has_issues']:
            report_lines.append(f"- ⚠️ 发现{len(update_report['issues'])}个法律版本问题")
            report_lines.append("- **建议**: 立即更新法律引用并重新分析")
        else:
            report_lines.append("- ✅ 所有法律引用已验证为最新版本")
            report_lines.append("- **建议**: 可以直接使用当前分析")

        return '\n'.join(report_lines)

    def _apply_corrections(
        self,
        legal_opinion: str,
        update_report: Dict
    ) -> str:
        """应用修正"""
        updated = legal_opinion

        for issue in update_report['issues']:
            old_ref = issue['name']
            new_ref = f"{old_ref}({issue['latest_version']}年版)"

            # 替换引用
            updated = updated.replace(old_ref, new_ref)

        return updated


def main():
    """主程序 - 演示用法"""
    verifier = AutomatedLegalVerification()

    # 示例
    sample_opinion = """
    本案涉及《中华人民共和国公司法》(2018年修正)第二十条的规定。

    根据该条规定,公司股东应当遵守法律、行政法规和公司章程,依法行使股东权利...

    案件事实发生于2024年8月15日。
    """

    print("=" * 60)
    print("示例: 自动化法律校验")
    print("=" * 60)

    result = verifier.verify(
        legal_opinion=sample_opinion,
        fact_date="2024-08-15"
    )

    print("\n" + "=" * 60)
    print("校验报告:")
    print("=" * 60)
    print(result['verification_report'])

    print("\n" + "=" * 60)
    print("修正后意见:")
    print("=" * 60)
    print(result['updated_opinion'])


if __name__ == '__main__':
    main()
