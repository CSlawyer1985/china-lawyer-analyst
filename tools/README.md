# 自动化监测与检索工具

## 概述

本工具集为 china-lawyer-analyst v3.0 提供自动化监测和增强检索能力。

**功能**：
1. ✅ 自动监测最高法院官网发布的最新司法解释
2. ✅ 集成 Gety MCP 检索本地文档库
3. ✅ 集成 Unifuncs 进行 Web 搜索和页面提取
4. ✅ 检查法规更新，提供版本对比建议
5. ✅ 生成待处理队列，辅助模块更新

---

## 快速开始

### 1. 监测新司法解释

```bash
cd tools/monitor
python court-monitor.py
```

### 2. 增强检索

```python
from tools.retrieval.enhanced_retrieval import EnhancedRetrieval

retrieval = EnhancedRetrieval()

# 综合检索
results = retrieval.search("保证方式")

# 检查更新
update_info = retrieval.check_latest_law("保证方式", current_version="2020")
```

### 3. 运行测试

```bash
cd tools/retrieval
python test_retrieval.py
```

---

## 工具列表

| 工具 | 文件 | 功能 |
|------|------|------|
| 监测工具 | `tools/monitor/court-monitor.py` | 自动监测最新司法解释 |
| 检索工具 | `tools/retrieval/enhanced_retrieval.py` | 增强检索（Gety + Unifuncs） |
| 测试工具 | `tools/retrieval/test_retrieval.py` | 测试集成功能 |
| 配置文件 | `tools/monitor/config.yml` | 工具配置 |

---

## 版本

v1.0.0 - 2026-01-16
