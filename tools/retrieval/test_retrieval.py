#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检索工具测试脚本

测试 Gety MCP 和 Unifuncs 集成

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


def test_gety_integration():
    """测试 Gety MCP 集成"""
    print("="*50)
    print("测试 Gety MCP 集成")
    print("="*50)

    retrieval = EnhancedRetrieval()

    # 测试检索
    results = retrieval.search(
        query="保证方式",
        sources=['gety'],
        max_results=3
    )

    print(f"\n✅ Gety 检索结果：")
    print(f"找到 {len(results['gety'])} 条结果")

    for i, result in enumerate(results['gety'], 1):
        print(f"\n{i}. {result.get('title', 'N/A')}")
        print(f"   来源：{result.get('connector', 'N/A')}")
        print(f"   摘要：{result.get('snippet', 'N/A')[:100]}...")

    return len(results['gety']) > 0


def test_unifuncs_integration():
    """测试 Unifuncs 集成"""
    print("\n" + "="*50)
    print("测试 Unifuncs 集成")
    print("="*50)

    retrieval = EnhancedRetrieval()

    # 测试检索
    results = retrieval.search(
        query="担保制度司法解释 2024",
        sources=['unifuncs'],
        max_results=3
    )

    print(f"\n✅ Unifuncs 检索结果：")
    print(f"找到 {len(results['unifuncs'])} 条结果")

    for i, result in enumerate(results['unifuncs'], 1):
        print(f"\n{i}. {result.get('title', 'N/A')}")
        print(f"   链接：{result.get('url', 'N/A')}")
        print(f"   摘要：{result.get('snippet', 'N/A')[:100]}...")

    return len(results['unifuncs']) > 0


def test_official_databases():
    """测试官方数据库检索"""
    print("\n" + "="*50)
    print("测试官方数据库检索")
    print("="*50)

    retrieval = EnhancedRetrieval()

    # 测试检索
    results = retrieval.search(
        query="预约合同",
        sources=['official'],
        max_results=5
    )

    print(f"\n✅ 官方数据库检索结果：")
    print(f"找到 {len(results['official'])} 个检索入口")

    for i, result in enumerate(results['official'], 1):
        print(f"\n{i}. {result.get('database', 'N/A')}")
        print(f"   标题：{result.get('title', 'N/A')}")
        print(f"   搜索链接：{result.get('url', 'N/A')}")

    return len(results['official']) > 0


def test_check_latest_law():
    """测试检查最新法规"""
    print("\n" + "="*50)
    print("测试检查最新法规")
    print("="*50)

    retrieval = EnhancedRetrieval()

    # 测试1：有更新的情况
    print("\n【测试1】检查是否有更新（当前版本：2019）")
    update_info = retrieval.check_latest_law(
        query="保证方式",
        current_version="2019"
    )

    print(f"是否有更新：{'是' if update_info['has_update'] else '否'}")
    print(f"最新版本：{update_info.get('latest_version', 'N/A')}")
    print(f"推荐：\n{update_info.get('recommendation', 'N/A')}")

    # 测试2：当前已是最新
    print("\n【测试2】检查是否有更新（当前版本：2024）")
    update_info = retrieval.check_latest_law(
        query="保证方式",
        current_version="2024"
    )

    print(f"是否有更新：{'是' if update_info['has_update'] else '否'}")
    print(f"推荐：{update_info.get('recommendation', 'N/A')}")

    return True


def test_comprehensive_search():
    """测试综合检索"""
    print("\n" + "="*50)
    print("测试综合检索（所有源）")
    print("="*50)

    retrieval = EnhancedRetrieval()

    # 综合检索
    results = retrieval.search(
        query="越权代表",
        sources=None,  # 使用所有源
        max_results=10
    )

    print(f"\n✅ 综合检索结果：")
    print(f"- Gety: {len(results['gety'])} 条")
    print(f"- Unifuncs: {len(results['unifuncs'])} 条")
    print(f"- 官方数据库: {len(results['official'])} 条")
    print(f"- 合并去重后: {len(results['merged'])} 条")

    print("\n合并结果（Top 5）：")
    for i, result in enumerate(results['merged'][:5], 1):
        print(f"\n{i}. {result.get('title', 'N/A')}")
        print(f"   来源：{result.get('source', 'N/A')}")
        print(f"   相关性：{result.get('relevance', 0):.2f}")

    return len(results['merged']) > 0


def main():
    """运行所有测试"""
    print("\n" + "="*50)
    print("增强检索工具测试套件")
    print("="*50)

    tests = [
        ("Gety MCP 集成", test_gety_integration),
        ("Unifuncs 集成", test_unifuncs_integration),
        ("官方数据库检索", test_official_databases),
        ("检查最新法规", test_check_latest_law),
        ("综合检索", test_comprehensive_search),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = "✅ 通过" if success else "❌ 失败"
        except Exception as e:
            results[test_name] = f"❌ 错误: {e}"
            import traceback
            traceback.print_exc()

    # 汇总
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)

    for test_name, result in results.items():
        print(f"{test_name}: {result}")

    # 统计
    passed = sum(1 for r in results.values() if "通过" in r)
    total = len(results)

    print(f"\n总计：{passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查配置和MCP服务器状态")


if __name__ == '__main__':
    main()
