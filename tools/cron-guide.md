# Cron 定时任务配置指南

## 概述

设置定时任务，自动运行司法解释监测工具。

---

## 快速设置

### 方法 1：使用脚本自动添加（推荐）

```bash
# 运行设置脚本
cd /Users/CS/Trae/Claude/china-lawyer-analyst
./tools/setup-cron.sh
```

### 方法 2：手动添加

```bash
# 1. 编辑 crontab
crontab -e

# 2. 添加以下行
# 每周一上午9:00运行监测
0 9 * * 1 cd /Users/CS/Trae/Claude/china-lawyer-analyst && python3 tools/monitor/court-monitor.py >> tools/monitor/cron.log 2>&1
```

---

## Cron 表达式说明

### 基本格式

```
* * * * * 命令
│ │ │ │ │
│ │ │ │ └─ 星期几（0-7，0和7都表示周日）
│ │ │ └─── 月份（1-12）
│ │ └───── 日期（1-31）
│ └─────── 小时（0-23）
└───────── 分钟（0-59）
```

### 常用示例

| 表达式 | 说明 |
|--------|------|
| `0 9 * * 1` | 每周一上午9:00 |
| `0 9 * * *` | 每天上午9:00 |
| `0 */6 * * *` | 每6小时 |
| `0 0 * * 0` | 每周日午夜 |
| `0 9 1 * *` | 每月1号上午9:00 |

---

## 推荐配置

### 配置 1：每周监测（推荐）

```bash
# 每周一上午9:00监测新司法解释
0 9 * * 1 cd /Users/CS/Trae/Claude/china-lawyer-analyst && python3 tools/monitor/court-monitor.py >> tools/monitor/cron.log 2>&1
```

**优点**：
- ✅ 及时发现新司法解释
- ✅ 不影响工作日使用
- ✅ 日志便于排查问题

### 配置 2：每日监测

```bash
# 每天上午9:00监测
0 9 * * * cd /Users/CS/Trae/Claude/china-lawyer-analyst && python3 tools/monitor/court-monitor.py >> tools/monitor/cron.log 2>&1
```

**适用场景**：
- 需要更及时的更新
- 重要的司法解释发布期

### 配置 3：仅监测工作日

```bash
# 周一到周五上午9:00
0 9 * * 1-5 cd /Users/CS/Trae/Claude/china-lawyer-analyst && python3 tools/monitor/court-monitor.py >> tools/monitor/cron.log 2>&1
```

---

## 日志管理

### 查看日志

```bash
# 查看最新日志
tail -f tools/monitor/cron.log

# 查看最近100行
tail -n 100 tools/monitor/cron.log

# 搜索错误
grep "ERROR" tools/monitor/cron.log
```

### 日志轮转（可选）

```bash
# 在 crontab 中添加日志清理任务
# 每月1号清理旧日志
0 0 1 * * cd /Users/CS/Trae/Claude/china-lawyer-analyst && find tools/monitor/ -name "*.log" -mtime +90 -delete
```

---

## 监控cron任务

### 查看已安装的cron任务

```bash
# 查看当前用户的crontab
crontab -l

# 查看cron执行日志（macOS）
log show --predicate 'process == "cron"' --last 1h
```

### 测试cron任务

```bash
# 手动运行测试
cd /Users/CS/Trae/Claude/china-lawyer-analyst
python3 tools/monitor/court-monitor.py

# 检查是否生成队列文件
ls -la queue.json NOTIFICATION.md
```

---

## 故障排除

### 问题 1：cron任务没有执行

**检查步骤**：

1. **确认cron服务运行中**
   ```bash
   # macOS
   sudo launchctl list | grep cron

   # Linux
   sudo systemctl status cron
   ```

2. **检查crontab语法**
   ```bash
   crontab -l
   ```

3. **查看系统日志**
   ```bash
   # macOS
   log show --predicate 'process == "cron"' --last 1h

   # Linux
   sudo tail -f /var/log/syslog | grep CRON
   ```

### 问题 2：脚本执行失败

**检查步骤**：

1. **查看cron日志**
   ```bash
   cat tools/monitor/cron.log
   ```

2. **检查Python路径**
   ```bash
   # 在crontab中指定完整Python路径
   which python3
   # 输出：/usr/local/bin/python3（示例）

   # 修改crontab为：
   0 9 * * 1 cd /Users/CS/Trae/Claude/china-lawyer-analyst && /usr/local/bin/python3 tools/monitor/court-monitor.py >> tools/monitor/cron.log 2>&1
   ```

3. **检查工作目录权限**
   ```bash
   ls -la /Users/CS/Trae/Claude/china-lawyer-analyst
   ```

### 问题 3：发送通知失败

**解决方案**：

使用macOS通知：
```bash
# 在脚本最后添加通知命令
osascript -e 'display notification "发现新司法解释" with title "China Lawyer Analyst"'
```

---

## 完整示例配置

### crontab 完整示例

```bash
# 编辑 crontab
crontab -e

# 添加以下内容：

# china-lawyer-analyst 司法解释监测任务

# 每周一上午9:00监测新司法解释
0 9 * * 1 cd /Users/CS/Trae/Claude/china-lawyer-analyst && /usr/local/bin/python3 tools/monitor/court-monitor.py >> tools/monitor/cron.log 2>&1

# 每月1号清理90天前的日志
0 0 1 * * cd /Users/CS/Trae/Claude/china-lawyer-analyst && find tools/monitor/ -name "*.log" -mtime +90 -delete

# 每周日午夜发送通知（可选）
0 0 * * 0 cd /Users/CS/Trae/Claude/china-lawyer-analyst && if [ -f NOTIFICATION.md ]; then osascript -e 'display notification "发现新司法解释" with title "China Lawyer Analyst"'; fi
```

---

## 卸载

### 移除cron任务

```bash
# 编辑crontab
crontab -e

# 删除相关行，保存退出
```

### 或使用命令清空

```bash
# 备份当前crontab
crontab -l > crontab-backup.txt

# 清空crontab
crontab -r

# 重新添加其他任务（如有）
crontab -e
```

---

## 最佳实践

1. **使用完整路径**
   - Python路径：`/usr/local/bin/python3`
   - 工作目录：`/Users/CS/Trae/Claude/china-lawyer-analyst`

2. **记录日志**
   - 将输出重定向到日志文件
   - 定期清理旧日志

3. **设置合理频率**
   - 监测任务：每周一次即可
   - 避免频繁请求官网

4. **错误处理**
   - 使用 `2>&1` 捕获错误输出
   - 定期检查日志

---

**版本**：v1.0.0
**最后更新**：2026-01-16
**维护者**：china-lawyer-analyst 项目组
