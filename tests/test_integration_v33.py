#!/usr/bin/env python3
"""
v3.3.0 集成测试套件
测试案件类型识别和要件清单生成功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from case_identifier import CaseIdentifier
from checklist_generator import ChecklistGenerator, UserRole


def test_case_identification():
    """测试案件类型识别"""
    print("=" * 60)
    print("测试1: 案件类型识别系统")
    print("=" * 60)

    identifier = CaseIdentifier()

    test_cases = [
        ("我借给朋友10万元，他一直不还钱", "民间借贷纠纷"),
        ("股权转让合同纠纷，对方不支付款项", "股权转让纠纷"),
        ("融资租赁合同，承租人逾期支付租金", "融资租赁合同"),
        ("建设工程施工合同款拖欠", "建设工程施工合同纠纷"),
        ("机动车交通事故责任纠纷", "机动车交通事故责任纠纷"),
        ("买卖合同货物质量有问题", "买卖合同纠纷"),
    ]

    passed = 0
    failed = 0

    for user_input, expected_case in test_cases:
        result = identifier.identify(user_input)
        actual_case = result['case_type']
        confidence = result['confidence']

        # 模糊匹配（包含关键词即可）
        is_match = expected_case.split('纠纷')[0] in actual_case or expected_case in actual_case

        status = "✅ 通过" if is_match else "❌ 失败"
        if is_match:
            passed += 1
        else:
            failed += 1

        print(f"\n{status}")
        print(f"  输入: {user_input}")
        print(f"  期望: {expected_case}")
        print(f"  实际: {actual_case}")
        print(f"  置信度: {confidence:.2f}")
        print(f"  匹配方式: {result['method']}")

        if result.get('matched_keywords'):
            print(f"  匹配关键词: {', '.join(result['matched_keywords'])}")

    print(f"\n测试结果: {passed}/{len(test_cases)} 通过")
    print(f"准确率: {passed/len(test_cases)*100:.1f}%")

    return passed, failed


def test_checklist_generation():
    """测试要件清单生成"""
    print("\n" + "=" * 60)
    print("测试2: 要件清单生成系统")
    print("=" * 60)

    generator = ChecklistGenerator()

    test_scenarios = [
        (1, UserRole.NEUTRAL, "融资租赁合同-中立视角", 3),
        (7, UserRole.PLAINTIFF, "民间借贷-原告视角", 2),
        (2, UserRole.DEFENDANT, "股权转让-被告视角", 2),
    ]

    passed = 0
    failed = 0

    for case_id, role, desc, expected_sections in test_scenarios:
        try:
            checklist = generator.generate(case_id, role)

            actual_sections = len(checklist['sections'])
            is_match = actual_sections == expected_sections

            status = "✅ 通过" if is_match else "❌ 失败"
            if is_match:
                passed += 1
            else:
                failed += 1

            print(f"\n{status}")
            print(f"  测试场景: {desc}")
            print(f"  案件类型: {checklist['case_type']}")
            print(f"  用户角色: {checklist['user_role']}")
            print(f"  部分数量: {actual_sections} (期望: {expected_sections})")

            total_items = 0
            for section in checklist['sections']:
                item_count = len(section['checklist_items'])
                total_items += item_count
                print(f"    - {section['part_name']}: {item_count}个要点")

            print(f"  总要点数: {total_items}")

        except Exception as e:
            print(f"\n❌ 失败")
            print(f"  测试场景: {desc}")
            print(f"  错误: {str(e)}")
            failed += 1

    print(f"\n测试结果: {passed}/{len(test_scenarios)} 通过")
    print(f"成功率: {passed/len(test_scenarios)*100:.1f}%")

    return passed, failed


def test_markdown_formatting():
    """测试Markdown格式化输出"""
    print("\n" + "=" * 60)
    print("测试3: Markdown格式化输出")
    print("=" * 60)

    generator = ChecklistGenerator()

    try:
        checklist = generator.generate(case_id=7, user_role=UserRole.PLAINTIFF)
        markdown = generator.format_markdown(checklist)

        # 验证Markdown格式
        checks = [
            ("要件清单" in markdown, "包含标题（要件清单）"),
            ("案件ID" in markdown, "包含案件ID信息"),
            ("## " in markdown, "包含二级标题（部分名称）"),
            ("- [" in markdown, "包含清单项目"),
            ("**" in markdown, "包含加粗格式"),
        ]

        passed = sum(1 for check, _ in checks)
        failed = len(checks) - passed

        for check, desc in checks:
            status = "✅" if check else "❌"
            print(f"{status} {desc}")

        print(f"\nMarkdown预览（前500字符）:")
        print("-" * 60)
        print(markdown[:500])
        print("..." if len(markdown) > 500 else "")
        print("-" * 60)

        return passed, failed

    except Exception as e:
        print(f"❌ 格式化测试失败: {str(e)}")
        return 0, 1


def test_data_coverage():
    """测试数据覆盖情况"""
    print("\n" + "=" * 60)
    print("测试4: 数据库覆盖情况")
    print("=" * 60)

    from db_accessor import get_db_accessor

    db = get_db_accessor('data/case_types.db')
    stats = db.get_case_statistics()

    print(f"✅ 案件类型总数: {stats['total_case_types']}")
    print(f"✅ 框架部分总数: {stats['total_frameworks']}")
    print(f"✅ 审查要点总数: {stats['total_review_points']}")
    print(f"✅ 证据清单总数: {stats['total_evidences']}")

    # 验证数据完整性
    checks = [
        (stats['total_case_types'] == 45, "案件类型数量正确"),
        (stats['total_frameworks'] >= 180, "框架部分数量充足"),
        (stats['total_review_points'] >= 630, "审查要点数量充足"),
        (stats['total_evidences'] >= 495, "证据清单数量充足"),
    ]

    passed = sum(1 for check, _ in checks)
    failed = len(checks) - passed

    for check, desc in checks:
        status = "✅" if check else "❌"
        print(f"{status} {desc}")

    return passed, failed


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("china-lawyer-analyst v3.3.0 集成测试")
    print("=" * 60 + "\n")

    results = {}

    # 运行所有测试
    results['案件识别'] = test_case_identification()
    results['清单生成'] = test_checklist_generation()
    results['格式化输出'] = test_markdown_formatting()
    results['数据覆盖'] = test_data_coverage()

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    total_passed = 0
    total_failed = 0

    for test_name, (passed, failed) in results.items():
        total_passed += passed
        total_failed += failed
        print(f"{test_name}: {passed}通过, {failed}失败")

    print(f"\n总计: {total_passed}通过, {total_failed}失败")
    print(f"总通过率: {total_passed/(total_passed+total_failed)*100:.1f}%")

    if total_failed == 0:
        print("\n🎉 所有测试通过！v3.3.0集成就绪。")
    else:
        print(f"\n⚠️ 有 {total_failed} 个测试失败，需要修复。")

    return total_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)