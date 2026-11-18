#!/usr/bin/env bash
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DEST="$HOME/.codex/skills/market-radar"

echo "=== [1/3] 检查基础运行环境 ==="
python3 --version
gh --version | head -n 1 || echo "提示: 未检测到 gh CLI，可通过 brew install gh 安装"

echo "=== [2/3] 安装/更新团队共享技能 (market-radar) 至 ~/.codex/skills/ ==="
mkdir -p "$SKILL_DEST/scripts"
cp -f "$REPO_ROOT/SKILL.md" "$SKILL_DEST/SKILL.md"
cp -f "$REPO_ROOT/scripts/"*.py "$REPO_ROOT/scripts/"*.json "$REPO_ROOT/scripts/"*.html "$REPO_ROOT/scripts/"*.js "$SKILL_DEST/scripts/" 2>/dev/null || true
echo "已同步 Skill 至: $SKILL_DEST"

echo "=== [3/3] 检查 DeepSeek-V4.1-Flash / Harness 环境变量模板 ==="
ENV_EXAMPLE="$REPO_ROOT/team-toolkit/.env.template"
cat <<'EOT' > "$ENV_EXAMPLE"
# 团队统一模型配置模板 (复制为项目根目录 .env 使用，切勿提交真实 Key 至 Git)
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4.1-flash
DEEPSEEK_API_KEY=your_api_key_here
EOT
echo "已生成配置模板: $ENV_EXAMPLE"
echo "=== 团队工具链初始化完成 ==="
