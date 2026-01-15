#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速更新检查脚本

在法律分析前快速检查是否有更新的法规

使用方法：
    python3 tools/check_update.py "保证方式"

作者：china-lawyer-analyst 项目组
版本：v1.0.0
最后更新：2026-01-16
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.retrieval.enhanced_retrieval import EnhancedRetrieval


def check_update(keyword, current_version=None):
    """
    检查法规更新

    Args:
        keyword: 关键词（如"保证方式"）
        current_version: 当前版本（如"2020"），可选

    Returns:
        dict: 更新信息
    """
    retrieval = EnhancedRetrieval()

    # 如果没有指定当前版本，尝试从 metadata.json 获取
    if not current_version:
        current_version = guess_current_version(keyword)

    # 检查更新
    update_info = retrieval.check_latest_law(
        query=keyword,
        current_version=current_version
    )

    return update_info


def guess_current_version(keyword):
    """
    根据关键词猜测当前版本

    Args:
        keyword: 关键词

    Returns:
        str: 版本号
    """
    # 简单映射：关键词 → 模块ID → 版本
    keyword_to_module = {
        "保证": "security-law-2020",
        "担保": "security-law-2020",
        "预约": "contract-general-2023",
        "越权": "contract-general-2023",
    }

    for key, module_id in keyword_to_module.items():
        if key in keyword:
            # 从模块ID提取年份
            if "2020" in module_id:
                return "2020"
            elif "2023" in module_id:
                return "2023"

    # 默认返回2020
    return "2020"


def print_update_info(update_info):
    """打印更新信息"""
    print("\n" + "="*50)
    print("法规更新检查")
    print("="*50)

    print(f"\n检索关键词：{update_info['query']}")
    print(f"当前版本：{update_info['current_version']}")
    print(f"检查时间：{update_info['checked_at']}")

    if update_info['has_update']:
        print(f"\n⚠️  发现更新！")
        print(f"最新版本：{update_info.get('latest_version', 'N/A')}")

        if update_info['new_regulations']:
            print(f"\n找到 {len(update_info['new_regulations'])} 条新规定：")

            for i, reg in enumerate(update_info['new_regulations'][:5], 1):
                print(f"\n{i}. {reg.get('title', 'N/A')}")
                print(f"   {reg.get('url', 'N/A')}")
    else:
        print(f"\n✅ 当前版本已是最新")

    print(f"\n建议：\n{update_info['recommendation']}")
    print("="*50)


def main():
    """主程序"""
    if len(sys.argv) < 2:
        print("使用方法：python3 tools/check_update.py <关键词> [当前版本]")
        print("\n示例：")
        print("  python3 tools/check_update.py 保证方式")
        print("  python3 tools/check_update.py 保证方式 2020")
        sys.exit(1)

    keyword = sys.argv[1]
    current_version = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"\n检查更新：{keyword}")

    try:
        update_info = check_update(keyword, current_version)
        print_update_info(update_info)

        # 保存结果到文件
        result_file = Path("tools/update_check_result.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(update_info, f, ensure_ascii=False, indent=2)

        print(f"\n📝 结果已保存到：{result_file.absolute()}")

    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
