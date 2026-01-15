#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强检索集成示例

展示如何在 china-lawyer-analyst Skill 中集成增强检索工具

作者：china-lawyer-analyst 项目组
版本：v1.0.0
最后更新：2026-01-16
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.retrieval.enhanced_retrieval import EnhancedRetrieval


# ============================================
# 示例 1：基础检索
# ============================================

def example_1_basic_search():
    """示例1：基础综合检索"""
    print("\n" + "="*50)
    print("示例 1：基础综合检索")
    print("="*50)

    retrieval = EnhancedRetrieval()

    # 检索
    results = retrieval.search("预约合同", max_results=5)

    # 显示结果
    print(f"\n找到 {len(results['merged'])} 条结果：")

    for i, item in enumerate(results['merged'][:3], 1):
        print(f"\n{i}. {item.get('title', 'N/A')}")
        print(f"   来源：{item.get('source', 'N/A')}")


# ============================================
# 示例 2：检查法规更新
# ============================================

def example_2_check_update():
    """示例2：检查法规更新"""
    print("\n" + "="*50)
    print("示例 2：检查法规更新")
    print("="*50)

    retrieval = EnhancedRetrieval()

    # 检查是否有更新
    update_info = retrieval.check_latest_law(
        query="保证方式",
        current_version="2020"
    )

    # 显示结果
    print(f"\n当前版本：{update_info['current_version']}")
    print(f"最新版本：{update_info.get('latest_version', 'N/A')}")
    print(f"是否有更新：{'是' if update_info['has_update'] else '否'}")
    print(f"\n推荐：\n{update_info['recommendation']}")


# ============================================
# 示例 3：集成到 Skill 路由系统
# ============================================

def route_with_enhanced_retrieval(query: str):
    """
    集成增强检索的路由系统

    这是如何在 SKILL.md 或 router.md 中集成的示例
    """
    print("\n" + "="*50)
    print("示例 3：集成到 Skill 路由系统")
    print("="*50)

    # Step 1: 原有两级路由（模拟）
    print("\n[Step 1] 两级路由")
    modules = ["核心模块", "投资领域模块", "担保制度索引"]
    print(f"加载模块：{', '.join(modules)}")

    # Step 2: 检查最新法规
    print("\n[Step 2] 检查最新法规")
    retrieval = EnhancedRetrieval()

    # 提取关键词
    keywords = extract_keywords(query)
    print(f"提取关键词：{keywords}")

    # 获取当前版本（模拟）
    current_version = "2020"
    print(f"当前版本：{current_version}")

    # 检查更新
    update_info = retrieval.check_latest_law(
        query=keywords,
        current_version=current_version
    )

    # Step 3: 如果有更新，添加提醒
    if update_info['has_update']:
        print(f"\n⚠️  发现更新！")
        alert = {
            "type": "update_alert",
            "message": update_info['recommendation'],
            "new_regulations": update_info['new_regulations']
        }
        modules.append(alert)
        print(f"添加提醒：{alert['type']}")
    else:
        print(f"\n✅ 当前版本已是最新")

    # Step 4: 如果索引不足，使用增强检索
    print("\n[Step 4] 检查是否需要增强检索")
    if needs_enhanced_retrieval(query):
        print("需要增强检索")

        external_results = retrieval.search(
            query=keywords,
            sources=['unifuncs', 'gety'],
            max_results=3
        )

        print(f"找到 {len(external_results['merged'])} 条外部结果")
        modules.extend(external_results['merged'])
    else:
        print("无需增强检索")

    return modules


def extract_keywords(query: str) -> str:
    """从查询中提取关键词"""
    # 简单示例：提取前两个关键词
    words = query.split()
    return ' '.join(words[:2]) if len(words) > 2 else query


def needs_enhanced_retrieval(query: str) -> bool:
    """判断是否需要增强检索"""
    # 示例：如果查询包含"最新""2024"等词，需要增强检索
    keywords = ['最新', '2024', '2025', '近期', '刚刚发布']
    return any(keyword in query for keyword in keywords)


# ============================================
# 示例 4：检索相关案例
# ============================================

def example_4_search_cases():
    """示例4：检索相关案例"""
    print("\n" + "="*50)
    print("示例 4：检索相关案例")
    print("="*50)

    retrieval = EnhancedRetrieval()

    # 检索案例
    cases = retrieval.search_cases(
        keyword="保证合同纠纷",
        court_level="最高人民法院",
        date_range="2023-2024",
        max_results=3
    )

    # 显示结果
    print(f"\n找到 {len(cases)} 个相关案例：")

    for i, case in enumerate(cases, 1):
        print(f"\n{i}. {case.get('title', 'N/A')}")
        print(f"   链接：{case.get('url', 'N/A')}")


# ============================================
# 主程序
# ============================================

def main():
    """运行所有示例"""
    print("\n" + "="*50)
    print("增强检索工具集成示例")
    print("="*50)

    examples = [
        ("基础检索", example_1_basic_search),
        ("检查更新", example_2_check_update),
        ("Skill集成", lambda: route_with_enhanced_retrieval("保证方式最新规定")),
        ("检索案例", example_4_search_cases),
    ]

    for example_name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ {example_name} 示例失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*50)
    print("示例运行完成")
    print("="*50)


if __name__ == '__main__':
    main()
