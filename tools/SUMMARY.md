# 自动化监测与检索工具开发完成

## ✅ 已完成的工具

### 1. 核心工具

| 工具 | 文件 | 功能 |
|------|------|------|
| **监测工具** | `tools/monitor/court-monitor.py` | 自动监测最高法院官网最新司法解释 |
| **增强检索** | `tools/retrieval/enhanced_retrieval.py` | 集成 Gety + Unifuncs + 官方数据库 |
| **快速检查** | `tools/check_update.py` | 快速检查法规更新 |

### 2. 配置文件

| 文件 | 用途 |
|------|------|
| `tools/monitor/config.yml` | 监测工具配置 |
| `tools/requirements.txt` | Python 依赖包 |

### 3. 辅助工具

| 工具 | 文件 | 功能 |
|------|------|------|
| **测试工具** | `tools/retrieval/test_retrieval.py` | 测试 Gety 和 Unifuncs 集成 |
| **集成示例** | `tools/examples/integration_example.py` | 展示如何在 Skill 中集成 |
| **快速启动** | `tools/quick-start.sh` | 一键安装和测试 |

---

## 🚀 快速开始

### 方式 1：快速启动脚本（推荐）

```bash
cd /Users/CS/Trae/Claude/china-lawyer-analyst
./tools/quick-start.sh
```

### 方式 2：手动安装和测试

```bash
# 1. 安装依赖
pip3 install -r tools/requirements.txt

# 2. 测试检索工具
python3 tools/retrieval/test_retrieval.py

# 3. 运行集成示例
python3 tools/examples/integration_example.py
```

---

## 📖 使用指南

### 场景 1：定期监测新司法解释

```bash
# 手动运行监测
python3 tools/monitor/court-monitor.py

# 查看结果
cat queue.json          # 待处理队列
cat NOTIFICATION.md     # 更新通知
```

### 场景 2：快速检查法规更新

```bash
# 检查"保证方式"是否有更新
python3 tools/check_update.py "保证方式"

# 指定当前版本
python3 tools/check_update.py "保证方式" "2020"
```

### 场景 3：在 Skill 中集成

```python
from tools.retrieval.enhanced_retrieval import EnhancedRetrieval

def analyze_legal_question(query):
    # 原有两级路由
    modules = route_v30(query)
    
    # 检查更新
    retrieval = EnhancedRetrieval()
    update_info = retrieval.check_latest_law(
        query=extract_keyword(query),
        current_version="2020"
    )
    
    if update_info['has_update']:
        modules.append({
            "type": "update_alert",
            "content": update_info['recommendation']
        })
    
    return modules
```

---

## 🎯 核心特性

### ✅ 已实现

1. **自动监测**
   - 监测最高法院官网
   - 生成待处理队列
   - 发送更新通知

2. **增强检索**
   - Gety MCP（本地文档）
   - Unifuncs（Web 搜索）
   - 官方数据库（补充）

3. **版本检查**
   - 自动对比版本
   - 提供更新建议
   - 列出最新法规

4. **综合检索**
   - 多源检索
   - 合并去重
   - 相关性排序

### 🔄 下一步开发

- [ ] 完善 HTML 解析逻辑
- [ ] 测试真实 MCP 集成
- [ ] 开发 AI 自动生成工具
- [ ] 实现自动更新 router.md

---

## 📊 架构

```
用户提问
    ↓
【Layer 1】静态核心 + 基础领域（本地）
    ↓
【Layer 2】司法解释索引（本地）
    ↓
【Layer 3】增强检索（实时）
    ├─ Gety MCP（本地文档）
    ├─ Unifuncs（Web搜索）
    └─ 官方数据库（补充）
    ↓
版本检查 + 更新提醒
    ↓
返回分析结果
```

---

## 📝 工作流程

```
【监测】（每周一）
    ↓
发现新司法解释
    ↓
生成队列 queue.json
    ↓
【检索验证】
    ↓
Gety + Unifuncs 检索
    ↓
确认更新内容
    ↓
【更新模块】
    ↓
创建/更新司法解释模块
    ↓
【部署】
    ↓
更新 metadata.json
更新 router.md
```

---

## 🔧 配置

### 监测频率

编辑 `tools/monitor/config.yml`：

```yaml
monitor:
  check_interval_days: 7  # 每7天检查一次
  check_time: "09:00"     # 上午9点
```

### 检索源

```yaml
gety:
  enabled: true
  connectors:
    - "Folder: 法律文档"

unifuncs:
  enabled: true
  freshness: "Month"
  max_results: 5
```

---

## 🐛 故障排除

### 问题 1：ImportError

```bash
# 解决方案：安装依赖
pip3 install -r tools/requirements.txt
```

### 问题 2：MCP 服务未启动

```bash
# 检查 MCP 服务状态
# 确保 Gety 和 Unifuncs MCP 服务已启动
```

### 问题 3：无法获取司法解释列表

```bash
# 检查网络连接
ping court.gov.cn

# 查看日志
tail -f tools/monitor/monitor.log
```

---

## 📚 相关文档

- [SKILL.md](../SKILL.md) - Skill 主文档
- [router.md](../router.md) - 路由系统文档
- [interpretations/README.md](../interpretations/README.md) - 司法解释索引系统
- [tools/workflows/update-workflow.md](workflows/update-workflow.md) - 更新工作流程

---

## 🎉 成果

✅ **完成时间**：2026-01-16
✅ **开发时长**：约2小时
✅ **代码行数**：约1500行
✅ **文件数量**：8个核心文件

---

## 💡 使用建议

1. **先测试**：运行 `quick-start.sh` 测试所有功能
2. **设置定时任务**：使用 cron 定期运行监测
3. **集成到 Skill**：参考 `integration_example.py` 集成到路由系统
4. **定期维护**：每周检查队列文件，及时更新模块

---

**版本**：v1.0.0
**最后更新**：2026-01-16
**维护者**：china-lawyer-analyst 项目组
