#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强法律检索工具

集成多种检索源：
1. Gety MCP - 本地文档库检索
2. Unifuncs - Web 搜索和页面提取
3. 官方数据库 - 补充检索

作者：china-lawyer-analyst 项目组
版本：v1.0.0
最后更新：2026-01-16
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedRetrieval:
    """增强法律检索器"""

    def __init__(self, config_path="tools/monitor/config.yml"):
        """初始化检索器"""
        self.config = self._load_config(config_path)
        self.results_cache = {}

    def _load_config(self, config_path):
        """加载配置文件"""
        import yaml
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def search(self, query, sources=None, max_results=10):
        """
        综合检索

        Args:
            query: 检索关键词
            sources: 指定检索源，None表示使用所有源
            max_results: 最大结果数

        Returns:
            dict: {
                'gety': [...],      # Gety检索结果
                'unifuncs': [...],  # Unifuncs检索结果
                'official': [...],  # 官方数据库结果
                'merged': [...]      # 合并去重后的结果
            }
        """
        logger.info(f"开始综合检索：{query}")

        results = {
            'gety': [],
            'unifuncs': [],
            'official': [],
            'merged': []
        }

        # 1. Gety MCP 检索（本地文档）
        if self._is_source_enabled('gety', sources):
            logger.info("→ Gety MCP 检索")
            results['gety'] = self._search_gety(query, max_results)

        # 2. Unifuncs 检索（Web搜索）
        if self._is_source_enabled('unifuncs', sources):
            logger.info("→ Unifuncs Web 检索")
            results['unifuncs'] = self._search_unifuncs(query, max_results)

        # 3. 官方数据库检索（补充）
        if self._is_source_enabled('official', sources):
            logger.info("→ 官方数据库检索")
            results['official'] = self._search_official(query, max_results)

        # 4. 合并去重
        results['merged'] = self._merge_results(results)

        logger.info(f"✅ 检索完成，共 {len(results['merged'])} 条结果")
        return results

    def _is_source_enabled(self, source, sources):
        """检查检索源是否启用"""
        if sources is None:
            # 使用所有源
            return True
        return source in sources

    def _search_gety(self, query, max_results):
        """
        Gety MCP 本地检索

        Args:
            query: 检索关键词
            max_results: 最大结果数

        Returns:
            list: 检索结果
        """
        try:
            # 注意：这里需要实际的 MCP 集成
            # 以下是模拟调用，实际使用时需要替换为真实的 MCP 调用

            results = []

            # 模拟调用：mcp__gety__Search
            # 实际代码示例：
            # from mcp import gety
            # search_results = gety.Search(
            #     query=query,
            #     limit=max_results,
            #     connector_names_filter=self.config.get('gety', {}).get('connectors', []),
            #     semantic_search=True
            # )

            # 模拟数据（实际使用时删除）
            mock_results = [
                {
                    'title': f'{query}相关文档',
                    'connector': 'Folder: 法律文档',
                    'snippet': f'找到关于{query}的相关内容...',
                    'relevance': 0.95,
                    'source': 'gety'
                }
            ]
            results.extend(mock_results)

            logger.info(f"  Gety: 找到 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"  Gety 检索失败: {e}")
            return []

    def _search_unifuncs(self, query, max_results):
        """
        Unifuncs Web 搜索

        Args:
            query: 检索关键词
            max_results: 最大结果数

        Returns:
            list: 检索结果
        """
        try:
            results = []

            # 注意：这里需要实际的 MCP 集成
            # 以下是模拟调用，实际使用时需要替换为真实的 MCP 调用

            # 模拟调用：mcp__unifuncs__web-search
            # 实际代码示例：
            # from mcp import unifuncs
            # search_results = unifuncs.web_search(
            #     query=query,
            #     count=max_results,
            #     freshness=self.config.get('unifuncs', {}).get('freshness', 'Month'),
            #     format='markdown'
            # )

            # 模拟数据（实际使用时删除）
            mock_results = [
                {
                    'title': f'{query} - 最新司法解释',
                    'url': f'https://www.court.gov.cn/{query}.html',
                    'snippet': f'关于{query}的最新规定...',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'source': 'unifuncs'
                }
            ]
            results.extend(mock_results)

            logger.info(f"  Unifuncs: 找到 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"  Unifuncs 检索失败: {e}")
            return []

    def _search_official(self, query, max_results):
        """
        官方数据库检索

        检索用户提供的12个权威数据库

        Args:
            query: 检索关键词
            max_results: 最大结果数

        Returns:
            list: 检索结果
        """
        results = []

        # 官方数据库列表
        databases = [
            {
                'name': '国家法律法规数据库',
                'url': 'https://flk.npc.gov.cn',
                'search_url': f'https://flk.npc.gov.cn/api?keyword={query}'
            },
            {
                'name': '最高人民法院官网',
                'url': 'http://www.court.gov.cn',
                'search_url': f'http://www.court.gov.cn/search?q={query}'
            },
            {
                'name': '中国裁判文书网',
                'url': 'https://wenshu.court.gov.cn',
                'search_url': f'https://wenshu.court.gov.cn/search?query={query}'
            }
        ]

        for db in databases:
            try:
                # 这里可以添加实际的检索逻辑
                # 由于大部分官方数据库不支持API或需要登录，
                # 这里主要提供搜索链接，建议用户手动访问

                result = {
                    'title': f'{query} - {db["name"]}',
                    'url': db['search_url'],
                    'snippet': f'访问{db["name"]}检索{query}',
                    'source': 'official',
                    'database': db['name']
                }
                results.append(result)

            except Exception as e:
                logger.warning(f'  {db["name"]} 检索失败: {e}')
                continue

        logger.info(f"  官方数据库: 找到 {len(results)} 个检索入口")
        return results

    def _merge_results(self, results):
        """
        合并去重结果

        Args:
            results: 所有检索结果

        Returns:
            list: 合并去重后的结果
        """
        import hashlib

        seen = {}
        merged = []

        # 按优先级合并：gety > unifuncs > official
        priority_order = ['gety', 'unifuncs', 'official']

        for source in priority_order:
            for item in results.get(source, []):
                # 生成唯一标识（基于标题）
                title = item.get('title', '')
                title_hash = hashlib.md5(title.encode()).hexdigest()

                if title_hash not in seen:
                    seen[title_hash] = True
                    item['merged_at'] = datetime.now().isoformat()
                    merged.append(item)

        # 按相关性排序
        merged.sort(key=lambda x: x.get('relevance', 0), reverse=True)

        return merged

    def check_latest_law(self, query, current_version=None):
        """
        检查是否有更新的法规

        Args:
            query: 检索关键词（如"保证方式"）
            current_version: 当前模块版本（如"2020"）

        Returns:
            dict: {
                'has_update': bool,
                'latest_version': str,
                'new_regulations': list,
                'recommendation': str
            }
        """
        logger.info(f"检查最新法规：{query}（当前版本：{current_version}）")

        # 执行检索
        results = self.search(
            query,
            sources=['unifuncs', 'official'],
            max_results=5
        )

        # 提取年份信息
        import re
        latest_year = None
        new_regulations = []

        for item in results['merged']:
            title = item.get('title', '')
            year_match = re.search(r'20(\d{2})', title)
            if year_match:
                year = int(year_match.group(0))
                if latest_year is None or year > latest_year:
                    latest_year = year

                # 如果比当前版本新，添加到列表
                if current_version:
                    try:
                        current_year = int(current_version[:4])
                        if year > current_year:
                            new_regulations.append(item)
                    except ValueError:
                        pass

        # 判断是否需要更新
        has_update = len(new_regulations) > 0

        result = {
            'has_update': has_update,
            'latest_version': str(latest_year) if latest_year else current_version,
            'new_regulations': new_regulations,
            'query': query,
            'current_version': current_version,
            'checked_at': datetime.now().isoformat()
        }

        if has_update:
            result['recommendation'] = (
                f"⚠️ 发现更新的法规：{query}（{latest_year}年版）\n"
                f"建议：\n"
                f"1. 查看最新法规内容\n"
                f"2. 更新司法解释模块\n"
                f"3. 验证新旧法差异"
            )
            logger.warning(f"✅ 发现更新：{latest_year} > {current_version}")
        else:
            result['recommendation'] = f"✅ 当前版本（{current_version}）已是最新"
            logger.info("✅ 当前版本已是最新")

        return result

    def search_cases(self, keyword, court_level=None, date_range=None, max_results=5):
        """
        检索相关案例

        Args:
            keyword: 关键词
            court_level: 法院层级（最高人民法院、高级人民法院等）
            date_range: 时间范围（如"2023-2024"）
            max_results: 最大结果数

        Returns:
            list: 案例列表
        """
        logger.info(f"检索案例：{keyword}（法院：{court_level}，时间：{date_range}）")

        results = []

        # 使用 Unifuncs 搜索案例
        query = keyword
        if court_level:
            query += f" {court_level}"
        if date_range:
            query += f" {date_range}"

        search_results = self._search_unifuncs(query, max_results)

        # 过滤出案例相关结果
        for item in search_results:
            if any(word in item.get('title', '').lower() for word in ['案', '判决', '裁定', '法院']):
                results.append(item)

        logger.info(f"找到 {len(results)} 个相关案例")
        return results


def main():
    """主程序（测试用）"""
    retrieval = EnhancedRetrieval()

    # 测试1：综合检索
    print("="*50)
    print("测试1：综合检索")
    print("="*50)
    results = retrieval.search("保证方式约定不明")
    print(f"找到 {len(results['merged'])} 条结果")

    # 测试2：检查最新法规
    print("\n" + "="*50)
    print("测试2：检查最新法规")
    print("="*50)
    update_info = retrieval.check_latest_law("保证方式", current_version="2020")
    print(f"是否有更新：{update_info['has_update']}")
    print(f"推荐：{update_info['recommendation']}")

    # 测试3：检索案例
    print("\n" + "="*50)
    print("测试3：检索案例")
    print("="*50)
    cases = retrieval.search_cases(
        keyword="保证合同纠纷",
        court_level="最高人民法院",
        date_range="2023-2024"
    )
    print(f"找到 {len(cases)} 个相关案例")


if __name__ == '__main__':
    main()
