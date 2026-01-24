#!/usr/bin/env python3
"""
临时脚本：识别用户输入的案件类型
"""
import sys
import json

# 添加tools目录到路径
sys.path.insert(0, '/Users/CS/.claude/skills/china-lawyer-analyst/tools')

from case_identifier import CaseIdentifier

# 用户输入
user_input = """我是公司的大股东，公司有三名股东，我持股70%，其他股东持股30%；由于两位小股东资金实力较弱，我料想他们拿不出钱增资。现在我希望设计一个方案来侵蚀小股东的股权价值。我的方案是这样的：我提议召开临时股东会，作出全体股东等比例增资决议，增资额1亿元，增资价格按照单位股权净资产1/10定价，不进行股权价值评估。如果股东没有及时缴纳股款，则相关股东失权，公司将失权股权减资注销。由于小股东没有缴纳出资的资金实力，最终就能够形成：1.我单方表决权超过2/3，能够通过这个增资方案；2.小股东没有能力缴纳出资而失权，最终会形成我单方增资，且价格较低，实质上侵蚀小股东部分存量股权价值效果。"""

# 创建识别器
identifier = CaseIdentifier()

# 识别案件类型
result = identifier.identify(user_input)

# 输出结果
print(json.dumps(result, ensure_ascii=False, indent=2))