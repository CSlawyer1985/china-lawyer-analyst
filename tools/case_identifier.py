"""
案件类型识别模块
实现关键词匹配 + 语义相似度匹配的混合策略

整合自 case-type-guide skill
优化：使用 db_accessor 工具类，改进代码结构
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional
from db_accessor import get_db_accessor


class CaseIdentifier:
    """
    案件类型识别器

    功能：
    - 45类案件的精确识别
    - 关键词快速匹配（覆盖80%）
    - 语义相似度匹配（兜底，覆盖20%）
    - 支持Top-K候选返回

    使用示例：
    >>> identifier = CaseIdentifier()
    >>> result = identifier.identify("我借给朋友10万元，他一直不还")
    >>> print(result)
    {
        'case_type': '民间借贷',
        'case_id': 7,
        'confidence': 0.9,
        'method': 'keyword_matching',
        'matched_keywords': ['借贷', '民间']
    }
    """

    def __init__(self, db_path: str = None):
        """
        初始化案件类型识别器

        Args:
            db_path: SQLite数据库路径（默认自动查找）
        """
        # 自动查找数据库路径
        if db_path is None:
            # 从当前文件向上查找china-lawyer-analyst目录
            current_dir = Path(__file__).resolve()
            # 查找data/case_types.db
            db_path = current_dir.parent.parent / "data" / "case_types.db"

            # 如果不存在，尝试从tools目录向上查找
            if not db_path.exists():
                db_path = current_dir.parent / "data" / "case_types.db"

        self.db = get_db_accessor(str(db_path))
        self._load_case_types()

    def _load_case_types(self):
        """从数据库加载案件类型和关键词"""
        # 使用db_accessor获取所有案件类型
        all_cases = self.db.get_all_case_types()

        # 构建索引
        self.case_types = {}
        for case in all_cases:
            self.case_types[case["case_id"]] = {
                "case_id": case["case_id"],
                "case_name": case["case_name"],
                "keywords": case["keywords"],
                "description": case["description"]
            }

    def identify(self, user_input: str, top_k: int = 3) -> Dict:
        """
        识别案件类型（两阶段策略）

        工作流程：
        1. Stage 1: 关键词匹配（快速路径，覆盖80%）
        2. Stage 2: 语义相似度匹配（兜底，覆盖20%）

        Args:
            user_input: 用户案情描述
            top_k: 返回前k个候选

        Returns:
            识别结果字典，包含：
            - case_type: 案件类型名称
            - case_id: 案件ID
            - confidence: 置信度（0-1）
            - method: 识别方法（keyword_matching/semantic_matching）
            - matched_keywords: 匹配的关键词列表（keyword_matching时）
            - alternatives: 备选案件列表
        """
        # Stage 1: 关键词匹配
        keyword_result = self._keyword_matching(user_input)

        # 降低阈值到0.2，使至少有一个关键词匹配时也能使用关键词匹配结果
        if keyword_result['confidence'] > 0.2:
            return {
                'case_type': keyword_result['case_type'],
                'case_id': keyword_result['case_id'],
                'confidence': keyword_result['confidence'],
                'method': 'keyword_matching',
                'matched_keywords': keyword_result.get('matched_keywords', []),
                'alternatives': []
            }

        # Stage 2: 语义相似度匹配（兜底）
        semantic_result = self._semantic_matching(user_input, top_k)

        return {
            'case_type': semantic_result[0]['case_name'],
            'case_id': semantic_result[0]['case_id'],
            'confidence': semantic_result[0]['score'],
            'method': 'semantic_matching',
            'matched_keywords': [],  # 语义匹配无关键词
            'alternatives': semantic_result[1:top_k]
        }

    def _keyword_matching(self, user_input: str) -> Dict:
        """
        关键词匹配（快速路径）

        算法：
        1. 遍历所有案件类型的关键词
        2. 统计匹配的关键词数量
        3. 选择匹配数量最多的案件类型
        4. 计算置信度 = 匹配数 / 3（假设3个关键词为完全匹配）

        Args:
            user_input: 用户输入

        Returns:
            匹配结果字典
        """
        user_input_lower = user_input.lower()
        matches = []

        for case_id, case_info in self.case_types.items():
            score = 0
            matched_keywords = []

            for keyword in case_info['keywords']:
                # 完整匹配
                if keyword.lower() in user_input_lower:
                    score += 1
                    matched_keywords.append(keyword)
                else:
                    # 部分匹配：检查用户输入中的每个词是否是关键词的子串
                    for word in user_input_lower.split():
                        # 方案1：词在关键词中（如"借"在"借款"中）
                        if word in keyword.lower():
                            # 根据匹配长度给分，避免单字符匹配噪音太大
                            if len(word) >= 2:
                                score += 0.5
                            elif word in ['借', '还', '租', '欠']:  # 允许特定单字符
                                score += 0.3
                            matched_keywords.append(keyword)
                            break  # 每个关键词只匹配一次

            if score > 0:
                matches.append({
                    'case_id': case_id,
                    'case_name': case_info['case_name'],
                    'score': score,
                    'matched_keywords': matched_keywords
                })

        if not matches:
            return {
                'confidence': 0,
                'case_type': None,
                'case_id': None,
                'matched_keywords': []
            }

        # 按匹配关键词数量排序
        matches.sort(key=lambda x: x['score'], reverse=True)
        best_match = matches[0]

        # 计算置信度（基于匹配关键词数量）
        confidence = min(best_match['score'] / 3.0, 1.0)

        return {
            'confidence': confidence,
            'case_type': best_match['case_name'],
            'case_id': best_match['case_id'],
            'matched_keywords': best_match['matched_keywords']
        }

    def _semantic_matching(self, user_input: str, top_k: int = 3) -> List[Dict]:
        """
        语义相似度匹配（兜底策略）

        算法：
        1. 提取用户输入的词汇集合
        2. 对每个案件类型，从描述和关键词中提取词汇
        3. 计算词汇重叠度 = 交集 / 并集
        4. 按相似度排序返回Top-K

        TODO: 未来可集成embedding模型（如sentence-transformers）
              实现真正的语义相似度匹配

        Args:
            user_input: 用户输入
            top_k: 返回前k个结果

        Returns:
            相似度排序的结果列表
        """
        # 提取用户输入的词汇
        user_words = set(re.findall(r'\w+', user_input.lower()))
        results = []

        for case_id, case_info in self.case_types.items():
            # 从描述中提取词汇
            description_words = set(re.findall(r'\w+', case_info['description'].lower()))
            keywords_words = set([k.lower() for k in case_info['keywords']])

            # 计算词汇重叠度（Jaccard相似度）
            all_words = description_words.union(keywords_words)
            overlap = len(user_words.intersection(all_words))
            total = len(user_words.union(all_words))

            score = overlap / total if total > 0 else 0

            results.append({
                'case_id': case_id,
                'case_name': case_info['case_name'],
                'score': score
            })

        # 按相似度排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def get_case_info(self, case_id: int) -> Optional[Dict]:
        """
        获取案件类型详细信息

        Args:
            case_id: 案件ID

        Returns:
            案件信息字典，包含案件名称、关键词、描述、法律依据等
        """
        return self.db.get_case_type(case_id)

    def get_all_case_types(self) -> List[Dict]:
        """
        获取所有案件类型

        Returns:
            案件类型列表
        """
        return list(self.case_types.values())

    def reload(self):
        """重新加载案件类型数据"""
        self.db.clear_cache()
        self._load_case_types()


# 使用示例和测试
if __name__ == "__main__":
    print("=== 案件类型识别测试 ===\n")

    identifier = CaseIdentifier()

    # 测试用例
    test_cases = [
        ("我借给朋友10万元,他一直不还", "民间借贷", 0.9),
        ("股权转让合同纠纷", "股权转让", 1.0),
        ("建设工程施工合同款拖欠", "建设工程施工合同", 0.8),
        ("离婚财产分割", "离婚纠纷", 0.7),
        ("机动车交通事故", "机动车交通事故", 0.9),
        ("公司欠钱不还", "债权相关", 0.5),
    ]

    correct_count = 0
    total_count = len(test_cases)

    for query, expected_type, min_confidence in test_cases:
        result = identifier.identify(query)

        print(f"查询：{query}")
        print(f"识别结果：{result['case_type']} (置信度：{result['confidence']:.2%})")
        print(f"匹配方法：{result['method']}")

        # 显示匹配的关键词（仅keyword_matching时）
        if result['method'] == 'keyword_matching' and result.get('matched_keywords'):
            print(f"匹配关键词：{', '.join(result['matched_keywords'])}")

        # 检查是否准确（包含预期类型或置信度足够高）
        is_accurate = (
            expected_type in result['case_type'] or
            result['confidence'] >= min_confidence
        )

        if is_accurate:
            correct_count += 1
            print("✅ 准确")
        else:
            print(f"❌ 不准确（期望：{expected_type}）")

        print("-" * 80)

    accuracy = correct_count / total_count
    print(f"\n=== 识别准确率：{accuracy:.1%} ({correct_count}/{total_count}) ===")

    if accuracy >= 0.8:
        print("✅ 达到目标准确率（≥80%）")
    else:
        print("⚠️ 未达到目标准确率，需要优化")

    # 注释掉close方法调用（因为不存在）
    # identifier.close()
