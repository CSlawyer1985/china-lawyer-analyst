#!/bin/bash
# China Lawyer Analyst v2.0 - GitHub 发布脚本

echo "======================================"
echo "China Lawyer Analyst v2.0 发布脚本"
echo "======================================"
echo ""

# 配置变量（请修改为你的实际信息）
GITHUB_USERNAME="YOUR_USERNAME"  # ← 替换为你的 GitHub 用户名
REPO_NAME="china-lawyer-analyst"
REPO_DESCRIPTION="中国法律分析 Claude Skill - MOE架构 v2.0，按需加载领域模块，Token优化37%"

echo "1. 检查 Git 仓库..."
if [ ! -d .git ]; then
    echo "❌ 错误：当前目录不是 Git 仓库"
    exit 1
fi
echo "✅ Git 仓库已就绪"
echo ""

echo "2. 当前提交信息："
git log -1 --oneline
echo ""

echo "3. 创建 GitHub 仓库..."
echo "   请访问以下 URL 创建仓库："
echo "   https://github.com/new"
echo ""
echo "   仓库名称：$REPO_NAME"
echo "   描述：$REPO_DESCRIPTION"
echo "   可见性：根据需要选择 Public 或 Private"
echo "   ⚠️  不要初始化 README、.gitignore 或 license（已存在）"
echo ""

read -p "按回车键继续，仓库创建完成后按回车..."

echo ""
echo "4. 添加远程仓库..."
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo "✅ 远程仓库已添加：origin → https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo ""

echo "5. 推送到 GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 发布成功！"
    echo ""
    echo "仓库地址："
    echo "  https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "下一步："
    echo "  1. 访问仓库，添加描述和 Topics（建议：law, ai, claude, moe, chinese-law）"
    echo "  2. 在 About 部分添加项目说明"
    echo "  3. 考虑添加 LICENSE（推荐 MIT License）"
else
    echo ""
    echo "❌ 推送失败，请检查："
    echo "  1. GitHub 用户名是否正确（当前：$GITHUB_USERNAME）"
    echo "  2. 仓库是否已创建"
    echo "  3. 是否需要 GitHub 身份验证（Personal Access Token）"
    echo ""
    echo "手动推送命令："
    echo "  git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
fi
