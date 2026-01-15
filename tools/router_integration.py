#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成到 router.md 的三级路由增强系统

在现有的两级路由基础上，添加第三级：实时检索增强

使用方法：
在 router.md 中导入此模块，调用 enhanced_route() 函数

作者：china-lawyer-analyst 项目组
版本：v3.1.0
最后更新：2026-01-16
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.retrieval.enhanced_retrieval import EnhancedRetrieval


def enhanced_route_v3(query: str):
    """
    v3.1 三级路由系统（含实时检索增强）

    在原有两级路由基础上，添加第三级检索增强：
    - Level 1: 静态核心 + 基础领域模块
    - Level 2: 司法解释索引
    - Level 3: 实时检索增强（Gety + Unifuncs + 官方数据库）

    Args:
        query: 用户问题

    Returns:
        dict: {
            'modules': list,         # 加载的模块列表
            'update_alert': dict,    # 更新提醒（如有）
            'external_results': list # 外部检索结果（如有）
        }
    """
    result = {
        'modules': [],
        'update_alert': None,
        'external_results': []
    }

    print(f"\n{'='*50}")
    print(f"三级路由系统 v3.1")
    print(f"查询：{query}")
    print(f"{'='*50}")

    # ========== Level 1: 静态核心 + 基础领域 ==========
    print(f"\n[Level 1] 静态核心 + 基础领域模块")

    # 这里应该调用原有的 route_v30() 函数
    # 为了示例，我们模拟加载模块
    core_modules = [
        "core/philosophy.md",
        "core/foundations-universal.md",
        "core/frameworks-core.md",
        "core/process.md"
    ]

    # 识别领域（模拟）
    domain = identify_domain(query)
    if domain:
        domain_module = f"domains/{domain}.md"
        result['modules'].extend(core_modules + [domain_module])
        print(f"  ✓ 加载核心模块（4个）")
        print(f"  ✓ 加载领域模块：{domain_module}")
    else:
        result['modules'].extend(core_modules)
        print(f"  ✓ 加载核心模块（4个）")
        print(f"  ! 未识别到具体领域")

    # ========== Level 2: 司法解释索引 ==========
    print(f"\n[Level 2] 司法解释索引")

    interp_module = identify_interpretation(query)
    if interp_module:
        index_file = f"interpretations/{interp_module}/index.md"
        result['modules'].append(index_file)
        print(f"  ✓ 加载索引：{index_file}")

        # 提取需要的条文
        articles = extract_articles(query, interp_module)
        if articles:
            for article in articles:
                article_file = f"interpretations/{interp_module}/articles/{article}"
                result['modules'].append(article_file)
            print(f"  ✓ 加载条文详解：{len(articles)}个")
    else:
        print(f"  ! 未检测到司法解释需求")

    # ========== Level 3: 实时检索增强 ==========
    print(f"\n[Level 3] 实时检索增强")

    # 判断是否需要增强检索
    needs_enhancement = check_if_needs_enhancement(query)

    if needs_enhancement:
        retrieval = EnhancedRetrieval()

        # 3.1 检查版本更新
        print(f"  → 检查法规更新...")
        keywords = extract_keywords(query)
        current_version = get_current_version(interp_module)

        update_info = retrieval.check_latest_law(
            query=keywords,
            current_version=current_version
        )

        if update_info['has_update']:
            result['update_alert'] = {
                'type': '法规更新提醒',
                'current_version': current_version,
                'latest_version': update_info.get('latest_version'),
                'recommendation': update_info['recommendation'],
                'new_regulations': update_info.get('new_regulations', [])
            }
            print(f"  ⚠️  发现更新：{current_version} → {update_info.get('latest_version')}")
        else:
            print(f"  ✓ 当前版本已是最新（{current_version}）")

        # 3.2 补充检索（如果索引不足）
        if needs_supplement_search(query):
            print(f"  → 补充检索...")

            external_results = retrieval.search(
                query=keywords,
                sources=['unifuncs', 'gety'],
                max_results=3
            )

            if external_results['merged']:
                result['external_results'] = external_results['merged'][:3]
                print(f"  ✓ 找到 {len(result['external_results'])} 条补充结果")
            else:
                print(f"  ! 未找到补充结果")
    else:
        print(f"  ✓ 无需增强检索")

    # ========== 汇总 ==========
    print(f"\n{'='*50}")
    print(f"路由完成")
    print(f"{'='*50}")
    print(f"加载模块：{len(result['modules'])}个")
    print(f"更新提醒：{'是' if result['update_alert'] else '否'}")
    print(f"外部结果：{len(result['external_results'])}条")

    return result


# ========== 辅助函数 ==========

def identify_domain(query: str) -> str:
    """
    识别问题所属的法律领域

    Args:
        query: 用户问题

    Returns:
        str: 领域ID（如 'contract-law', 'investment-law'）
    """
    keywords_domain = {
        'contract-law': ['合同', '违约', '解除合同', '预约合同'],
        'investment-law': ['担保', '保证', '抵押', '质押'],
        'tort-law': ['侵权', '损害赔偿', '人身损害'],
        'corporate-law': ['公司', '股东', '股权'],
        'construction-law': ['建设工程', '施工', '工程款'],
    }

    query_lower = query.lower()

    for domain, keywords in keywords_domain.items():
        if any(keyword in query for keyword in keywords):
            return domain

    return None


def identify_interpretation(query: str) -> str:
    """
    识别需要的司法解释模块

    Args:
        query: 用户问题

    Returns:
        str: 模块ID（如 'security-law-2020'）
    """
    keywords_interp = {
        'security-law-2020': ['保证', '担保', '抵押', '质押', '先诉抗辩权'],
        'contract-general-2023': ['预约合同', '意向书', '越权代表', '违反强制性规定'],
    }

    for interp_id, keywords in keywords_interp.items():
        if any(keyword in query for keyword in keywords):
            return interp_id

    return None


def extract_articles(query: str, interp_id: str) -> list:
    """
    从查询中提取需要的具体条文

    Args:
        query: 用户问题
        interp_id: 司法解释模块ID

    Returns:
        list: 条文文件列表
    """
    # 简化示例：根据关键词映射到条文
    keywords_articles = {
        '保证方式约定不明': ['article-25.md'],
        '相对人善意': ['article-7.md'],
        '抵押财产转让': ['article-37.md'],
        '预约合同认定': ['article-6.md', 'article-7.md'],
    }

    for keyword, articles in keywords_articles.items():
        if keyword in query:
            return articles

    return []


def extract_keywords(query: str) -> str:
    """从查询中提取检索关键词"""
    # 移除常见疑问词
    stopwords = ['如何', '怎么', '什么是', '怎样', '是否', '有没有']

    keywords = query
    for word in stopwords:
        keywords = keywords.replace(word, '')

    # 提取前10个字作为关键词
    return keywords[:10].strip()


def get_current_version(interp_id: str) -> str:
    """
    从模块ID中提取当前版本

    Args:
        interp_id: 模块ID（如 'security-law-2020'）

    Returns:
        str: 版本号（如 '2020'）
    """
    if interp_id and '-' in interp_id:
        return interp_id.split('-')[-1]
    return "2020"  # 默认版本


def check_if_needs_enhancement(query: str) -> bool:
    """
    判断是否需要增强检索

    Args:
        query: 用户问题

    Returns:
        bool: 是否需要增强检索
    """
    # 如果查询包含"最新""2024""2025"等关键词，需要增强检索
    enhancement_keywords = ['最新', '2024', '2025', '近期', '刚刚发布', '新规定']

    return any(keyword in query for keyword in enhancement_keywords)


def needs_supplement_search(query: str) -> bool:
    """
    判断是否需要补充检索

    Args:
        query: 用户问题

    Returns:
        bool: 是否需要补充检索
    """
    # 如果问题很长或很具体，可能需要补充检索
    return len(query) > 50 or '案例' in query or '实务' in query


# ========== 使用示例 ==========

def example_usage():
    """使用示例"""
    print("\n" + "="*50)
    print("三级路由系统使用示例")
    print("="*50)

    # 示例1：常规问题（无需增强检索）
    print("\n【示例1】常规问题")
    result1 = enhanced_route_v3("甲乙公司签订保证合同，未约定保证方式")

    # 示例2：需要检查更新的问题
    print("\n【示例2】检查更新")
    result2 = enhanced_route_v3("2024年最新的保证方式规定是什么")

    if result2['update_alert']:
        print(f"\n⚠️  更新提醒：")
        print(f"{result2['update_alert']['recommendation']}")


if __name__ == '__main__':
    example_usage()
