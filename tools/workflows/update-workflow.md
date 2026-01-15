# 司法解释更新工作流程

---

## 工作流程概述

本工作流程定义了司法解释模块从发现、生成、审核到部署的完整流程，确保更新高效、质量可控。

**流程图**：
```
发现新司法解释
    ↓
【步骤1】AI生成初稿（0.5小时）
    ↓
【步骤2】人工审核修改（0.5小时）
    ↓
【步骤3】验证测试（0.2小时）
    ↓
【步骤4】部署上线（0.1小时）
    ↓
总计：约1小时（相比v2.2的8小时，节省87.5%）
```

---

## 步骤1：AI生成初稿

### 1.1 触发条件

**自动触发**：
- 监测工具发现新司法解释（tools/monitor/court-monitor.py）
- 每周一 9:00 AM 自动运行

**手动触发**：
- 用户手动发现新司法解释
- 用户提交 Feature Request

### 1.2 生成流程

**方式1：使用自动化工具（推荐）**

```bash
# 1. 确认待处理队列
cat queue.json

# 2. 运行生成工具
cd tools/generator
python draft-generator.py --queue

# 3. 查看生成结果
ls draft/
```

**方式2：使用模板手动创建**

```bash
# 1. 复制模板
cp -r interpretations/_template interpretations/{new-id}

# 2. 修改文件
cd interpretations/{new-id}
# 编辑 README.md、index.md、metadata.json、external-links.md

# 3. 创建条文详解（可选）
mkdir articles
# 根据需要创建 article-{number}.md
```

### 1.3 输出物

- `draft/{id}/README.md`：模块概要
- `draft/{id}/index.md`：条文索引
- `draft/{id}/metadata.json`：元数据
- `draft/{id}/external-links.md`：外部链接
- `draft/{id}/articles/article-{number}.md`：条文详解

**预计耗时**：30分钟

---

## 步骤2：人工审核修改

### 2.1 审核清单

使用 `tools/workflows/review-checklist.md` 进行审核：

**第一层：结构验证（自动）**
- [ ] 文件结构完整
- [ ] JSON格式正确
- [ ] 命名规范符合

**第二层：内容验证（AI辅助+人工）**
- [ ] 法律准确性
- [ ] 内容完整性
- [ ] Token优化

**第三层：人工审核（最终把关）**
- [ ] 深度分析能力
- [ ] 实用性
- [ ] 可维护性

### 2.2 常见修改

**修改1：条文解读不准确**
- 重新核对官方文本
- 参考权威解读
- 修改条文详解

**修改2：新旧法对比不完整**
- 补充旧法内容
- 完善对比分析
- 说明变化影响

**修改3：Token超标**
- 精简冗余内容
- 删除重复信息
- 保留核心要点

**修改4：深度分析不足**
- 补充实务案例
- 增加争议焦点讨论
- 提供实务建议

### 2.3 质量标准

**及格标准**：
- ⭐⭐⭐ 内容准确性达标
- ⭐⭐⭐⭐ 深度分析基本达标
- Token消耗符合标准

**优秀标准**：
- ⭐⭐⭐⭐⭐ 内容准确无误
- ⭐⭐⭐⭐⭐ 深度分析优秀
- Token消耗显著低于标准

**预计耗时**：30分钟

---

## 步骤3：验证测试

### 3.1 自动化验证

**结构验证**：
```bash
python tools/validator/structure-check.py --id {module-id}
```

**Token统计**：
```bash
python tools/validator/token-count.py --id {module-id}
```

**综合验证**：
```bash
python tools/validator/validate.py --id {module-id} --full
```

### 3.2 手动测试

**测试场景1：快速查询**
```
问题：{典型问题}
操作：加载 index.md → 查找条文
验证：能否快速定位？
```

**测试场景2：深度分析**
```
问题：{具体问题}
操作：加载 index.md + article-{number}.md
验证：内容是否足够深入？
```

**测试场景3：外部检索**
```
需求：需要条文全文
操作：访问 external-links.md 的数据源
验证：链接是否有效？
```

### 3.3 测试记录

```markdown
## 测试记录

**模块ID**：{id}
**测试日期**：YYYY-MM-DD
**测试人**：{name}

### 测试场景
- [ ] 场景1：快速查询 - [ ] 通过 / [ ] 失败
- [ ] 场景2：深度分析 - [ ] 通过 / [ ] 失败
- [ ] 场景3：外部检索 - [ ] 通过 / [ ] 失败

### 问题记录
- {问题1}
- {问题2}

### 修复建议
- {建议1}
- {建议2}
```

**预计耗时**：12分钟

---

## 步骤4：部署上线

### 4.1 部署流程

**1. 移动到正式目录**
```bash
# 从 draft/ 移动到 interpretations/
mv draft/{id} interpretations/{id}
```

**2. 更新全局索引**
```bash
# 更新 interpretations/metadata.json
# 添加新模块到 interpretations 列表
```

**3. 更新路由系统**
```bash
# 更新 router.md（如果需要）
# 添加新的触发关键词
```

**4. 提交版本控制**
```bash
git add interpretations/{id}
git commit -m "Add {id} interpretation module"
```

### 4.2 部署验证

**验证清单**：
- [ ] 文件已移动到正确位置
- [ ] 全局索引已更新
- [ ] 路由系统已更新
- [ ] Git提交已完成

**预计耗时**：6分钟

---

## 完整示例

### 示例：新增"公司法司法解释（2024）"

#### 步骤1：AI生成初稿

```bash
# 1. 查看待处理队列
cat queue.json
# 输出：[{"title": "最高人民法院关于适用《中华人民共和国公司法》若干问题的规定（四）", "date": "2024-01-15", ...}]

# 2. 生成初稿
cd tools/generator
python draft-generator.py --queue

# 3. 查看生成结果
ls draft/
# 输出：corporate-law-2024/
```

#### 步骤2：人工审核修改

```bash
# 1. 阅读生成内容
cd draft/corporate-law-2024
cat README.md
cat index.md

# 2. 审核和修改
# 使用 review-checklist.md 审核
# 发现问题：条文解读不够准确，新旧对比不完整

# 3. 修改内容
# 重新核对官方文本，补充旧法内容，完善对比分析
```

#### 步骤3：验证测试

```bash
# 1. 自动化验证
python tools/validator/validate.py --id corporate-law-2024 --full

# 2. 手动测试
# 测试场景：快速查询"股东代表诉讼"
# 加载 index.md → 查找相关条文 → 验证内容准确性
```

#### 步骤4：部署上线

```bash
# 1. 移动到正式目录
mv draft/corporate-law-2024 ../../interpretations/

# 2. 更新全局索引
# 编辑 interpretations/metadata.json，添加新模块

# 3. 提交版本控制
git add interpretations/corporate-law-2024
git commit -m "Add corporate-law-2024 interpretation module"
```

**总耗时**：约1小时

---

## 异常处理

### 异常1：AI生成质量差

**表现**：
- 条文解读错误
- 新旧法对比不准确
- 内容不完整

**处理**：
- ⚠️ 返回修改
- 使用模板手动创建
- 或调整AI提示词后重新生成

### 异常2：Token超标

**表现**：
- README.md > 1,000 tokens
- index.md > 500 tokens
- article-X.md > 300 tokens

**处理**：
- ⚠️ 返回修改
- 精简内容，删除冗余
- 保留核心要点

### 异常3：验证失败

**表现**：
- 结构验证失败
- 链接无效
- 格式错误

**处理**：
- 修复错误
- 重新验证
- 或使用模板重新创建

---

## 版本管理

### 版本号规则

**模块版本**：
- 初始版本：v1.0.0
- 内容修正：v1.0.1、v1.0.2...
- 重大更新：v1.1.0、v1.2.0...
- 架构变更：v2.0.0

**全局版本**（metadata.json）：
- 新增模块：次版本+1（v3.0 → v3.1）
- 架构变更：主版本+1（v3 → v4）

### 更新日志

**格式**：
```markdown
## 更新日志

- YYYY-MM-DD: vX.X.X 初始版本，收录XX条索引
- YYYY-MM-DD: vX.X.Y 修正条文解读错误
- YYYY-MM-DD: vX.Y.0 补充XX个条文详解
```

---

## 最佳实践

### 1. 定期维护

**每周**：
- 运行监测工具
- 检查待处理队列

**每月**：
- 审核用户反馈
- 优化索引结构

**每季度**：
- 更新外部链接
- 优化Token估算

### 2. 质量优先

**原则**：
- 宁可慢一点，也要保证质量
- 法律准确性永远是第一位的
- 深度分析是核心竞争力

**实践**：
- 充分的人工审核时间
- 使用权威数据源验证
- 参考多个专业解读

### 3. 持续改进

**收集反馈**：
- 用户使用反馈
- 测试发现问题
- 性能优化建议

**优化迭代**：
- 优化AI生成提示词
- 改进模板结构
- 完善工作流程

---

## 工具支持

### 自动化工具

- **监测工具**：tools/monitor/court-monitor.py
- **生成工具**：tools/generator/draft-generator.py
- **验证工具**：tools/validator/validate.py

### 文档参考

- **审核清单**：tools/workflows/review-checklist.md
- **模板说明**：interpretations/_template/
- **系统说明**：interpretations/README.md

---

**版本**：v3.0.0
**最后更新**：2026-01-16
**维护者**：china-lawyer-analyst 项目组
