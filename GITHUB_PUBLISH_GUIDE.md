# GitHub 发布指南

## 快速发布（5分钟）

### 步骤 1：创建 GitHub 仓库

1. 访问：https://github.com/new
2. 填写信息：
   - **Repository name**：`china-lawyer-analyst`
   - **Description**：`中国法律分析 Claude Skill - MOE架构 v2.0，按需加载领域模块，Token优化37%`
   - **Visibility**：Public 或 Private（根据需要选择）
   - **⚠️ 重要**：不要勾选 "Add a README file"（已存在）

3. 点击 "Create repository"

### 步骤 2：获取 GitHub 用户名

查看你的 GitHub 主页 URL：
- `https://github.com/你的用户名/china-lawyer-analyst`

### 步骤 3：推送代码

```bash
cd /Users/CS/Trae/Claude/china-lawyer-analyst

# 替换 YOUR_USERNAME 为你的实际 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/china-lawyer-analyst.git
git branch -M main
git push -u origin main
```

### 步骤 4：验证

访问：`https://github.com/YOUR_USERNAME/china-lawyer-analyst`

应该能看到 29 个文件，包括：
- SKILL.md（v2.0 主入口）
- SKILL-v1.md（v1.0 完整版）
- README.md（使用说明）
- core/、domains/、shared/（模块目录）

---

## 进阶配置（可选）

### 添加 Topics（标签）

在仓库页面 → Settings → Topics，添加：
- `law`
- `ai`
- `claude`
- `chinese-law`
- `moe`
- `legal-analysis`

### 添加 License

推荐使用 **MIT License**：
1. Settings → Licenses
2. 选择 "MIT License"
3. 填写年份：`2026`
4. 填写作者：`陈石律师（浙江海泰律师事务所）`

### 设置仓库描述

Settings → General → Description：
```
中国法律分析 Claude Skill - MOE架构 v2.0

✅ 智能路由系统（100%准确率）
✅ 按需加载模块（Token节省37%）
✅ 8大法律领域覆盖
✅ 10步法中国法律分析流程

作者：陈石律师（浙江海泰律师事务所）
技术支持：Claude Code + Claude Agent SDK
```

### 设置仓库网站

Settings → General → Website：
```
https://claude.ai/claude-code
```

---

## 常见问题

### Q1：推送时提示 "Permission denied"

**原因**：需要 GitHub 身份验证

**解决**：
```bash
# 使用 Personal Access Token（推荐）
# 1. 生成 Token：https://github.com/settings/tokens
# 2. 选择权限：repo（全选）
# 3. 使用 Token 推送：
git remote set-url origin https://TOKEN@github.com/YOUR_USERNAME/china-lawyer-analyst.git
git push -u origin main
```

### Q2：提示 "repository already exists"

**原因**：远程仓库已添加

**解决**：
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/china-lawyer-analyst.git
git push -u origin main
```

### Q3：想使用 SSH 而不是 HTTPS

**解决**：
```bash
git remote set-url origin git@github.com:YOUR_USERNAME/china-lawyer-analyst.git
git push -u origin main
```

---

## 发布成功后的下一步

1. **验证文件完整性**：检查所有 29 个文件都已上传
2. **测试 clone**：`git clone https://github.com/YOUR_USERNAME/china-lawyer-analyst.git`
3. **分享仓库**：复制仓库 URL 分享给其他人
4. **设置 Stars**：自己 Star 一下，方便后续查找

---

**需要帮助？**

如果遇到问题，请提供：
1. 错误信息截图
2. 执行的命令
3. GitHub 用户名和仓库名
