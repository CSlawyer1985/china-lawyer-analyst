# China Lawyer Analyst v3.0 - 用户使用指南

## 🎯 快速开始

### 第一次使用？

```bash
cd /Users/CS/Trae/Claude/china-lawyer-analyst

# 一键安装和测试
./tools/quick-start.sh

# 设置定时任务（可选）
./tools/setup-cron.sh
```

---

## 📚 三种使用方式

### 方式 1：作为 Skill 使用（推荐）

在 Claude Code 中调用：

```
请使用 china-lawyer-analyst skill 分析以下法律问题：
[粘贴案件事实或法律问题]
```

**功能**：
- ✅ 自动识别法律领域
- ✅ 按需加载模块（Token 优化 56%）
- ✅ 智能条文加载
- ✅ 检查最新法规（v3.1 新增）

### 方式 2：命令行检索工具

```bash
# 检查法规更新
python3 tools/check_update.py "保证方式"

# 查看帮助
python3 tools/check_update.py
```

### 方式 3：Python API 集成

```python
from tools.retrieval.enhanced_retrieval import EnhancedRetrieval

# 创建检索器
retrieval = EnhancedRetrieval()

# 综合检索
results = retrieval.search("保证方式")

# 检查更新
update_info = retrieval.check_latest_law("保证方式", "2020")
```

---

## 🔍 核心功能

### 1. 两级路由系统（v3.0）

**一级路由**：静态核心 + 基础领域
- 自动识别8大法律领域
- 按需加载领域模块

**二级路由**：司法解释索引
- 智能检测司法解释需求
- 索引优先（~500 tokens）
- 按需加载条文（~300 tokens/条文）

### 2. 实时检索增强（v3.1）

**三级路由**：实时检索增强
- **Gety MCP**：检索本地文档库
- **Unifuncs**：Web 搜索最新法规
- **官方数据库**：12个权威数据库入口
- **版本检查**：自动对比版本，提供更新建议

### 3. 自动监测功能

- 监测最高法院官网
- 每周自动检查新司法解释
- 生成待处理队列
- 发送更新通知

---

## 📊 Token 优化效果

| 问题类型 | v2.2 Token | v3.0 Token | 节省率 |
|---------|-----------|-----------|--------|
| 担保合同纠纷 | 37,958 | 17,900 | 52.8% |
| 预约合同纠纷 | 37,958 | 13,900 | 63.4% |
| **平均节省** | - | - | **56.2%** |

---

## 🛠️ 工具使用

### 监测新司法解释

```bash
# 手动运行监测
python3 tools/monitor/court-monitor.py

# 查看结果
cat queue.json          # 待处理队列
cat NOTIFICATION.md     # 更新通知
```

### 检查法规更新

```bash
# 快速检查
python3 tools/check_update.py "保证方式"

# 指定当前版本
python3 tools/check_update.py "保证方式" "2020"
```

### 测试检索功能

```bash
# 运行测试套件
python3 tools/retrieval/test_retrieval.py

# 运行集成示例
python3 tools/examples/integration_example.py
```

---

## ⏰ 定时任务设置

### 自动设置（推荐）

```bash
./tools/setup-cron.sh
```

### 手动设置

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每周一上午9:00运行）
0 9 * * 1 cd /Users/CS/Trae/Claude/china-lawyer-analyst && python3 tools/monitor/court-monitor.py >> tools/monitor/cron.log 2>&1
```

详细说明：[tools/cron-guide.md](tools/cron-guide.md)

---

## 📖 文档导航

### 核心文档
- [SKILL.md](../SKILL.md) - Skill 主文档
- [router.md](../router.md) - 路由系统说明
- [metadata.json](../metadata.json) - 元数据索引

### 司法解释模块
- [interpretations/README.md](../interpretations/README.md) - 索引系统说明
- [interpretations/security-law-2020/README.md](../interpretations/security-law-2020/README.md) - 担保制度解释
- [interpretations/contract-general-2023/README.md](../interpretations/contract-general-2023/README.md) - 合同编通则解释

### 工具文档
- [tools/README.md](tools/README.md) - 工具使用说明
- [tools/SUMMARY.md](tools/SUMMARY.md) - 开发完成总结
- [tools/cron-guide.md](tools/cron-guide.md) - Cron 配置指南
- [tools/workflows/update-workflow.md](tools/workflows/update-workflow.md) - 更新工作流程

---

## 🎓 使用场景

### 场景 1：合同纠纷分析

**输入**：
```
甲乙公司签订软件开发合同，约定2023年6月30日前交付。
乙方延迟交付1.5周，且软件存在缺陷。甲方拒绝付款。
```

**系统行为**：
1. 识别领域：`contract-law`
2. 加载模块：核心模块 + 合同法领域
3. Token消耗：~17,800（节省 53.1%）

### 场景 2：担保合同纠纷（含更新检查）

**输入**：
```
甲公司向乙银行借款，丙公司提供保证担保，
保证合同约定"丙公司承担保证责任"，未约定保证方式。
```

**系统行为**：
1. 识别领域：`investment-law`
2. 加载模块：核心模块 + 投融资领域 + 担保制度索引
3. **检查更新**：检测是否有2024年新规定
4. Token消耗：~21,000（节省 44.7%）

### 场景 3：查询最新法规

**输入**：
```
2024年最新的预约合同规定有哪些变化？
```

**系统行为**：
1. 识别领域：`contract-law`
2. 加载模块：核心模块 + 合同法领域 + 合同编通则索引
3. **触发增强检索**：
   - 检索 Unifuncs（2024年最新内容）
   - 检索官方数据库
   - 提供更新建议
4. 返回综合结果

---

## 💡 最佳实践

### 1. 定期更新

- ✅ 每周自动运行监测工具
- ✅ 关注更新通知（NOTIFICATION.md）
- ✅ 及时更新司法解释模块

### 2. 合理使用

- ✅ 简单问题：使用 Skill 调用
- ✅ 复杂问题：提供详细案情
- ✅ 最新法规：明确注明时间要求

### 3. 结果验证

- ✅ 重要案件：咨询专业律师
- ✅ 系统提示：注意更新提醒
- ✅ 多源验证：对比多个数据源

---

## 🔧 故障排除

### 问题 1：Skill 加载失败

**检查**：
```bash
# 查看文件是否存在
ls SKILL.md router.md metadata.json

# 检查版本
cat metadata.json | grep version
```

### 问题 2：检索工具无结果

**检查**：
```bash
# 运行测试
python3 tools/retrieval/test_retrieval.py

# 检查依赖
pip3 list | grep -E "(requests|beautifulsoup4|yaml)"
```

### 问题 3：Cron 任务未执行

**检查**：
```bash
# 查看日志
tail -f tools/monitor/cron.log

# 查看 cron 任务
crontab -l | grep court-monitor
```

---

## 📈 版本历史

### v3.1.0 (2026-01-16)
- ✅ 新增：实时检索增强（三级路由）
- ✅ 新增：Gety MCP 集成
- ✅ 新增：Unifuncs 集成
- ✅ 新增：版本自动检查
- ✅ 新增：自动化监测工具
- ✅ 优化：Token 节省提升到 56.2%

### v3.0.0 (2026-01-16)
- ✅ 重大架构升级：混合架构
- ✅ 司法解释索引系统
- ✅ 两级路由系统
- ✅ 迁移完成：2个司法解释模块

### v2.2.0
- ✅ MOE 架构改造
- ✅ 按需加载领域模块

---

## 🎉 快速上手

1. **安装依赖**
   ```bash
   pip3 install -r tools/requirements.txt
   ```

2. **运行测试**
   ```bash
   ./tools/quick-start.sh
   ```

3. **设置定时任务**
   ```bash
   ./tools/setup-cron.sh
   ```

4. **开始使用**
   ```
   请使用 china-lawyer-analyst skill 分析以下法律问题：
   [您的问题]
   ```

---

## 📞 获取帮助

- **查看文档**：[tools/README.md](tools/README.md)
- **查看示例**：[tools/examples/integration_example.py](tools/examples/integration_example.py)
- **运行测试**：`python3 tools/retrieval/test_retrieval.py`

---

**制作团队**：陈石律师（浙江海泰律师事务所）
**技术支持**：Claude Code + Claude Agent SDK
**架构设计**：混合架构（Mixture of Experts + 动态索引）
**版本**：v3.1.0
**最后更新**：2026-01-16
