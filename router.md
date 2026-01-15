# 智能路由系统 (Intelligent Routing System)

---

## 系统概述

本文件定义了 china-lawyer-analyst v2.0 MOE 架构的智能路由系统，用于根据用户问题自动识别法律领域，并按需加载相应的核心模块、领域模块和共享模块。

**版本**: v2.0.0
**最后更新**: 2026-01-15
**作者**: 陈石律师（浙江海泰律师事务所）

---

## 路由架构

```
用户输入问题
      ↓
[关键词匹配]
      ↓
[领域识别]
      ↓
[模块组合决策]
      ↓
[Token预估]
      ↓
加载模块清单
```

---

## 1. 关键词库 (DOMAIN_KEYWORDS)

### 1.1 合同法领域 (contract-law)

**触发关键词**：
- 合同、协议、违约、违约金、解除合同
- 买卖合同、租赁合同、服务合同、技术开发合同
- 合同审查、合同起草、合同纠纷
- 要约、承诺、合同成立、合同效力
- 继续履行、补救措施、赔偿损失

**关键词权重**：
- "合同": 1.0
- "协议": 0.9
- "违约": 0.8
- "违约金": 0.7
- "解除合同": 0.7

**Token估算**: 7,900 tokens

---

### 1.2 侵权法领域 (tort-law)

**触发关键词**：
- 侵权、损害赔偿、过错责任、无过错责任
- 安全保障义务、产品责任、环境污染
- 人身损害、财产损害、精神损害
- 过错推定、举证责任倒置
- 加害行为、损害事实、因果关系
- **新增**：滑倒、摔伤、骨折、烧伤、烫伤
- **新增**：医疗费、误工费、护理费、住院
- **新增**：商场、超市、购物中心、公共场所
- **新增**：警示标识、安全、防护

**关键词权重**：
- "侵权": 1.0
- "损害赔偿": 0.9
- "安全保障义务": 0.8
- "产品责任": 0.8
- "过错责任": 0.7
- **新增**："滑倒": 0.9, "摔伤": 0.9, "骨折": 0.8
- **新增**："医疗费": 0.7, "误工费": 0.7

**Token估算**: 5,500 tokens

---

### 1.3 建设工程领域 (construction-law)

**触发关键词**：
- 建设工程、施工合同、工程款、工程价款
- 工期、质量、验收、保修
- 实际施工人、发包人、承包人、分包人
- 工程价款优先受偿权
- 工期延误、质量责任、竣工验收

**关键词权重**：
- "建设工程": 1.0
- "施工合同": 0.9
- "工程款": 0.8
- "工程价款": 0.8
- "发包人"/"承包人": 0.7

**Token估算**: 4,500 tokens

**特殊规则**: 建设工程问题自动加载合同法领域

---

### 1.4 公司法领域 (corporate-law)

**触发关键词**：
- **优化**：股东、股权、股东大会
- 董事会、监事会、经理、法定代表人
- 股权转让、增资扩股、减资、公司清算
- 公司治理、股东权利、股东代表诉讼
- 法人格否认、公司合并、公司分立
- **新增**：股东会、股权结构、出资

**关键词权重**：
- **优化**："股东": 1.0, "股权": 0.9, "股权转让": 0.9
- "董事会": 0.7, "股东大会": 0.7
- "公司治理": 0.8, "公司清算": 0.8

**Token估算**: 5,000 tokens

**优化说明**：移除过于宽泛的"公司"关键词，避免误触发

---

### 1.5 投融资领域 (investment-law)

**触发关键词**：
- 投资、融资、股权投资、债权融资
- 对赌、估值、反稀释、优先清算
- 担保、保证、抵押、质押
- 投资协议、增资协议、股权转让协议
- 融资租赁、保理、供应链金融

**关键词权重**：
- "投资": 1.0
- "融资": 0.9
- "对赌": 0.8
- "担保": 0.8
- "抵押"/"质押": 0.7

**Token估算**: 4,800 tokens

---

### 1.6 劳动法领域 (labor-law)

**触发关键词**：
- 劳动合同、工资、加班费、经济补偿
- 解除劳动合同、违法解除、工伤
- 社会保险、五险一金
- 劳动争议、劳动仲裁
- 试用期、竞业限制、培训协议

**关键词权重**：
- "劳动合同": 1.0
- "工资": 0.8
- "工伤": 0.9
- "加班费": 0.7
- "解除劳动合同": 0.8

**Token估算**: 4,200 tokens

---

### 1.7 知识产权领域 (ip-law)

**触发关键词**：
- 著作权、版权、商标、专利
- 知识产权、侵权、许可使用
- 商业秘密、反不正当竞争
- 著作权侵权、商标侵权、专利侵权
- 知识产权许可、技术转让
- **新增**：照片、摄影、图片、视频
- **新增**：未经许可、擅自使用、商业广告
- **新增**：版权保护、著作权保护、专利申请
- **新增**：商标注册、原创、署名权

**关键词权重**：
- "著作权"/"版权": 1.0
- "商标": 0.9
- "专利": 0.9
- "知识产权": 1.0
- "商业秘密": 0.8
- **新增**："照片": 0.7, "摄影": 0.8, "未经许可": 0.9
- **新增**："擅自使用": 0.8, "商业广告": 0.7

**Token估算**: 4,500 tokens

**优化说明**：补充照片、摄影等场景关键词，提升识别准确率

---

### 1.8 诉讼仲裁领域 (litigation-arbitration)

**触发关键词**：
- 诉讼、起诉、应诉、管辖
- 证据、举证责任、证明标准
- 上诉、再审、执行
- 仲裁、仲裁条款、仲裁机构
- 财产保全、证据保全、先予执行

**关键词权重**：
- "诉讼": 1.0
- "起诉": 0.9
- "仲裁": 0.9
- "管辖": 0.7
- "证据": 0.8

**Token估算**: 5,200 tokens

**特殊规则**: 诉讼仲裁问题通常与其他领域问题并存，作为补充模块加载

---

## 2. 路由算法

### 2.1 Step 1: 关键词匹配

```python
def route_by_keywords(query: str) -> List[str]:
    """基于关键词匹配识别领域"""

    # 定义关键词库（见上文第1节）
    DOMAIN_KEYWORDS = {
        "contract-law": [...],
        "tort-law": [...],
        "construction-law": [...],
        "corporate-law": [...],
        "investment-law": [...],
        "labor-law": [...],
        "ip-law": [...],
        "litigation-arbitration": [...]
    }

    # 提取用户输入的关键词
    query_keywords = extract_keywords(query)

    # 匹配领域
    detected_domains = []
    domain_scores = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = 0
        matched_keywords = []

        for keyword in keywords:
            if keyword in query:
                weight = get_keyword_weight(keyword)
                score += weight
                matched_keywords.append(keyword)

        if score > 0:
            domain_scores[domain] = score
            detected_domains.append(domain)

    # 按得分排序
    detected_domains.sort(key=lambda x: domain_scores[x], reverse=True)

    return detected_domains
```

---

### 2.2 Step 2: 领域组合逻辑（优化版 v2.0.1）

```python
def determine_module_combination(detected_domains: List[Tuple[str, float]]) -> List[str]:
    """根据检测到的领域确定加载模块组合（优化版）"""

    if not detected_domains:
        # 规则 3: 未识别领域，使用默认配置
        return ["contract-law", "litigation-arbitration"]

    # 提取域名和得分
    domain_names = [d[0] for d in detected_domains]
    max_score = detected_domains[0][1] if detected_domains else 0

    # 优化规则：区分"低置信度单领域"和"真正未识别"
    # 如果只有一个领域，且得分 >= 0.8，视为有效单领域
    # 如果有多个领域，但最高得分 < 1.5，使用默认配置
    if len(domain_names) == 1:
        if max_score >= 0.8:
            # 单领域，置信度足够
            return [domain_names[0]]
        else:
            # 单领域，但置信度太低，使用默认配置
            return ["contract-law", "litigation-arbitration"]
    else:
        # 多领域情况
        if max_score < 1.5:
            # 最高得分太低，使用默认配置
            return ["contract-law", "litigation-arbitration"]

        # **新增**：动态过滤低得分领域
        # 只保留得分 >= max_score * 0.5 的领域（避免加载弱相关领域）
        score_threshold = max_score * 0.5
        filtered_domains = [(d, s) for d, s in detected_domains if s >= score_threshold]
        domain_names = [d[0] for d in filtered_domains]

        # 规则 2: 多领域交叉问题
        result = domain_names.copy()

        # 智能组合：建设工程 → 自动加载合同法
        if "construction-law" in result and "contract-law" not in result:
            result.append("contract-law")

        # 优先级排序
        priority = [
            "construction-law",
            "corporate-law",
            "investment-law",
            "contract-law",
            "tort-law",
            "ip-law",
            "labor-law",
            "litigation-arbitration"
        ]

        result.sort(key=lambda x: priority.index(x) if x in priority else 99)

        return result
```

**优化说明**：
1. **置信度阈值**：单领域得分 >= 0.8 视为有效，否则使用默认模块
2. **动态过滤**：多领域中，只保留得分 >= max_score * 0.5 的领域
3. **避免过度加载**：过滤弱相关领域（如得分 < max_score * 50%）

---

### 2.3 Step 3: 共享模块决策

```python
def determine_shared_modules(query: str) -> List[str]:
    """根据任务需求确定共享模块"""

    shared_modules = []

    # 需要法律检索
    if any(kw in query for kw in ["检索", "查找", "法条", "法律依据", "相关法规"]):
        shared_modules.append("legal-research")

    # 需要文书写作
    if any(kw in query for kw in ["起诉状", "答辩状", "法律意见书", "合同", "协议", "律师函"]):
        shared_modules.append("legal-writing")

    # 需要谈判
    if any(kw in query for kw in ["谈判", "和解", "调解", "协商"]):
        shared_modules.append("negotiation")

    # 需要尽职调查
    if any(kw in query for kw in ["尽职调查", "风险评估", "合规", "审查"]):
        shared_modules.append("due-diligence")

    # 需要数据库指引
    if any(kw in query for kw in ["数据库", "案例库", "裁判文书"]):
        shared_modules.append("databases")

    # 需要合同范本
    if any(kw in query for kw in ["范本", "模板", "样本", "示例"]):
        shared_modules.append("templates")

    # 需要验证工具
    if any(kw in query for kw in ["验证", "检查", "评分", "评估"]):
        shared_modules.extend(["rubric", "checklist", "pitfalls"])

    return shared_modules
```

---

### 2.4 Step 4: Token预估

```python
TOKEN_MAP = {
    # 核心模块（始终加载）
    "philosophy": 2200,
    "foundations-universal": 5600,
    "frameworks-core": 3700,
    "process": 2800,

    # 领域模块（按需加载）
    "contract-law": 7900,
    "tort-law": 5500,
    "construction-law": 4500,
    "corporate-law": 5000,
    "investment-law": 4800,
    "labor-law": 4200,
    "ip-law": 4500,
    "litigation-arbitration": 5200,

    # 共享模块（按需加载）
    "legal-research": 1200,
    "legal-writing": 1300,
    "negotiation": 1700,
    "due-diligence": 1200,
    "databases": 1100,
    "templates": 1200,
    "rubric": 1300,
    "checklist": 1400,
    "pitfalls": 1400
}

def estimate_tokens(core_modules: List[str],
                    domain_modules: List[str],
                    shared_modules: List[str]) -> Dict[str, int]:
    """预估 Token 消耗"""

    total = 0

    # 核心模块（始终加载）
    for module in ["philosophy", "foundations-universal", "frameworks-core", "process"]:
        total += TOKEN_MAP[module]

    # 领域模块
    for module in domain_modules:
        total += TOKEN_MAP[module]

    # 共享模块
    for module in shared_modules:
        total += TOKEN_MAP[module]

    # 计算节省率
    original_tokens = 37958  # v1.0 总 tokens
    reduction_rate = (1 - total / original_tokens) * 100

    return {
        "total_tokens": total,
        "original_tokens": original_tokens,
        "saved_tokens": original_tokens - total,
        "reduction_rate": f"{reduction_rate:.1f}%"
    }
```

---

## 3. 路由示例

### 3.1 示例 1: 单领域问题（合同纠纷）

**用户输入**：
```
甲乙公司签订软件开发合同，约定2023年6月30日前交付。
乙方延迟交付1.5周，且软件存在缺陷。甲方拒绝付款。
```

**路由决策**：
```json
{
  "query_analysis": {
    "detected_keywords": ["合同", "交付", "违约", "拒绝付款"],
    "detected_domains": ["contract-law"]
  },
  "load_list": {
    "core": ["philosophy", "foundations-universal", "frameworks-core", "process"],
    "domains": ["contract-law"],
    "shared": ["legal-writing", "checklist"]
  },
  "token_estimation": {
    "total_tokens": 17800,
    "original_tokens": 37958,
    "saved_tokens": 20158,
    "reduction_rate": "53.1%"
  }
}
```

**透明化反馈**：
```
【系统提示】已识别问题类型：合同纠纷
【加载模块】核心模块（13,800 tokens）+ 合同法领域（7,900 tokens）+ 共享模块（6,100 tokens）
【Token 消耗】17,800 tokens（节省 53.1%）

--- 开始分析 ---
```

---

### 3.2 示例 2: 多领域问题（建设工程 + 合同）

**用户输入**：
```
XX建筑公司与XX房地产公司签订建设工程施工合同，
工程延期2个月竣工，发包人拒绝支付剩余工程款。
```

**路由决策**：
```json
{
  "query_analysis": {
    "detected_keywords": ["建设工程", "施工合同", "工程延期", "发包人", "工程款"],
    "detected_domains": ["construction-law", "contract-law"]
  },
  "load_list": {
    "core": ["philosophy", "foundations-universal", "frameworks-core", "process"],
    "domains": ["construction-law", "contract-law"],
    "shared": ["legal-research", "checklist"]
  },
  "token_estimation": {
    "total_tokens": 26200,
    "original_tokens": 37958,
    "saved_tokens": 11758,
    "reduction_rate": "31.0%"
  }
}
```

**透明化反馈**：
```
【系统提示】已识别问题类型：建设工程纠纷（涉及合同法）
【加载模块】核心模块（13,800 tokens）+ 建设工程领域（4,500 tokens）+ 合同法领域（7,900 tokens）+ 共享模块（0 tokens）
【Token 消耗】26,200 tokens（节省 31.0%）

--- 开始分析 ---
```

---

### 3.3 示例 3: 纯侵权问题

**用户输入**：
```
王某某在XX购物中心购物时，踩到地面水渍滑倒导致右腿骨折，
医疗费5万元、误工费3万元。监控显示地面有水渍、无警示标识。
```

**路由决策**：
```json
{
  "query_analysis": {
    "detected_keywords": ["滑倒", "骨折", "医疗费", "误工费", "警示标识"],
    "detected_domains": ["tort-law"]
  },
  "load_list": {
    "core": ["philosophy", "foundations-universal", "frameworks-core", "process"],
    "domains": ["tort-law"],
    "shared": ["legal-research", "checklist"]
  },
  "token_estimation": {
    "total_tokens": 20400,
    "original_tokens": 37958,
    "saved_tokens": 17558,
    "reduction_rate": "46.3%"
  }
}
```

**透明化反馈**：
```
【系统提示】已识别问题类型：侵权责任纠纷
【加载模块】核心模块（13,800 tokens）+ 侵权法领域（5,500 tokens）+ 共享模块（1,100 tokens）
【Token 消耗】20,400 tokens（节省 46.3%）

--- 开始分析 ---
```

---

## 4. 路由失败处理

### 4.1 未识别领域

**情况**：用户输入不包含任何已知关键词

**处理策略**：
1. 加载默认模块组合：核心模块 + 合同法领域 + 诉讼仲裁领域
2. 在反馈中提示用户："未明确识别问题类型，已加载通用模块"

**示例**：
```
【系统提示】未明确识别问题类型，已加载默认模块（合同法 + 诉讼仲裁）
【建议】您可以手动指定领域，如"请使用合同法模块分析..."
```

---

### 4.2 识别错误

**情况**：路由识别的领域与用户意图不符

**处理策略**：
1. 提供"手动指定领域"选项
2. 用户可以显式指定：`请使用 [领域名称] 模块分析...`

**示例**：
```
用户：请使用侵权法模块分析这个问题...
【系统提示】已手动指定领域：侵权法（tort-law）
【加载模块】核心模块 + 侵权法领域 + 共享模块
```

---

## 5. 性能优化

### 5.1 缓存机制

- **核心模块缓存**：核心模块始终使用，缓存到内存
- **高频领域缓存**：合同法、诉讼仲裁等高频模块缓存
- **缓存失效**：模块更新后清除缓存

### 5.2 并行加载

- 核心模块、领域模块、共享模块并行读取
- 减少 I/O 等待时间

---

## 6. 路由测试用例

### 6.1 单领域问题测试

| 测试用例 | 预期领域 | 预期 Token |
|---------|---------|-----------|
| 软件开发合同纠纷 | contract-law | ~17,800 |
| 商场滑倒摔伤 | tort-law | ~20,400 |
| 股权转让纠纷 | corporate-law | ~21,800 |

### 6.2 多领域问题测试

| 测试用例 | 预期领域 | 预期 Token |
|---------|---------|-----------|
| 建设工程施工合同 + 工程款 | construction-law + contract-law | ~26,200 |
| 公司投资 + 对赌协议 | corporate-law + investment-law | ~25,600 |

---

## 7. 路由准确率指标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| 单领域识别准确率 | >90% | 关键词匹配测试集 |
| 多领域识别准确率 | >85% | 交叉问题测试集 |
| 误识别率 | <5% | 负面测试集 |
| 用户满意度 | >85% | 用户反馈 |

---

## 8. 版本历史

### v2.0.0 (2026-01-15)
- ✅ 初始版本
- ✅ 定义8大领域关键词库
- ✅ 实现路由算法（关键词匹配、领域组合、共享模块决策）
- ✅ 提供3个路由示例
- ✅ 定义路由失败处理机制

---

**版本**: v2.0.0
**最后更新**: 2026-01-15
**作者**: 陈石律师（浙江海泰律师事务所）
**文件路径**: `/Users/CS/Trae/Claude/china-lawyer-analyst/router.md`
